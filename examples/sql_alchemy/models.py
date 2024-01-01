from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt
import datetime

Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'
    id= Column(Integer, primary_key=True)
    title = Column(String(255), unique=False, nullable=False)
    content = Column(String)
    markdown = Column(String)
    json = Column(JSON)
    created_on = Column(DateTime)
    edited_on = Column(DateTime)
    published_on = Column(DateTime)
    unpublished_on = Column(DateTime)
    deleted_on = Column(DateTime)
    user = relationship("User", back_populates="posts")
    user_id = Column(Integer, ForeignKey('users.id'))
    is_published = Column(Boolean, default=False, nullable=False)
    is_unpublished = Column(Boolean, default=False, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_draft = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_visible_to_admins = Column(Boolean, default=False, nullable=False)
    is_visible_to_users = Column(Boolean, default=False, nullable=False)
    is_visible_to_visitors = Column(Boolean, default=False, nullable=False)
    is_visible_to_subscribers = Column(Boolean, default=False, nullable=False)
    is_visible_to_subscribers_with_tier_2 = Column(Boolean, default=False, nullable=False)
    is_visible_to_subscribers_with_tier_3 = Column(Boolean, default=False, nullable=False)

    def create_post(self, title, user, content, draft):
        self.title = title
        self.user = user
        self.content = content
        self.is_draft = draft
        self.created_on = datetime.datetime.now()

    def edit_post(self, title, content, draft):
        self.title = title
        self.content = content
        self.is_draft = draft
        self.edited_on = datetime.datetime.now()

    def publish_post(self, featured):
        self.is_published = True
        self.is_draft = False
        self.is_featured = featured
        self.published_on = datetime.datetime.now()

    def unpublish_post(self):
        self.is_published = False
        self.is_draft = True

    def delete_post(self):
        self.is_published = False
        self.is_draft = False
        self.is_deleted = True
        self.is_visible_to_visitors = False
        self.is_visible_to_subscribers = False
        self.is_visible_to_admins = False
        self.deleted_on = datetime.datetime.now()

    def make_visible(self, admins, users, visitors, subscribers, tier_1, tier_2, tier_3):
        self.is_visible_to_admins = admins
        self.is_visible_to_users = users
        self.is_visible_to_visitors = visitors
        self.is_visible_to_subscribers = subscribers
        self.is_visible_to_subscribers = tier_1
        self.is_visible_to_subscribers_with_tier_2 = tier_2
        self.is_visible_to_subscribers_with_tier_3 = tier_3


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=False, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    hash = Column(String(255), nullable=True)
    created_on = Column(DateTime, nullable=False)
    verified = Column(Boolean, default=False, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=True)
    posts = relationship("Post", order_by=Post.id, back_populates="user")

    def set_password(self, password):
        self.hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self._password_hash.encode('utf-8'))

    def create_user(self, name, email, password, is_admin=False):
        self.name = name
        self.email = email
        self.set_password(password)
        self.is_admin = is_admin
        self.created_on = datetime.datetime.now()

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
