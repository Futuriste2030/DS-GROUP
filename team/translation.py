from modeltranslation.translator import register, TranslationOptions
from .models import TeamMember, TeamExperience, TeamCertification, Testimonial


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('name', 'role', 'department', 'bio', 'bio_2', 'quote', 'skills', 'office', 'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')


@register(TeamExperience)
class TeamExperienceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(TeamCertification)
class TeamCertificationTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ('client_name', 'client_role', 'title', 'text')
