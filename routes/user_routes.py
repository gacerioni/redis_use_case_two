from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models.user import User

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/create_user', methods=['GET', 'POST'])
def create_user():
    user_service = current_app.config['user_service']

    if request.method == 'POST':
        user_id = request.form['user_id']
        username = request.form['username']
        email = request.form['email']
        country = request.form['country']

        # Create a User instance
        new_user = User(user_id, username, email, country)

        # Save user to Redis using the UserService
        user_service.save_user(new_user)

        flash('User created successfully!')
        return redirect(url_for('user_bp.list_users'))  # Redirect to the user listing page

    return render_template('create_user.html')
