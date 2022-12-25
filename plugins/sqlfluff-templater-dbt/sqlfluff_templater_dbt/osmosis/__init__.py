# type: ignore
import dbt.adapters.factory

# This is critical because `get_adapter` is all over dbt-core
# as they expect a singleton adapter instance per plugin,
# so dbt-niceDatabase will have one adapter instance named niceDatabase.
# This makes sense in dbt-land where we have a single Project/Profile
# combination executed in process from start to finish or a single tenant RPC
# This doesn't fit our paradigm of one adapter per DbtProject in a multitenant server,
# so we create an adapter instance **independent** of the FACTORY cache
# and attach it directly to our RuntimeConfig which is passed through
# anywhere dbt-core needs config including in all `get_adapter` calls
dbt.adapters.factory.get_adapter = lambda config: config.adapter

import os
import re
import threading
import time
import uuid
from collections import OrderedDict, UserDict
from copy import copy
from enum import Enum
from functools import lru_cache, partial
from hashlib import md5
from itertools import chain
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import agate
from dbt.adapters.base import BaseRelation
from dbt.adapters.factory import Adapter, get_adapter_class_by_name
from dbt.clients import jinja  # monkey-patched for perf
from dbt.config.runtime import RuntimeConfig
from dbt.context.providers import generate_runtime_model_context
from dbt.contracts.connection import AdapterResponse
from dbt.contracts.graph.manifest import (
    ManifestNode,
    MaybeNonSource,
    MaybeParsedSource,
)
from dbt.events.functions import fire_event  # monkey-patched for perf
from dbt.exceptions import CompilationException, InternalException, RuntimeException
from dbt.flags import DEFAULT_PROFILES_DIR, set_from_args
from dbt.node_types import NodeType
from dbt.parser.manifest import ManifestLoader, process_node
from dbt.parser.sql import SqlBlockParser, SqlMacroParser
from dbt.task.sql import SqlCompileRunner, SqlExecuteRunner
from dbt.tracking import disable_tracking
from dbt.version import __version__ as dbt_version
from pydantic import BaseModel
from rich.progress import track
from ruamel.yaml import YAML

from .exceptions import (
    InvalidOsmosisConfig,
    MissingOsmosisConfig,
    SanitizationRequired,
)
from .log_controller import logger
from .patch import write_manifest_for_partial_parse

__all__ = [
    "DbtProject",
    "DbtProjectContainer",
    "DbtYamlManager",
    "ConfigInterface",
    "has_jinja",
    "DbtOsmosis",  # for compat
]

CACHE = {}
CACHE_VERSION = 1
SQL_CACHE_SIZE = 1024

MANIFEST_ARTIFACT = "manifest.json"
DBT_MAJOR_VER, DBT_MINOR_VER, DBT_PATCH_VER = (
    int(v) for v in re.search(r"^([0-9\.])+", dbt_version).group().split(".")
)
RAW_CODE = "raw_code" if DBT_MAJOR_VER >= 1 and DBT_MINOR_VER >= 3 else "raw_sql"
COMPILED_CODE = (
    "compiled_code" if DBT_MAJOR_VER >= 1 and DBT_MINOR_VER >= 3 else "compiled_sql"
)

JINJA_CONTROL_SEQS = ["{{", "}}", "{%", "%}", "{#", "#}"]

T = TypeVar("T")


def has_jinja(query: str) -> bool:
    """Utility to check for jinja prior to certain compilation procedures"""
    return any(seq in query for seq in JINJA_CONTROL_SEQS)


def memoize_get_rendered(function):
    """Custom memoization function for dbt-core jinja interface"""

    def wrapper(
        string: str,
        ctx: Dict[str, Any],
        node: ManifestNode = None,
        capture_macros: bool = False,
        native: bool = False,
    ):
        v = md5(string.strip().encode("utf-8")).hexdigest()
        v += "__" + str(CACHE_VERSION)
        if capture_macros == True and node is not None:
            if node.is_ephemeral:
                return function(string, ctx, node, capture_macros, native)
            v += "__" + node.unique_id
        rv = CACHE.get(v)
        if rv is not None:
            return rv
        else:
            rv = function(string, ctx, node, capture_macros, native)
            CACHE[v] = rv
            return rv

    return wrapper


# Performance hacks
# jinja.get_rendered = memoize_get_rendered(jinja.get_rendered)
disable_tracking()
fire_event = lambda e: None


class ConfigInterface:
    """This mimic dbt-core args based interface for dbt-core
    class instantiation"""

    def __init__(
        self,
        threads: Optional[int] = 1,
        target: Optional[str] = None,
        profiles_dir: Optional[str] = None,
        project_dir: Optional[str] = None,
        vars: Optional[str] = "{}",
    ):
        self.threads = threads
        if target:
            self.target = target  # We don't want target in args context if it is None
        self.profiles_dir = profiles_dir or DEFAULT_PROFILES_DIR
        self.project_dir = project_dir
        self.vars = vars  # json.dumps str
        self.dependencies = []
        self.single_threaded = threads == 1
        self.quiet = True

    @classmethod
    def from_str(cls, arguments: str) -> "ConfigInterface":
        import argparse
        import shlex

        parser = argparse.ArgumentParser()
        args = parser.parse_args(shlex.split(arguments))
        return cls(
            threads=args.threads,
            target=args.target,
            profiles_dir=args.profiles_dir,
            project_dir=args.project_dir,
        )


class YamlHandler(YAML):
    """A `ruamel.yaml` wrapper to handle dbt YAML files with sane defaults"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.indent(mapping=2, sequence=4, offset=2)
        self.width = 800
        self.preserve_quotes = True
        self.default_flow_style = False


class ManifestProxy(UserDict):
    """Proxy for manifest dictionary (`flat_graph`), if we need mutation then we should
    create a copy of the dict or interface with the dbt-core manifest object instead"""

    def _readonly(self, *args, **kwargs):
        raise RuntimeError("Cannot modify ManifestProxy")

    __setitem__ = _readonly
    __delitem__ = _readonly
    pop = _readonly
    popitem = _readonly
    clear = _readonly
    update = _readonly
    setdefault = _readonly


class DbtAdapterExecutionResult:
    """Interface for execution results, this keeps us 1 layer removed from dbt interfaces which may change"""

    def __init__(
        self,
        adapter_response: AdapterResponse,
        table: agate.Table,
        raw_sql: str,
        compiled_sql: str,
    ) -> None:
        self.adapter_response = adapter_response
        self.table = table
        self.raw_sql = raw_sql
        self.compiled_sql = compiled_sql


class DbtAdapterCompilationResult:
    """Interface for compilation results, this keeps us 1 layer removed from dbt interfaces which may change"""

    def __init__(
        self,
        raw_sql: str,
        compiled_sql: str,
        node: ManifestNode,
        injected_sql: Optional[str] = None,
    ) -> None:
        self.raw_sql = raw_sql
        self.compiled_sql = compiled_sql
        self.node = node
        self.injected_sql = injected_sql


class DbtProject:
    """Container for a dbt project. The dbt attribute is the primary interface for
    dbt-core. The adapter attribute is the primary interface for the dbt adapter"""

    ADAPTER_TTL = 3600

    def __init__(
        self,
        target: Optional[str] = None,
        profiles_dir: Optional[str] = None,
        project_dir: Optional[str] = None,
        threads: Optional[int] = 1,
        vars: Optional[str] = "{}",
    ):
        self.args = ConfigInterface(
            threads=threads,
            target=target,
            profiles_dir=profiles_dir,
            project_dir=project_dir,
            vars=vars,
        )

        self.parse_project(init=True)

        # Utilities
        self._yaml_handler: Optional[YamlHandler] = None
        self._sql_parser: Optional[SqlBlockParser] = None
        self._macro_parser: Optional[SqlMacroParser] = None
        self._sql_runner: Optional[SqlExecuteRunner] = None
        self._sql_compiler: Optional[SqlCompileRunner] = None

        # Tracks internal state version
        self._version: int = 1
        self.mutex = threading.Lock() if not self.args.single_threaded else None
        # atexit.register(lambda dbt_project: dbt_project.adapter.connections.cleanup_all, self)

    def get_adapter(self):
        """This inits a new Adapter which is fundamentally different than
        the singleton approach in the core lib"""
        adapter_name = self.config.credentials.type
        return get_adapter_class_by_name(adapter_name)(self.config)

    def init_adapter(self):
        """Initialize a dbt adapter."""
        if hasattr(self, "_adapter"):
            self._adapter.connections.cleanup_all()
        # The setter verifies connection, resets TTL, and updates adapter ref on config
        self.adapter = self.get_adapter()

    @property
    def adapter(self):
        """dbt-core adapter with TTL and automatic reinstantiation"""
        if time.time() - self._adapter_ttl > self.ADAPTER_TTL:
            logger().info("TTL expired, reinitializing adapter!")
            self.init_adapter()
        return self._adapter

    @adapter.setter
    def adapter(self, adapter: Adapter):
        """Verify connection and reset TTL on adapter set, update adapter prop ref on config"""
        self._adapter = self._verify_connection(adapter)
        self._adapter_ttl = time.time()
        self.config.adapter = self.adapter

    def parse_project(self, init: bool = False) -> None:
        """Parses project on disk from `ConfigInterface` in args attribute, verifies connection
        to adapters database, mutates config, adapter, and dbt attributes"""
        if init:
            set_from_args(self.args, self.args)
            self.config = RuntimeConfig.from_args(self.args)
            self.init_adapter()

        project_parser = ManifestLoader(
            self.config,
            self.config.load_dependencies(),
            self.adapter.connections.set_query_header,
        )
        # temporarily patched so we write partial parse to correct directory until its fixed in dbt core
        project_parser.write_manifest_for_partial_parse = partial(
            write_manifest_for_partial_parse, project_parser
        )
        # endpatched (https://github.com/dbt-labs/dbt-core/blob/main/core/dbt/parser/manifest.py#L545)
        self.dbt = project_parser.load()
        self.dbt.build_flat_graph()
        project_parser.save_macros_to_adapter(self.adapter)
        self._sql_parser = None
        self._macro_parser = None
        self._sql_compiler = None
        self._sql_runner = None

    @classmethod
    def from_args(cls, args: ConfigInterface) -> "DbtProject":
        """Instatiate the DbtProject directly from a ConfigInterface instance"""
        return cls(
            target=args.target,
            profiles_dir=args.profiles_dir,
            project_dir=args.project_dir,
            threads=args.threads,
        )

    @property
    def yaml_handler(self) -> YamlHandler:
        """A YAML handler for loading and dumping yaml files on disk"""
        if self._yaml_handler is None:
            self._yaml_handler = YamlHandler()
        return self._yaml_handler

    @property
    def sql_parser(self) -> SqlBlockParser:
        """A dbt-core SQL parser capable of parsing and adding nodes to the manifest via `parse_remote` which will
        also return the added node to the caller. Note that post-parsing this still typically requires calls to
        `_process_nodes_for_ref` and `_process_sources_for_ref` from `dbt.parser.manifest`
        """
        if self._sql_parser is None:
            self._sql_parser = SqlBlockParser(self.config, self.dbt, self.config)
        return self._sql_parser

    @property
    def macro_parser(self) -> SqlMacroParser:
        """A dbt-core macro parser"""
        if self._macro_parser is None:
            self._macro_parser = SqlMacroParser(self.config, self.dbt)
        return self._macro_parser

    @property
    def sql_runner(self) -> SqlExecuteRunner:
        """A runner which is used internally by the `execute_sql` function of `dbt.lib`.
        The runners `node` attribute can be updated before calling `compile` or `compile_and_execute`.
        """
        if self._sql_runner is None:
            self._sql_runner = SqlExecuteRunner(
                self.config, self.adapter, node=None, node_index=1, num_nodes=1
            )
        return self._sql_runner

    @property
    def sql_compiler(self) -> SqlCompileRunner:
        """A runner which is used internally by the `compile_sql` function of `dbt.lib`.
        The runners `node` attribute can be updated before calling `compile` or `compile_and_execute`.
        """
        if self._sql_compiler is None:
            self._sql_compiler = SqlCompileRunner(
                self.config, self.adapter, node=None, node_index=1, num_nodes=1
            )
        return self._sql_compiler

    def _verify_connection(self, adapter: Adapter) -> Adapter:
        """Verification for adapter + profile. Used as a passthrough,
        ie: `self.adapter = _verify_connection(get_adapter(...))`
        This also seeds the master connection"""
        try:
            adapter.connections.set_connection_name()
            adapter.debug_query()
        except Exception as query_exc:
            raise RuntimeException("Could not connect to Database") from query_exc
        else:
            return adapter

    def adapter_probe(self) -> bool:
        """Check adapter connection, useful for long running processes such as the server or workbench"""
        if not hasattr(self, "adapter") or self.adapter is None:
            return False
        try:
            with self.adapter.connection_named("osmosis-heartbeat"):
                self.adapter.debug_query()
        except Exception:
            # TODO: we can decide to reinit the Adapter here
            return False
        logger().info("Heartbeat received for %s", self.project_name)
        return True

    def fn_threaded_conn(
        self, fn: Callable[..., T], *args, **kwargs
    ) -> Callable[..., T]:
        """Used for jobs which are intended to be submitted to a thread pool,
        the 'master' thread should always have an available connection for the duration of
        typical program runtime by virtue of the `_verify_connection` method.
        Threads however require singleton seeding"""

        def _with_conn() -> T:
            self.adapter.connections.set_connection_name()
            return fn(*args, **kwargs)

        return _with_conn

    def generate_runtime_model_context(self, node: ManifestNode):
        """Wraps dbt context provider"""
        return generate_runtime_model_context(node, self.config, self.dbt)

    @property
    def project_name(self) -> str:
        """dbt project name"""
        return self.config.project_name

    @property
    def project_root(self) -> str:
        """dbt project root"""
        return self.config.project_root

    @property
    def manifest(self) -> ManifestProxy:
        """dbt manifest dict"""
        return ManifestProxy(self.dbt.flat_graph)

    def safe_parse_project(self, reinit: bool = False) -> None:
        """This is used to reseed the DbtProject safely post-init. This is
        intended for use by the osmosis server"""
        if reinit:
            self.clear_caches()
        _config_pointer = copy(self.config)
        try:
            self.parse_project(init=reinit)
        except Exception as parse_error:
            self.config = _config_pointer
            raise parse_error
        self.write_manifest_artifact()

    def write_manifest_artifact(self) -> None:
        """Write a manifest.json to disk"""
        artifact_path = os.path.join(
            self.config.project_root, self.config.target_path, MANIFEST_ARTIFACT
        )
        self.dbt.write(artifact_path)

    def clear_caches(self) -> None:
        """Clear least recently used caches and reinstantiable container objects"""
        self.get_ref_node.cache_clear()
        self.get_source_node.cache_clear()
        self.get_macro_function.cache_clear()
        self.compile_sql.cache_clear()

    @lru_cache(maxsize=10)
    def get_ref_node(self, target_model_name: str) -> MaybeNonSource:
        """Get a `ManifestNode` from a dbt project model name"""
        return self.dbt.resolve_ref(
            target_model_name=target_model_name,
            target_model_package=None,
            current_project=self.config.project_name,
            node_package=self.config.project_name,
        )

    @lru_cache(maxsize=10)
    def get_source_node(
        self, target_source_name: str, target_table_name: str
    ) -> MaybeParsedSource:
        """Get a `ManifestNode` from a dbt project source name and table name"""
        return self.dbt.resolve_source(
            target_source_name=target_source_name,
            target_table_name=target_table_name,
            current_project=self.config.project_name,
            node_package=self.config.project_name,
        )

    def get_server_node(self, sql: str, node_name="name"):
        """Get a node for SQL execution against adapter"""
        self._clear_node(node_name)
        sql_node = self.sql_parser.parse_remote(sql, node_name)
        process_node(self.config, self.dbt, sql_node)
        return sql_node

    @lru_cache(maxsize=10)
    def get_node_by_path(self, path: str):
        """Find an existing node given relative file path."""
        for node in self.dbt.nodes.values():
            if node.original_file_path == path:
                return node
        return None

    @lru_cache(maxsize=100)
    def get_macro_function(self, macro_name: str) -> Callable[[Dict[str, Any]], Any]:
        """Get macro as a function which takes a dict via argument named `kwargs`,
        ie: `kwargs={"relation": ...}`

        make_schema_fn = get_macro_function('make_schema')\n
        make_schema_fn({'name': '__test_schema_1'})\n
        make_schema_fn({'name': '__test_schema_2'})"""
        return partial(
            self.adapter.execute_macro, macro_name=macro_name, manifest=self.dbt
        )

    def adapter_execute(
        self, sql: str, auto_begin: bool = False, fetch: bool = False
    ) -> Tuple[AdapterResponse, agate.Table]:
        """Wraps adapter.execute. Execute SQL against database"""
        return self.adapter.execute(sql, auto_begin, fetch)

    def execute_macro(
        self,
        macro: str,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Wraps adapter execute_macro. Execute a macro like a function."""
        return self.get_macro_function(macro)(kwargs=kwargs)

    def execute_sql(self, raw_sql: str) -> DbtAdapterExecutionResult:
        """Execute dbt SQL statement against database"""
        # if no jinja chars then these are synonymous
        compiled_sql = raw_sql
        if has_jinja(raw_sql):
            # jinja found, compile it
            compiled_sql = self.compile_sql(raw_sql).compiled_sql
        return DbtAdapterExecutionResult(
            *self.adapter_execute(compiled_sql, fetch=True),
            raw_sql,
            compiled_sql,
        )

    def execute_node(self, node: ManifestNode) -> DbtAdapterExecutionResult:
        """Execute dbt SQL statement against database from a ManifestNode"""
        raw_sql: str = getattr(node, RAW_CODE)
        compiled_sql: Optional[str] = getattr(node, COMPILED_CODE, None)
        if compiled_sql:
            # node is compiled, execute the SQL
            return self.execute_sql(compiled_sql)
        # node not compiled
        if has_jinja(raw_sql):
            # node has jinja in its SQL, compile it
            compiled_sql = self.compile_node(node).compiled_sql
        # execute the SQL
        return self.execute_sql(compiled_sql or raw_sql)

    @lru_cache(maxsize=SQL_CACHE_SIZE)
    def compile_sql(self, raw_sql: str, retry: int = 3) -> DbtAdapterCompilationResult:
        """Creates a node with `get_server_node` method. Compile generated node.
        Has a retry built in because even uuidv4 cannot gaurantee uniqueness at the speed
        in which we can call this function concurrently. A retry significantly increases the stability
        """
        temp_node_id = str(uuid.uuid4())
        try:
            node = self.compile_node(self.get_server_node(raw_sql, temp_node_id))
        except Exception as exc:
            if retry > 0:
                return self.compile_sql(raw_sql, retry - 1)
            raise exc
        else:
            return node
        finally:
            self._clear_node(temp_node_id)

    def compile_node(self, node: ManifestNode) -> DbtAdapterCompilationResult:
        """Compiles existing node."""
        self.sql_compiler.node = node
        # this is essentially a convenient wrapper to adapter.get_compiler
        compiled_node = self.sql_compiler.compile(self.dbt)
        return DbtAdapterCompilationResult(
            getattr(compiled_node, RAW_CODE),
            getattr(compiled_node, COMPILED_CODE),
            compiled_node,
        )

    def _clear_node(self, name="name"):
        """Removes the statically named node created by `execute_sql` and `compile_sql` in `dbt.lib`"""
        self.dbt.nodes.pop(f"{NodeType.SqlOperation}.{self.project_name}.{name}", None)

    def get_relation(
        self, database: str, schema: str, name: str
    ) -> Optional[BaseRelation]:
        """Wrapper for `adapter.get_relation`"""
        return self.adapter.get_relation(database, schema, name)

    def create_relation(self, database: str, schema: str, name: str) -> BaseRelation:
        """Wrapper for `adapter.Relation.create`"""
        return self.adapter.Relation.create(database, schema, name)

    def create_relation_from_node(self, node: ManifestNode) -> BaseRelation:
        """Wrapper for `adapter.Relation.create_from`"""
        return self.adapter.Relation.create_from(self.config, node)

    def get_columns_in_relation(self, node: ManifestNode) -> List[str]:
        """Wrapper for `adapter.get_columns_in_relation`"""
        return self.adapter.get_columns_in_relation(
            self.create_relation_from_node(node)
        )

    def get_or_create_relation(
        self, database: str, schema: str, name: str
    ) -> Tuple[BaseRelation, bool]:
        """Get relation or create if not exists. Returns tuple of relation and
        boolean result of whether it existed ie: (relation, did_exist)"""
        ref = self.get_relation(database, schema, name)
        return (
            (ref, True)
            if ref
            else (self.create_relation(database, schema, name), False)
        )

    def create_schema(self, node: ManifestNode):
        """Create a schema in the database"""
        return self.execute_macro(
            "create_schema",
            kwargs={"relation": self.create_relation_from_node(node)},
        )

    def materialize(
        self, node: ManifestNode, temporary: bool = True
    ) -> Tuple[AdapterResponse, None]:
        """Materialize a table in the database"""
        return self.adapter_execute(
            # Returns CTAS string so send to adapter.execute
            self.execute_macro(
                "create_table_as",
                kwargs={
                    "sql": getattr(node, COMPILED_CODE),
                    "relation": self.create_relation_from_node(node),
                    "temporary": temporary,
                },
            ),
            auto_begin=True,
        )


class DbtProjectContainer:
    """This class manages multiple DbtProjects which each correspond
    to a single dbt project on disk. This is mostly for osmosis server use"""

    def __init__(self):
        self._projects: Dict[str, DbtProject] = OrderedDict()
        self._default_project: Optional[str] = None

    def get_project(self, project_name: str) -> Optional[DbtProject]:
        """Primary interface to get a project and execute code"""
        return self._projects.get(project_name)

    @lru_cache(maxsize=10)
    def get_project_by_root_dir(self, root_dir: str) -> Optional[DbtProject]:
        """Get a project by its root directory."""
        root_dir = os.path.abspath(os.path.normpath(root_dir))
        for project in self._projects.values():
            if os.path.abspath(project.project_root) == root_dir:
                return project
        return None

    def get_default_project(self) -> Optional[DbtProject]:
        """Gets the default project which at any given time is the
        earliest project inserted into the container"""
        return self._projects.get(self._default_project)

    def add_project(
        self,
        target: Optional[str] = None,
        profiles_dir: Optional[str] = None,
        project_dir: Optional[str] = None,
        threads: Optional[int] = 1,
        name_override: Optional[str] = "",
        vars: Optional[str] = "{}",
    ) -> DbtProject:
        """Add a DbtProject with arguments"""
        project = DbtProject(target, profiles_dir, project_dir, threads, vars)
        project_name = name_override or project.config.project_name
        if self._default_project is None:
            self._default_project = project_name
        self._projects[project_name] = project
        return project

    def add_parsed_project(self, project: DbtProject) -> DbtProject:
        """Add an already instantiated DbtProject"""
        self._projects.setdefault(project.config.project_name, project)
        return project

    def add_project_from_args(self, args: ConfigInterface) -> DbtProject:
        """Add a DbtProject from a ConfigInterface"""
        project = DbtProject.from_args(args)
        self._projects.setdefault(project.config.project_name, project)
        return project

    def drop_project(self, project_name: str) -> None:
        """Drop a DbtProject"""
        project = self.get_project(project_name)
        if project is None:
            return
        project.clear_caches()
        project.adapter.connections.cleanup_all()
        self._projects.pop(project_name)
        if self._default_project == project_name:
            if len(self) > 0:
                self._default_project = self._projects.keys()[0]
            else:
                self._default_project = None

    def drop_all_projects(self) -> None:
        """Drop all DbtProjectContainers"""
        self._default_project = None
        for project in self._projects:
            self.drop_project(project)

    def reparse_all_projects(self) -> None:
        """Reparse all projects"""
        for project in self:
            project.safe_parse_project()

    def registered_projects(self) -> List[str]:
        """Convenience to grab all registered project names"""
        return list(self._projects.keys())

    def __len__(self):
        """Allows len(DbtProjectContainer)"""
        return len(self._projects)

    def __getitem__(self, project: str):
        """Allows DbtProjectContainer['jaffle_shop']"""
        maybe_project = self.get_project(project)
        if maybe_project is None:
            raise KeyError(project)
        return maybe_project

    def __delitem__(self, project: str):
        """Allows del DbtProjectContainer['jaffle_shop']"""
        self.drop_project(project)

    def __iter__(self):
        """Allows project for project in DbtProjectContainer"""
        for project in self._projects:
            yield self.get_project(project)

    def __contains__(self, project):
        """Allows 'jaffle_shop' in DbtProjectContainer"""
        return project in self._projects

    def __repr__(self):
        """Canonical string representation of DbtProjectContainer instance"""
        return "\n".join(
            f"Project: {project.project_name}, Dir: {project.project_root}"
            for project in self
        )

    def __call__(self) -> "DbtProjectContainer":
        """This allows the object to be used as a callable, primarily for FastAPI dependency injection
        ```python
        dbt_project_container = DbtProjectContainer()
        def register(x_dbt_project: str = Header(default=None)):
            dbt_project_container.add_project(...)
        def compile(x_dbt_project: str = Header(default=None), dbt = Depends(dbt_project_container), request: fastapi.Request):
            query = request.body()
            dbt.get_project(x_dbt_project).compile(query)
        ```
        """
        return self


DbtOsmosis = DbtProject


class SchemaFileOrganizationPattern(str, Enum):
    SchemaYaml = "schema.yml"
    FolderYaml = "folder.yml"
    ModelYaml = "model.yml"
    UnderscoreModelYaml = "_model.yml"
    SchemaModelYaml = "schema/model.yml"


class SchemaFileLocation(BaseModel):
    target: Path
    current: Optional[Path] = None

    @property
    def is_valid(self) -> bool:
        return self.current == self.target


class SchemaFileMigration(BaseModel):
    output: Dict[str, Any] = {}
    supersede: Dict[Path, List[str]] = {}


class DbtYamlManager(DbtProject):
    """The DbtYamlManager class handles developer automation tasks surrounding
    schema yaml files organziation, documentation, and coverage."""

    audit_report = """
    :white_check_mark: [bold]Audit Report[/bold]
    -------------------------------

    Database: [bold green]{database}[/bold green]
    Schema: [bold green]{schema}[/bold green]
    Table: [bold green]{table}[/bold green]

    Total Columns in Database: {total_columns}
    Total Documentation Coverage: {coverage}%

    Action Log:
    Columns Added to dbt: {n_cols_added}
    Column Knowledge Inherited: {n_cols_doc_inherited}
    Extra Columns Removed: {n_cols_removed}
    """

    # TODO: Let user supply a custom arg / config file / csv of strings which we
    # consider placeholders which are not valid documentation, these are just my own
    # We may well drop the placeholder concept too
    placeholders = [
        "Pending further documentation",
        "Pending further documentation.",
        "No description for this column",
        "No description for this column.",
        "Not documented",
        "Not documented.",
        "Undefined",
        "Undefined.",
        "",
    ]

    def __init__(
        self,
        target: Optional[str] = None,
        profiles_dir: Optional[str] = None,
        project_dir: Optional[str] = None,
        threads: Optional[int] = 1,
        fqn: Optional[str] = None,
        dry_run: bool = False,
    ):
        super().__init__(target, profiles_dir, project_dir, threads)
        self.fqn = fqn
        self.dry_run = dry_run

    def _filter_model(self, node: ManifestNode) -> bool:
        """Validates a node as being actionable. Validates both models and sources."""
        fqn = self.fqn or ".".join(node.fqn[1:])
        fqn_parts = fqn.split(".")
        logger().debug("%s: %s -> %s", node.resource_type, fqn, node.fqn[1:])
        return (
            # Verify Resource Type
            node.resource_type in (NodeType.Model, NodeType.Source)
            # Verify Package == Current Project
            and node.package_name == self.project_name
            # Verify Materialized is Not Ephemeral if NodeType is Model [via short-circuit]
            and (
                node.resource_type != NodeType.Model
                or node.config.materialized != "ephemeral"
            )
            # Verify FQN Length [Always true if no fqn was supplied]
            and len(node.fqn[1:]) >= len(fqn_parts)
            # Verify FQN Matches Parts [Always true if no fqn was supplied]
            and all(left == right for left, right in zip(fqn_parts, node.fqn[1:]))
        )

    @staticmethod
    def get_patch_path(node: ManifestNode) -> Optional[Path]:
        if node is not None and node.patch_path:
            return Path(node.patch_path.split("://")[-1])

    def filtered_models(
        self, subset: Optional[MutableMapping[str, ManifestNode]] = None
    ) -> Iterator[Tuple[str, ManifestNode]]:
        """Generates an iterator of valid models"""
        for unique_id, dbt_node in (
            subset.items()
            if subset
            else chain(self.dbt.nodes.items(), self.dbt.sources.items())
        ):
            if self._filter_model(dbt_node):
                yield unique_id, dbt_node

    def get_osmosis_config(
        self, node: ManifestNode
    ) -> Optional[SchemaFileOrganizationPattern]:
        """Validates a config string. If input is a source, we return the resource type str instead"""
        if node.resource_type == NodeType.Source:
            return None
        osmosis_config = node.config.get("dbt-osmosis")
        if not osmosis_config:
            raise MissingOsmosisConfig(
                f"Config not set for model {node.name}, we recommend setting the config at a directory level through the `dbt_project.yml`"
            )
        try:
            return SchemaFileOrganizationPattern(osmosis_config)
        except ValueError as exc:
            raise InvalidOsmosisConfig(
                f"Invalid config for model {node.name}: {osmosis_config}"
            ) from exc

    def get_schema_path(self, node: ManifestNode) -> Optional[Path]:
        """Resolve absolute schema file path for a manifest node"""
        schema_path = None
        if node.resource_type == NodeType.Model and node.patch_path:
            schema_path: str = node.patch_path.partition("://")[-1]
        elif node.resource_type == NodeType.Source:
            if hasattr(node, "source_name"):
                schema_path: str = node.path
        if schema_path:
            return Path(self.project_root).joinpath(schema_path)

    def get_target_schema_path(self, node: ManifestNode) -> Path:
        """Resolve the correct schema yml target based on the dbt-osmosis config for the model / directory"""
        osmosis_config = self.get_osmosis_config(node)
        if not osmosis_config:
            return Path(node.root_path, node.original_file_path)
        # Here we resolve file migration targets based on the config
        if osmosis_config == SchemaFileOrganizationPattern.SchemaYaml:
            schema = "schema"
        elif osmosis_config == SchemaFileOrganizationPattern.FolderYaml:
            schema = node.fqn[-2]
        elif osmosis_config == SchemaFileOrganizationPattern.ModelYaml:
            schema = node.name
        elif osmosis_config == SchemaFileOrganizationPattern.SchemaModelYaml:
            schema = "schema/" + node.name
        elif osmosis_config == SchemaFileOrganizationPattern.UnderscoreModelYaml:
            schema = "_" + node.name
        else:
            raise InvalidOsmosisConfig(
                f"Invalid dbt-osmosis config for model: {node.fqn}"
            )
        return Path(node.root_path, node.original_file_path).parent / Path(
            f"{schema}.yml"
        )

    @staticmethod
    def get_database_parts(node: ManifestNode) -> Tuple[str, str, str]:
        return node.database, node.schema, getattr(node, "alias", node.name)

    def bootstrap_existing_model(
        self, model_documentation: Dict[str, Any], node: ManifestNode
    ) -> Dict[str, Any]:
        """Injects columns from database into existing model if not found"""
        model_columns: List[str] = [
            c["name"].lower() for c in model_documentation.get("columns", [])
        ]
        database_columns = self.get_columns(node)
        for column in database_columns:
            if column.lower() not in model_columns:
                logger().info(":syringe: Injecting column %s into dbt schema", column)
                model_documentation.setdefault("columns", []).append({"name": column})
        return model_documentation

    def get_columns(self, node: ManifestNode) -> List[str]:
        """Get all columns in a list for a model"""
        parts = self.get_database_parts(node)
        table = self.adapter.get_relation(*parts)
        columns = []
        if not table:
            logger().info(
                ":cross_mark: Relation %s.%s.%s does not exist in target database, cannot resolve columns",
                *parts,
            )
            return columns
        try:
            columns = [c.name for c in self.adapter.get_columns_in_relation(table)]
        except CompilationException as error:
            logger().info(
                ":cross_mark: Could not resolve relation %s.%s.%s against database active tables during introspective query: %s",
                *parts,
                str(error),
            )
        return columns

    @staticmethod
    def assert_schema_has_no_sources(schema: Mapping) -> Mapping:
        """Inline assertion ensuring that a schema does not have a source key"""
        if schema.get("sources"):
            raise SanitizationRequired(
                "Found `sources:` block in a models schema file. We require you separate sources in order to organize your project."
            )
        return schema

    def build_schema_folder_mapping(
        self,
        target_node_type: Optional[Union[NodeType.Model, NodeType.Source]] = None,
    ) -> Dict[str, SchemaFileLocation]:
        """Builds a mapping of models or sources to their existing and target schema file paths"""
        if target_node_type == NodeType.Source:
            # Source folder mapping is reserved for source importing
            target_nodes = self.dbt.sources
        elif target_node_type == NodeType.Model:
            target_nodes = self.dbt.nodes
        else:
            target_nodes = {**self.dbt.nodes, **self.dbt.sources}
        # Container for output
        schema_map = {}
        logger().info("...building project structure mapping in memory")
        # Iterate over models and resolve current path vs declarative target path
        for unique_id, dbt_node in self.filtered_models(target_nodes):
            schema_path = self.get_schema_path(dbt_node)
            osmosis_schema_path = self.get_target_schema_path(dbt_node)
            schema_map[unique_id] = SchemaFileLocation(
                target=osmosis_schema_path, current=schema_path
            )
        return schema_map

    def draft_project_structure_update_plan(self) -> Dict[Path, SchemaFileMigration]:
        """Build project structure update plan based on `dbt-osmosis:` configs set across dbt_project.yml and model files.
        The update plan includes injection of undocumented models. Unless this plan is constructed and executed by the `commit_project_restructure` function,
        dbt-osmosis will only operate on models it is aware of through the existing documentation.

        Returns:
            MutableMapping: Update plan where dict keys consist of targets and contents consist of outputs which match the contents of the `models` to be output in the
            target file and supersede lists of what files are superseded by a migration
        """

        # Container for output
        blueprint: Dict[Path, SchemaFileMigration] = {}
        logger().info(
            ":chart_increasing: Searching project stucture for required updates and building action plan"
        )
        with self.adapter.connection_named("dbt-osmosis"):
            for unique_id, schema_file in self.build_schema_folder_mapping(
                target_node_type=NodeType.Model
            ).items():
                if not schema_file.is_valid:
                    blueprint.setdefault(
                        schema_file.target,
                        SchemaFileMigration(
                            output={"version": 2, "models": []}, supersede={}
                        ),
                    )
                    node = self.dbt.nodes[unique_id]
                    if schema_file.current is None:
                        # Bootstrapping Undocumented Model
                        blueprint[schema_file.target].output["models"].append(
                            self.get_base_model(node)
                        )
                    else:
                        # Model Is Documented but Must be Migrated
                        if not schema_file.current.exists():
                            continue
                        # TODO: We avoid sources for complexity reasons but if we are opinionated, we don't have to
                        schema = self.assert_schema_has_no_sources(
                            self.yaml_handler.load(schema_file.current)
                        )
                        models_in_file: Iterable[Dict[str, Any]] = schema.get(
                            "models", []
                        )
                        for documented_model in models_in_file:
                            if documented_model["name"] == node.name:
                                # Bootstrapping Documented Model
                                blueprint[schema_file.target].output["models"].append(
                                    self.bootstrap_existing_model(
                                        documented_model, node
                                    )
                                )
                                # Target to supersede current
                                blueprint[schema_file.target].supersede.setdefault(
                                    schema_file.current, []
                                ).append(documented_model["name"])
                                break
                        else:
                            ...  # Model not found at patch path -- We should pass on this for now
                else:
                    ...  # Valid schema file found for model -- We will update the columns in the `Document` task

        return blueprint

    def commit_project_restructure_to_disk(
        self, blueprint: Optional[Dict[Path, SchemaFileMigration]] = None
    ) -> bool:
        """Given a project restrucure plan of pathlib Paths to a mapping of output and supersedes which is in itself a mapping of Paths to model names,
        commit changes to filesystem to conform project to defined structure as code fully or partially superseding existing models as needed.

        Args:
            blueprint (Dict[Path, SchemaFileMigration]): Project restructure plan as typically created by `build_project_structure_update_plan`

        Returns:
            bool: True if the project was restructured, False if no action was required
        """

        # Build blueprint if not user supplied
        if not blueprint:
            blueprint = self.draft_project_structure_update_plan()

        # Verify we have actions in the plan
        if not blueprint:
            logger().info(":1st_place_medal: Project structure approved")
            return False

        # Print plan for user auditability
        self.pretty_print_restructure_plan(blueprint)

        logger().info(
            ":construction_worker: Executing action plan and conforming projecting schemas to defined structure"
        )
        for target, structure in blueprint.items():
            if not target.exists():
                # Build File
                logger().info(":construction: Building schema file %s", target.name)
                if not self.dry_run:
                    target.parent.mkdir(exist_ok=True, parents=True)
                    target.touch()
                    self.yaml_handler.dump(structure.output, target)

            else:
                # Update File
                logger().info(":toolbox: Updating schema file %s", target.name)
                target_schema: Optional[Dict[str, Any]] = self.yaml_handler.load(target)
                if not target_schema:
                    target_schema = {"version": 2}
                elif "version" not in target_schema:
                    target_schema["version"] = 2
                target_schema.setdefault("models", []).extend(
                    structure.output["models"]
                )
                if not self.dry_run:
                    self.yaml_handler.dump(target_schema, target)

            # Clean superseded schema files
            for dir, models in structure.supersede.items():
                preserved_models = []
                raw_schema: Dict[str, Any] = self.yaml_handler.load(dir)
                models_marked_for_superseding = set(models)
                models_in_schema = set(
                    map(lambda mdl: mdl["name"], raw_schema.get("models", []))
                )
                non_superseded_models = models_in_schema - models_marked_for_superseding
                if len(non_superseded_models) == 0:
                    logger().info(":rocket: Superseded schema file %s", dir.name)
                    if not self.dry_run:
                        dir.unlink(missing_ok=True)
                else:
                    for model in raw_schema["models"]:
                        if model["name"] in non_superseded_models:
                            preserved_models.append(model)
                    raw_schema["models"] = preserved_models
                    if not self.dry_run:
                        self.yaml_handler.dump(raw_schema, dir)
                    logger().info(
                        ":satellite: Model documentation migrated from %s to %s",
                        dir.name,
                        target.name,
                    )

        return True

    @staticmethod
    def pretty_print_restructure_plan(
        blueprint: Dict[Path, SchemaFileMigration]
    ) -> None:
        logger().info(
            list(
                map(
                    lambda plan: (blueprint[plan].supersede or "CREATE", "->", plan),
                    blueprint.keys(),
                )
            )
        )

    def build_node_ancestor_tree(
        self,
        node: ManifestNode,
        family_tree: Optional[Dict[str, List[str]]] = None,
        members_found: Optional[List[str]] = None,
        depth: int = 0,
    ) -> Dict[str, List[str]]:
        """Recursively build dictionary of parents in generational order"""
        if family_tree is None:
            family_tree = {}
        if members_found is None:
            members_found = []
        for parent in node.depends_on.nodes:
            member = self.dbt.nodes.get(parent, self.dbt.sources.get(parent))
            if member and parent not in members_found:
                family_tree.setdefault(f"generation_{depth}", []).append(parent)
                members_found.append(parent)
                # Recursion
                family_tree = self.build_node_ancestor_tree(
                    member, family_tree, members_found, depth + 1
                )
        return family_tree

    def inherit_column_level_knowledge(
        self,
        family_tree: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """Inherit knowledge from ancestors in reverse insertion order to ensure that the most recent ancestor is always the one to inherit from"""
        knowledge: Dict[str, Dict[str, Any]] = {}
        for generation in reversed(family_tree):
            for ancestor in family_tree[generation]:
                member: ManifestNode = self.dbt.nodes.get(
                    ancestor, self.dbt.sources.get(ancestor)
                )
                if not member:
                    continue
                for name, info in member.columns.items():
                    knowledge.setdefault(name, {"progenitor": ancestor})
                    deserialized_info = info.to_dict()
                    # Handle Info:
                    # 1. tags are additive
                    # 2. descriptions are overriden
                    # 3. meta is merged
                    # 4. tests are ignored until I am convinced those shouldn't be hand curated with love
                    if deserialized_info["description"] in self.placeholders:
                        deserialized_info.pop("description", None)
                    deserialized_info["tags"] = list(
                        set(
                            deserialized_info.pop("tags", [])
                            + knowledge[name].get("tags", [])
                        )
                    )
                    if not deserialized_info["tags"]:
                        deserialized_info.pop("tags")  # poppin' tags like Macklemore
                    deserialized_info["meta"] = {
                        **knowledge[name].get("meta", {}),
                        **deserialized_info["meta"],
                    }
                    if not deserialized_info["meta"]:
                        deserialized_info.pop("meta")
                    knowledge[name].update(deserialized_info)
        return knowledge

    def get_node_columns_with_inherited_knowledge(
        self,
        node: ManifestNode,
    ) -> Dict[str, Dict[str, Any]]:
        """Build a knowledgebase for the model based on iterating through ancestors"""
        family_tree = self.build_node_ancestor_tree(node)
        knowledge = self.inherit_column_level_knowledge(family_tree)
        return knowledge

    @staticmethod
    def get_column_sets(
        database_columns: Iterable[str],
        yaml_columns: Iterable[str],
        documented_columns: Iterable[str],
    ) -> Tuple[List[str], List[str], List[str]]:
        """Returns:
        missing_columns: Columns in database not in dbt -- will be injected into schema file
        undocumented_columns: Columns missing documentation -- descriptions will be inherited and injected into schema file where prior knowledge exists
        extra_columns: Columns in schema file not in database -- will be removed from schema file
        """
        missing_columns = [
            x
            for x in database_columns
            if x.lower() not in (y.lower() for y in yaml_columns)
        ]
        undocumented_columns = [
            x
            for x in database_columns
            if x.lower() not in (y.lower() for y in documented_columns)
        ]
        extra_columns = [
            x
            for x in yaml_columns
            if x.lower() not in (y.lower() for y in database_columns)
        ]
        return missing_columns, undocumented_columns, extra_columns

    def propagate_documentation_downstream(
        self, force_inheritance: bool = False
    ) -> None:
        schema_map = self.build_schema_folder_mapping()
        with self.adapter.connection_named("dbt-osmosis"):
            for unique_id, node in track(list(self.filtered_models())):
                logger().info(
                    "\n:point_right: Processing model: [bold]%s[/bold] \n", unique_id
                )
                # Get schema file path, must exist to propagate documentation
                schema_path: Optional[SchemaFileLocation] = schema_map.get(unique_id)
                if schema_path is None or schema_path.current is None:
                    logger().info(
                        ":bow: No valid schema file found for model %s", unique_id
                    )  # We can't take action
                    continue

                # Build Sets
                database_columns: Set[str] = set(self.get_columns(node))
                yaml_columns: Set[str] = set(column for column in node.columns)

                if not database_columns:
                    logger().info(
                        ":safety_vest: Unable to resolve columns in database, falling back to using yaml columns as base column set\n"
                    )
                    database_columns = yaml_columns

                # Get documentated columns
                documented_columns: Set[str] = set(
                    column
                    for column, info in node.columns.items()
                    if info.description and info.description not in self.placeholders
                )

                # Queue
                (
                    missing_columns,
                    undocumented_columns,
                    extra_columns,
                ) = self.get_column_sets(
                    database_columns, yaml_columns, documented_columns
                )

                if force_inheritance:
                    # Consider all columns "undocumented" so that inheritance is not selective
                    undocumented_columns = database_columns

                # Engage
                n_cols_added = 0
                n_cols_doc_inherited = 0
                n_cols_removed = 0
                if (
                    len(missing_columns) > 0
                    or len(undocumented_columns)
                    or len(extra_columns) > 0
                ):
                    schema_file = self.yaml_handler.load(schema_path.current)
                    (
                        n_cols_added,
                        n_cols_doc_inherited,
                        n_cols_removed,
                    ) = self.update_schema_file_and_node(
                        missing_columns,
                        undocumented_columns,
                        extra_columns,
                        node,
                        schema_file,
                    )
                    if n_cols_added + n_cols_doc_inherited + n_cols_removed > 0:
                        # Dump the mutated schema file back to the disk
                        if not self.dry_run:
                            self.yaml_handler.dump(schema_file, schema_path.current)
                        logger().info(":sparkles: Schema file updated")

                # Print Audit Report
                n_cols = float(len(database_columns))
                n_cols_documented = (
                    float(len(documented_columns)) + n_cols_doc_inherited
                )
                perc_coverage = (
                    min(100.0 * round(n_cols_documented / n_cols, 3), 100.0)
                    if n_cols > 0
                    else "Unable to Determine"
                )
                logger().info(
                    self.audit_report.format(
                        database=node.database,
                        schema=node.schema,
                        table=node.name,
                        total_columns=n_cols,
                        n_cols_added=n_cols_added,
                        n_cols_doc_inherited=n_cols_doc_inherited,
                        n_cols_removed=n_cols_removed,
                        coverage=perc_coverage,
                    )
                )

    @staticmethod
    def remove_columns_not_in_database(
        extra_columns: Iterable[str],
        node: ManifestNode,
        yaml_file_model_section: Dict[str, Any],
    ) -> int:
        """Removes columns found in dbt model that do not exist in database from both node and model simultaneously
        THIS MUTATES THE NODE AND MODEL OBJECTS so that state is always accurate"""
        changes_committed = 0
        for column in extra_columns:
            node.columns.pop(column, None)
            yaml_file_model_section["columns"] = [
                c for c in yaml_file_model_section["columns"] if c["name"] != column
            ]
            changes_committed += 1
            logger().info(":wrench: Removing column %s from dbt schema", column)
        return changes_committed

    def update_schema_file_and_node(
        self,
        missing_columns: Iterable[str],
        undocumented_columns: Iterable[str],
        extra_columns: Iterable[str],
        node: ManifestNode,
        yaml_file: Dict[str, Any],
    ) -> Tuple[int, int, int]:
        """Take action on a schema file mirroring changes in the node."""
        # We can extrapolate this to a general func
        noop = 0, 0, 0
        if node.resource_type == NodeType.Source:
            KEY = "tables"
            yaml_file_models = None
            for src in yaml_file.get("sources", []):
                if src["name"] == node.source_name:
                    # Scope our pointer to a specific portion of the object
                    yaml_file_models = src
        else:
            KEY = "models"
            yaml_file_models = yaml_file
        if yaml_file_models is None:
            return noop
        for yaml_file_model_section in yaml_file_models[KEY]:
            if yaml_file_model_section["name"] == node.name:
                logger().info(":microscope: Looking for actions")
                n_cols_added = self.add_missing_cols_to_node_and_model(
                    missing_columns, node, yaml_file_model_section
                )
                n_cols_doc_inherited = (
                    self.update_undocumented_columns_with_prior_knowledge(
                        undocumented_columns, node, yaml_file_model_section
                    )
                )
                n_cols_removed = self.remove_columns_not_in_database(
                    extra_columns, node, yaml_file_model_section
                )
                return n_cols_added, n_cols_doc_inherited, n_cols_removed
        logger().info(":thumbs_up: No actions needed")
        return noop
