"""Template helpers for rendering Western digits as Arabic-Indic numerals."""
from django import template

register = template.Library()

# Western 0-9 -> Arabic-Indic ٠-٩, plus decimal/thousands separators.
_DIGITS = str.maketrans({
    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
    '.': '٫', ',': '٬',
})


@register.filter(name='ar')
def arabic_numerals(value):
    """Convert any Western digits in ``value`` to Arabic-Indic numerals."""
    if value is None:
        return ''
    return str(value).translate(_DIGITS)
