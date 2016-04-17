from wtforms import form, fields
from wtforms.validators import ValidationError
from wtforms import validators as val
import models
from fields import (AkkeriImageUploadField, AkkeriUserImageUploadField,
    ImageUploadWithPreviewField, day_subdir, cleaned_filename)
import imghdr
from flask_admin.form import ImageUploadField

def picture_validation(form, field):
    if field.data:
        filename = field.data.filename
        if filename[-4:] != '.jpg':
            raise ValidationError('file must be .jpg')
        if imghdr.what(field.data) != 'jpeg':
            raise ValidationError('file must be a valid jpeg image.')
    field.data = field.data.stream.read()
    return True


class LoginForm(form.Form):
    login = fields.TextField(validators=[val.required()])
    password = fields.PasswordField(validators=[val.required()])
    
    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise val.ValidationError('Invalid user')
        if not user.check_password(self.password.data):
            raise val.ValidationError('Invalid password')

    def get_user(self):
        login = self.login.data or ''
        if login.find('@') > -1:
            return models.User.query.filter_by(email=login).first()
        else:
            return models.User.query.filter_by(username=login).first()


class UserForm(form.Form):
    fullname = fields.StringField(u'Full name', validators=[val.required()])
    email = fields.StringField(u'Email', validators=[val.required()])
    user_location = fields.StringField(u"Your location", validators=[val.required()])
    image = AkkeriUserImageUploadField(
                label='Image',
                base_path=AkkeriImageUploadField.base_path,
                url_relative_path=AkkeriImageUploadField.url_relative_path,
                relative_path=day_subdir(),
                namegen=cleaned_filename,
                allow_overwrite=False,
                thumbnail_size=(100, 100, True))


class ImageWithPreviewForm(form.Form):
    image_path= ImageUploadWithPreviewField(
                label='Image',
                base_path=AkkeriImageUploadField.base_path,
                url_relative_path=AkkeriImageUploadField.url_relative_path,
                relative_path=day_subdir(),
                namegen=cleaned_filename,
                allow_overwrite=False,
                thumbnail_size=(100, 100, True))
