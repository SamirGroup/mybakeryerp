from django import template

register = template.Library()


@register.filter
def has_role(user, role):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name='admin').exists():
        return True
    return user.groups.filter(name=role).exists()


@register.filter
def user_role(user):
    if not user.is_authenticated:
        return ''
    if user.is_superuser or user.groups.filter(name='admin').exists():
        return 'admin'
    group = user.groups.first()
    return group.name if group else ''
