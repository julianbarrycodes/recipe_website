# app/models.py
from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)  # Store the image filename

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    recipe = db.relationship('Recipe', backref='comments')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # 1-5 stars
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='ratings')
    recipe = db.relationship('Recipe', backref='ratings')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='one_rating_per_user_recipe'),)
