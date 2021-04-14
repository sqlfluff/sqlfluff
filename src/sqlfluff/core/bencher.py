"""Safe implementation of benchit.

This handles the library possibly not being present in conda.
"""

try:
    from benchit import BenchIt  # noqa: F401
    BENCHIT_INSTALLED = True
except ModuleNotFoundError:
    BENCHIT_INSTALLED = False


class SafeBencher:
    """Safe Benchit class."""
    def __init__(self, strict=False):
        if BENCHIT_INSTALLED:
            self._bencher = BenchIt()
        else:
            self._bencher = None
            if strict:
                raise RuntimeError("Benchit not found. Please pip install bench-it to use this feature.")

    def __bool__(self):
        """Return true if enabled."""
        return self._bencher is not None

    def __call__(self, *args, **kwargs):
        """Pass through call to bencher."""
        if self._bencher:
            return self._bencher(*args, **kwargs)

    def display(self):
        """Pass display through to bencher."""
        if self._bencher:
            return self._bencher.display()
