from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func

# Initialize the database and Bcrypt instances
db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """ Connect the Flask app to the database """
    db.app = app
    db.init_app(app)


class Book(db.Model):
    """ Model representing a book in the database"""

    __tablename__ = 'books'  # Name of the database table

    # Columns for the books table
    id = db.Column(db.Text, primary_key=True, autoincrement=False, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text)
    short_description = db.Column(db.Text)
    description = db.Column(db.Text)
    cover_image = db.Column(db.Text)
    avg_rating = db.Column(db.Float)
    page_count = db.Column(db.Integer)
    date_published = db.Column(db.Text)
    publisher = db.Column(db.Text)
    categories = db.Column(db.Text)

    # Define relationships to the other models
    book_lists = db.relationship('BookList', backref='book', cascade="all")
    reviews = db.relationship('BookReview', back_populates='book')


class BookList(db.Model):
    """ Model representing a user's book list """

    __tablename__ = 'book_lists' # Name of the database table

    # Columns for the book_lists table
    book_id = db.Column(db.Text, db.ForeignKey('books.id', ondelete='cascade'), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    list_name = db.Column(db.Text)
    date_added = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

class BookReview(db.Model):
    """ Model representing a review from a user on a book """
    
    __tablename__ = 'book_reviews' # Name of the database table

    # Columns for the book_reviews table
    book_id = db.Column(db.Text, db.ForeignKey('books.id', ondelete='cascade'), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    review = db.Column(db.Text)
    rating = db.Column(db.Integer)

    # Define relationships to the other models
    user = db.relationship('User', back_populates='reviews')
    book = db.relationship('Book', back_populates='reviews')

class User(db.Model):
    """ Model respresenting a user of the site """

    __tablename__ = 'users' # Name of the database table

    # Columns for the users table
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text,nullable=False,unique=True)
    profile_image_url = db.Column(db.Text,default="/static/images/default-pic.png")
    password = db.Column(db.Text,nullable=False)

    # Define relationships to the other models
    book_lists = db.relationship('BookList',backref='user',cascade="all")
    reviews = db.relationship('BookReview', back_populates='user')

    @classmethod
    def register(cls, first_name, last_name, email, password):
        """ Register a new user and create a hashed password using bcrypt """

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
        """ Authenticate a user with their email and password using bcrypt """

        user = cls.query.filter_by(email=email).first() #Locate user by email

        if user:
            is_authenticated = bcrypt.check_password_hash(user.password, password) # Check password
            if is_authenticated:
                return user # Return the user if authentification passes
        
        return False # Return false if authentification fails