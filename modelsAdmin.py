from django.contrib import admin
from models import Duration
from forms import DurationAdminForm

class DurationAdmin(admin.ModelAdmin):
    form = DurationAdminForm
