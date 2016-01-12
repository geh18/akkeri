from flask_admin import Admin, AdminIndexView, helpers, expose, form
from flask import url_for, redirect, request
from flask_admin.contrib.sqla import ModelView
import flask_login
import bcrypt
import sys
from forms import LoginForm
from config import STATIC_IMAGES

# Used for admin model view class discovery
current_module = sys.modules[__name__]


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
class AttachmentModelView(AdminModelView):
    column_list = (
            'attachment_path', 'title', 'owner', 'added')


class ImageModelView(AdminModelView):
    # form_edit_rules = ('title', 'image_path', 'caption')
    # form_create_rules = form_edit_rules
    column_list = ('title', 'image_path', 'caption')
    # raise Exception(STATIC_IMAGES)
    form_extra_fields = {
        'image_path': form.ImageUploadField(
            'Image',
            url_relative_path='images/',
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
        if attr[0]=='X' or not attr[0].isupper():
            continue
        model = getattr(models, attr)
        model_view_class = getattr(
                current_module, attr + 'ModelView', AdminModelView)
        if model.__bases__ and db.Model in model.__bases__:
            admin.add_view(model_view_class(model, db.session))
    return admin
