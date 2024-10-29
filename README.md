# DreamReads

[https://dreamreads.onrender.com/](https://dreamreads.onrender.com/)

DreamsReads is a minimal recreation of GoodReads, the popular app where users keep track of their book habits and goals.

### DreamReads allows users to:

- Browse and search books from the Google Books API
  - Google Books API allows applications to perform full text searches and retrieve book information
  - In the Dream Reads app the following fields are retreived from the API: Specialized book id, Title, Authors, Description, Book cover image, Book avg rating, Page count, Date of publish, Publishers, and Book categories.
- Add books to three shelves/lists (Want to Read, Currently Reading, Read)
- Browse books that have been added to the user's Mybooks site.
- Shelves can be updated based on the book status.
- Rate books on a list on a 1-5 star scale
- Leave a review for books on a list

## DreamsReads | HomePage

![Alt text](/DreamReads/static/images/GoodReads%20Home.png)

## DreamsReads | Search for Books

![Alt text](/DreamReads/static/images/DreamReads%20Search.png)

## DreamsReads | MyBooks

![Alt text](/DreamReads/static/images/DreamsReads%20MyBooks.png)

## DreamsReads | Rating & Reviews

![Alt text](/DreamReads/static/images/DreamsReads%20Review.png)

## Setup
### Clone this repository
```bash
$ git clone https://github.com/seanism4113/Capstone_Project-1.git
$ cd DreamReads
```
### Create virtual environment and gather requirements
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

### Set .env constants
```bash
$ touch .env
```
- In the env file you will need to create a constant for:
```bash
API_KEY = 
DATABASE_URL = 
SECRET_KEY = 
```

API_KEY is a key obtained from GOOGLE BOOKS API.  You MUST have a google account to obtain an API Key.
[Google Cloud](https://console.cloud.google.com)
  - Find APIs & Services from the navigation menu dropdown in the top left
  - Click on Credentials
  - Click Create Credentials --> API Key

DATABASE URL
- Connect to your local database or an online database.  Example of connection to postgres: DATABASE_URL ='postgresql:///dreamReads_db'

SECRET_KEY
- Create your own secret key.  Example  SECRET_KEY = 'secretkey'

### Run project
```bash
$ flask run --debug
```
### Open page in browser
- Go to http://localhost:5000/

## Resources Used:

- [Google Books API ](https://developers.google.com/books/docs/overview)

## Technology Used

- Python
- Flask
- WTForms
- SQLAlchemy
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [Google Fonts](https://fonts.google.com/)
