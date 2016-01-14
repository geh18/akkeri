import os

class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'Dab55owosBoRi3DreshrenMiec3recCoij3Hirnid5Nold'

    # Database related
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
            'sqlite://memory')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ###########################################
    # Custom settings, specific to Akkeri, below
    # ###########################################

    # Placement of images and attachments.
    # The actual directory each setting points to depends on the
    # paths specified in current_app.static_folder (for the filesystem)
    # and current_app.static_url_path (for URLs).

    IMAGES_SUBDIR = 'images'
    ATTACHMENTS_SUBDIR = 'attachments'

    def __init__(self):
        """
        Automatically add any environment variables starting with FLASK__ to
        the config (sans the prefix)..
        """
        for k in environ:
            if k.startswith('FLASK__'):
                setattr(self, k.replace('FLASK__', ''), os.environ[k])


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class StagingConfig(DevelopmentConfig):
    pass


class TestingConfig(Config):
    TESTING = True
