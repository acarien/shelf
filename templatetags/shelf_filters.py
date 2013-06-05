from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter()
def get_reading_date_string(value):
	delta = value - date.today()

	if delta.days == 0:
		return "Due today"
	elif delta.days == 1:
		return "Due tomorrow"
	elif delta.days > 1 and delta.days <= 6:
		return 'Due on {0} '.format(value.strftime('%A'))		
	elif delta.days > 6:
		return "Due in more than one week"
	else:
		return "Not due"
