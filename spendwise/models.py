from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from passlib.hash import bcrypt


# Initializing the database 
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # total_limit = db.Column(db.Float, default=0.0)  # Add this line
    budget = db.Column(db.Float, default=0.0)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.hash(password)
# Hash the password using Passlib's bcrypt
    @staticmethod
    def check_password(hashed_password, password):
        return bcrypt.verify(password,hashed_password)
    
    def __repr__(self):
         return f"User('{self.username}')"

class Expense(db.Model):
    __tablename__='expense'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date,default=datetime.utcnow, nullable=False)
    category = db.Column(db.String(100), nullable=True) 
    category_limit = db.Column(db.Float, nullable=True) 

    def __init__(self, user_id, description, amount, date,category=None):
        self.user_id = user_id
        self.description = description
        self.amount = amount
        self.date = date
        self.category= category 

    def __repr__(self):
         return f"Expense('{self.description}', {self.amount})"
