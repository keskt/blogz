from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123!@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ixhjkkfdxfghj'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_posts', 'get_post', 'index' ]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

def not_empty(textString):
    if textString and textString.strip():
        return True
    else:
        return False

@app.route('/newpost', methods=['GET','POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error = ''
        body_error = ''
        if not not_empty(title):
            title_error = 'Not a valid title'
            title = ''
        
        if not not_empty(body):
            body_error = 'Not a valid post'
            body = ''

        if not title_error and not body_error:
            owner = User.query.filter_by(username=session['username']).first()
            post = Blog(title, body, owner)
            db.session.add(post)
            db.session.commit()
            return redirect('/idpost?id={0}'.format(post.id))
        else: 
            return render_template('newpost.html', title=title, title_error=title_error, body=body, body_error=body_error)
    return render_template('newpost.html')

@app.route('/blog')
def blog_posts():
    if request.args:
        username = request.args.get('user')
        owner = User.query.filter_by(username=username).first()
        posts = Blog.query.filter_by(owner=owner).all()
        return render_template('blog.html', posts=posts)
    else:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts)

@app.route('/idpost')
def get_post():
    id = request.args.get('id')
    post = Blog.query.get(id)
    return render_template('idpost.html', post=post)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('This username does not exist', 'error')
            return redirect('/login')
        if user.password != password:
            flash('Password is incorrect', 'error')
            return redirect('/login')
        elif user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
    return render_template('login.html')


def not_empty(textString):
    if textString and textString.strip():
        return True
    else:
        return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('That username already exists', 'error')
            return redirect('/signup')
        if not not_empty(username) or not not_empty(password) or not not_empty(verify):
            flash('One or more fields is invalid', 'error')
            return redirect('/signup')
        if password != verify:
            flash('The passwords do not match', 'error')
            return redirect('/signup')
        if len(username) < 3:
            flash('Not a valid username', 'error')
            return redirect('/signup')
        if len(password) < 3:
            flash('Not a valid password', 'error')
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)
if __name__ == '__main__':
    app.run()
