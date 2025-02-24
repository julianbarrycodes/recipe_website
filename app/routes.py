import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from . import db
from .models import Recipe, User, Comment, Rating
from .forms import LoginForm, RegisterForm, RegistrationForm, CommentForm
from functools import wraps
from flask import abort

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@main.route("/")
def index():
    if current_user.is_authenticated:
        recipes = Recipe.query.all()
        return render_template("index.html", recipes=recipes)
    return render_template("landing.html")

@main.route("/recipe/<int:recipe_id>", methods=['GET', 'POST'])
@login_required
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = CommentForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        # Handle rating
        rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        if rating:
            rating.value = int(form.rating.data)
        else:
            rating = Rating(value=int(form.rating.data), user_id=current_user.id, recipe_id=recipe_id)
            db.session.add(rating)
        
        # Handle comment
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            recipe_id=recipe_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment and rating have been posted!', 'success')
        return redirect(url_for('main.recipe', recipe_id=recipe_id))
    
    # Calculate average rating
    avg_rating = db.session.query(db.func.avg(Rating.value)).filter_by(recipe_id=recipe_id).scalar() or 0
    
    return render_template(
        "recipe.html",
        recipe=recipe,
        form=form,
        avg_rating=round(avg_rating, 1)
    )

@main.route("/admin_dashboard")
@login_required
@admin_required
def admin_dashboard():
    recipes = Recipe.query.all()
    return render_template("admin.html", recipes=recipes)

@main.route("/add_recipe", methods=["POST"])
@login_required
@admin_required
def add_recipe():
    try:
        name = request.form["name"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        
        # Check if an image file was uploaded
        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving image to: {image_path}")  # Debug print
            image_file.save(image_path)
        else:
            filename = None
            print("No image file uploaded")  # Debug print

        new_recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions, image_filename=filename)
        db.session.add(new_recipe)
        db.session.commit()
        print("Recipe added successfully")  # Debug print
        return redirect(url_for("main.admin_dashboard"))
    except Exception as e:
        print(f"Error adding recipe: {str(e)}")  # Debug print
        db.session.rollback()
        flash('Error adding recipe', 'danger')
        return redirect(url_for("main.admin_dashboard"))

@main.route("/delete_recipe/<int:recipe_id>")
@login_required
@admin_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
    return redirect(url_for("main.admin_dashboard"))

@main.route("/update_recipe/<int:recipe_id>", methods=["POST"])
@login_required
@admin_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        recipe.name = request.form["name"]
        recipe.ingredients = request.form["ingredients"]
        recipe.instructions = request.form["instructions"]
        # Handle new image file
        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            recipe.image_filename = filename  # Update image filename
        db.session.commit()
    return redirect(url_for("main.admin_dashboard"))

@main.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    results = Recipe.query.filter(Recipe.name.ilike(f"%{query}%")).all() if query else []
    return render_template("search_results.html", recipes=results, query=query)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Redirect to the page they were trying to access
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    return render_template('login.html', title='Sign In', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', title='Register', form=form)
            
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/debug")
def debug():
    users = User.query.all()
    recipes = Recipe.query.all()
    comments = Comment.query.all()
    ratings = Rating.query.all()
    
    return render_template("debug.html", 
        users=users, 
        recipes=recipes,
        comments=comments,
        ratings=ratings
    )

@main.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403
