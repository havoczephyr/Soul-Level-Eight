from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms import StringField, BooleanField, FileField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from ds_blog.models import User



class TimelineEntryForm(FlaskForm):
    character_name = StringField('Character Name', validators=[DataRequired()])
    #slash_data contains: journey_cycle, last_bonfire.
    slash_data = TextAreaField('Slash Data', validators=[DataRequired()])
    #player_game_data contains: play_time, total_deaths 
    player_game_data = TextAreaField('Player Game Data', validators=[DataRequired()])
    #attributes contains: SL, VIT, ATN, END, STR, DEX, RES, INT, FTH 
    attributes = TextAreaField('Attributes', validators=[DataRequired()])
    #charAsm contains: primary/secondary left/right weapon, helmet, armor, gauntlet, leggings
    char_equip = TextAreaField('Character Equipment(charAsm)', validators=[DataRequired()])
    #base_stats contains max_HP, max_stamina, soft_humanity
    base_stats = TextAreaField('Base Stats', validators=[DataRequired()])
    submit = SubmitField('Submit Data')

class AnnouncementsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post', validators=[DataRequired()])

class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is taken!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember me.')

    submit = SubmitField('Log In')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=2, max=20)])
    email = StringField('Email', validators=[Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update Account')
    darkmode = BooleanField('Dark Mode')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('That email is taken!')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken!') 


