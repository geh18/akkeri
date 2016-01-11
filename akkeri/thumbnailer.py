# encoding=utf8

# To a large extent based upon flask-thumbnails by Dmitriy Sokolov,
# see https://github.com/silentsokolov/flask-thumbnails

import os
import errno
from PIL import Image, ImageOps
from flask import safe_join

class Thumbnail(object):
    def __init__(self, app):
        """
        We assume that images are under 'images/' and cached thumbnails under
        'cache/tn/' inside the app static_folder. The cache dir is created
        if it does not exist already.

        Usage: in app.py, do this:

            from akkeri.thumbnailer import Thumbnail
            thumb = Thumbnail(app)

        TODO: make the directories/urls configurable.
        """
        self.app = app
        self.img_root = safe_join(self.app.static_folder, 'images');
        self.cache_root = safe_join(self.app.static_folder, 'cache/tn');
        if not os.path.isdir(self.cache_root):
            os.makedirs(self.cache_root)
        self.cache_baseurl = safe_join(self.app.static_url_path, 'cache/tn');
        app.jinja_env.filters['thumbnail'] = self.thumbnail

    def thumbnail(self, img_path, size, crop=False, quality=80):
        """
        This is the Jinja2 thumbnail helper function which takes a path
        relative to self.img_root and returns another which starts with
        self.cache_baseurl.

        Parameters:

        - img_path: partial image url - e.g. '2016/whatever.jpg'.
        - size: width x height geometry - e.g. '100x100'.
        - crop: Boolean; if True crop the original while keeping ratio.
        - quality: JPEG quality 1-100; default 82.

        Example usage in a template:

            <img src="{{i.image_path | thumbnail('100x100', crop=True)}}">
        """
        width, height = [int(x) for x in size.split('x')]
        subdir = ''
        if img_path.find('/') > -1:
            subdir, filename = os.path.split(img_path)
        else:
            filename = img_path
        basename, ext = os.path.splitext(filename)
        target_name = self._get_filename(
            basename, ext, size, int(crop), quality)
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

    @staticmethod
    def _get_filename(name, ext, *args):
        for v in args:
            if v:
                name += '_%s' % v
        name += ext

        return name
