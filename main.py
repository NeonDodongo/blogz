from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from sqlalchemy import desc

app = Flask(__name__)

app.config['DEBUG'] = True
# Connect to MySQL server
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
# Print SQL comms in terminal
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'asdfg67890tytyty'

# Create python database object
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(150))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner, post_date=None):
        self.title = title
        self.content = content
        self.owner = owner
        if post_date is None:
            post_date = datetime.utcnow()
        self.post_date = post_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(20))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if username != "" and password != "" and confirm != "":
            if password == confirm:
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    new_user = User(username, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['username'] = username
                    return render_template('/make-post.html', username=username)
                else:
                    flash('Username is taken :(', 'error')
                    return redirect('/make-post')
            else:
                flash('Passwords do not match', 'error')
                return render_template('signup.html', username=username)
        else:
            flash('Fields cannot be blank', 'error')
            return render_template('signup.html', username=username)

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user:
            if password == user.password:
                session['username'] = username
                return render_template('make-post.html')
            else:
                flash('Incorrect password', 'error')
                return render_template('login.html', username=username)
        else:
            flash('Login failed, invalid credentials', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    blog_posts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', entries=blog_posts, users=users)

@app.route('/make-post', methods=['POST'])
def blog_post():
    title = request.form['title']
    content = request.form['content']
    owner = User.query.filter_by(username=session['username']).first()

    if title != "" and content !="":
        new_post = Blog(title, content, owner)

        db.session.add(new_post)
        db.session.commit()

        return render_template('post-confirm.html')
    
    else:
        flash('Fields cannot be blank', 'error')
        return redirect('/make-post')

@app.route('/', methods=['POST', 'GET'])
def index():
    user_id = request.args.get('id')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        user_posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', user_posts=user_posts, user=user)
    
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    entry_id = request.args.get('id')
    if entry_id:
        single_post = Blog.query.get(entry_id)
        return render_template('single-post.html', entry=single_post)
    
    users = User.query.all()
    blog_posts = Blog.query.order_by(desc(Blog.post_date)).all()
    return render_template('blog.html', entries=blog_posts, users=users)

@app.route('/singleUser', methods=['POST', 'GET'])
def my_posts():
    user_id = request.args.get('id')
    if user_id:
        user_posts = Blog.query.filter_by(owner_id=user_id)
        user = User.query.filter_by(id=user_id).first()
        return render_template('singleUser.html', user_posts=user_posts, user=user)

    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    user_posts = Blog.query.filter_by(owner_id=user_id).order_by(desc(Blog.post_date)).all()
    return render_template('singleUser.html', user=user, user_posts=user_posts)

@app.route('/make-post', methods=['GET'])
def make_post():
    return render_template('make-post.html')

if __name__ == '__main__':
    app.run()


