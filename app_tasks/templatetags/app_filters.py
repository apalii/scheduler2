from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name='ticket_only')
def ticket_only(value):
    if '#' in value:
        return value[:value.find('#')]
    return value