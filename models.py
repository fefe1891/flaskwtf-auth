from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    is_admin = db.Column(db.Boolean, default=False)
    
    username = db.Column(db.String(20), primary_key=True, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    feedback = db.relationship("Feedback", backref="user", cascade="all, delete")
    
    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """Register a user. Hashes their password and adds user to the system."""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        
        # Creating a new user instance
        user = cls(
            username=username,
            password=hashed_utf8,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(user)
        return user
        

    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct. Return user if valid; else return False."""
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
    
    
class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('users.username'),nullable=False)