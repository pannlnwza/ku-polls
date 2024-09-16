"""
Admin interface for the polls app.

This module registers the Question and Choice models with the Django admin
site.
"""
from django.contrib import admin
from .models import Choice, Question


class ChoiceInline(admin.TabularInline):
    """Allows editing of choices directly on the Question admin page."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for the Question model."""

    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date', 'end_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'id', 'pub_date', 'end_date',
                    'is_published', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
