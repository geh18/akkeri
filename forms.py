from wtforms import form, fields, validators
import models

class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')
        if not user.check_password(self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        login = self.login.data or ''
        if login.find('@') > -1:
            return models.User.query.filter_by(email=login).first()
        else:
            return models.User.query.filter_by(username=login).first()
