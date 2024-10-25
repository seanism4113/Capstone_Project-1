from dotenv import load_dotenv
import os
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, session, url_for, g as stored, jsonify
from models import connect_db, db, User, Book, BookList, BookReview
from forms import JoinForm, SignInForm, ProfileForm, AddBooktoListForm, BookReviewForm
from sqlalchemy.exc import IntegrityError
import requests
from search import sortSearchContent

# load variables from environment
load_dotenv()

# Flask configurationx
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CURRENT_USER_KEY = "current_user"
API_KEY = os.getenv("API_KEY")
baseUrl = "https://www.googleapis.com/books/v1/volumes"

# Setup database and create tables
connect_db(app)
db.create_all()


# global variable to hold results of book searches
results_list = []


@app.errorhandler(404)
def page_not_found(e):
    """ Redirect to 404 page for all URLs that do not exist """
    return render_template('404.html'), 404


@app.before_request
def add_user_to_stored():
    """ If logged in, add current user to Flask's global variable renamed stored """

    stored.user = User.query.filter_by(id=session.get(CURRENT_USER_KEY)).first() if CURRENT_USER_KEY in session else None

@app.context_processor
def inject_user():
    """ Allow html pages to be able to access stored user """
    return dict(stored_user=stored.user)

def process_signin(user):
    """ Add the user to session """
    session[CURRENT_USER_KEY] = user.id


def process_signout():
    """ Remove the user from session """
    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]


def signin_required(func):
    """ Decorator to require the user to be logged in """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not stored.user:
            flash('Access unauthorized', 'danger')
            return redirect(url_for('homepage'))
        return func(*args, **kwargs)
    return wrapper


def signout_required(func):
    """ Decorator to require the user to be logged out """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if stored.user:
            flash('Access unauthorized', 'danger')
            return redirect(url_for('homepage'))
        return func(*args, **kwargs)
    return wrapper


def get_books(query, max_results=40):
    """ Queries the API for books.  The API has a max results query of 40 so that is what it is set to """
    try:
        response = requests.get(f"{baseUrl}?q={query}&maxResults={max_results}&key={API_KEY}")
        return response.json().get("items", [])
    except request.requestException as error:
        print(f"Error retrieving books: {error}")
        return []


@app.route("/")
def homepage():
    """ Renders the homepage if logged out or the mybooks page if logged in"""
    if stored.user:
        return redirect(url_for('show_mybooks'))
    else:    
        return render_template('homepage-anon.html')


@app.route('/register', methods=['GET', 'POST'])
@signout_required
def register():
    """ Renders the Register form which hashes the password,  checks that password and
        user information was entered correctly, and adds user to db.
    """
    form = JoinForm()

    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('The passwords do not match', 'danger')
            return render_template('users/register.html', form=form)

        try:
            user = User.register(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()
            process_signin(user)
            return redirect(url_for('homepage'))

        except IntegrityError:
            db.session.rollback()
            flash(f"An account already exists with the email address {form.email.data}", 'danger')

    return render_template('users/register.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
@signout_required
def signin():
    """ Route for form to login user """

    form = SignInForm()

    if form.validate_on_submit():
        user = User.authenticate(
            email = form.email.data,
            password = form.password.data
        )

        if not user:
            if User.query.filter_by(email = form.email.data).first() is None:
                flash(f"An account for {form.email.data} was not found", 'danger')
            else:
                flash('Your password is incorrect', 'danger')
            return redirect(url_for('signin'))
        
        process_signin(user)
        return redirect(url_for('homepage'))
 
    return render_template('users/signin.html', form=form)


@app.route('/signout')
@signin_required
def signout():
    """ Route to logout user """
    process_signout()
    flash("Signout successful", 'success')
    return redirect(url_for('homepage'))


@app.route('/user/show/<id_first_last>')
@signin_required
def show_profile(id_first_last):
    """ Shows the user's basic profile information """

    return render_template('/users/profile.html')


@app.route('/user/edit', methods=['GET', 'POST'])
@signin_required
def edit_profile():
    """ Allows the user to edit their profile information """

    form = ProfileForm(obj=stored.user)

    if form.validate_on_submit():
        stored.user.first_name = form.first_name.data
        stored.user.last_name = form.last_name.data
        stored.user.email = form.email.data
        stored.user.profile_image_url = form.profile_image_url.data
        
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('show_profile', id_first_last=f"{stored.user.id}-{stored.user.first_name}-{stored.user.last_name}" ))

    return render_template('/users/profile-edit.html', form=form)


# Utilize in the browse genre and search books routes
def get_user_books():
    if stored.user:
        return {book.id: list_name for book, list_name in db.session.query(Book, BookList.list_name).join(BookList).filter_by(user_id=stored.user.id).all()}
    return {}


@app.route('/genres/', defaults={'genre': ''})
@app.route('/genres/<string:genre>')
def browse_genre(genre):
    """  Allows the user to browse books by genre and renders the browse page.  Includes the form
        to add book to a list on this page.
    """

    global results_list
    form = AddBooktoListForm()
    results_list = sortSearchContent(get_books(f'subject:{genre}')) if genre else []
    return render_template('/searches/search-genre.html',search = genre, form=form, results_list = results_list, mybooks_list=get_user_books())


@app.route("/search")
def search_books():
    """  Allows the user to search books and renders the search page.  Includes the form
        to add book to a list on this page.
    """

    global results_list
    form = AddBooktoListForm()
    query = request.args.get("q", "").strip()
    results_list = sortSearchContent(get_books(query)) if query else []
    return render_template('/searches/search-books.html', search = query, form=form, results_list = results_list, mybooks_list=get_user_books())


@app.route('/list/add', methods=['POST'])
@signin_required
def add_book_to_list():
    """ Add book to lists for Read, Want to Read and Currently Reading
        It uses the global results list to find the index that was clicked and uses the information
        for that index to add the books to both the Book table and BookList table
    """

    global results_list
    form = AddBooktoListForm()

    list_choice = request.form.get('choice')
    list_index = int(request.form.get('index'))
    book_id = results_list[list_index]['id']

    if Book.query.filter_by(id=book_id).first():
        book_list_item = BookList.query.filter(BookList.book_id == book_id).first()
        book_list_item.list_name = list_choice
        db.session.commit()
        return redirect(request.referrer)

    
    book = Book(    
        id = results_list[list_index]['id'],
        title = results_list[list_index]['title'],
        authors = results_list[list_index]['authors'],
        short_description = results_list[list_index]['short_description'],
        description = results_list[list_index]['description'],
        cover_image = results_list[list_index]['cover_image'],
        avg_rating = results_list[list_index]['avg_rating'],
        page_count = results_list[list_index]['page_count'],
        date_published = results_list[list_index]['date_published'],
        publisher = results_list[list_index]['publisher'],
        categories = results_list[list_index]['categories']
    )
    db.session.add(book)
    db.session.commit()

    book_list = BookList(
        book_id = book.id,
        user_id = stored.user.id,
        list_name = list_choice
    )
    db.session.add(book_list)
    db.session.commit()

    return redirect(request.referrer)


@app.route('/list/edit', methods = ['POST'])
@signin_required
def edit_book_list():
    """ Route for user to edit which list a book is on"""
    form = AddBooktoListForm()
    list_choice = request.form.get('choice')
    list_index = request.form.get('index')

    book_list_item = BookList.query.filter_by(book_id=list_index).first()
    book_list_item.list_name = list_choice
    db.session.commit()
    return redirect(request.referrer)


@app.route('/list/remove', methods = ['POST'])
@signin_required
def remove_book_list():
    """ Allows user to remove a book from a list.  This removes the entry from
        the Book table and BookList table
    """
    book_id = request.form.get('index')
    BookList.query.filter_by(book_id = book_id).delete()
    Book.query.filter_by(id = book_id).delete()
    db.session.commit()
    return redirect(request.referrer)


@app.route('/mybooks')
@signin_required
def show_mybooks():
    """ Displays the page for the user's Books which has it broken down by lists """
    form = AddBooktoListForm()
    shelf = request.args.get('shelf', 'All').strip()
    books_query = db.session.query(Book, BookList.list_name, BookList.date_added).join(BookList).filter(BookList.user_id == stored.user.id)
    user_books = books_query.all() if shelf == 'All' else books_query.filter(BookList.list_name == shelf). all()
    list_length = {'all': len(books_query.all()),
                   'read': len(books_query.filter(BookList.list_name == 'Read').all()),
                    'current-read' : len(books_query.filter(BookList.list_name == 'Currently Reading').all()),
                    'to-read' : len(books_query.filter(BookList.list_name == 'Want to Read').all())  }


    return render_template('/books/mybooks.html', form=form, user_books = user_books, shelf = shelf, books_query=books_query, list_length=list_length)


@app.route('/review/edit/<book_id>', methods=['GET', 'POST'])
@signin_required
def review_book(book_id):
    """ Displays route which allows user to leave a review and rating for a book """
    book = Book.query.filter_by(id=book_id).first_or_404()
    form = BookReviewForm()

    review = BookReview.query.filter_by(user_id=stored.user.id, book_id=book.id).first()

    form = BookReviewForm(obj=review)

    if form.validate_on_submit():
        if review:
            review.review = form.review.data
            review.rating = form.rating.data

        else:
            review = BookReview(book_id = book.id,
                            user_id = stored.user.id,
                            review = form.review.data,
                            rating = form.rating.data
                            )
            db.session.add(review)

        db.session.commit()
        flash('Your review has been submitted', 'success')
        return redirect(url_for('show_mybooks'))
    else:
        print('Form validation failed', form.errors)
    return render_template('/books/book-review.html', book=book, form=form, review=review)


@app.route('/review/delete/<book_id>', methods=['POST'])
@signin_required
def delete_review(book_id):
    """ Allows user to delete a review """

    review = BookReview.query.filter_by(user_id=stored.user.id, book_id=book_id).first()
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('show_mybooks'))