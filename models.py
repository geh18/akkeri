# coding: utf-8
import bcrypt
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, text)
from sqlalchemy.orm import relationship
from app import db


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
    preview_image = Column(ForeignKey(
        u'images.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    available_to_others = Column(
        Boolean, nullable=False, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

    owner = relationship(u'User')
    image = relationship(u'Image')
    posts = relationship('XPostAttachment', back_populates='attachment')
    tags = relationship('Tag', secondary=x_attachment_tag,
                        back_populates='attachments')

    def __unicode__(self):
        return self.attachment_path


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
    added_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship(u'User')
    post = relationship(u'Post')


class Image(db.Model):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('images_id_seq'::regclass)"))
    owner_id = Column(
        ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'),
        nullable=False, index=True)
    image_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    image_taken = Column(DateTime)
    width = Column(Integer, nullable=False, server_default=text("0"))
    height = Column(Integer, nullable=False, server_default=text("0"))
    bytes = Column(Integer, nullable=False, server_default=text("0"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    available_to_others = Column(
        Boolean, nullable=False, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

    owner = relationship(u'User')
    posts = relationship('XPostImage', back_populates='image')
    tags = relationship('Tag', secondary=x_image_tag, back_populates='images')

    def __unicode__(self):
        return self.image_path


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
        return u'%s - %s' % (self.label, self.name_en)


class Post(db.Model):
    __tablename__ = 'posts'

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
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    is_draft = Column(Boolean, nullable=False, server_default=text("false"))
    summary = Column(Text)
    body = Column(Text)
    post_type_id = Column(ForeignKey(
        u'post_types.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    language_id = Column(ForeignKey(
        u'languages.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    created = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))
    published = Column(DateTime, index=True)

    author = relationship(u'User', primaryjoin='Post.author_id == User.id')
    language = relationship(u'Language')
    last_changed_by_user = relationship(
        u'User', primaryjoin='Post.last_changed_by == User.id')
    post_type = relationship(u'PostType')
    images = relationship('XPostImage', back_populates='post')
    attachments = relationship('XPostAttachment', back_populates='post')
    tags = relationship('Tag', secondary=x_post_tag, back_populates='posts')

    def __unicode__(self):
        return u'%s [%d]' % (self.title, self.id)


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
    created = Column(DateTime, server_default=text("now()"))

    posts = relationship('Post', secondary=x_post_tag, back_populates='tags')
    images = relationship('Image', secondary=x_image_tag,
                          back_populates='tags')
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
    active = Column(Boolean, nullable=False, server_default=text("true"))
    show_profile = Column(Boolean, nullable=False,
                          server_default=text("false"))
    is_superuser = Column(Boolean, nullable=False,
                          server_default=text("false"))
    created = Column(DateTime, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

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
    linked_at = Column(DateTime, server_default=text("now()"))

    attachment = relationship(u'Attachment', back_populates='posts')
    post = relationship(u'Post', back_populates='attachments')

    def __unicode__(self):
        return u'<XPostAttachment %d: %s for %s>' % (
            self.id, self.attachment, self.post)


class XPostImage(db.Model):
    __tablename__ = 'x_post_image'

    id = Column(Integer, primary_key=True, server_default=text(
        "nextval('x_post_image_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE',
                                onupdate=u'CASCADE'), nullable=False)
    image_id = Column(
        ForeignKey(u'images.id', ondelete=u'CASCADE', onupdate=u'CASCADE'),
        nullable=False)
    image_order = Column(Integer, nullable=False, server_default=text("1"))
    custom_title = Column(String)
    custom_caption = Column(Text)
    linked_at = Column(DateTime, server_default=text("now()"))

    image = relationship(u'Image', back_populates='posts')
    post = relationship(u'Post', back_populates='images')

    def __unicode__(self):
        return u'<XPostImage %d: %s for %s>' % (self.id, self.image, self.post)
