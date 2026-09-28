from modeltranslation.translator import register, TranslationOptions
from .models import Project, ProjectPoint, ProjectStep


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'category', 'location', 'area', 'duration', 'excerpt', 'intro', 'description', 'challenge_title', 'challenge', 'solution_title', 'solution', 'scope_title', 'scope_description', 'result_title', 'result', 'testimonial_title', 'testimonial_text', 'testimonial_name', 'testimonial_role', 'image_1_alt', 'image_2_alt', 'video_cover_alt', 'meta_title', 'meta_description', 'meta_keywords', 'og_title', 'og_description')


@register(ProjectPoint)
class ProjectPointTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(ProjectStep)
class ProjectStepTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
