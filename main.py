from flask import redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from hashutils import make_pw_hash, check_pw_hash, make_salt

from models import User, Blog
from app import app, db

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
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                if password == confirm:
                    new_user = User(username, password)
                    db.session.add(new_user)
                    db.session.commit()
                    session['username'] = username
                    return redirect('/make-post')
                else:
                    flash('Passwords do not match', 'error')
                    return render_template('signup.html', username=username)
            else:
                flash('Username is taken :(', 'error')
                return render_template('signup.html')
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
                return redirect('/make-post')
            else:
                flash('Incorrect password', 'error')
                return render_template('login.html', username=username)
        else:
            flash('Login failed, user does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/make-post', methods=['POST', 'GET'])
def blog_post():
    if request.method == 'POST':
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

    return render_template('make-post.html', username=session['username'])
    

@app.route('/', methods=['POST', 'GET'])
def index():
    user_id = request.args.get('id')
    if user_id:
        user = User.query.filter_by(id=user_id).first()
        user_posts = Blog.query.filter_by(owner_id=user_id).order_by(desc(Blog.post_date))
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

@app.route('/blog/', methods=['POST', 'GET'])
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

if __name__ == '__main__':
    app.run()


