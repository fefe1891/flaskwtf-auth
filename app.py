from flask import Flask, render_template, redirect, session, abort, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import LoginForm, UserRegistrationForm, FeedbackForm
from models import db, User, Feedback, bcrypt
from werkzeug.exceptions import Unauthorized
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

bcrypt.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///user_feedback_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    

@app.route('/')
def home():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session: # Check if user is already logged in
        return redirect(f"/users/{session['username']}")
    
    form = UserRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        
        # check if the username already taken
        if User.query.get(username):
            form.username.errors = ['Username taken. Please choose another one.']
            return render_template('register.html', form=form)
        
        user = User.register(username, password, first_name, last_name, email)
        db.session.add(user)
        db.session.commit()
        
        session['username'] = username # Log in the user
        return redirect(f"/users/{username}")
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session: # Check if user is already logged in
        return redirect(f"/users/{session['username']}") # Redirect to users page
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        
        if user:
            # Successful login
            session['username'] = username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid username/password.']
            
    return render_template('login.html', form=form)
        
        
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' not in session or not User.query.get(session['username']).is_admin:
        abort(403) # Forbidden access
        
        # Display all users
        users = User.query.all()
        return render_template('admin_dashboard.html', users=users)

@app.route('/secret')
def secret():
    if 'username' not in session:
        raise Unauthorized("You must be logged in to view this page.")
    return 'You made it!'


@app.errorhandler(404)
def page_not_found(err):
    return render_template('error.html', error_title="Page Not Found", error_message="Sorry, this is not the page you're looking for."), 404


@app.errorhandler(Unauthorized)
def unauthorized_error(err):
    return render_template('unauthorized_error.html', error_title="Unauthorized", error_message="You must be logged in to view this page."), 401

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>')
def user_detail(username):
    if 'username' not in session or session['username'] != username:
        return redirect('/login')
    
    user = User.query.get(username) # get the user details
    if user:
        return render_template('/user_detail.html', user=user)
    else:
        return abort(404) # if user not found, return 404 error
    
    
@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session or session['username'] != username:
        return redirect('/login')
    user = User.query.get(username)
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
    return redirect('/')
    

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or session['username'] != username:
        return redirect('/login')
    
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        
        db.session.add(feedback)
        db.session.commit()
        
        return redirect(f'/users/{username}')
    
    return render_template('feedback_add.html', form=form)
    
    
@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback or 'username' not in session or session['username'] !=feedback.username:
        return redirect('/login')
    
    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.commit()
        
        return redirect(f'/users/{feedback.username}')
    
    return render_template('feedback_edit.html', form=form, feedback=feedback)
    
    
@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback or 'username' not in session or session['username'] != feedback.username:
        return redirect('/login')
    
    db.session.delete(feedback)
    db.session.commit()
    
    return redirect(f'/users/{feedback.username}')