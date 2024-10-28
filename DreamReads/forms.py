from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField, TextAreaField, SubmitField
from wtforms.validators import DataRequired,Length, Email

class JoinForm(FlaskForm):
    """ Form for new user registration"""

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)]) # User's password with minimum length
    confirm_password = PasswordField('Re-enter password', validators=[Length(min=6)]) # Confirm the password

class SignInForm(FlaskForm):
    """ Form for user sign-in"""

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)]) # User's password with minimum length

class ProfileForm(FlaskForm):
    """ Form for updating a user's profile """

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image_url = StringField('Profile Image',default="/static/images/default-pic.png")

class AddBooktoListForm(FlaskForm):
    """ Form for adding a book to a user's reading list """

    list_choice = SelectField('Add to List', choices = [('Want to Read', 'Want to Read'),('Currently Reading', 'Currently Reading'), ('Read', 'Read')]) # Options the user can select for the book list

class BookReviewForm(FlaskForm):
    """ Form for adding a book review and rating to a book """

    review = TextAreaField('Review', validators=[Length(max=500)], render_kw={"placeholder" : "Enter your review (optional)"}) # Text area for user review
    rating = HiddenField('Rating', validators=[DataRequired()]) # Hidden field for rating. Rating is (1-5)
