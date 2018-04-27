from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'itsasecret'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    bodytext = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title, bodytext,owner):
        self.title = title
        self.bodytext = bodytext
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True) 
    password = db.Column(db.String(120))   
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if (not username) or (username.strip() == ""):
                flash("Please specify username.")
                error_exists=True
        else:

            user = User.query.filter_by(username=username).first()
            if user:
                if user.password != password:
                    flash('User password incorrect!')
                    return render_template('login.html')
                else:
                    session['username'] = username
                    flash("Logged in")
                    return redirect('/newpost')
     
             
            else:
                flash('user does not exists!')
                return render_template('login.html')
        
    return render_template('login.html')

@app.route('/signup',methods=['POST', 'GET'])

def signup():

    if request.method == 'POST':
        error_exists = False
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']
    
       
                        
    #Validation 2:
        if (not username) or (username.strip() == ""):
            flash("Please specify username.")
            error_exists=True
        else:
            if len(username) <3 :
                flash("Invalid Username.")
                error_exists=True

        if (not password) or (password.strip() == ""):
            flash("Please specify the password.")
            error_exists=True
        else:
            if len(password) <3:
                flash("Invalid Password.")
                error_exists=True
        
            if (not verifypassword) or (verifypassword.strip() == ""):
                flash("Please verify password.")
                error_exists=True
            if verifypassword != password:
                flash("Passwords do not match.")
                error_exists=True

    #Validation 3:
        user = User.query.filter_by(username=username).first()
        if user:
            flash('username already exists!')
            error_exists=True
            
    
        if not error_exists :

            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            

            return redirect('/newpost')
        else:
            return render_template('signup.html',username=username)

    return render_template('signup.html')

 
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
 

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        error_exists = False
        title_error = ""
        bodytext_error = ""
        title=request.form['title']
        bodytext=request.form['bodytext']
        #blog =Blog(title, bodytext, owner)
    
        if (not title) or (title.strip() == ""):
           title_error = "Please provide a title for the blog"
           error_exists=True
           

        if (not bodytext) or (bodytext.strip() == ""):
            bodytext_error = "Please provide blog text for the blog"
            error_exists = True
        
        if not error_exists :

            blog = Blog(title, bodytext,owner)
            db.session.add(blog)
            db.session.commit()

            return redirect('/blog?id={0}'.format(blog.id))
        else:
            return render_template('newblog.html',title="Post New Blog",title_error=title_error,bodytext_error=bodytext_error,titlevalue=title,textarea=bodytext)  
    
    else:
        return render_template('newblog.html', title="Post New Blog")

@app.route('/index',methods=['GET'])
def index():
    #user_id = request.args.get('id')
    #if not user_id:
        user_list = db.session.query(User.username).all()  
        return render_template('index.html',title="Blog Users",user_list=user_list)

        
@app.route('/blog', methods=['GET'])
def list_blogs():
    
    blogid = request.args.get('id')
    username = request.args.get('user')

    if not blogid and not username:
        posted_blogs = db.session.query(User.username,Blog.title,Blog.bodytext,Blog.id).join(Blog).all()
        return render_template('blog.html', title="All blogs", 
            posted_blogs = posted_blogs)
    
    else:
        if not username:
            id = int(blogid) 
            posted_blog = Blog.query.get(id)
            user= User.query.get(posted_blog.owner_id)
            return render_template('detailblog.html',title="Blog Detail",blog=posted_blog, user=user)
        else:
            posted_blogs = db.session.query(User.username,Blog.title,Blog.bodytext,Blog.id).join(Blog).filter(User.username == username).all()
            return render_template('blog.html',title="User Blogs", posted_blogs=posted_blogs)


if __name__ == '__main__':
    app.run()
    