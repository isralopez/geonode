import autocomplete_light
from models import Project

autocomplete_light.register(
    Project,
    search_fields=['^title'],
    autocomplete_js_attributes={
        'placeholder': 'Document name..',
    },
)
