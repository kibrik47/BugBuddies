from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import bcrypt
import os
from bson import ObjectId
from werkzeug.utils import secure_filename

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

@app.route('/forum/<category>')
def forum(category):
    session['category'] = category
    return render_template('forum.html', category=category)

@app.route('/forum/<category>/unresolved')
def unresolved_posts(category):
    # Add logic to fetch unresolved posts for the given category
    # For now, let's return a simple message
    return f"Unresolved posts for {category}"

@app.route('/forum/<category>/post', methods=['GET', 'POST'])
def post_issue(category):
    if 'username' not in session:
        # If the user is not logged in, redirect them to the login page
        flash('You need to be logged in to post an issue.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        print(request.files)
        # Access form data
        issue_topic = request.form['issueTopic']  # Assuming the name attribute is 'postTitle'
        description = request.form['description']
        labels = request.form['labels']
        specs = request.form['specs']

        # Save uploaded screenshot
        if 'screenshot' in request.files:
            screenshot = request.files['screenshot']
            screenshot_filename = secure_filename(screenshot.filename)
            screenshot_path = os.path.join(app.root_path, 'templates', 'static', 'images', 'screenshots', screenshot_filename)
            screenshot.save(screenshot_path)

        # Insert the issue details into the database
        posts = mongo.db.posts
        post_data = {
            'category': category,
            'issue_topic': issue_topic,
            'description': description,
            'labels': labels,
            'specs': specs,
            'screenshot_filename': screenshot_filename if 'screenshot' in request.files else None,
            'username': session['username']
        }
        result = posts.insert_one(post_data)

        # Get the newly inserted post's ID
        new_post_id = result.inserted_id

        # Redirect to the view_post page with the correct category and post ID
        return redirect(url_for('view_post', category=category, post_id=new_post_id))

    return render_template('post.html', category=category)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            
            # Retrieve the category from the session, or use a default value
            category = session.get('category', 'Default Category')

            return redirect(url_for('forum', category=category))  # Redirect to the forum page with the correct category
        else:
            flash('Invalid username/password combination', 'error')

    return render_template('login.html')

@app.route('/forum/<category>/post/<post_id>')
def view_post(category, post_id):
    # Fetch post details using its ID
    posts = mongo.db.posts
    post_data = posts.find_one({'_id': ObjectId(post_id)})

    if post_data is None:
        flash('Post not found.', 'error')
        return redirect(url_for('forum', category=category))

    # Render a template to display post details
    return render_template('view_post.html', category=category, post=post_data)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            # Hash the password before storing it in the database
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
