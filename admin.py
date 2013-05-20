from django.contrib import admin
from shelf.models import Article, Duration
from shelf.modelsAdmin import DurationAdmin

admin.site.register(Article)
admin.site.register(Duration, DurationAdmin)
