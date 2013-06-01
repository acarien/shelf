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
	elif delta.days > 1 and delta.days <= 5:
		return "Due in the following 5 days"
	elif delta.days > 5:
		return "Due in more than 5 days"
	else:
		return "Not due"
