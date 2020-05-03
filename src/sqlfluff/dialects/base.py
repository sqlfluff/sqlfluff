"""Defines the base dialect class."""


class LateBoundDialectObject:
    """Defines a late-bound dialect object.

    It returns a single dialect object on expansion.

    These are defined using a callable, which is only called
    once everything else is defined. Very useful for template
    inheritance.
    """
    def __init__(self, func):
        self.func = func

    def expand(self, dialect):
        """Expand this object into it's true dialect object.

        The inner function is passed an instance of the current dialect
        and so has access to the current sets of that dialect.
        """
        return self.func(dialect)


class LateBoundDialectModule:
    """Defines a late-bound dialect module.

    It returns an iterable of (name, dialectobject) tuples.

    These are defined using a callable, which is only called
    once everything else is defined. Very useful for template
    inheritance.
    """
    def __init__(self, func=None):
        self.func = func

    def call(self, dialect):
        """The call point to override when subclassing."""
        if self.func:
            return self.func(dialect)
        raise NotImplementedError(
            "{0} does not have a `call` or `func` method defined!".format(
                self.__class__.__name__))

    def expand(self, dialect):
        """Expand this object into it's contained dialect objects.

        This function also provides some basic validation.

        The inner function is passed an instance of the current dialect
        and so has access to the current sets of that dialect.
        """
        for name, elem in self.call(dialect):
            assert isinstance(name, str)
            yield name, elem


class Dialect:
    """Serves as the basis for runtime resolution of Grammar.

    Args:
        name (:obj:`str`): The name of the dialect, used for lookup.
        lexer_struct (iterable of :obj:`tuple`): A structure defining
            the lexing config for this dialect.

    """
    def __init__(self, name, lexer_struct=None, library=None, sets=None, modules=None):
        self._library = library or {}
        self.name = name
        self.lexer_struct = lexer_struct
        self.expanded = False
        self._sets = sets or {}
        self._modules = modules or []

    def __repr__(self):
        return "<Dialect: {0}>".format(self.name)

    def register_modules(self, *modules):
        """Register a module on the dialect."""
        for module in modules:
            assert isinstance(module, LateBoundDialectModule)
            self._modules.append(module)

    def expand(self):
        """Expand any callable references to concrete ones.

        This must be called before using the dialect. But
        allows more flexible definitions to happen at runtime.

        """
        # Are we already expanded?
        if self.expanded:
            return
        # Expand any callable elements of the dialect.
        for key in self._library:
            if isinstance(self._library[key], LateBoundDialectObject):
                # If the element is callable, call it passing the current
                # dialect and store the result it it's place.
                # Use the .replace() method for it's error handling.
                self.replace(**{key: self._library[key].expand(self)})
        # Expand any loaded modules
        for module in self._modules:
            for name, elem in module.expand(self):
                # Use the .add() method to use it's error handling.
                self.add(**{name: elem})
        self.expanded = True

    def sets(self, label):
        """Allows access to sets belonging to this dialect.

        These sets belong to the dialect and are copied for sub
        dialects. These are used in combination with late-bound
        dialect objects to create some of the bulk-produced rules.

        """
        if label not in self._sets:
            self._sets[label] = set()
        return self._sets[label]

    def copy_as(self, name):
        """Copy this dialect and create a new one with a different name.

        This is the primary method for inheritance, after which, the
        `replace` method can be used to override particular rules.
        """
        # Copy sets if they are passed, so they can be mutated independently
        new_sets = {}
        for label in self._sets:
            new_sets[label] = self._sets[label].copy()

        return self.__class__(
            name=name,
            library=self._library.copy(),
            lexer_struct=self.lexer_struct.copy(),
            sets=new_sets,
            # No need to copy modules, as they have no state.
            modules=self._modules
        )

    def segment(self, replace=False):
        """This is the decorator for elements, it should be called as a method.

        e.g.
        @dialect.segment()
        class SomeSegment(BaseSegment):
            blah blah blah

        """
        def segment_wrap(cls):
            """Wrap a segment and register it against the dialect."""
            n = cls.__name__
            if replace:
                if n not in self._library:
                    raise ValueError("{0!r} is not already registered in {1!r}".format(n, self))
            else:
                if n in self._library:
                    raise ValueError("{0!r} is already registered in {1!r}".format(n, self))
            self._library[n] = cls
            # Pass it back after registering it
            return cls
        # return the wrapping function
        return segment_wrap

    def add(self, **kwargs):
        """Add a segment to the dialect directly.

        This is the alternative to the decorator route, most useful for segments
        defined using `make`. Segments are passed in as kwargs.

        e.g.
        dialect.add(SomeSegment=KeyworkSegment.make(blah, blah, blah))

        Note that mutiple segments can be added in the same call as this method
        will iterate through the kwargs
        """
        for n in kwargs:
            if n in self._library:
                raise ValueError("{0!r} is already registered in {1!r}".format(n, self))
            self._library[n] = kwargs[n]

    def replace(self, **kwargs):
        """Override a segment on the dialect directly.

        Usage is very similar to add, but elements specfied must already exist.
        """
        for n in kwargs:
            if n not in self._library:
                raise ValueError("{0!r} is not already registered in {1!r}".format(n, self))
            self._library[n] = kwargs[n]

    def ref(self, name):
        """Return an object which acts as a late binding reference to the element named.

        NB: This requires the dialect to be expanded.

        """
        if not self.expanded:
            raise RuntimeError("Dialect must be expanded before use.")

        if name in self._library:
            res = self._library[name]
            if res:
                return res
            else:
                raise ValueError(
                    "Unexpected Null response while fetching {0!r} from {1}".format(
                        name, self.name))
        else:
            raise RuntimeError(
                "Grammar refers to {0!r} which was not found in the {1} dialect".format(
                    name, self.name))

    def set_lexer_struct(self, lexer_struct):
        """Set the lexer struct for the dialect.

        This is what is used for base dialects. For derived dialects
        (which don't exist yet) the assumption is that we'll introduce
        some kind of *patch* function which could be used to mutate
        an existing `lexer_struct`.
        """
        self.lexer_struct = lexer_struct

    def get_lexer_struct(self):
        """Fetch the lexer struct for this dialect."""
        if self.lexer_struct:
            return self.lexer_struct
        else:
            raise ValueError(
                "Lexing struct has not been set for dialect {0}".format(
                    self))

    def patch_lexer_struct(self, lexer_patch):
        """Patch an existing lexer struct.

        Used to edit the lexer of a sub-dialect.
        """
        buff = []
        if not self.lexer_struct:
            raise ValueError("Lexer struct must be defined before it can be patched!")

        # Make a new data struct for lookups
        patch_dict = {elem[0]: elem for elem in lexer_patch}

        for elem in self.lexer_struct:
            if elem[0] in patch_dict:
                buff.append(patch_dict[elem[0]])
            else:
                buff.append(elem)
        # Overwrite with the buffer once we're done
        self.lexer_struct = buff
