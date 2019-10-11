from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

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

            post = Blog(title=title, body=body)
            db.session.add(post)
            db.session.commit()
            return redirect('/idpost?id={0}'.format(post.id))
        else: 
            return render_template('newpost.html', title=title, title_error=title_error, body=body, body_error=body_error)
    return render_template('newpost.html')

@app.route('/blog')
def index():
    posts = Blog.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/idpost')
def get_post():
    id = request.args.get('id')
    post = Blog.query.get(id)
    return render_template('idpost.html', post=post)


if __name__ == '__main__':
    app.run()
