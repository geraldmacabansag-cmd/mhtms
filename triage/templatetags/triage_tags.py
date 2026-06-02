from django import template

register = template.Library()

PRIORITY_BADGE = {
    'critical': 'danger',
    'high': 'warning',
    'medium': 'info',
    'low': 'success',
}
PRIORITY_ROW = {
    'critical': 'table-danger',
    'high': 'table-warning',
    'medium': 'table-info',
    'low': 'table-success',
}
STATUS_BADGE = {
    'waiting': 'secondary',
    'consultation': 'primary',
    'treated': 'success',
    'admitted': 'warning',
    'discharged': 'dark',
    'transferred': 'info',
}
PRIORITY_DOT = {
    'critical': '#dc3545',
    'high': '#fd7e14',
    'medium': '#0dcaf0',
    'low': '#198754',
}

@register.filter
def priority_badge(priority):
    return PRIORITY_BADGE.get(priority, 'secondary')

@register.filter
def priority_row_class(priority):
    return PRIORITY_ROW.get(priority, '')

@register.filter
def status_badge(status):
    return STATUS_BADGE.get(status, 'secondary')

@register.filter
def priority_dot_color(priority):
    return PRIORITY_DOT.get(priority, '#6c757d')

@register.filter
def priority_icon(priority):
    icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
    }
    return icons.get(priority, '⚪')

@register.inclusion_tag('triage/tags/priority_badge.html')
def show_priority_badge(priority):
    return {
        'priority': priority,
        'badge_class': PRIORITY_BADGE.get(priority, 'secondary'),
        'dot_color': PRIORITY_DOT.get(priority, '#6c757d'),
    }

@register.inclusion_tag('triage/tags/status_badge.html')
def show_status_badge(status):
    return {
        'status': status,
        'badge_class': STATUS_BADGE.get(status, 'secondary'),
    }

@register.simple_tag
def is_critical(priority):
    return priority == 'critical'
