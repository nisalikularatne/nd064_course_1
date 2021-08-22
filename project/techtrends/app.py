import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys
# Function to get a database connection.
# This function connects to database with the name `database.db`
conn_counter = 0
def get_db_connection():
    global conn_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_counter+=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('article non existent')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article ' + post[2] + ' retrieved')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us Page is retrieved')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New Article '+title+ ' created')
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    connection.close()

    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, "data": {"db_connection_count": conn_counter, "post_count": len(posts)}}),
        status=200,
        mimetype='application/json'
    )

    return response


# start the application on port 3111 check
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )
    app.logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    app.logger.addHandler(stdout_handler)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    app.logger.addHandler(stderr_handler)
