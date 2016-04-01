# coding: utf-8
import bcrypt
import datetime
import os
import PIL
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
    text)
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship
from app import db
from flask import current_app
from akkeri.utils import slugify
import flask_login


# NOTE:
# Much of the code for the model classes was initially generated using
# sqlacodegen
#

# Table objects

# Pure (or almost-pure) association tables for M2M relationships
# are represented as Table objects rather than model classes. They are
# collected here at the top for easy reference.

# These are the tables used for tagging attachments, images and posts.
# Extra columns not represented (and not important): id, tagged_at.

x_attachment_tag = db.Table(
    'x_attachment_tag', db.metadata,
    Column('attachment_id', Integer, ForeignKey('attachments.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

x_image_tag = db.Table(
    'x_image_tag', db.metadata,
    Column('image_id', Integer, ForeignKey('images.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

x_post_tag = db.Table(
    'x_post_tag', db.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

# Roles for users. Extra columns not represented: id, granted_at.

x_user_role = db.Table(
    'x_user_role', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)


# Model classes

class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('attachments_id_seq'::regclass)"))
    owner_id = Column(
        ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'),
        nullable=False, index=True)
    attachment_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    bytes = Column(Integer, nullable=False, server_default=text("0"))
    attachment_date = Column(DateTime)
    # NOTE: preview_image + image are not currently used and are inaccessible
    # in the admin
    preview_image = Column(ForeignKey(
        u'images.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    available_to_others = Column(
        Boolean, nullable=False, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"),
                   default=datetime.datetime.now)
    changed = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now,
                     onupdate=datetime.datetime.now)

    owner = relationship(u'User')
    posts = relationship('XPostAttachment', back_populates='attachment')
    tags = relationship('Tag', secondary=x_attachment_tag,
                        back_populates='attachments')

    def __unicode__(self):
        return self.attachment_path

    def get_full_attachment_path(self):
        try:
            base_dir = current_app.static_folder
            subdir = current_app.config.get(
                'ATTACHMENTS_SUBDIR', 'attachments')
        except RuntimeError:
            base_dir = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'static')
            subdir = 'attachments'
        base_dir = os.path.join(base_dir, subdir)
        return os.path.join(base_dir, self.attachment_path)


@listens_for(Attachment, 'before_insert')
def attachment_before_insert(mapper, connection, instance):
    filename = instance.get_full_attachment_path()
    if os.path.isfile(filename):
        instance.bytes = os.path.getsize(filename)
    else:
        instance.bytes = 0


class Featured(db.Model):
    __tablename__ = 'featured'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('featured_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE',
                                onupdate=u'CASCADE'), nullable=False)
    featured_from = Column(DateTime, nullable=False,
                           index=True, server_default=text("now()"))
    featured_to = Column(DateTime, nullable=False,
                         index=True, server_default=text("now()"))
    for_frontpage = Column(Boolean, nullable=False,
                           server_default=text("false"))
    for_category_page = Column(
        Boolean, nullable=False, server_default=text("true"))
    added_by = Column(ForeignKey(
        u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    added_at = Column(DateTime, nullable=False, server_default=text("now()"),
                      default=datetime.datetime.now)

    user = relationship(u'User')
    post = relationship(u'Post')


"""class PostImage(db.Model):
    __tablename__ = 'post_image'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('images_id_seq'::regclass)"))
    owner_id = Column(
        ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'),
        nullable=False, index=True)
    image_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    width = Column(Integer, nullable=False, server_default=text("0"))
    height = Column(Integer, nullable=False, server_default=text("0"))
    bytes = Column(Integer, nullable=False, server_default=text("0"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE',
                                onupdate=u'CASCADE'), nullable=False)
    tags = relationship('Tag', back_populates='images')

    owner = relationship(u'User')
    post = relationship(u'Post', back_populates='images')

    def get_full_image_path(self):
        try:
            base_dir = current_app.static_folder
            subdir = current_app.config.get('IMAGES_SUBDIR', 'images')
        except RuntimeError:
            base_dir = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'static')
            subdir = 'images'
        base_dir = os.path.join(base_dir, subdir)
        return os.path.join(base_dir, (self.image_path or ''))

    def __unicode__(self):
        return self.image_path"""


class Image(db.Model):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('images_id_seq'::regclass)"))
    owner_id = Column(
        ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'),
        nullable=True, index=True)
    image_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    image_taken = Column(DateTime)
    width = Column(Integer, nullable=True, server_default=text("0"))
    height = Column(Integer, nullable=True, server_default=text("0"))
    bytes = Column(Integer, nullable=True, server_default=text("0"))
    active = Column(Boolean, nullable=True, server_default=text("true"))
    available_to_others = Column(
        Boolean, nullable=True, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"),
                   default=datetime.datetime.now)
    changed = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now,
                     onupdate=datetime.datetime.now)
    post_id = Column(ForeignKey(u'posts.id'))

    tags = relationship('Tag', secondary=x_image_tag, back_populates='images')
    owner = relationship(u'User')
    post = relationship(u'Post', backref='images')

    def __unicode__(self):
        return self.image_path or u''

    def get_full_image_path(self):
        try:
            base_dir = current_app.static_folder
            subdir = current_app.config.get('IMAGES_SUBDIR', 'images')
        except RuntimeError:
            base_dir = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'static')
            subdir = 'images'
        base_dir = os.path.join(base_dir, subdir)
        return os.path.join(base_dir, (self.image_path or ''))


@listens_for(Image, 'before_insert')
def image_before_insert(mapper, connection, target):
    filename = target.get_full_image_path()
    if os.path.isfile(filename):
        target.bytes = os.path.getsize(filename)
        with PIL.Image.open(filename) as im:
            target.width, target.height = im.size
    else:
        target.bytes = 0
        target.width = 0
        target.height = 0


class Language(db.Model):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    name_is = Column(String)
    name_en = Column(String)

    def __unicode__(self):
        return u'%s - %s' % (self.code, self.name_en)


class PostType(db.Model):
    __tablename__ = 'post_types'

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)
    name_is = Column(String)
    name_en = Column(String)

    def __unicode__(self):
        return u'%s' % self.label


class PostDisplay(db.Model):
    __tablename__ = 'post_display'

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)
    description = Column(String)

    def __unicode__(self):
        return u'%s' % self.label


class Post(db.Model):
    __tablename__ = 'posts'

    # Class constants, used in controllers and in the get_url method
    POST_TYPE_IDS = (1, 2, 3, 4)
    PAGE_TYPE_ID = 5
    PROFILE_TYPE_ID = 6

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('posts_id_seq'::regclass)"))
    author_id = Column(
        ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'),
        nullable=False, index=True)
    last_changed_by = Column(ForeignKey(
        u'users.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    author_visible = Column(Boolean, nullable=False,
                            server_default=text("true"))
    author_line = Column(String)
    title = Column(String, nullable=True)
    slug = Column(String, nullable=False, unique=True)
    is_draft = Column(Boolean, nullable=False, server_default=text("false"))
    summary = Column(Text)
    cover_image = Column(String, nullable=False)
    location = Column(String, nullable=False)
    body = Column(Text)
    post_type_id = Column(ForeignKey(
        u'post_types.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    language_id = Column(ForeignKey(
        u'languages.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    created = Column(DateTime, index=True, server_default=text("now()"),
                     default=datetime.datetime.now)
    changed = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now,
                     onupdate=datetime.datetime.now)
    published = Column(DateTime, index=True)
    post_display_id = Column(ForeignKey(
        u'post_display.id', ondelete='SET NULL',
        onupdate=u'CASCADE'), nullable=True)

    author = relationship(u'User', primaryjoin='Post.author_id == User.id')
    language = relationship(u'Language')
    last_changed_by_user = relationship(
        u'User', primaryjoin='Post.last_changed_by == User.id')
    post_type = relationship(u'PostType')
    post_display = relationship(u'PostDisplay')

    tags = relationship('Tag', secondary=x_post_tag, back_populates='posts')
    attachments = relationship(
        'XPostAttachment', back_populates='post',
        order_by=lambda: XPostAttachment.attachment_order)

    def __unicode__(self):
        return u'%s [%d]' % (self.title, self.id)

    @property
    def first_image(self):
        return self.images[0] if self.images else None

    def get_url(self):
        if self.post_type_id == self.PAGE_TYPE_ID:
            prefix = 'page'
        elif self.post_type_id == self.PROFILE_TYPE_ID:
            prefix = 'profile'
        else:
            prefix = 'post'
        return '/%s/%s/' % (prefix, self.slug)


def post_before_upd_ins(mapper, connection, instance):
    """
    This def contains actions to be performed before inserting or updating a
    Post. It is called from post_before_insert and post_before_update.
    """
    user = flask_login.current_user
    # if not user.getattr('id', None): # user = None
    # last_changed_by
    if user and not instance.last_changed_by_user:
        instance.last_changed_by_user = user
    # is_draft and published exclude each other
    if not instance.is_draft and instance.published is None:
        instance.published = datetime.datetime.now()
    elif instance.is_draft and instance.published:
        instance.published = None
    # guess post_type if missing:
    if user and not instance.post_type:
        instance.post_type_id = user.default_post_type_id()
    # automatic slug generation/update:
    slug = slugify(instance.title, fallback='without-title')
    if len(slug) > 36:
        slug = slug[:35] if slug[35] == '-' else slug[:36]
    id_prefix = instance.id \
        or connection.scalar("select max(id)+1 from posts") or 1
    pub = instance.published
    date_prefix = str(pub.date()) if pub else ''
    if date_prefix and instance.post_type_id in instance.POST_TYPE_IDS:
        # we're dealing with a post, article or newsitem: prefix with date
        dated_slug = date_prefix + '_' + slug
        if instance.slug == dated_slug:
            slug = dated_slug
        else:
            # check if we have it already, and append id_prefix if we do
            found = connection.scalar(
                "select id from posts where slug = '%s'" % dated_slug)
            if found and found != instance.id:
                slug = date_prefix + '_' + str(id_prefix) + slug
            else:
                slug = dated_slug
    else:
        # pages/profiles/unpublished: prefix with the expected or actual id:
        slug = str(id_prefix) + '_' + slug
    instance.slug = slug
    # TODO: slug history table for URL permanence?

    # set author
    instance.author = user
    instance.author_id = user.id


@listens_for(Post, 'before_insert')
def post_before_insert(mapper, connection, instance):
    post_before_upd_ins(mapper, connection, instance)
    # special-purpose code for insert goes here...


@listens_for(Post, 'before_update')
def post_before_update(mapper, connection, instance):
    post_before_upd_ins(mapper, connection, instance)
    # special-purpose code for update goes here...


class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('roles_id_seq'::regclass)"))
    label = Column(String, nullable=False, unique=True)
    description = Column(String)

    users = relationship('User', secondary=x_user_role, back_populates='roles')

    def __unicode__(self):
        return self.label


class Tag(db.Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('tags_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)
    is_important = Column(Boolean, nullable=False,
                          server_default=text("false"))
    for_images = Column(Boolean, nullable=False, server_default=text("true"))
    for_attachments = Column(Boolean, nullable=False,
                             server_default=text("true"))
    for_posts = Column(Boolean, nullable=False, server_default=text("true"))
    created = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now)
    images = relationship('Image', secondary=x_image_tag,
                          back_populates='tags')
    posts = relationship('Post', secondary=x_post_tag, back_populates='tags')

    attachments = relationship(
        'Attachment', secondary=x_attachment_tag, back_populates='tags')

    def __unicode__(self):
        return self.name


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('users_id_seq'::regclass)"))
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    fullname = Column(String, nullable=False)
    user_location = Column(String)
    image = Column(String)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    show_profile = Column(Boolean, nullable=False,
                          server_default=text("false"))
    is_superuser = Column(Boolean, nullable=False,
                          server_default=text("false"))
    created = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now)
    changed = Column(DateTime, server_default=text("now()"),
                     default=datetime.datetime.now,
                     onupdate=datetime.datetime.now)

    roles = relationship('Role', secondary=x_user_role, back_populates='users')

    def __unicode__(self):
        return self.username

    def set_password(self, plaintext):
        """
        Given a plaintext password, set the password field of this object
        to its bcrypt hash.
        """
        if isinstance(plaintext, unicode):
            plaintext = plaintext.encode('utf-8')
        self.password = bcrypt.hashpw(plaintext, bcrypt.gensalt())

    def check_password(self, plaintext):
        """
        Given a plaintext password, see if it matches the current bcrypted
        value of the password field belonging to this object.
        Returns True if there is a match, but False otherwise.
        """
        if isinstance(plaintext, unicode):
            plaintext = plaintext.encode('utf-8')
        return bcrypt.hashpw(plaintext, str(self.password)) == self.password

    @property
    def is_authenticated(self):
        return self.active

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return u'%d' % self.id

    def default_post_type_id(self):
        """
        Return a default post_type_id for material authored by this user.
        Returns None if the user is an editor or superuser, otherwise
        returns the type corresponding to the group he or she belongs to.
        NOTE: Since the values are hardcoded, this is quite tightly coupled to
        the database.
        """
        if self.is_superuser:
            return None
        group_labels = set([r.label for r in self.roles
                            if r.label.startswith('group')])
        if 'group_editor' in group_labels:
            return None
        elif 'group_refugee' in group_labels:
            return 1  # refugee's journey
        elif 'group_volunteer' in group_labels:
            return 2  # volunteer's tale
        elif 'group_oped' in group_labels:
            return 3  # article/oped
        return None


# Association models, with extra info attached to the link.

class XPostAttachment(db.Model):
    __tablename__ = 'x_post_attachment'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('x_post_attachment_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE',
                                onupdate=u'CASCADE'), nullable=False)
    attachment_id = Column(
        ForeignKey(
            u'attachments.id', ondelete=u'CASCADE', onupdate=u'CASCADE'),
        nullable=False)
    attachment_order = Column(Integer, nullable=False,
                              server_default=text("1"))
    custom_title = Column(String)
    custom_caption = Column(Text)
    linked_at = Column(DateTime, server_default=text("now()"),
                       default=datetime.datetime.now)

    attachment = relationship(u'Attachment', back_populates='posts')
    post = relationship(u'Post', back_populates='attachments')

    def __unicode__(self):
        return u'<XPostAttachment %d: %s for %s>' % (
            self.id, self.attachment, self.post)


"""class XPostImage(db.Model):
    __tablename__ = 'x_post_image'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('x_post_image_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE',
                                onupdate=u'CASCADE'), nullable=False)
    image_id = Column(
        ForeignKey(u'images.id', ondelete=u'CASCADE', onupdate=u'CASCADE'),
        nullable=False)
    image_order = Column(Integer, nullable=True, server_default=text("1"))
    custom_title = Column(String)
    custom_caption = Column(Text)
    linked_at = Column(DateTime, server_default=text("now()"),
                       default=datetime.datetime.now)

    image = relationship(u'Image', back_populates='posts')
    post = relationship(u'Post', back_populates='images')

    @property
    def image_path(self):
        return self.image.image_path

    @property
    def title(self):
        return self.custom_title or self.image.title or u''

    @property
    def caption(self):
        return self.custom_caption or self.image.caption or u''

    @property
    def width(self):
        return self.image.width

    @property
    def height(self):
        return self.image.height

    @property
    def bytes(self):
        return self.image.bytes

    def __unicode__(self):
        return u'<XPostImage %d: %s for %s>' % (self.id, self.image,
        self.post)"""
