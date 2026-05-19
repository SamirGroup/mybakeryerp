from django import template

register = template.Library()

@register.filter
def startswith(value, arg):
    """Check if string starts with arg"""
    if not value:
        return False
    return value.startswith(arg)

@register.filter
def divide(value, arg):
    """Divide value by arg, return 0 if arg is 0"""
    try:
        arg = float(arg)
        value = float(value)
        if arg == 0:
            return 0
        return value / arg
    except (ValueError, TypeError):
        return 0
