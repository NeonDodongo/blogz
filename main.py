from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
# Connect to MySQL server
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:@5ukALS02c@localhost:8889/build-a-blog'
# Print SQL comms in terminal
app.config['SQLALCHEMY_ECHO'] = True

# Create python database object
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(150))

    def __init__(self, title, content):
        self.title = title
        self.content = content

@app.route('/blog-post', methods=['POST'])
def blog_post():
    title = request.form['title']
    content = request.form['content']

    new_post = Blog(title, content)

    db.session.add(new_post)
    db.session.commit()

    return render_template('post-confirm.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    entry_id = request.args.get('id')
    if entry_id:
        single_post = Blog.query.get(entry_id)
        return render_template('single-post.html', entry=single_post)

    blog_posts = Blog.query.all()
    return render_template('blog.html', entries=blog_posts)

@app.route('/make-post', methods=['GET'])
def make_post():
    return render_template('make-post.html')

if __name__ == '__main__':
    app.run()


