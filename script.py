from flask import Flask, render_template, redirect,url_for, flash, request, Response, send_file, current_app
from flask_wtf import FlaskForm
from sqlite3 import IntegrityError, OperationalError
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, JSON, text, desc, String, ForeignKey
import os
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms_alchemy import PhoneNumberField
import phonenumbers
from mysql.connector import connect,Error
from flask_wtf.file import FileAllowed
from sqlalchemy.orm import relationship


# Create a Flask Instance
app = Flask(__name__)

# Configure your MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:UPITTdb73@localhost/archeological_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# csrf tokens - secret key
app.config['SECRET_KEY'] = "Secret"

#Initialize the db
db = SQLAlchemy(app)

app.app_context().push()

# Flask_Login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logintail'

# Create a model
class UserProfiles(db.Model, UserMixin):
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    organisation = db.Column(db.String(100), nullable=False)
    affiliation = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), primary_key=True, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='registeredUser')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def userPassword(self):
        raise AttributeError('password is not a readable attribute')
    
    @userPassword.setter
    def userPassword(self, userPassword):
        self.password = generate_password_hash(userPassword)

    def verify_password(self, userPassword):
        return check_password_hash(self.password, userPassword)
    
    # Create A String
    def _repr_(self):
        return '<Name %r>' % self.firstName
    
    def get_id(self):
        return self.email
    
class UserProfileDetails(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), db.ForeignKey('user_profiles.email'), nullable=False, unique=True)
    description = db.Column(db.String(500), default='No Description')
    phone_number = db.Column(db.String(20), default='123-456-7890')
    UserProfiles = db.relationship("UserProfiles", backref=db.backref('user_profile_details', lazy=True))
    
# Create a register form class
class RegisterForm(FlaskForm):
    firstName = StringField("Enter Your First Name", validators=[InputRequired('First Name is Required')])
    lastName = StringField("Enter Your Last Name", validators=[InputRequired('Last Name is Required')])
    org = StringField("Enter Your Organisation", validators=[InputRequired('Organisation is Required')])
    affiliation = SelectField('Select Affiliation', 
                    choices=[
                             ('Select Affiliation', 'Select Affiliation'),
                             ('K-12 Student', 'K-12 Student'), 
                             ('Undergraduate Student', 'Undergraduate Student'), 
                             ('Graduate student', 'Graduate student'),
                             ('K-12 Teacher', 'K-12 Teacher'),
                             ('Higher Ed. Faculty', 'Higher Ed. Faculty'),
                             ('Independent Researcher', 'Independent Researcher'),
                             ('Public Agency Archeologist', 'Public Agency Archeologist'),
                             ('CRM Form Archeologist', 'CRM Form Archeologist'),
                             ('NonProfessional/Avocational Archeologist', 'NonProfessional/Avocational Archeologist'),
                             ('General Public', 'General Public'),
                             ('Native American/Indigenous researcher', 'Native American/Indigenous researcher')
                            ], validators=[DataRequired('Affiliation is Required')])
    email = EmailField("Enter Your Email", validators=[InputRequired('Email is Required'), Email('This field requires a valid email address')])
    password = PasswordField("Enter Your Password", validators=[InputRequired('Password is Required'), EqualTo('conPassword', message='Passwords must match'), Length(min=8, message='Must be atleast 8 characters')])
    conPassword = PasswordField("Confirm Password", validators=[InputRequired('Confirm your password')])
    register = SubmitField("Register")

# Form validation using WTForms
class ContributorForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    contributional_dataset_name = StringField('Dataset Name to which you are contributing to', validators=[DataRequired(), Length(min=2, max=500)])
    file = FileField('File (CSV or Excel)', validators=[DataRequired(), FileAllowed(['csv', 'xlsx'], 'Only CSV or Excel files allowed')])
    submit = SubmitField("Submit Request")

# Create a profile form class
class ProfileForm(FlaskForm):
    firstName = StringField("First Name", validators=[InputRequired('First Name is Required')])
    lastName = StringField("Last Name", validators=[InputRequired('Last Name is Required')])
    org = StringField("Organisation", validators=[InputRequired('Organisation is Required')])
    affiliation = SelectField('Select Affiliation', 
                    choices=[
                             ('Select Affiliation', 'Select Affiliation'),
                             ('K-12 Student', 'K-12 Student'), 
                             ('Undergraduate Student', 'Undergraduate Student'), 
                             ('Graduate student', 'Graduate student'),
                             ('K-12 Teacher', 'K-12 Teacher'),
                             ('Higher Ed. Faculty', 'Higher Ed. Faculty'),
                             ('Independent Researcher', 'Independent Researcher'),
                             ('Public Agency Archeologist', 'Public Agency Archeologist'),
                             ('CRM Form Archeologist', 'CRM Form Archeologist'),
                             ('NonProfessional/Avocational Archeologist', 'NonProfessional/Avocational Archeologist'),
                             ('General Public', 'General Public'),
                             ('Native American/Indigenous researcher', 'Native American/Indigenous researcher')
                            ], validators=[DataRequired('Affiliation is Required')])
    email = EmailField("Email", validators=[InputRequired('Email is Required'), Email('This field requires a valid email address')], render_kw={'readonly': True})
    password = PasswordField("New Password", validators=[EqualTo('conPassword', message='Passwords must match'), Length(min=8, message='Must be atleast 8 characters')])
    conPassword = PasswordField("Confirm Password")
    description = TextAreaField("Please briefly describe the geographical areas, time periods, or other subjects for which you would like to contribute information", validators=[Length(max=300)])
    phone_number = PhoneNumberField('Phone Number')
    register = SubmitField("Save")

# Create profile page functionality
@app.route('/profile/<string:email>', methods=['GET', 'POST'])
@login_required
def profile(email):
    form = ProfileForm()
    user_to_update = UserProfiles.query.get_or_404(email)
    userdetails_to_update = UserProfileDetails.query.filter_by(email=email).first()
    if request.method == "POST":
        user_to_update.firstName = request.form['firstName']
        user_to_update.lastName = request.form['lastName']
        user_to_update.organisation = request.form['org']
        user_to_update.affiliation = request.form['affiliation']
        user_to_update.email = request.form['email']

        # if password is updated, then hash it before updating in the database
        password = request.form['password']
        if password:
            hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user_to_update.password = hashed_pw
        
        # if there is no entry in the details table, then create a new row with details.
        if userdetails_to_update is None:
            userdetails_to_update = UserProfileDetails(email=user_to_update.email,description =  request.form['description'], phone_number=request.form['phone_number'])
        else:
            userdetails_to_update.description = request.form['description']
            userdetails_to_update.phone_number = request.form['phone_number']
        try:
            db.session.add(user_to_update)
            db.session.add(userdetails_to_update)
            db.session.commit()
            flash("User Udpated Successfully!")
            return render_template("profile.html", form=form, user_to_update =user_to_update, userdetails_to_update = userdetails_to_update)
        except:
            flash("User Udpated error!")
            return render_template("profile.html", form=form, user_to_update =user_to_update, userdetails_to_update = userdetails_to_update)
    else:
        return render_template("profile.html", form=form, user_to_update = user_to_update, userdetails_to_update = userdetails_to_update)

@login_manager.user_loader
def load_user(email):
    return UserProfiles.query.filter_by(email=email).first()

#Approval for New Project - Database
class NewPro_Request(db.Model, UserMixin):
    __tablename__= 'db_req'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(100), primary_key = True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='registeredUser')
    status = db.Column(db.String(100), nullable=False, default='Pending')
    request_sent_on = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)


# Database and table details added by User After Approval 
class db_created_by_user(db.Model, UserMixin):
    __tablename__= 'db_created_by_user'
    id = db.Column(db.Integer(),primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    title_name = db.Column(db.String(500), nullable=False)
    table_name = db.Column(db.String(500),primary_key=True, nullable=False)
    column_names = db.Column(db.String(500), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='registeredUser')
    request_sent_on = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    

# Create a DB form class for the user to enter the DB details asking for Approval
class DB_Form(FlaskForm):
    title = StringField("Enter the title of your Database", validators=[InputRequired('Database Title is Required')])
    submit = SubmitField("Submit Request")

# Create a Data base - After Approval user specifies the DB, Tables and the columns.
class create_db(FlaskForm):
    # title = StringField("Enter the title of your Database", validators=[InputRequired('Database Title is Required')])

    table_name = StringField("Enter the Table Name for the Database", validators=[InputRequired('Table Name is Required')])
    columns = StringField("Enter the Column Names", validators=[InputRequired('Names of Columns is Required')])
    submit = SubmitField("Submit Request")

# Create a new project request model
class NewPro_Request(db.Model, UserMixin):
    __tablename__= 'CreateNewProjectReq'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    email = db.Column(db.String(100), primary_key = True, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='registeredUser')
    status = db.Column(db.String(100), nullable=False, default='Pending')
    request_sent_on = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

# Create a new project review form class
class ReviewForm(FlaskForm):
    decision = SelectField('Approve Request', 
                    choices=[
                             ('pending', 'Pending'), 
                             ('approve', 'Approve'), 
                             ('reject', 'Reject'),
                            ])
    submit = SubmitField("Submit Request")

class ReviewConForm(FlaskForm):
    decision = SelectField('Approve Request', 
                    choices=[
                             ('pending', 'Pending'), 
                             ('approve', 'Approve'), 
                             ('reject', 'Reject'),
                            ])
    submit = SubmitField("Submit Request")

# create a login form class
class LoginForm(FlaskForm):
    email = EmailField("Enter Your Email", validators=[InputRequired('Email is Required'), Email('This field requires a valid email address')])
    password = PasswordField("Enter Your Password", validators=[InputRequired('Password is Required'), Length(min=8, message='Must be atleast 8 characters')])
    login = SubmitField("Login")

# Create a route decorator
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logintail', methods=['GET', 'POST'])
def logintail():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = LoginForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''

        # Lookup User by Email Address
        pw_to_check = UserProfiles.query.filter_by(email=email).first()
        if pw_to_check:
            # check if hashed password in db is matching the entered password
            if check_password_hash(pw_to_check.password, password):
                login_user(pw_to_check)
                return redirect(url_for('dashboard', firstName = pw_to_check.firstName, email = email, pw_to_check = pw_to_check))
            else: 
                flash("The password you entered is incorrect. Please try again.")
        else:
            flash("The email address you entered is not registered. Please sign up to create an account.")
    return render_template('login.html', email = email, passed = passed, form = form)


# Create a route for dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    firstName = current_user.firstName
    email = current_user.email
    newProjectReq = NewPro_Request.query.filter(NewPro_Request.email == email).order_by(desc(NewPro_Request.request_sent_on)).all()
    
    # get all submitted requests to contribute to existing databases.
    contributeReqs = Contributor.query.filter(Contributor.email == email).all()
    contributorDetails = []
    if contributeReqs is not None:
        for row in contributeReqs:
            # query all requests matching this ID
            reqsFromDB = Request.query.filter(Request.contributor_id == row.id).first()
            extracted_data = {
            'contributorId': row.id,
            'requestID': reqsFromDB.id,
            'email': row.email,
            'filePath': reqsFromDB.file_path,
            'status': reqsFromDB.status,
            'datasetName': row.contributional_dataset_name
            }
            contributorDetails.append(extracted_data)
                
    if current_user.role == 'moderator':
        # Create new project requests:
        getReqToCreateProject = NewPro_Request.query.filter(NewPro_Request.status == 'pending').order_by(desc(NewPro_Request.request_sent_on)).all()
        requestDetails = []
        for row in getReqToCreateProject:
            owner_email = row.email
            ownerDetails= UserProfiles.query.filter_by(email=owner_email).first()
            # ownerSecondaryDetails = UserProfileDetails.query.filter_by(email=email).first()
            extracted_data = {
                'firstName': ownerDetails.firstName,
                'lastName': ownerDetails.lastName,
                'organisation': ownerDetails.organisation,
                'affiliation': ownerDetails.affiliation,
                'id': row.id,
                'email': row.email,
                'title': row.title,
                'role': row.role,
                'status': row.status,
                'request_sent_on': row.request_sent_on
            # Add more columns as needed
            }
            requestDetails.append(extracted_data)

        # Write moderate view of contribute requests
        getAllReqsToContribute = Contributor.query.all()
        getAllDataOfContributor = []
        if getAllReqsToContribute:
            for row in getAllReqsToContribute:
                conReqs = Request.query.filter(Request.contributor_id == row.id).first()
                extracted_data = {
                    'contributorId': row.id,
                    'requestID': conReqs.id,
                    'email': row.email,
                    'filePath': conReqs.file_path,
                    'status': conReqs.status,
                    'datasetName': row.contributional_dataset_name
                }
                getAllDataOfContributor.append(extracted_data)
        return render_template('dashboard.html', firstName = firstName, email = email, newProjectReq=newProjectReq, getReqToCreateProject = requestDetails, getAllDataOfContributor = getAllDataOfContributor)
    return render_template('dashboard.html', firstName = firstName, email = email, newProjectReq=newProjectReq, contributeReqs=contributeReqs, contributorDetails = contributorDetails)

# Create route for moderator to review and approve new project requests
@app.route('/review/<string:email>-<int:id>', methods=['GET', 'POST'])
@login_required
def review(email,id):
    getRequesterDetails = UserProfiles.query.filter_by(email=email).first()
    getSecondaryDetails = UserProfileDetails.query.filter_by(email=email).first()
    projectDetails = NewPro_Request.query.filter_by(id=id).first()
    form = ReviewForm()
    if  request.method == "POST":
        projectDetails.status = request.form['decision']
        if projectDetails.status == 'Approve' or projectDetails.status == 'approve':
            projectDetails.role = 'owner'
        db.session.add(projectDetails)
        db.session.commit()
        flash(f"New Project Request about {getRequesterDetails.lastName}'s {projectDetails.title} Reviwed")
        pw_to_check = UserProfiles.query.filter_by(email=current_user.email).first()
        return redirect(url_for('dashboard', email = current_user.email, pw_to_check=pw_to_check))
    return render_template("review.html", form = form, email=email, id=id, getRequesterDetails = getRequesterDetails, getSecondaryDetails = getSecondaryDetails, projectDetails = projectDetails)

# Create route for moderator to review and approve contributions to existing projects.
@app.route('/reviewContribute/<string:email>-<int:id>', methods=['GET', 'POST'])
@login_required
def reviewContribute(email,id):
    getRequesterDetails = UserProfiles.query.filter_by(email=email).first()
    getSecondaryDetails = UserProfileDetails.query.filter_by(email=email).first()
    contributorDetails = Contributor.query.filter_by(id=id).first()
    requestTable = Request.query.filter_by(contributor_id = contributorDetails.id).first()
    form = ReviewForm()
    if  request.method == "POST":
        requestTable.status = request.form['decision']
        db.session.add(requestTable)
        db.session.commit()
        if requestTable.status == 'approve':
            try:
                # Update the request status to 'approved'
                request_to_approve = Request.query.get(requestTable.id)
                request_to_approve.status = 'approved'
                #db.session.commit()
                # Notify contributor
                contributor_email = request_to_approve.contributor.email
                notify_user(contributor_email, f'Your request for file {request_to_approve.file_path} has been approved.', 'success')
                # Get the dataset name from the approved request
                contributional_dataset_name = request_to_approve.contributor.contributional_dataset_name
                # Connect to the MySQL database
                engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
                connection = engine.connect()
                # Read the existing dataset into a pandas DataFrame
                existing_dataset = pd.read_sql_table(contributional_dataset_name, con=connection)
                # Read the newly uploaded file into a pandas DataFrame
                new_file_path = request_to_approve.file_path
                new_data = pd.read_excel(new_file_path)
                # Append the new data to the existing dataset
                merged_dataset = pd.concat([existing_dataset, new_data], ignore_index=True)
                # Store the merged dataset in a new table
                new_table_name = f"{contributional_dataset_name}"
                merged_dataset.to_sql(new_table_name, con=connection, index=False, if_exists='replace')
                # Optional: Drop the temporary table created during the previous attempts
                temp_table_name = f"temp_{contributional_dataset_name}_{requestTable.id}"
                connection.execute(text(f"DROP TABLE IF EXISTS {temp_table_name}"))
                # Close the connection
                connection.close()
                flash('Request approved successfully! New file added to the existing table.', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
                app.logger.error(f'Error in approve_request: {str(e)}')
                return redirect(url_for('dashboard'))
        if requestTable.status == 'reject':
            # Update the request status to 'rejected'
            request_to_reject = Request.query.get(requestTable.id)
            request_to_reject.status = 'rejected'
            #db.session.commit()
            # Notify contributor
            contributor_email = request_to_reject.contributor.email
            notify_user(contributor_email, f'Your request for file {request_to_reject.file_path} has been rejected.', 'danger')
            flash('Request rejected successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash("Request Reviwed")
        pw_to_check = UserProfiles.query.filter_by(email=current_user.email).first()
        return redirect(url_for('dashboard', email = current_user.email, pw_to_check=pw_to_check))
    return render_template("reviewContribute.html", form = form, email=email, id=id, getRequesterDetails = getRequesterDetails, getSecondaryDetails = getSecondaryDetails, contributorDetails = contributorDetails, requestTable = requestTable)

# Create logout functionality
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    firstName = None
    lastName = None
    org = None
    Affiliation = None
    email = None
    password = None
    conPassword = None
    form = RegisterForm()
    if  form.validate_on_submit():
        firstName = form.firstName.data
        user = UserProfiles.query.filter_by(email=form.email.data).first()
        firstName = form.firstName.data
        email = form.email.data
        if user is None:
            # hash password
            hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user = UserProfiles(firstName=form.firstName.data,
                    lastName=form.lastName.data,
                    organisation=form.org.data,
                    affiliation=form.affiliation.data,
                    email=form.email.data,
                    password=hashed_pw
                )
            db.session.add(user)
            db.session.commit()
            flash("Congratulations on successfully registering with us. Happy exploring!")
            pw_to_check = UserProfiles.query.filter_by(email=email).first()
            return redirect(url_for('dashboard', firstName = firstName, email = email, pw_to_check=pw_to_check))
        else:
            flash("Sorry, The Email you entered is already registered, login now.") 
    firstName = ''
    form.firstName.data = ''
    form.lastName.data = ''
    form.org.data = ''
    form.affiliation.data = ''
    form.email.data = ''
    form.password.data = ''
    form.conPassword.data = ''
    registered_users_list = UserProfiles.query.order_by(UserProfiles.date_added)
    return render_template('register.html', firstName = firstName, form=form, registered_users_list = registered_users_list)

def get_table_names():
    with app.app_context():
        result = db.session.execute(text('SHOW TABLES'))
        return [row[0] for row in result]

# def get_table_data(table_name, limit=10):
#     with app.app_context():
#         query = text(f"SELECT * FROM `{table_name}` LIMIT {limit}")
#         result = db.session.execute(query)
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())
#         return df

def get_full_table_data(table_name):
    with app.app_context():
        query = text(f"SELECT * FROM `{table_name}`")
        result = db.session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

# THIS CODE IS FOR DISPLAYING ALL THE TABLES AND USING THE DISPLAYTABLES.HTML FILE.....DO NOT DELETE
#@app.route('/displayTables')
#def display_tables():
#    table_names = get_table_names()
#    tables = {name: get_table_data(name) for name in table_names}
#    #tables = {'database1': get_table_data('database1')}
#    return render_template('displayTables.html', tables=tables)

# DISPLAY DATABASE1
@app.route('/displayTableDatabase1')
def display_table_database1():
    tables = {'database1': get_full_table_data('database1')}
    return render_template('displayTableDatabase1.html', tables=tables)

# DISPLAY DATABASE2
@app.route('/displayTableDatabase2')
def display_table_database2():
    tables = {'database2': get_full_table_data('database2')}
    return render_template('displayTableDatabase2.html', tables=tables)

@app.route('/download/<string:table_name>/<string:format>', methods=['GET'])
def download_table(table_name, format):
    if format not in ['csv', 'excel', 'pdf']:
        return "Invalid format", 400

    # Fetch data from the database (you need to implement this)
    # For example, assuming you have a function get_full_table_data(table_name)
    table_data = get_full_table_data(table_name)

    if table_data is None:
        return "Table not found", 404

    # Convert the table data to the desired format
    if format == 'csv':
        output = BytesIO()
        table_data.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'{table_name}.csv')

    elif format == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            table_data.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'{table_name}.xlsx')

    #elif format == 'pdf':
        # You'll need to install weasyprint: pip install WeasyPrint
    #    from weasyprint import HTML
    #    output = BytesIO()
    #    HTML(string=table_data.to_html()).write_pdf(output)
    #    output.seek(0)
    #    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name=f'{table_name}.pdf')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/requestform')
def requestform():
    return render_template('requestform.html')

@app.route('/createRequest', methods=['GET', 'POST'])
def createRequest():
    form = DB_Form()
    if  form.validate_on_submit():
        title = NewPro_Request.query.filter_by(title=form.title.data).first()
        if title is None:
            title = NewPro_Request(email=current_user.email,
                                   title=form.title.data
                    )
            db.session.add(title)
            db.session.commit()
            flash("Added to Database")
            return redirect(url_for('dashboard'))

        else:
            flash("Sorry, The Title you entered is already taken, try new title") 
    form.title.data = ''
    
    return render_template('createRequest.html',form = form)

@app.route('/create_database/<string:title>', methods=['GET', 'POST'])
def create_database(title):
    
    form = create_db()

    if form.validate_on_submit():

        table_name = db_created_by_user.query.filter_by(table_name=form.table_name.data).first()
        title_name = db_created_by_user.query.filter_by(title_name=title).first()
        if (table_name and title_name) is None:
            title_name = db_created_by_user(email=current_user.email,
                                        title_name=title,
                                   table_name=form.table_name.data,
                              column_names = form.columns.data
                        )
    
            db.session.add(title_name)
            db.session.commit()
            flash("Added to Database")
            #return redirect(url_for('dashboard'))
        else:
             flash("Sorry, The Table you entered is already present, try creating a new table") 
             #return redirect(url_for('dashboard'))
    
        table = form.table_name.data
        column_names = form.columns.data.split(',')
        
        try:
            with connect(
                host="localhost",
                user="root",
                password="Qwerty123",
            ) as connection:
                # Create a new database after Approval
                with connection.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE {title}")
                    flash(f"Database '{title}' created successfully!")  
        except Error as e:
            flash(f"Error creating database: {e} ! Try Again", "error")
            return redirect(url_for('dashboard'))
           
        try:
            with connect(
                host="localhost",
                user="root",
                password="Qwerty123",
                database=title,  # Specify the newly created database
            ) as connection:
                # Create the table
                columns_sql = ', '.join([f"{col} VARCHAR(255)" for col in column_names])
                create_table_query = f"CREATE TABLE {table} ({columns_sql})"
                with connection.cursor() as cursor:
                    cursor.execute(create_table_query)
                
                flash(f"Table '{table}' created successfully!") 
                return redirect(url_for('dashboard')) 
        except Error as e:
             flash(f"Error creating table: {e} ! Try Again", "error")
             return redirect(url_for('dashboard'))
  
    table_name=''
    title_name=''
        
    return render_template('create_database.html',form=form,title=title)

@app.route('/database_created', methods=['GET', 'POST'])
def databases_created():
    
    email = current_user.email
    dbCreatedByUser = db_created_by_user.query.filter(db_created_by_user.email == email).all()
    # newlyCreatedDatabases = create_db.query.filter(create)
    return render_template('database_created.html', email = email, dbCreatedByUser=dbCreatedByUser)

# Routes Aishwarya

class Contributor(db.Model):
    tablename = 'contributor'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False)
    contributional_dataset_name = Column(String(500), nullable=False)
    requests = relationship('Request', backref='contributor', lazy=True)

class Request(db.Model):
    _tablename_ = 'request'
    id = Column(Integer, primary_key=True)
    contributor_id = Column(Integer, ForeignKey('contributor.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    status = Column(String(20), default='pending', nullable=False)
                            
# Notify function (simulate notifications, replace with actual notification logic)
def notify_user(email, message, category='info'):
    flash(message, category)
    # Add your code to send a real notification (e.g., email, push notification, etc.) here

@app.route('/contributionRequestForm', methods=['GET', 'POST'])
def contributionRequestForm():
    form = ContributorForm()
    if form.validate_on_submit():
        # Handle form submission
        # current_user.email
        email = current_user.email
        contributional_dataset_name = form.contributional_dataset_name.data
        file = request.files['file']

        # Save file to a specific folder (you may need to create this folder)
        file_path = f"requestedUploads/{file.filename}"
        file.save(file_path)

        # Insert contributor data into the database
        new_contributor = Contributor(
            email=email,
            contributional_dataset_name=contributional_dataset_name
        )
        db.session.add(new_contributor)
        db.session.commit()

        # Insert request data into the database
        new_request = Request(contributor=new_contributor, file_path=file_path)
        db.session.add(new_request)
        db.session.commit()

        # Notify contributor
        notify_user(email, f'Thank you, for your submission! Your request is under review.', 'success')

        flash('Request submitted successfully!', 'success')

        # Clear the form fields
        form.process()  # Reset the form to handle new input
        pw_to_check = UserProfiles.query.filter_by(email=email).first()
        return redirect(url_for('dashboard', email = current_user.email, pw_to_check = pw_to_check))

    return render_template('contributionRequestForm.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)