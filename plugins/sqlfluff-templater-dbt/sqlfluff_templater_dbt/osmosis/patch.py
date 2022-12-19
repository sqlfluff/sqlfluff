"""A temporary patch for a method in dbt manifest loader we apply in osmosis.py

"""

import os

from dbt.clients.system import make_directory
from dbt.events.functions import fire_event
from dbt.events.types import ManifestWrongMetadataVersion
from dbt.parser.manifest import PARTIAL_PARSE_FILE_NAME
from dbt.version import __version__


def write_manifest_for_partial_parse(self):
    # Patched this 👇
    # path = os.path.join(self.root_project.target_path, PARTIAL_PARSE_FILE_NAME)
    path = os.path.join(
        self.root_project.project_root,
        self.root_project.target_path,
        PARTIAL_PARSE_FILE_NAME,
    )
    try:
        # This shouldn't be necessary, but we have gotten bug reports (#3757) of the
        # saved manifest not matching the code version.
        if self.manifest.metadata.dbt_version != __version__:
            fire_event(
                ManifestWrongMetadataVersion(version=self.manifest.metadata.dbt_version)
            )
            self.manifest.metadata.dbt_version = __version__
        manifest_msgpack = self.manifest.to_msgpack()
        make_directory(os.path.dirname(path))
        with open(path, "wb") as fp:
            fp.write(manifest_msgpack)
    except Exception:
        raise
