from __future__ import absolute_import

import os
import os.path as op
import datetime
import sys
import bcrypt
from PIL import Image
from jinja2 import Markup

from sqlalchemy import event
from wtforms import TextAreaField, HiddenField, fields
from wtforms.widgets import TextArea, HTMLString, html_params
from werkzeug.datastructures import FileStorage
# from werkzeug import secure_filename
from flask_admin import Admin, AdminIndexView, helpers, expose, form
from flask_admin.model.form import InlineFormAdmin
from flask import url_for, redirect, request, current_app, abort
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter

import flask_login

from forms import LoginForm
from akkeri.utils import slugify
from akkeri.thumbnailer import Thumbnail
from models import XPostImage


# Used for admin model view class discovery
current_module = sys.modules[__name__]


def cleaned_filename(obj, file_data):
    basename, ext = os.path.splitext(file_data.filename)
    return slugify(basename) + ext


def day_subdir(prefix_dir=None):
    "Date-based subdir -- note the trailing slash"
    td = datetime.date.today()
    if prefix_dir:
        return '%s/%04d/%02d/%02d/' % (prefix_dir, td.year, td.month, td.day)
    else:
        return '%04d/%02d/%02d/' % (td.year, td.month, td.day)


def _thumbnail(image_path, size='140x105', crop=True):
    if not image_path:
        return ''
    thumb = Thumbnail(None,
                      static_folder=current_app.static_folder,
                      static_url_path=current_app.static_url_path)
    return thumb.thumbnail(image_path, size, crop)


class AkkeriAdminIndexView(AdminIndexView):
    # AdminIndexView: Default view for /admin/ url
    @expose('/')
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(AkkeriAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            flask_login.login_user(user)
        if flask_login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(AkkeriAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for('.index'))


class AdminModelView(ModelView):
    """
    Base class for password-protected model views.
    """

    # Sets of access labels from the `roles` table with which some of the
    # assigned roles for each user must intersect. Of course, superusers have
    # access to everything regardless of these role labels. The list of
    # relevant labels is different for many ModelView subclasses.

    FULL_ACCESS_ROLES = set(['group_editor'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped'])

    # The column containing the user_id relevant for access control. Set this
    # to None if the corresponding model has no relevant column holding a
    # user_id. In such cases you may need to override get_query(),
    # get_count_query() and get_one().

    USER_ID_COLUMN = 'author_id'

    # Distinct form_columns for full access vs partial access.
    # Default is to give both types of users access to all columns.

    FULL_ACCESS_COLUMNS = None
    PARTIAL_ACCESS_COLUMNS = None

    def _create_or_edit_form(self, formtype, obj=None):
        if formtype == 'create':
            # key_prefix = 'cr'
            form_meth = getattr(super(AdminModelView, self), 'create_form')
        elif formtype == 'edit':
            # key_prefix = 'ed'
            form_meth = getattr(super(AdminModelView, self), 'edit_form')
        else:
            raise RuntimeError('Bad formtype: ' + formtype)
        if self.FULL_ACCESS_COLUMNS == self.PARTIAL_ACCESS_COLUMNS:
            # The question is moot, since both kinds of users have equal access
            return form_meth(obj)
        if self.with_full_access:
            self.form_columns = self.FULL_ACCESS_COLUMNS
            self._refresh_forms_cache()
            form = form_meth(obj)
            return form
        else:
            self.form_columns = self.PARTIAL_ACCESS_COLUMNS
            self._refresh_forms_cache()
            form = form_meth(obj)
            return form

    def create_form(self, obj=None):
        return self._create_or_edit_form('create', obj)

    def edit_form(self, obj=None):
        return self._create_or_edit_form('edit', obj)

    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    def _access_check(self, full_check=False):
        user = flask_login.current_user
        if not hasattr(user, 'is_superuser'):
            # Initialization, or user not logged in
            return False
        if user.is_superuser:
            return True
        check_against = \
            self.FULL_ACCESS_ROLES if full_check else self.PARTIAL_ACCESS_ROLES
        labels = set([_.label for _ in user.roles])
        return True if check_against & labels else False

    @property
    def with_full_access(self):
        return self._access_check(full_check=True)

    @property
    def with_partial_access(self):
        return self._access_check(full_check=False)

    def _apply_partial_filter(self, query):
        if self.with_full_access:
            return query
        elif self.with_partial_access:
            ucol = self.USER_ID_COLUMN
            if ucol is None:
                return query
            filter = {ucol: flask_login.current_user.id}
            return query.filter_by(**filter)
        else:
            return abort(403)

    def get_one(self, id):
        obj = super(AdminModelView, self).get_one(id)
        if self.with_full_access:
            return obj
        elif self.with_partial_access:
            ucol = self.USER_ID_COLUMN
            if ucol is None:
                return obj
            uid = flask_login.current_user.id
            if getattr(obj, self.USER_ID_COLUMN, None) == uid:
                return obj
        return abort(403)

    def get_query(self):
        query = super(AdminModelView, self).get_query()
        return self._apply_partial_filter(query)

    def get_count_query(self):
        query = super(AdminModelView, self).get_count_query()
        return self._apply_partial_filter(query)


class OptionalOwnerAdminModelView(AdminModelView):
    """
    Used for admin model views with an Owner/Author field which is selectable
    by users with full access but not by those who have partial access.
    """
    OWNER_FIELD_NAME = 'owner'

    def create_model(self, form):
        owner = None
        try:
            owner = getattr(form, self.OWNER_FIELD_NAME).data
        except AttributeError:
            setattr(form, self.OWNER_FIELD_NAME,
                    HiddenField(
                        default=lambda: flask_login.current_user,
                        _name=self.OWNER_FIELD_NAME, _form=form))
            form._fields[self.OWNER_FIELD_NAME] = getattr(
                form, self.OWNER_FIELD_NAME)
        if not owner:
            getattr(form, self.OWNER_FIELD_NAME).data \
                    = flask_login.current_user
        super(OptionalOwnerAdminModelView, self).create_model(form)


class UniqueUploadMixin(object):
    """
    Used for uploads of both attachments and images in order to ensure that
    filenames are unique and no existing files are overwritten.
    """

    def _ensure_unique(self, filename):
        """
        Causes the target file to be renamed if its filename clashes with a
        preexisting one. Requires the derived class to support the _get_path()
        method, either directly or indirectly.
        """
        path = self._get_path(filename)
        orig_path = path
        try_add = 0
        while os.path.exists(path):
            if try_add > 100:
                raise ValueError('Image "%s" already exists' % filename)
            else:
                try_add += 1
                base, ext = os.path.splitext(orig_path)
                path = '%s--%d%s' % (base, try_add, ext)
        if try_add:
            base, ext = os.path.splitext(filename)
            filename = '%s--%d%s' % (base, try_add, ext)
        return filename


class AkkeriFileUploadInput(form.FileUploadInput):
    """
    Once an attachment has been uploaded, we want the corresponding attachment
    URL to be immutable. Hence we remove the Delete and Upload buttons from the
    edit form. Instead, we show a link to the file itself for easy retrieval.
    """

    data_template = (
            '<div class="akkeri-attachment-file-path">'
            ' <a href="%(full_path)s" target="_blank">%(filename)s</a>'
            '</div>')

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)
        template = self.data_template if field.data else self.empty_template
        if field.data and isinstance(field.data, FileStorage):
            value = field.data.filename
        else:
            value = field.data or ''
        return HTMLString(template % {
            'file': html_params(type='file', value=value, **kwargs),
            'filename': value,
            'full_path': os.path.join(
                current_app.static_url_path,
                current_app.config.get('ATTACHMENTS_SUBDIR', 'attachments'),
                value)
            })


class AttachmentUploadField(form.FileUploadField, UniqueUploadMixin):
    widget = AkkeriFileUploadInput()

    def validate(self, form, extra_validators=None):
        return True

    def _save_file(self, data, filename):
        filename = self._ensure_unique(filename)
        return super(AttachmentUploadField, self)._save_file(data, filename)

    @staticmethod
    def base_path():
        return os.path.join(
            current_app.static_folder,
            current_app.config.get(
                'ATTACHMENTS_SUBDIR', 'attachments'))


class AttachmentModelView(OptionalOwnerAdminModelView):
    FULL_ACCESS_ROLES = set(['group_editor', 'all_attachments'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped', 'own_attchments'])
    USER_ID_COLUMN = 'owner_id'
    FULL_ACCESS_COLUMNS = (
            'owner', 'attachment_path', 'title', 'credit', 'caption',
            'attachment_date', 'active', 'available_to_others', 'tags',
            'added', 'changed')
    PARTIAL_ACCESS_COLUMNS = (
            'attachment_path', 'title', 'credit', 'caption',
            'attachment_date', 'active', 'tags')
    column_list = (
            'attachment_path', 'title', 'owner', 'added')
    form_excluded_columns = ('bytes', 'posts', )
    form_widget_args = {
        'added': {'disabled': True},
        'changed': {'disabled': True},
    }
    form_overrides = {
        'attachment_path': AttachmentUploadField,
    }
    form_args = {
        'owner': dict(default=lambda: flask_login.current_user),
        'active': dict(default=True),
        # passed to the AttachmentUploadField constructor
        'attachment_path': dict(
            label='Attachment File',
            base_path=AttachmentUploadField.base_path,
            relative_path=day_subdir(),
            namegen=cleaned_filename,
            allow_overwrite=False),
    }


class AkkeriImageUploadInput(form.ImageUploadInput):
    """
    Once an image has been uploaded, we want the corresponding image URL to be
    immutable. Hence we remove the Delete and Upload buttons from the edit
    form. Also, we show a larger, proportionally scaled thumbnail than that
    ordinarily provided by flask-admin.
    """

    data_template = (
            '<div class="akkeri-image-thumbnail">'
            ' <img %(image)s>'
            '</div>')

    def get_url(self, field):
        filename = field.data
        return _thumbnail(filename, '250x250', False)


class AkkeriImageUploadField(form.ImageUploadField, UniqueUploadMixin):
    widget = AkkeriImageUploadInput()
    url_relative_path = 'images/'

    def validate(self, form, extra_validators=None):
        return True

    def _save_file(self, data, filename):
        filename = self._ensure_unique(filename)
        if self.image is None:
            self.image = Image.open(data)
        return super(AkkeriImageUploadField, self)._save_file(data, filename)

    @staticmethod
    def base_path():
        return os.path.join(
            current_app.static_folder,
            current_app.config.get(
                'IMAGES_SUBDIR', 'images'))


class ImageModelView(OptionalOwnerAdminModelView):
    FULL_ACCESS_ROLES = set(['group_editor', 'all_images'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped', 'own_images'])
    FULL_ACCESS_COLUMNS = (
            'owner', 'image_path', 'title', 'credit', 'caption',
            'image_taken', 'active', 'available_to_others', 'tags',
            'added', 'changed')
    PARTIAL_ACCESS_COLUMNS = (
            'image_path', 'title', 'credit', 'caption',
            'image_taken', 'active', 'tags', )
    USER_ID_COLUMN = 'owner_id'
    column_list = ('title', 'owner', 'added', 'image_path')
    form_overrides = {
        'image_path': AkkeriImageUploadField,
    }

    def _tn(view, ctx, model, name):
        thumburl = _thumbnail(model.image_path)
        return Markup(u'<img src="%s" alt="%s">' % (thumburl, model.title))
    column_formatters = {'image_path': _tn}
    form_excluded_columns = ('bytes', 'width', 'height')
    form_args = {
        'owner': dict(default=lambda: flask_login.current_user),
        'active': dict(default=True),
        # Passed to the AkkeriImageUploadField constructor
        'image_path': dict(
            label='Image',
            base_path=AkkeriImageUploadField.base_path,
            url_relative_path=AkkeriImageUploadField.url_relative_path,
            relative_path=day_subdir(),
            namegen=cleaned_filename,
            allow_overwrite=False,
            thumbnail_size=(100, 100, True)),
    }
    form_widget_args = {
        'added': {'disabled': True},
        'changed': {'disabled': True},
    }


class TMCETextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' tinymce-editor'
        else:
            kwargs.setdefault('class', 'tinymce-editor')
        return super(TMCETextAreaWidget, self).__call__(field, **kwargs)


class TMCETextAreaField(TextAreaField):
    widget = TMCETextAreaWidget()


@event.listens_for(XPostImage, 'after_delete')
def _handle_image_delete(mapper, conn, target):
    pass


class CustomInlineFieldListWidget(form.RenderTemplateWidget):
    def __init__(self):
        super(CustomInlineFieldListWidget, self).\
                            __init__('admin/model/field_list.html')


class CustomInlineModelFormList(InlineModelFormList):
    widget = CustomInlineFieldListWidget()


class CustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList


class XPostImageInline(InlineFormAdmin):
    form_excluded_columns = ['linked_at']

    form_label = 'Image'

    def __init__(self):
        return super(XPostImageInline, self).__init__(XPostImage)

    def postprocess_form(self, form_class):
        form_class.upload = fields.FileField('Image')
        return form_class

    def on_model_change(self, form, model):
        file_data = request.files.get(form.upload.name)
        if file_data:
            file_name = cleaned_filename(self, file_data)
            base_path = AkkeriImageUploadField.base_path() + '/'
            day_dir = day_subdir()
            model.image.image_path = day_dir + file_name

            image = base_path + day_dir + file_name

            if not op.exists(op.dirname(base_path + day_dir)):
                os.makedirs(os.path.dirname(base_path + day_dir), mode=0755)
            file_data.save(image)


class PostModelView(OptionalOwnerAdminModelView):
    FULL_ACCESS_ROLES = set(['group_editor', 'all_posts'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped', 'own_posts'])
    FULL_ACCESS_COLUMNS = (
        'author', 'language', 'post_type', 'title', 'summary',
        'body', 'is_draft', 'published', 'post_display', 'author_visible',
        'author_line', 'images', 'attachments', 'tags')
    PARTIAL_ACCESS_COLUMNS = (
        'title', 'location', 'is_draft', 'summary', 'body', 'published',
        'images', 'attachments', 'tags')
    USER_ID_COLUMN = 'author_id'
    OWNER_FIELD_NAME = 'author'
    column_list = (
            'title', 'slug', 'post_type', 'created', 'published')
    form_excluded_columns = ('created', 'changed')
    form_overrides = {
        'body': TMCETextAreaField,
    }

    inline_model_form_converter = CustomInlineModelConverter
    inline_models = [XPostImageInline()]

    create_template = 'admin/model/tmce_editor.html'
    edit_template = create_template


class HiddenWithoutFullAccessModelView(AdminModelView):
    """
    Inherit from this in order to hide the menu item without making it
    impossible for the ordinary logged-in user to access the page.
    """
    USER_ID_COLUMN = None

    def is_visible(self):
        return self.with_full_access


class OnlyForFullAccessModelView(HiddenWithoutFullAccessModelView):
    """
    Inherit from this in order to limit access to superusers and editors.
    """
    def is_accessible(self):
        return flask_login.current_user.is_authenticated \
            and self.with_full_access

    def inaccessible_callback(self, name, **kwargs):
        if flask_login.current_user.is_authenticated:
            # Logged in, but without full rights: Forbidden
            return abort(403)
        # Not logged in: Redirect to login page.
        return redirect(url_for('login', next=request.url))


class UserModelView(OnlyForFullAccessModelView):
    """
    Special settings for user class.
    """
    FULL_ACCESS_ROLES = set(['group_editor', 'all_users'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped'])
    USER_ID_COLUMN = 'id'

    form_edit_rules = (
            'username', 'email', 'fullname', 'user_location', 'active',
            'show_profile', 'is_superuser')
    column_list = (
            'username', 'email', 'fullname', 'is_superuser', 'created')

    def create_model(self, form):
        pw = form.password.data
        if isinstance(pw, unicode):
            pw = pw.encode('utf-8')
        form.password.data = bcrypt.hashpw(pw, bcrypt.gensalt())
        super(UserModelView, self).create_model(form)


class TagModelView(AdminModelView):
    USER_ID_COLUMN = None
    FULL_ACCESS_COLUMNS = (
            'name', 'is_important', 'for_posts', 'for_images',
            'for_attachments', 'posts', 'images', 'attachments')
    PARTIAL_ACCESS_COLUMNS = ('name', )


class PostDisplayModelView(OnlyForFullAccessModelView):
    pass


class RoleModelView(OnlyForFullAccessModelView):
    pass


class PostTypeModelView(OnlyForFullAccessModelView):
    # display primary key
    column_display_pk = True


class LanguageModelView(OnlyForFullAccessModelView):
    pass


class FeaturedModelView(OnlyForFullAccessModelView):
    pass


def setup_admin(app, db, login_manager):
    import models

    admin = Admin(
        app, name='Akkeri', index_view=AkkeriAdminIndexView(),
        template_mode='bootstrap3')

    for attr in dir(models):
        if attr[0] == 'X' or not attr[0].isupper():
            continue
        model = getattr(models, attr)
        model_view_class = getattr(
                current_module, attr + 'ModelView', AdminModelView)
        if hasattr(model, '__bases__') and db.Model in model.__bases__:
            admin.add_view(model_view_class(model, db.session))
    return admin
