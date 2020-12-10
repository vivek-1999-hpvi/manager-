from flask_wtf import FlaskForm
from wtforms import BooleanField, validators,StringField,TextAreaField,PasswordField,SelectField,SubmitField,IntegerField,SelectMultipleField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired,Length,Email,EqualTo
from flask_wtf.file import FileField,FileAllowed
from wtforms.fields.html5 import EmailField

class RegistrationForm(FlaskForm):
   first_name = StringField("First Name",validators=[InputRequired(),Length(min=2,max=30)])
   last_name= StringField("Last Name",validators=[InputRequired(),Length(min=2,max=30)])
   phone=StringField("Phone Number",validators=[InputRequired(),Length(max=10,min=10)])
   email = EmailField('Email', [validators.DataRequired(), validators.Email()])
   typex=SelectField(u'Type',choices=[('1','Employee'),('2','Manager')])
   password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
   cpassword = PasswordField("Confirm Password", validators=[InputRequired(), Length(min=8, max=20),EqualTo('password')])
   image=FileField(validators=[FileAllowed(['jpg','png','jpeg'],'images only'),InputRequired()])
   submit=SubmitField("Sign Up")

class DepartmentForm(FlaskForm):
   department= SelectField(u'Type',choices=[('1','d1'),('2','d2'),('3','d3'),('4','d4'),('5','d5')])
   submit=SubmitField("Submit")

class LoginForm(FlaskForm):
   email = EmailField('Email', [validators.DataRequired(), validators.Email()])
   password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
   remember = BooleanField('Remember Me') 
   submit=SubmitField("Login")

class EmptyForm(FlaskForm):
   a=6

class AddProject(FlaskForm):
   Name=StringField("Name",validators=[InputRequired()])
   content= TextAreaField(u'Content', [validators.DataRequired()])
   deadline=DateField("Deadline")
   users=SelectMultipleField(u'Users', coerce=int)
   submit=SubmitField("Create Project")




