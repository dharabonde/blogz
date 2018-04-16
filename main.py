from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'itsasecret'
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        titleNew = request.form['titleNew']
        blogText = request.form['newEntry']
        titleerror = ''
        textError = ''

        if not titleNew:
            titleerror = "Oops.. where's your title??"
        if not blogText:
            textError = "No Text.. No New Blog!! "

        if not textError and not titleerror:
            new_entry = Blog(titleNew, blogText)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', titleerror=titleerror, textError=textError, 
                titleNew=titleNew, blogText=blogText)
    
    return render_template('newpost.html', title='New Entry')

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Build-a-blog')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

    
@app.route('/')
def index():
    return redirect('/blog')


if  __name__ == "__main__":
    app.run()