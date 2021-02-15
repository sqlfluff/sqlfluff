"""Module used to test foo within the jinja template."""
schema = "sch1"


def table(name):
    """Return the parameter with foo_ in front of it."""
    return f"foo_{name}"
