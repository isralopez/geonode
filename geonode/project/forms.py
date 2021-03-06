import json
import os
import taggit
import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.forms import HiddenInput, TextInput
from modeltranslation.forms import TranslationModelForm

from mptt.forms import TreeNodeMultipleChoiceField

from geonode.people.models import Profile
from geonode.project.models import Project
from geonode.maps.models import Map
from geonode.layers.models import Layer
from geonode.base.models import Region


class ProjectForm(TranslationModelForm):
    date = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    date.widget.widgets[0].attrs = {
        "class": "datepicker",
        'data-date-format': "yyyy-mm-dd"}
    date.widget.widgets[1].attrs = {"class": "time"}
    temporal_extent_start = forms.DateField(
        required=False,
        label="Fecha  de Inicio Temporal",
        widget=forms.DateInput(
            attrs={
                "class": "datepicker",
                'data-date-format': "yyyy-mm-dd"}))
    temporal_extent_end = forms.DateField(
        required=False,
        label="Fecha de Termino Temporal",
        widget=forms.DateInput(
            attrs={
                "class": "datepicker",
                'data-date-format': "yyyy-mm-dd"}))

    resource = forms.ChoiceField(label='Asociado con', help_text="Seleccione un recurso asociado")

    poc = forms.ModelChoiceField(
        empty_label="Person outside GeoNode (fill form)",
        label="Informacion de Contacto",
        required=False,
        queryset=Profile.objects.exclude(
            username='AnonymousUser'))

    metadata_author = forms.ModelChoiceField(
        empty_label="Person outside GeoNode (fill form)",
        label="Metadatos de Autor",
        required=False,
        queryset=Profile.objects.exclude(
            username='AnonymousUser'))

    keywords = taggit.forms.TagField(
        required=False,
        label="Palabras Clave",
        help_text=_("A space or comma-separated list of keywords"))

    distribution_url = forms.CharField(
        required=False,
        label="Liga a la Aplicacion",
        help_text="Direccion donde se puede visualizar la aplicacion descrita"
    )

    #abstract = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        rbases = list(Layer.objects.all())
        rbases += list(Map.objects.all())
        rbases.sort(key=lambda x: x.title)
        rbases_choices = []
        rbases_choices.append(['no_link', '---------'])
        for obj in rbases:
            type_id = ContentType.objects.get_for_model(obj.__class__).id
            obj_id = obj.id
            form_value = "type:%s-id:%s" % (type_id, obj_id)
            display_text = '%s (%s)' % (obj.title, obj.polymorphic_ctype.model)
            rbases_choices.append([form_value, display_text])
        self.fields['resource'].choices = rbases_choices
        if self.instance.content_type:
            self.fields['resource'].initial = 'type:%s-id:%s' % (
                self.instance.content_type.id, self.instance.object_id)

        for field in self.fields:
            help_text = self.fields[field].help_text
            self.fields[field].help_text = None
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {
                        'class': 'has-popover',
                        'data-content': help_text,
                        'data-placement': 'right',
                        'data-container': 'body',
                        'data-html': 'true'})

    def save(self, *args, **kwargs):
        contenttype_id = None
        contenttype = None
        object_id = None
        resource = self.cleaned_data['resource']
        if resource != 'no_link':
            matches = re.match("type:(\d+)-id:(\d+)", resource).groups()
            contenttype_id = matches[0]
            object_id = matches[1]
            contenttype = ContentType.objects.get(id=contenttype_id)
        self.cleaned_data['content_type'] = contenttype_id
        self.cleaned_data['object_id'] = object_id
        self.instance.object_id = object_id
        self.instance.content_type = contenttype
        return super(ProjectForm, self).save(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['owner','title','abstract','purpose','date_type','date', 'academic_coordinator', 'technical_coordinator',
                  'colaborators','edition', 'source', 'rights',
                  'temporal_extent_start', 'temporal_extent_end',
                   'project_belong', 'knowledge_model', 'disciplines', 'credits_to', 'vinc_intitutions',
                  'develop_arch', 'repo_link', 'min_inst_req', 'min_deploy_req'
            ]
        exclude = (
            'uuid',
            'contacts',
            'workspace',
            'store',
            'name',
            'uuid',
            'storeType',
            'typename',
            'bbox_x0',
            'bbox_x1',
            'bbox_y0',
            'bbox_y1',
            'srid',
            'category',
            'csw_typename',
            'csw_schema',
            'csw_mdsource',
            'csw_type',
            'csw_wkt_geometry',
            'metadata_uploaded',
            'metadata_xml',
            'csw_anytext',
            'content_type',
            'object_id',
            'doc_file',
            'extension',
            'doc_type',
            'popular_count',
            'share_count',
            'thumbnail',
            'doc_url',
            'maintenance_frequency',
            'thumbnail_url',
            'detail_url',
            'restriction_code_type',
            'constraints_other',
            'featured',
            'rating',
            'spatial_representation_type',
            'regions',
            'supplemental_information',
            'data_quality_statement',
            'distribution_description',
            'language')


class DocumentDescriptionForm(forms.Form):
    title = forms.CharField(300)
    abstract = forms.CharField(1000, widget=forms.Textarea, required=False)
    keywords = forms.CharField(500, required=False)


class ProjectReplaceForm(forms.ModelForm):

    """
    The form used to replace a document.
    """

    class Meta:
        model = Project
        fields = ['doc_file', 'doc_url']

    def clean(self):
        """
        Ensures the doc_file or the doc_url field is populated.
        """
        cleaned_data = super(ProjectReplaceForm, self).clean()
        doc_file = self.cleaned_data.get('doc_file')
        doc_url = self.cleaned_data.get('doc_url')

        if not doc_file and not doc_url:
            raise forms.ValidationError(_("Document must be a file or url."))

        if doc_file and doc_url:
            raise forms.ValidationError(
                _("A document cannot have both a file and a url."))

        return cleaned_data

    def clean_doc_file(self):
        """
        Ensures the doc_file is valid.
        """
        doc_file = self.cleaned_data.get('doc_file')

        if doc_file and not os.path.splitext(
                doc_file.name)[1].lower()[
                1:] in settings.ALLOWED_DOCUMENT_TYPES:
            raise forms.ValidationError(_("This file type is not allowed"))

        return doc_file


class GeocyberCreateForm(TranslationModelForm):

    """
    The project upload form.
    """
    permissions = forms.CharField(
        widget=HiddenInput(
            attrs={
                'name': 'permissions',
                'id': 'permissions'}),
        required=True)

    """
    resource = forms.CharField(
        required=False,
        label=_("Asociar con"),
        widget=TextInput(
            attrs={
                'name': 'q',
                'id': 'resource'}))
    """

    class Meta:
        model = Project
        fields = ['title', 'doc_file', 'license',]
        widgets = {
            'name': HiddenInput(attrs={'cols': 80, 'rows': 20}),
        }

    def clean_permissions(self):
        """
        Ensures the JSON field is JSON.
        """
        permissions = self.cleaned_data['permissions']

        try:
            return json.loads(permissions)
        except ValueError:
            raise forms.ValidationError(_("Permissions must be valid JSON."))

    def clean(self):
        """
        Ensures the doc_file or the doc_url field is populated.
        """
        cleaned_data = super(GeocyberCreateForm, self).clean()
        doc_file = self.cleaned_data.get('doc_file')
        doc_url = self.cleaned_data.get('doc_url')

        if not doc_file and not doc_url:
            raise forms.ValidationError(_("El projecto debe contener un archivo o url."))

        if doc_file and doc_url:
            raise forms.ValidationError(
                _("Un Projecto no puede tener ambos: Archivo y URL"))

        return cleaned_data

    def clean_doc_file(self):
        """
        Ensures the doc_file is valid.
        """
        doc_file = self.cleaned_data.get('doc_file')

        if doc_file and not os.path.splitext(
                doc_file.name)[1].lower()[
                1:] in settings.ALLOWED_DOCUMENT_TYPES:
            raise forms.ValidationError(_("Este tipo de archivo no esta permitido"))

        return doc_file