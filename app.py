from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__, static_folder='templates/static', static_url_path='/static')
app.secret_key = "your_secret_key"

# Configure MongoDB connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'
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
    return f"Post an issue in {category}"

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username' : request.form['username']})

    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            session['category'] = 'Default Category'  # Set a default category
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            session['category'] = 'Default Category'  # Set a default category
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('category', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
