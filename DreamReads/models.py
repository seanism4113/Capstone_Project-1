from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func
import enum
from sqlalchemy import Enum

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Text, primary_key=True, autoincrement=False, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text)
    short_description = db.Column(db.Text)
    description = db.Column(db.Text)
    cover_image = db.Column(db.Text)
    avg_rating = db.Column(db.Text)
    page_count = db.Column(db.Text)
    date_published = db.Column(db.Text)
    publisher = db.Column(db.Text)
    categories = db.Column(db.Text)

    book_lists = db.relationship('BookList', backref='book', cascade="all")
    reviews = db.relationship('BookReview', back_populates='book')


class BookList(db.Model):

    __tablename__ = 'book_lists'

    book_id = db.Column(db.Text, db.ForeignKey('books.id', ondelete='cascade'), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    list_name = db.Column(db.Text)
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

class BookReview(db.Model):
    __tablename__ = 'book_reviews'

    book_id = db.Column(db.Text, db.ForeignKey('books.id', ondelete='cascade'), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    review = db.Column(db.Text)
    rating = db.Column(db.Integer)

    user = db.relationship('User', back_populates='reviews')
    book = db.relationship('Book', back_populates='reviews')

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text,nullable=False,unique=True)
    profile_image_url = db.Column(db.Text,default="/static/images/default-pic.png")
    password = db.Column(db.Text,nullable=False)

    book_lists = db.relationship('BookList',backref='user',cascade="all")
    reviews = db.relationship('BookReview', back_populates='user')

    @classmethod
    def register(cls, first_name, last_name, email, password):

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = hashed_password,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, email, password):

        user = cls.query.filter_by(email=email).first()

        if user:
            is_authenticated = bcrypt.check_password_hash(user.password, password)
            if is_authenticated:
                return user
        
        return False