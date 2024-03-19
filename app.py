from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import bcrypt
import os
from bson import ObjectId
from werkzeug.utils import secure_filename
from werkzeug.urls import url_quote



app = Flask(__name__, static_folder='templates/static', static_url_path='/static')
app.secret_key = "admin"

# Configure MongoDB connection
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/bugbuddies-db'

mongo = PyMongo(app)

def create_app(mongo_uri='mongodb://mongodb:27017/bugbuddies-db'):
    # Update the existing app configuration
    app.config['MONGO_URI'] = mongo_uri
    

    # Register routes and configurations
    register_routes(app, mongo)

    return app, mongo

def register_routes(app, mongo):
    # Your route registrations here
    pass

def fetch_recent_posts(category, limit=5):
    posts = mongo.db.posts.find({'category': category})
    all_posts = list(posts)
    formatted_posts = []
    for post in all_posts:
        formatted_post = {
            'post_id': str(post['_id']),  # Convert ObjectId to string
            'issue_topic': post['issue_topic'],
            'short_description': post['description'][:100],  # Limit to the first 100 characters
            'category': post['category'],
             'comments': post.get('comments', []),  # Include comments in the formatted post
            # Add other fields you need
        }
        formatted_posts.append(formatted_post)

    return formatted_posts

def register_routes(app, mongo):
    # Routes
    @app.route('/')
    def index():
        app.logger.info(f"Category value: {session.get('category')}")
        if 'username' in session:
            return render_template('index.html', category=session.get('category', 'Default Category'))
    
        return render_template('index.html', category='Default Category')

    @app.route('/forum/<category>')
    def forum(category):
        session['category'] = category
        all_posts = fetch_recent_posts(category)
        return render_template('forum.html', category=category, all_posts=all_posts)

    @app.route('/forum/<category>/post', methods=['GET', 'POST'])
    def post_issue(category):
        if 'username' not in session:
            # If the user is not logged in, redirect them to the login page
            flash('You need to be logged in to post an issue.', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
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
                'username': session['username'],
                'comments': []
            }

            # Assuming you have form fields with names like 'commenter_name_1', 'comment_text_1', 'commenter_name_2', 'comment_text_2', etc.
            comment_index = 1
            while True:
                commenter_name = request.form.get(f'commenter_name_{comment_index}')
                comment_text = request.form.get(f'comment_text_{comment_index}')

                if commenter_name is None or comment_text is None:
                    break  # Break the loop if no more comments are found

                post_data['comments'].append({
                    'commenter_name': commenter_name,
                    'comment_text': comment_text
                })

                comment_index += 1

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

    @app.route('/forum/<category>/post/<post_id>', methods=['GET', 'POST'])
    def view_post(category, post_id):
        # Fetch post details using its ID
        posts = mongo.db.posts
        post_data = posts.find_one({'_id': ObjectId(post_id)})

        if post_data is None:
            flash('Post not found.', 'error')
            return redirect(url_for('forum', category=category))
        
        if request.method == 'POST':
            # Handle the form submission and update the comments in the database
            comment_text = request.form.get('comment_text')

            if session.get('username') and comment_text:
                # Add the new comment to the post data
                post_data.setdefault('comments', []).append({
                    'commenter_name': session['username'],
                    'comment_text': comment_text
                })

                # Update the post in the database
                posts.update_one({'_id': post_data['_id']}, {'$set': {'comments': post_data['comments']}})

                # Redirect back to the same post page
                return redirect(url_for('view_post', category=category, post_id=post_id))

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
    app, _ = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
