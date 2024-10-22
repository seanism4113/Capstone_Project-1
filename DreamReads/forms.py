from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField, TextAreaField, SubmitField
from wtforms.validators import DataRequired,Length, Email, Optional

class JoinForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Re-enter password', validators=[Length(min=6)])

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()]) 
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image_url = StringField('Profile Image',default="/static/images/default-pic.png")

class AddBooktoListForm(FlaskForm):
    list_choice = SelectField('Add to List', choices = [('Want to Read', 'Want to Read'),('Currently Reading', 'Currently Reading'), ('Read', 'Read')])

class BookReviewForm(FlaskForm):
    review = TextAreaField('Review', validators=[Length(max=500)], render_kw={"placeholder" : "Enter your review (optional)"})
    rating = HiddenField('Rating', validators=[DataRequired()])
