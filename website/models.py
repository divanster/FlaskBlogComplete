from . import db
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime



# Define User model
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150), unique=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    about_me = db.Column(db.Text)
    timezone = db.Column(db.String(100))  # Add a timezone field
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define followers relationship
    followers = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        backref=db.backref('following', lazy='dynamic'),
        lazy='dynamic'
    )

    # One-to-many relationship with BlogPost model
    blog_posts = db.relationship('BlogPost', back_populates='author', lazy=True)
    # One-to-many relationship with Comment model
    comments = db.relationship('Comment', back_populates='author', lazy=True)

    likes = db.relationship('Like', back_populates='user', lazy=True)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def following_posts(self):
        return BlogPost.query.join(
            followers, (followers.c.followed_id == BlogPost.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    BlogPost.timestamp.desc())

    def has_liked(self, post):
        return Like.query.filter_by(user_id=self.id, blog_post_id=post.id).first() is not None

    def unlike_post(self, post):
        like = Like.query.filter_by(user_id=self.id, post_id=post.id).first()
        if like:
            db.session.delete(like)
            db.session.commit()


# Define BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a relationship to the User model
    author = db.relationship('User', back_populates='blog_posts', lazy=True)

    # Define a relationship to the Comment model
    comments = db.relationship('Comment', backref='post_comments', lazy=True)

    likes = db.relationship('Like', back_populates='blog_post', lazy=True)

    def __repr__(self):
        return f'<BlogPost {self.id}>'

    def get_like_count(self):
        return len(self.likes)



# Define Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Add this line
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)

    # Define a relationship to the User model
    author = db.relationship('User', back_populates='comments', lazy=True)

    likes = db.relationship('Like', back_populates='comment', lazy=True)

    def __repr__(self):
        return f'<Comment {self.id}>'


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='likes', lazy=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    blog_post = db.relationship('BlogPost', back_populates='likes')
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    comment = db.relationship('Comment', back_populates='likes')

    def __repr__(self):
        return f'<Like {self.id}>'