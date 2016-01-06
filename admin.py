from flask_admin import Admin
from flask import url_for, redirect, request
from flask_admin.contrib.sqla import ModelView
import flask_login as login
import bcrypt

class AdminModelView(ModelView):
    """
    Base class for password-protected model views.
    """
    def is_accessible(self):
        return login.current_user.is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class UserModelView(AdminModelView):
    """
    Special settings for user class.
    """
    form_edit_rules = (
            'username', 'email', 'fullname', 'active', 'is_superuser')
    column_list = ('username', 'email', 'fullname', 'created')

    def create_model(self, form):
        pw = form.password.data
        if isinstance(pw, unicode):
            pw = pw.encode('utf-8')
        form.password.data = bcrypt.hashpw(pw, bcrypt.gensalt())
        super(UserModelView, self).create_model(form)

def setup_admin(app, db):
    import models
    admin = Admin(app, name='akkeri', template_mode='bootstrap3')
    # Whether this is true depends on import order
    if hasattr(models, 'User'):
        admin.add_view(UserModelView(models.User, db.session))
    login_manager = login.LoginManager()
    login_manager.init_app(app)
    return admin
