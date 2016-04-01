from __future__ import absolute_import

import os
import io
import os.path as op
import sys
import bcrypt
import cStringIO
from jinja2 import Markup
from sqlalchemy import event
from wtforms.form import Form
from wtforms import TextAreaField, fields, HiddenField
from wtforms.widgets import FileInput, TextArea
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from flask_admin import Admin, AdminIndexView, helpers, expose, form
from flask_admin.helpers import get_form_data
from flask_admin.model.form import InlineFormAdmin
from flask import url_for, redirect, request, abort, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from fields import AkkeriImageUploadField,\
                     _thumbnail, cleaned_filename, day_subdir
import flask_login



from forms import LoginForm, UserForm
from models import Image, User
# Used for admin model view class discovery
current_module = sys.modules[__name__]


class AkkeriAdminIndexView(AdminIndexView):
    # AdminIndexView: Default view for /admin/ url
    def __init__(self, db, *args, **kwargs):
        super(AkkeriAdminIndexView, self).__init__(*args, **kwargs)
        self.db = db

    def _base64_decode(self, s):
        """Add missing padding to string and return the decoded base64 string."""
        if not s:
            return None

        s = s[s.index(','):]
        if not s:
            return None
        try:
            return s.decode('base64')
        except:
            s += '=' * (-len(s) % 4)  # restore stripped '='
            return s.decode('base64')

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        if not flask_login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        flash_message = 'Your profile has been update :)'
        decoded_data = self._base64_decode(request.form.get('image'))
        if decoded_data:
            try:
                file_data = io.BytesIO(decoded_data)
                file = FileStorage(file_data, filename='virtual.jpg')
                request.files = ImmutableMultiDict([('image', file)])
            except:
                request.files = ImmutableMultiDict([])
                flash_message = 'A problem came up with uploading the image. Please contact system administration'
        user = flask_login.current_user
        form = UserForm(get_form_data(), obj=user)

        if request.method == 'POST' and form.validate():
            form.populate_obj(user)
            self.db.session.commit()
            flash(flash_message)
            return redirect(url_for('.index'))

        return self.render('admin/index.html', form=form)

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

    edit_template = 'admin/model/akkeri_edit.html'

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
        return redirect(url_for('admin.login_view', next=request.url))

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
    pass
    """
    Used for admin model views with an Owner/Author field which is selectable
    by users with full access but not by those who have partial access.
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
    """

"""
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
"""


class ImageModelView(OptionalOwnerAdminModelView):
    FULL_ACCESS_ROLES = set(['group_editor', 'all_images'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped', 'own_images'])
    FULL_ACCESS_COLUMNS = (
            'owner', 'image_path', 'title', 'credit', 'caption',
            'image_taken', 'active', 'available_to_others', 'tags',
            'added')
    PARTIAL_ACCESS_COLUMNS = (
            'image_path', 'title', 'credit', 'caption',
            'image_taken', 'active', 'tags', 'owner_id')
    USER_ID_COLUMN = 'owner_id'
    column_list = ('title', 'owner', 'added', 'image_path')
    form_overrides = {
        'image_path': AkkeriImageUploadField,
        'owner_id': HiddenField
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
    }


class TMCETextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' tinymce-editor'
        else:
            kwargs.setdefault('class', 'tinymce-editor')
        return super(TMCETextAreaWidget, self).__call__(field, **kwargs)


class ImageFileInput(FileInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('accept', 'image/*')
        return super(ImageFileInput, self).__call__(field, **kwargs)


class ImageFileField(fields.FileField):
    widget = ImageFileInput()


class TMCETextAreaField(TextAreaField):
    widget = TMCETextAreaWidget()


@event.listens_for(Image, 'after_delete')
def _handle_image_delete(mapper, conn, target):
    pass


class CustomInlineFieldListWidget(form.RenderTemplateWidget):
    def __init__(self):
        super(CustomInlineFieldListWidget, self).\
                            __init__('admin/model/field_list.html')


class CustomInlineModelFormList(InlineModelFormList):
    widget = CustomInlineFieldListWidget()

    def display_row_controls(self, field):
        return False


class CustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList


class ImageInline(InlineFormAdmin):
    form_columns = ('id', 'caption', 'owner_id')

    form_overrides = {
        'owner_id': HiddenField
    }

    def __init__(self):
        return super(ImageInline, self).__init__(Image)

    def postprocess_form(self, form_class):
        form_class.upload = ImageFileField('Image')
        return form_class

    def on_model_change(self, form, model):
        file_data = request.files.get(form.upload.name)
        if file_data:
            model.owner = flask_login.current_user
            file_name = cleaned_filename(self, file_data)
            base_path = AkkeriImageUploadField.base_path() + '/'
            day_dir = day_subdir()
            model.image_path = day_dir + file_name

            image = base_path + day_dir + file_name

            if not op.exists(op.dirname(base_path + day_dir)):
                os.makedirs(os.path.dirname(base_path + day_dir), mode=0755)
            file_data.save(image)


class PostModelView(OptionalOwnerAdminModelView):
    name = 'Write'
    column_searchable_list = ('title', 'author.fullname')
    FULL_ACCESS_ROLES = set(['group_editor', 'all_posts'])
    PARTIAL_ACCESS_ROLES = set([
        'group_refugee', 'group_volunteer', 'group_oped', 'own_posts'])
    FULL_ACCESS_COLUMNS = (
        'author', 'language', 'post_type', 'title', 'summary',
        'body', 'is_draft', 'published', 'post_display', 'author_visible',
        'author_line', 'images', 'attachments', 'tags')
    PARTIAL_ACCESS_COLUMNS = (
        'cover_image', 'title', 'body', 'location')
    USER_ID_COLUMN = 'author_id'
    OWNER_FIELD_NAME = 'author'
    column_list = (
            'title', 'slug', 'post_type', 'created', 'published')
    form_excluded_columns = ('created', 'changed')

    form_overrides = {
        'cover_image': AkkeriImageUploadField,
        # 'body': TMCETextAreaField,
    }

    def _tn(view, ctx, model, name):
        thumburl = _thumbnail(model.image_path)
        return Markup(u'<img src="%s" alt="%s">' % (thumburl, model.title))
    column_formatters = {'cover_image': _tn}
    form_args = {
        'cover_image': dict(
            label='Article Image',
            base_path=AkkeriImageUploadField.base_path,
            url_relative_path=AkkeriImageUploadField.url_relative_path,
            relative_path=day_subdir(),
            namegen=cleaned_filename,
            allow_overwrite=False,
            thumbnail_size=(100, 100, True)),
    }

    inline_model_form_converter = CustomInlineModelConverter
    inline_models = [ImageInline()]

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
            'roles', 'username', 'password', 'email', 'fullname',
            'user_location', 'image', 'active',
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
        app, name='Akkeri', index_view=AkkeriAdminIndexView(name='Me', db=db),
        template_mode='bootstrap3', base_template="admin/my_base.html")

    for attr in dir(models):
        if attr[0] == 'X' or not attr[0].isupper():
            continue
        model = getattr(models, attr)
        model_view_class = getattr(
                current_module, attr + 'ModelView', AdminModelView)
        extra = {}
        if hasattr(model_view_class, 'name'):
            extra = {'name': model_view_class.name,
                     'menu_icon_value': 'fa-pencil-square-o',
                     'menu_icon_type': 'fa'}
        if hasattr(model, '__bases__') and db.Model in model.__bases__:
            admin.add_view(model_view_class(model, db.session, **extra))
    return admin
