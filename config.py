import os

class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'Dab55owosBoRi3DreshrenMiec3recCoij3Hirnid5Nold'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
            'sqlite://memory')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
