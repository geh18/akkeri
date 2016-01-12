# encoding=utf8

# Much of this is based on flask-thumbnails by Dmitriy Sokolov, see
# https://github.com/silentsokolov/flask-thumbnails

import os
import errno
import re
from PIL import Image, ImageOps
from flask import safe_join

class Thumbnail(object):
    def __init__(self, app, static_folder=None, static_url_path=None,
                 img_subdir='images', cache_subdir='cache/tn'):
        """
        We assume that images are under 'images/' and cached thumbnails under
        'cache/tn/' inside the app static_folder. The cache dir is created
        if it does not exist already.

        Usage: in app.py, do this:

            from akkeri.thumbnailer import Thumbnail
            thumb = Thumbnail(app)

        If you want to use this independently of a flask, app, instead
        do something like this:

            from akkeri.thumbnailer import Thumbnail
            thumb = Thumbnail(None, static_folder=dir, static_url_path=url)
        """
        self.app = app
        self.img_subdir = img_subdir
        self.cache_subdir = cache_subdir
        if app:
            self.img_root = safe_join(self.app.static_folder, img_subdir);
            self.cache_root = safe_join(self.app.static_folder, cache_subdir);
            self.static_folder = app.static_folder
            self.static_url_path = app.static_url_path
        elif not static_folder or not static_url_path:
            raise ValueError(
                "Need either app or both static_folder and static_url_path")
        else:
            self.img_root = safe_join(static_folder, img_subdir)
            self.cache_root = safe_join(static_folder, cache_subdir);
            self.static_folder = static_folder
            self.static_url_path = static_url_path
        if not os.path.isdir(self.cache_root):
            os.makedirs(self.cache_root)
        self.cache_baseurl = safe_join(self.static_url_path, cache_subdir)
        self.img_baseurl = safe_join(self.static_url_path, img_subdir)
        if app:
            app.jinja_env.filters['thumbnail'] = self.thumbnail

    def thumbnail(self, img_path, size, crop=False, quality=80):
        """
        This is the Jinja2 thumbnail helper function which takes a path
        relative to self.img_root and returns another which starts with
        self.cache_baseurl. It can also be called as an ordinary method
        on a Thumbnail object.

        Parameters:

        - img_path: partial image url - e.g. '2016/01/whatever.jpg'.
        - size: width x height geometry - e.g. '100x100'.
        - crop: Boolean; if True crop the original while keeping ratio.
        - quality: JPEG quality 1-100; default 80.

        Example usage in a template:

          <img src="{{ i.image_path | thumbnail('100x100', crop=True) }}">
        """
        width, height = [int(x) for x in size.split('x')]
        subdir = ''
        if img_path.find('/') > -1:
            subdir, filename = os.path.split(img_path)
        else:
            filename = img_path
        target_name = self._get_target_name(
            filename, size, int(crop), quality)
        orig_fn = os.path.join(self.img_root, subdir, filename)
        thumb_dir = os.path.join(self.cache_root, subdir)
        thumb_fn = os.path.join(self.cache_root, subdir, target_name)
        thumb_url = os.path.join(self.cache_baseurl, subdir, target_name)
        if os.path.exists(thumb_fn):
            return thumb_url
        if not os.path.isdir(thumb_dir):
            os.makedirs(thumb_dir)
        try:
            image = Image.open(orig_fn)
            dim = (width, height)
            if crop:
                img = ImageOps.fit(image, dim, Image.ANTIALIAS)
            else:
                img = image.copy()
                img.thumbnail(dim, Image.ANTIALIAS)
            img.save(thumb_fn, image.format, quality=quality)
        except IOError:
            return None
        return thumb_url

    def reverse(self, thumbnail_url, path=False, force=False):
        """
        Given the putative URL of a thumbnail (which does not actually need to
        exist), return the URL of the original image, or None if the file does
        not exist.

        - If `path` is True, return the file path rather than the URL.
        - If `force` is True, return the url/path even if the original file
          does not exist.
        """
        cleaned_url = re.sub(r'_\d+x\d+_[01]_\d+(\.\w+)$', r'\1',
                             thumbnail_url)
        cleaned_path = cleaned_url.replace(
            self.cache_baseurl, self.img_root, 1)
        cleaned_url = cleaned_url.replace(
            self.cache_baseurl, self.img_baseurl, 1)
        if force or os.path.isfile(cleaned_path):
            return cleaned_path if path else cleaned_url
        else:
            return None

    @staticmethod
    def _get_target_name(filename, *args):
        """
        Appends the thumbnailing settings to the basename of the original file,
        yielding the filename for the thumbnail.
        """
        basename, ext = os.path.splitext(filename)
        for v in args:
            basename += '_%s' % v
        return basename + ext
