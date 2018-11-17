""" CLI helper utilities """

from six import StringIO
import sys
import itertools
import re
import textwrap

from .. import __version__ as pkg_version


color_lookup = {
    'red': "\u001b[31m",
    'green': "\u001b[32m",
    'blue': "\u001b[36m",
    'lightgrey': "\u001b[30;1m",
}


# American Spelling... :(
def colorize(s, color=None):
    if color:
        start_tag = color_lookup[color]
        end_tag = "\u001b[0m"
        return start_tag + s + end_tag
    else:
        return s


def get_python_version():
    return "{0[0]}.{0[1]}.{0[2]}".format(sys.version_info)


def get_package_version():
    return pkg_version


def wrap_elem(s, width):
    """ take a string, and attempt to wrap into a list of strings all less than <width> """
    return textwrap.wrap(s, width=width)


def wrap_field(label, val, width, max_label_width=10, sep_char=': '):
    """
    Wrap a field (label, val)
    Return a dict of {label_list, val_list, sep_char, lines}
    """
    if len(label) > max_label_width:
        label_width = max_label_width
        label_list = wrap_elem(label, width=max_label_width)
    else:
        label_width = width - len(label) - len(sep_char)
        label_list = [label]
    
    max_val_width = width - len(sep_char) - label_width
    val_list = wrap_elem(val, width=max_val_width)
    return dict(
        label_list=label_list,
        val_list=val_list,
        sep_char=sep_char,
        lines=max(len(label_list), len(val_list))
    )


def cli_table(fields, col_width=20, cols=2, divider_char=' ', sep_char=': ',
              label_color='lightgrey', float_format="{0:.2f}"):
    """ make a crude ascii table, assuming that `fields` is an iterable of (label, value) pairs """
    # First turn the fields, into a collection of fields with wordwrap applied
    col = 1
    first_row = True
    buff = StringIO()
    for label, value in fields:
        label = str(label)
        if isinstance(value, float):
            value = float_format.format(value)
        else:
            value = str(value)
        gap = col_width - len(label) - len(value) - len(sep_char)
        if gap < 0:
            raise ValueError("Label, seperator, value combination ({0},{1},{2}) overflows the column width of {3}".format(
                label, sep_char, value, col_width))
        # Check to see if we need a newline
        if col == 1 and not first_row:
            buff.write('\n')
        # Actually write the data
        buff.write(colorize(label + sep_char, color=label_color))
        buff.write((' ' * gap) + value)
        # If we're not the last column, add a divider, otherwise add a newline
        if col < cols:
            buff.write(divider_char)
            col += 1
        else:
            # set us back to col #1, don't write the newline yet
            # as we don't know if there is any more data. Mark us
            # as not on the first line anymore.
            col = 1
            first_row = False
    return buff.getvalue()
