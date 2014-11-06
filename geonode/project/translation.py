from modeltranslation.translator import translator, TranslationOptions
from geonode.project.models import Project

class ProjectTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'abstract',
        'purpose',
        'constraints_other',
        'supplemental_information',
        'distribution_description',
        'data_quality_statement',
    )

translator.register(Project, ProjectTranslationOptions)