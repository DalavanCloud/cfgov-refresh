from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.html import format_html, format_html_join

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)
from wagtail.contrib.modeladmin.views import EditView
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin.rich_text import HalloPlugin
from wagtail.wagtailcore import hooks

from ask_cfpb.models import Answer, Audience, Category, NextStep, SubCategory
from ask_cfpb.scripts import export_ask_data


class AnswerModelAdminSaveUserEditView(EditView):
    """
    An edit_handler that saves the current user as the 'last user'
    on an Answer object so that it can be passed to a created or updated page.
    """

    def save_instance_user(self):
        self.instance.last_user = self.request.user
        self.instance.save(skip_page_update=True)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.save_instance_user()
        return super(EditView, self).dispatch(request, *args, **kwargs)


class AnswerModelAdmin(ModelAdmin):
    model = Answer
    menu_label = 'Answers'
    menu_icon = 'list-ul'
    list_display = (
        'id',
        'question',
        'last_edited',
        'question_es',
        'last_edited_es')
    search_fields = (
        'id', 'question', 'question_es', 'answer', 'answer_es', 'search_tags')
    list_filter = ('category', 'featured', 'audiences')
    edit_view_class = AnswerModelAdminSaveUserEditView


class AudienceModelAdmin(ModelAdmin):
    model = Audience
    menu_icon = 'list-ul'
    menu_label = 'Audiences'


class NextStepModelAdmin(ModelAdmin):
    model = NextStep
    menu_label = 'Related resources'
    menu_icon = 'list-ul'
    list_display = (
        'title', 'text')


class SubCategoryModelAdmin(ModelAdmin):
    model = SubCategory
    menu_label = 'Subcategories'
    menu_icon = 'list-ul'
    list_display = (
        'name', 'weight', 'parent'
    )
    search_fields = (
        'name', 'weight')
    list_filter = ('parent',)


class CategoryModelAdmin(ModelAdmin):
    model = Category
    menu_label = 'Categories'
    menu_icon = 'list-ul'
    list_display = (
        'name', 'name_es', 'intro', 'intro_es')


@modeladmin_register
class MyModelAdminGroup(ModelAdminGroup):
    menu_label = 'Ask CFPB'
    menu_icon = 'list-ul'
    items = (
        AnswerModelAdmin,
        AudienceModelAdmin,
        CategoryModelAdmin,
        SubCategoryModelAdmin,
        NextStepModelAdmin)


def export_data(request):
    if request.method == 'POST':
        return export_ask_data.export_questions(http_response=True)
    return render(request, 'admin/export.html')



@hooks.register('register_rich_text_features')
def register_tips_feature(features):
    features.register_editor_plugin(
        'hallo', 'ask-tips',
        HalloPlugin(
            name='answermodule',
            js=['js/ask_cfpb_tips.js'],
        )
    )

@hooks.register('register_rich_text_features')
def register_html_feature(features):
    features.register_editor_plugin(
        'hallo', 'edit-html',
        HalloPlugin(
            name='editHtmlButton',
            js=['js/html_editor.js'],
        )
    )


def editor_css():
    return format_html(
        '<link rel="stylesheet" href="' +
        settings.STATIC_URL +
        'css/question-tips.css">\n')


hooks.register('insert_editor_css', editor_css)


@hooks.register('register_admin_menu_item')
def register_export_menu_item():
    return MenuItem(
        'Export Ask data',
        reverse('export-ask'),
        classnames='icon icon-download',
        order=99999,
    )


@hooks.register('register_admin_urls')
def register_export_url():
    return [url('export-ask', export_data, name='export-ask')]
