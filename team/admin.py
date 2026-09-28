from django.contrib import admin
from django.db import models
from ckeditor.widgets import CKEditorWidget
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from .models import TeamMember, TeamExperience, TeamCertification, Testimonial


class TeamExperienceInline(TranslationTabularInline):
    model = TeamExperience
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


class TeamCertificationInline(TranslationTabularInline):
    model = TeamCertification
    extra = 1


@admin.register(TeamMember)
class TeamMemberAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'role', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    inlines = [TeamExperienceInline, TeamCertificationInline]
    exclude = ('meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description', 'og_image', 'twitter_card', 'canonical_url', 'noindex', 'nofollow')
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }


@admin.register(Testimonial)
class TestimonialAdmin(TabbedTranslationAdmin):
    list_display = ['client_name', 'rating', 'order']
    list_editable = ['order']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
