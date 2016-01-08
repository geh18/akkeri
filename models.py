# coding: utf-8
import bcrypt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import relationship
from app import db
#from sqlalchemy.ext.declarative import declarative_base


#Base = declarative_base()
#metadata = Base.metadata

# NOTE:
# Much of the code for the model classes was initially generated using sqlacodegen


class Attachment(db.Model):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, server_default=text("nextval('attachments_id_seq'::regclass)"))
    owner_id = Column(ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False, index=True)
    attachment_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    bytes = Column(Integer, nullable=False, server_default=text("0"))
    attachment_date = Column(DateTime)
    preview_image = Column(ForeignKey(u'images.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    available_to_others = Column(Boolean, nullable=False, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

    owner = relationship(u'User')
    image = relationship(u'Image')


class Featured(db.Model):
    __tablename__ = 'featured'

    id = Column(Integer, primary_key=True, server_default=text("nextval('featured_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    featured_from = Column(DateTime, nullable=False, index=True, server_default=text("now()"))
    featured_to = Column(DateTime, nullable=False, index=True, server_default=text("now()"))
    for_frontpage = Column(Boolean, nullable=False, server_default=text("false"))
    for_category_page = Column(Boolean, nullable=False, server_default=text("true"))
    added_by = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    added_at = Column(DateTime, nullable=False, server_default=text("now()"))

    user = relationship(u'User')
    post = relationship(u'Post')


class Image(db.Model):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, server_default=text("nextval('images_id_seq'::regclass)"))
    owner_id = Column(ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False, index=True)
    image_path = Column(String, nullable=False, unique=True)
    title = Column(String)
    credit = Column(String)
    caption = Column(Text)
    image_taken = Column(DateTime)
    width = Column(Integer, nullable=False, server_default=text("0"))
    height = Column(Integer, nullable=False, server_default=text("0"))
    bytes = Column(Integer, nullable=False, server_default=text("0"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    available_to_others = Column(Boolean, nullable=False, server_default=text("false"))
    added = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

    owner = relationship(u'User')


class Language(db.Model):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    code = Column(String(2))
    name_is = Column(String)
    name_en = Column(String)


class PostType(db.Model):
    __tablename__ = 'post_types'

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False, unique=True)
    name_is = Column(String)
    name_en = Column(String)


class Post(db.Model):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, server_default=text("nextval('posts_id_seq'::regclass)"))
    author_id = Column(ForeignKey(u'users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False, index=True)
    last_changed_by = Column(ForeignKey(u'users.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    author_visible = Column(Boolean, nullable=False, server_default=text("true"))
    author_line = Column(String)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    is_draft = Column(Boolean, nullable=False, server_default=text("false"))
    summary = Column(Text)
    body = Column(Text)
    post_type_id = Column(ForeignKey(u'post_types.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    language_id = Column(ForeignKey(u'languages.id', ondelete=u'SET NULL', onupdate=u'CASCADE'))
    created = Column(DateTime, index=True, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))
    published = Column(DateTime, index=True)

    author = relationship(u'User', primaryjoin='Post.author_id == User.id')
    language = relationship(u'Language')
    user = relationship(u'User', primaryjoin='Post.last_changed_by == User.id')
    post_type = relationship(u'PostType')


class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, server_default=text("nextval('roles_id_seq'::regclass)"))
    label = Column(String, nullable=False, unique=True)
    description = Column(String)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, server_default=text("nextval('tags_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)
    is_important = Column(Boolean, nullable=False, server_default=text("false"))
    for_images = Column(Boolean, nullable=False, server_default=text("true"))
    for_attachments = Column(Boolean, nullable=False, server_default=text("true"))
    for_posts = Column(Boolean, nullable=False, server_default=text("true"))
    created = Column(DateTime, server_default=text("now()"))


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    fullname = Column(String, nullable=False)
    user_location = Column(String)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    show_profile = Column(Boolean, nullable=False, server_default=text("false"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))
    created = Column(DateTime, server_default=text("now()"))
    changed = Column(DateTime, server_default=text("now()"))

    def __repr__(self):
        return u'<User: %d %s>' % (self.id, self.username)

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
        return bcrypt.hashpw(plaintext, self.password) == self.password

    @property
    def is_authenticated(self):
        return self.active

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    @property
    def get_id(self):
        return u'%d' % self.id

class XAttachmentTag(db.Model):
    __tablename__ = 'x_attachment_tag'
    __table_args__ = (
        UniqueConstraint('attachment_id', 'tag_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_attachment_tag_id_seq'::regclass)"))
    attachment_id = Column(ForeignKey(u'attachments.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tag_id = Column(ForeignKey(u'tags.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tagged_at = Column(DateTime, server_default=text("now()"))

    attachment = relationship(u'Attachment')
    tag = relationship(u'Tag')


class XImageTag(db.Model):
    __tablename__ = 'x_image_tag'
    __table_args__ = (
        UniqueConstraint('image_id', 'tag_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_image_tag_id_seq'::regclass)"))
    image_id = Column(ForeignKey(u'images.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tag_id = Column(ForeignKey(u'tags.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tagged_at = Column(DateTime, server_default=text("now()"))

    image = relationship(u'Image')
    tag = relationship(u'Tag')


class XPostAttachment(db.Model):
    __tablename__ = 'x_post_attachment'

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_post_attachment_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    attachment_id = Column(ForeignKey(u'attachments.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    attachment_order = Column(Integer, nullable=False, server_default=text("1"))
    custom_title = Column(String)
    custom_caption = Column(Text)
    linked_at = Column(DateTime, server_default=text("now()"))

    attachment = relationship(u'Attachment')
    post = relationship(u'Post')


class XPostImage(db.Model):
    __tablename__ = 'x_post_image'

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_post_image_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    image_id = Column(ForeignKey(u'images.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    image_order = Column(Integer, nullable=False, server_default=text("1"))
    custom_title = Column(String)
    custom_caption = Column(Text)
    linked_at = Column(DateTime, server_default=text("now()"))

    image = relationship(u'Image')
    post = relationship(u'Post')


class XPostTag(db.Model):
    __tablename__ = 'x_post_tag'
    __table_args__ = (
        UniqueConstraint('post_id', 'tag_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_post_tag_id_seq'::regclass)"))
    post_id = Column(ForeignKey(u'posts.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tag_id = Column(ForeignKey(u'tags.id', ondelete=u'CASCADE', onupdate=u'CASCADE'))
    tagged_at = Column(DateTime, server_default=text("now()"))

    post = relationship(u'Post')
    tag = relationship(u'Tag')


class XUserRole(db.Model):
    __tablename__ = 'x_user_role'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('x_user_role_id_seq'::regclass)"))
    user_id = Column(ForeignKey(u'users.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    role_id = Column(ForeignKey(u'roles.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    granted_at = Column(DateTime, server_default=text("now()"))

    role = relationship(u'Role')
    user = relationship(u'User')
