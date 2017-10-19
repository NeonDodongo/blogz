from flask import Flask, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from hashutils import make_pw_hash, check_pw_hash, make_salt

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
    content = db.Column(db.String(175))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner, post_date=None):
        self.title = title
        self.content = content
        self.owner = owner
        if post_date is None:
            post_date = datetime.now()
        self.post_date = post_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    pw_hash = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return render_template('login.html')

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
            if check_pw_hash(password, user.pw_hash):
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
    return redirect('/blog')

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

    users = User.query.order_by(User.username)
    blogs = Blog.query.order_by(desc(Blog.post_date))
    last_active = {}
    for user in users:
        for blog in blogs:
            if user.id == blog.owner_id:
                last_active[user.id] = blog.post_date
                break
    return render_template('index.html', users=users, last_active=last_active)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    entry_id = request.args.get('id')
    if entry_id:
        single_post = Blog.query.get(entry_id)
        user = User.query.filter_by(id=single_post.owner_id).first()
        return render_template('single-post.html', entry=single_post, user=user)
    
    users = User.query.all()
    blog_posts = Blog.query.order_by(desc(Blog.post_date)).all()
    return render_template('blog.html', entries=blog_posts, users=users)

@app.route('/singleUser', methods=['POST', 'GET'])
def my_posts():
    user_id = request.args.get('id')
    if user_id:
        user_posts = Blog.query.filter_by(owner_id=user_id).order_by(desc(Blog.post_date))
        user = User.query.filter_by(id=user_id).first()
        return render_template('singleUser.html', user_posts=user_posts, user=user)

    username = session['username']
    user = User.query.filter_by(username=username).first()
    user_posts = Blog.query.filter_by(owner_id=user.id).order_by(desc(Blog.post_date)).all()
    return render_template('singleUser.html', user=user, user_posts=user_posts)

@app.route('/make-post', methods=['GET'])
def make_post():
    return render_template('make-post.html')

if __name__ == '__main__':
    app.run()


