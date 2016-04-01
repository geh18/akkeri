import PIL
import os
import random
import string
from flask_admin import form
from akkeri.thumbnailer import Thumbnail
from flask import current_app
import datetime
from akkeri.utils import slugify


def cleaned_filename(obj, file_data):
    basename, ext = os.path.splitext(file_data.filename)
    s = string.lowercase + string.digits
    random_name = ''.join(random.sample(s, 25))
    return slugify(random_name) + ext


def day_subdir(prefix_dir=None):
    "Date-based subdir -- note the trailing slash"
    td = datetime.date.today()
    if prefix_dir:
        return '%s/%04d/%02d/%02d/' % (prefix_dir, td.year, td.month, td.day)
    else:
        return '%04d/%02d/%02d/' % (td.year, td.month, td.day)


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


def _thumbnail(image_path, size='140x105', crop=True):
    if not image_path:
        return ''
    thumb = Thumbnail(None,
                      static_folder=current_app.static_folder,
                      static_url_path=current_app.static_url_path)
    return thumb.thumbnail(image_path, size, crop)


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


class AkkeriUserImageUploadInput(AkkeriImageUploadInput):
    croppie = """
        <div id="crop-avatar" class="hidden"></div>
        <div class="fileUpload btn btn-primary">
            <span>Upload</span>
            <input type="file" accept="image/*" id="image" class="upload">
        </div>
        <input type="button" class="btn btn-primary cancel-upload" value="Cancel">
        <input type="hidden" id="base64" name="image">
        <input type="checkbox" name="%(marker)s" class="hidden">
    """

    empty_template = """
        <div class="user-image">
            <div class="image-wrapper">
                <span class="avatar">Your image</span>
            </div>
            %s
        </div>
    """ % croppie
 
    data_template = """
        <div class="user-image">
            <div class="image-wrapper">
                <img %(image)s class="uploaded-image">
                <div class="delete-image" 
                     data-toggle="modal" 
                     data-target="#admin-modal"
                     data-modal="delete-image">x</div>
            </div>
    """ + croppie + """                
        </div>
    """


class AkkeriImageUploadField(form.ImageUploadField, UniqueUploadMixin):
    widget = AkkeriImageUploadInput()
    url_relative_path = 'images/'
    def validate(self, form, extra_validators=None):
        return True

    def _save_file(self, data, filename):
        filename = self._ensure_unique(filename)
        if self.image is None:
            self.image = PIL.Image.open(data)
        return super(AkkeriImageUploadField, self)._save_file(data, filename)

    @staticmethod
    def base_path():
        return os.path.join(
            current_app.static_folder,
            current_app.config.get(
                'IMAGES_SUBDIR', 'images'))

class AkkeriUserImageUploadField(AkkeriImageUploadField):
    widget = AkkeriUserImageUploadInput()


"""
class AkkeriFileUploadInput(form.FileUploadInput):
    Once an attachment has been uploaded, we want the corresponding attachment
    URL to be immutable. Hence we remove the Delete and Upload buttons from the
    edit form. Instead, we show a link to the file itself for easy retrieval.

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
                'ATTACHMENTS_SUBDIR', 'attachments'))"""
