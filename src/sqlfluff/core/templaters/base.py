"""Defines the templaters."""

from typing import Dict

_templater_lookup: Dict[str, "RawTemplater"] = {}


def templater_selector(s=None, **kwargs):
    """Instantitate a new templater by name."""
    s = s or "jinja"  # default to jinja
    try:
        cls = _templater_lookup[s]
        # Instantiate here, optionally with kwargs
        return cls(**kwargs)
    except KeyError:
        raise ValueError(
            "Requested templater {0!r} which is not currently available. Try one of {1}".format(
                s, ", ".join(_templater_lookup.keys())
            )
        )


def register_templater(cls):
    """Register a new templater by name.

    This is designed as a decorator for templaters.

    e.g.
    @register_templater()
    class RawTemplater(BaseSegment):
        blah blah blah

    """
    n = cls.name
    _templater_lookup[n] = cls
    return cls


class TemplatedFile:
    """A templated SQL file.

    This is the response of a templaters .process() method
    and contains both references to the orginal file and also
    the capability to split up that file when lexing.
    """

    def __init__(self, source_str, templated_str=None, fname=None, sliced_file=None):
        """Initialise the TemplatedFile.

        If no full_templated is provided then we assume that
        the file is NOT templated and that the templated view
        is the same as the source view.
        """
        self.source_str = source_str
        self.templated_str = templated_str or source_str
        # If no fname, we assume this is from a string or stdin.
        self.fname = fname
        # Assume that no sliced_file, means the file is not templated
        # TODO: Enable error handling.
        # if not sliced_file and templated_str != source_str:
        #     raise ValueError("Cannot instantiate a templated file unsliced!")
        self.sliced_file = sliced_file

    def __bool__(self):
        """Return true if there's a templated file."""
        return bool(self.templated_str)

    def __str__(self):
        """Return the templated file if coerced to string."""
        return self.templated_str

    def template_slice_to_source_slice(self, template_slice):
        """Convert a template slice to a source slice."""
        if not self.sliced_file:
            return template_slice, False

        # Find the relevant slices.
        start_idx = 0
        for idx, elem in enumerate(self.sliced_file):
            start_idx = idx
            if elem[2].stop > template_slice.start:
                break

        stop_idx = 0
        for idx, elem in enumerate(self.sliced_file[start_idx:]):
            stop_idx = idx
            if elem[2].stop >= template_slice.stop:
                break
        stop_idx += start_idx + 1

        slices = self.sliced_file[start_idx:stop_idx]

        # if it's a literal segment then we can get the exact position
        # otherwise we're greedy.
        is_literal = True
        # Start.
        if slices[0][0] == 'literal':
            offset = template_slice.start - slices[0][2].start
            source_start = slices[0][1].start + offset
        else:
            source_start = slices[0][1].start
            is_literal = False
        # Stop.
        if slices[-1][0] == 'literal':
            offset = slices[-1][2].stop - template_slice.stop
            source_stop = slices[-1][1].stop - offset
        else:
            source_stop = slices[-1][1].stop
            is_literal = False
        
        # Check any mid segments for whether they're literals
        if any(elem[0] != 'literal' for elem in slices):
            is_literal = False

        # Deal with the unlikely event that the slice is the wrong
        # way around.
        if source_start > source_stop:
            # If this happens, it's because one was templated and
            # the other isn't.
            raise NotImplementedError("I didn't *think* this was possible. Please report this.")

        return slice(source_start, source_stop), is_literal


@register_templater
class RawTemplater:
    """A templater which does nothing.

    This also acts as the base templating class.
    """

    name = "raw"
    templater_selector = "templater"

    def __init__(self, **kwargs):
        """Placeholder init function.

        Here we should load any initial config found in the root directory. The init
        function shouldn't take any arguments at this stage as we assume that it will load
        it's own config. Maybe at this stage we might allow override parameters to be passed
        to the linter at runtime from the cli - that would be the only time we would pass
        arguments in here.
        """

    @staticmethod
    def process(in_str, fname=None, config=None):
        """Process a string and return a TemplatedFile.

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.

        """
        return TemplatedFile(in_str, fname=fname), []

    def __eq__(self, other):
        """Return true if `other` is of the same class as this one.

        NB: This is useful in comparing configs.
        """
        return isinstance(other, self.__class__)
