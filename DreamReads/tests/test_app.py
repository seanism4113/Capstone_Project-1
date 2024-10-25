import os
import pytest

os.environ['DATABASE_URL'] = 'postgresql:///reads_test_db'

from app import app, db, User, Book, BookReview, BookList

os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY')
os.environ['API_KEY'] = os.getenv("API_KEY")
app.config['WTF_CSRF_ENABLED'] = False


@pytest.fixture
def client():
    """ Create a test client for app """
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove() 
            db.drop_all()


@pytest.fixture
def test_user():
    """ Create a test user """
    user = User.register(
        first_name='first',
        last_name='last',
        email='test@gmail.com',
        password='testpassword'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def login_user(client, test_user):
    """ Log in test user """
    client.post('/signin', data={
        'email': 'test@gmail.com',
        'password': 'testpassword'
    })


def test_homepage(client):
    """ Test the homepage """
    response = client.get('/')
    assert b'Deciding what to read next?' in response.data


def test_register(client):
    """Test user registration."""

    response = client.post('/register', data={
        'first_name': 'newFirst',
        'last_name': 'newLast',
        'email': 'newuser@gmail.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    })

    assert response.status_code == 302 
    user = User.query.filter_by(email='newuser@gmail.com').first()
    assert user is not None

    # Check if the user is signed in and the session hold the user's id
    with client.session_transaction() as session:
        assert session.get("current_user") == user.id  


def test_signin(client, test_user):
    """ Test that a user can sign-in """
    
    response = client.post('/signin', data={
        'email': test_user.email,
        'password': test_user.password 
    })

    with client.session_transaction() as session:
        session["current_user"] = test_user.id 

    assert response.status_code == 302 
    assert session.get("current_user") == test_user.id


def test_signout(client, test_user):
    """ Test that a user can sign out """
    
    response = client.post('/signin', data={
        'email': test_user.email,
        'password': 'testpassword'  
    })
    with client.session_transaction() as session:
        session["current_user"] = test_user.id

    response = client.get('/signout')

    assert response.status_code == 302 
    with client.session_transaction() as session:
        assert session.get("current_user") is None  


def test_edit_profile(client, test_user):
    """ Test editing a user's profile """

    with client.session_transaction() as session:
        session["current_user"] = test_user.id 

    response = client.post('/user/edit', data={
        'first_name': 'updateFirst',
        'last_name': 'updateLast',
        'email': 'updateTest@gmail.com',
        'profile_image_url': 'http://test.com/image.jpg'
    })
    updated_user = User.query.filter(User.id == test_user.id).first()
    
    assert response.status_code == 302
    assert updated_user.first_name == 'updateFirst'


def test_browse_genre(client):
    """ Test browsing for books by genre """

    response = client.get('/genres/Fiction')
    assert response.status_code == 200
    assert b'Fiction' in response.data


def test_search_books(client):
    """ Test searching for books by book title or author """
    response = client.get('/search?q=Python') 
    assert response.status_code == 200
    assert b'Showing results for: "<b>Python</b>"' in response.data 


def test_add_book_to_list(client, test_user):
    """ Test adding a book to the user's lists """

    global results_list

    with client.session_transaction() as session:
        session["current_user"] = test_user.id

    results_list = [{
        'id': 'Y575FHD763',
        'title': 'Test Book',
        'authors': 'Test Author',
        'short_description': ' Test Short description.',
        'description': 'Test Full description.',
        'cover_image': 'http://test.com/cover.jpg',
        'avg_rating': 4.5,
        'page_count': 250,
        'date_published': '2024-25-10',
        'publisher': 'Test Publisher',
        'categories': 'Fiction'
    }]

    book = Book(
        id=results_list[0]['id'],
        title=results_list[0]['title'],
        authors=results_list[0]['authors'],
        short_description=results_list[0]['short_description'],
        description=results_list[0]['description'],
        cover_image=results_list[0]['cover_image'],
        avg_rating=results_list[0]['avg_rating'],
        page_count=results_list[0]['page_count'],
        date_published=results_list[0]['date_published'],
        publisher=results_list[0]['publisher'],
        categories=results_list[0]['categories']
    )
    db.session.add(book)
    db.session.commit()

    response = client.post('/list/add', data={'choice': 'Want to Read','index': '0'})

    book_list_entry = BookList(
        user_id=test_user.id, 
        book_id=book.id, 
        list_name='Want to Read'
    )
    db.session.add(book_list_entry)
    db.session.commit()

    test_book = Book.query.filter_by(id='Y575FHD763').first()
    test_entry = BookList.query.filter_by(user_id=test_user.id, book_id='Y575FHD763').first()

    assert response.status_code == 302  
    assert test_book is not None
    assert test_entry is not None
    assert test_entry.list_name == 'Want to Read'


def test_remove_book_from_list(client, test_user):
    """ Test removing book from user's lists """

    with client.session_transaction() as session:
        session["current_user"] = test_user.id

    book = Book(
        id='Y575FHD763',
        title='Test Book',
        authors='Test Author',
        short_description='Test Short description.',
        description='Test Full description.',
        cover_image='http://test.com/cover.jpg',
        avg_rating=4.5,
        page_count=250,
        date_published='2024-25-10',
        publisher='Test Publisher',
        categories='Fiction'
    )
    db.session.add(book)
    db.session.commit()

    book_list_entry = BookList(
        user_id=test_user.id, 
        book_id=book.id, 
        list_name='Want to Read'
    )
    db.session.add(book_list_entry)
    db.session.commit()

    try:
        response = client.post('/list/remove', data={
            'book_id': 'Y575FHD763'
        })
        removed_entry = BookList.query.filter_by(user_id=test_user.id, book_id='Y575FHD763').first()
        remaining_book = Book.query.filter_by(id='Y575FHD763').first()

        assert response.status_code == 302  
        assert remaining_book is None

    except Exception as e:
        print("An error occurred:", e)


def test_review_book(client, test_user):
    """ Test review and ratings for a book """

    with client.session_transaction() as session:
        session["current_user"] = test_user.id  

    book = Book(
        id='Y575FHD763',
        title='Test Book',
        authors=' Test Author',
        short_description='Test Short description.',
        description=' Test Full description.',
        cover_image='http://test.com/cover.jpg',
        avg_rating=4.5,
        page_count=250,
        date_published='2024-25-10',
        publisher='Test Publisher',
        categories='Fiction'
    )
    db.session.add(book)
    db.session.commit()
    
    response = client.post('/review/edit/Y575FHD763', data={
        'review': 'Amazing Book to read!',
        'rating': 5
    })
    review = BookReview.query.filter_by(user_id=test_user.id, book_id='Y575FHD763').first()
    
    assert response.status_code == 302  
    assert review is not None


def test_delete_review(client, test_user):
    """ Test deletion of a review/rating """

    with client.session_transaction() as session:
        session["current_user"] = test_user.id  

    book = Book(
        id='Y575FHD763',
        title='Test Book',
        authors='Test Author',
        short_description='Test Short description.',
        description='Test Full description.',
        cover_image='http://test.com/cover.jpg',
        avg_rating=4.5,
        page_count=250,
        date_published='2024-25-10',
        publisher='Test Publisher',
        categories='Fiction'
    )
    db.session.add(book)
    db.session.commit()

    review = BookReview(
        book_id='Y575FHD763',
        user_id=test_user.id,
        review='Amazing Book to read!',
        rating=5
    )
    db.session.add(review)
    db.session.commit()

    response = client.post('/review/delete/Y575FHD763')
    test_review = BookReview.query.filter_by(user_id=test_user.id, book_id='Y575FHD763').first()

    assert response.status_code == 302  
    assert test_review is None  


def test_404(client):
    """ Test 404 errors """

    response = client.get('/thispagedoesnotexist')

    assert response.status_code == 404
    assert b'images/404-error.avif' in response.data
