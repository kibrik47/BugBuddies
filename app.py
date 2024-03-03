# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__, static_folder='templates/static', static_url_path='/static')
app.secret_key = "admin"

# Configure MongoDB connection
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/your_database'
mongo = PyMongo(app)

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', category=session.get('category', 'Default Category'))

    return render_template('index.html', category='Default Category')

# Add these lines for the forum routes
@app.route('/forum/<category>')
def forum(category):
    return render_template('forum.html', category=category)

@app.route('/forum/<category>/unresolved')
def unresolved_posts(category):
    # Add logic to fetch unresolved posts for the given category
    # For now, let's return a simple message
    return f"Unresolved posts for {category}"

@app.route('/forum/<category>/post')
def post_issue(category):
    # Add logic for posting an issue in the given category
    # For now, let's return a simple message
    return render_template('post.html', category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            session['category'] = 'Default Category'  # Set a default category
            return redirect(url_for('index'))
        else:
            flash('Invalid username/password combination', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            session['category'] = 'Default Category'  # Set a default category
            return redirect(url_for('index'))
        else:
            flash('That username already exists!', 'error')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('category', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
