from __future__ import absolute_import

import os
import datetime
import sys
import bcrypt
from PIL import Image

from flask_admin import Admin, AdminIndexView, helpers, expose, form
from flask import url_for, redirect, request, current_app
from flask_admin.contrib.sqla import ModelView
import flask_login

from forms import LoginForm
from akkeri.utils import slugify


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
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


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
                base, ext = os.path.splitext(path)
                path = '%s--%d%s' % (base, try_add, ext)
        if try_add:
            base, ext = os.path.splitext(filename)
            filename = '%s--%d%s' % (base, try_add, ext)
        return filename


class AttachmentUploadField(form.FileUploadField, UniqueUploadMixin):

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


class AttachmentModelView(AdminModelView):
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
        # passed to the AttachmentUploadField constructor
        'attachment_path': dict(
            label='Attachment File',
            base_path=AttachmentUploadField.base_path,
            relative_path=day_subdir(),
            namegen=cleaned_filename,
            allow_overwrite=False),
    }


class AkkeriImageUploadField(form.ImageUploadField, UniqueUploadMixin):

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


class ImageModelView(AdminModelView):
    column_list = ('title', 'image_path')
    form_overrides = {
        'image_path': AkkeriImageUploadField,
    }
    form_excluded_columns = ('bytes', 'width', 'height')
    # Passed to the AkkeriImageUploadField constructor
    form_args = {
        'image_path': dict(
            label='Image',
            base_path=AkkeriImageUploadField.base_path,
            url_relative_path=AkkeriImageUploadField.url_relative_path,
            relative_path=day_subdir(),
            namegen=cleaned_filename,
            allow_overwrite=False,
            thumbnail_size=(100, 100, True)),
    }


class PostModelView(AdminModelView):
    column_list = (
            'title', 'slug', 'post_type', 'created', 'published')


class UserModelView(AdminModelView):
    """
    Special settings for user class.
    """
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
