from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webform import LoginForm, PostForm, UserForm, NameForm, PasswordForm


app = Flask(__name__)

# Old SQLIte DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///our_users.db'

# New MySql DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sunny@localhost/our_users'

app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


db = SQLAlchemy(app)
migrate = Migrate(app, db)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



class Posts(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String(255))
     content = db.Column(db.Text)
    # author = db.Column(db.String(225))
     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
     slug = db.Column(db.String(225))
     # Foreign Key link (refer to primary key)
     poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
     
     
     

# Json Thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": "Pepperoni",
        "Mary": "Cheese",
        "Time": "Mushroom"
        
        }
    return favorite_pizza 
    #return {"Date": date.today()}



class Users(db.Model, UserMixin):
    
   
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email= db.Column(db.String(120), nullable=False,unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='poster')
    
   
    
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter    
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def __repr__(self):
        return '<Name %r>' % self.name

    


    
@app.route('/user/add', methods=['GET','POST'])    
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data,"sha256")
            user = Users(username=form.username.data,name=form.name.data, email=form.email.data,favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data  
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)    
    

@app.route('/')
def index():
    first_name = "Sarabpreet Bedi"
    
    
    favorite_pizza = ["Pepperoni","Cheese","Mushroom"]
    return render_template("index.html", first_name=first_name,
                      favorite_pizza=favorite_pizza )


@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data 
        form.name.data = ''
        flash("Form Submitted Successfully!")
        
    return render_template("name.html",
                           name= name,
                           form= form)

@app.route('/update/<int:id>', methods=['GET','POST']) 
@login_required
def update(id): 
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)  
    if request.method == "POST":
        name_to_update.name = request.form['name'] 
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem.... try again!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update, id=id)
                                   
    
@app.route('/delete/<int:id>') 
def delete(id):
       user_to_delete = Users.query.get_or_404(id)
       name = None
       form = UserForm()
       
       try:
           db.session.delete(user_to_delete)
           db.session.commit()
           flash("User Deleted Successfully!!")
           
           
           our_users = Users.query.order_by(Users.date_added)
           return render_template("add_user.html", form=form, name=name, our_users=our_users)    
    
       except:    
              flash("Whoops! There was a problem deleting user, Try Again...!!")
              return render_template("add_user.html", form=form, name=name, our_users=our_users)  


          

@app.route('/test_pwd', methods=['GET', 'POST'])
def test_pwd():
    email = None
    password =None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()
        #flash("Form Submitted Successfully!")
        
        passed =  check_password_hash(pw_to_check.password_hash, password)
        
    return render_template("test_pwd.html",
                           email= email,
                           password = password,
                            pw_to_check= pw_to_check,
                            passed = passed,
                           form= form)   

      
@app.route('/posts')
def posts():
    # Grab all the posts fromm the database
    
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)
      
      
# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''
           
        
        # Add post data to database
        db.session.add(post)
        db.session.commit()
        
        flash("Blog Post Submitted Successfully!")
        
    return render_template("add_post.html", form=form)   

@app.route('/posts/<int:id>')  
def post(id):
    post = Posts.query.get_or_404(id) 
    return render_template('post.html', post=post)
        
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST']) 
@login_required 
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
         post.title = form.title.data
         #post.author = form.author.data
         post.slug = form.slug.data
         post.content = form.content.data
         # Update database
         db.session.add(post)
         db.session.commit()
         flash("Post Has Been Updated!")
         return redirect(url_for('post', id=post.id))
     
    if current_user.id == post.poster_id:
       form.title.data = post.title
      #form.author.data = post.author
       form.slug.data = post.slug
       form.content.data = post.content
       return render_template('edit_post.html', form=form) 
   
    else:
       flash("You Aren't Authorized To Edit This Post")
       posts = Posts.query.order_by(Posts.date_posted)
       return render_template("posts.html", posts=posts)
     
@app.route('/posts/delete/<int:id>') 
@login_required     
def delete_post(id):
    
   post_to_delete = Posts.query.get_or_404(id)
   id = current_user.id
   if id == post_to_delete.poster.id:
        
     try:
        db.session.delete(post_to_delete)
        db.session.commit()
        
        flash("Blog Post Was Deleted!")
        
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)
    
     except:
      flash("Whoops! There was a problem deleting post, try again....")
      
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template('posts.html', posts=posts)
  
   else:
      flash("You Aren't Authorized To Delete The Posts")
      
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template('posts.html', posts=posts)
       
       
      

    

    
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
               login_user(user) 
               flash("Login Successfull!!")
               return redirect(url_for('dashboard'))
            else:
               flash("Wrong Password - Try Again!")
               
        else:
           flash("Thats User Doesn't Exist! Try Again...") 
            
               
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard(): 
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)  
    if request.method == "POST":
        name_to_update.name = request.form['name'] 
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
        except:
             flash("Error! Looks like there was a problem.... try again!")
             return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
       return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id =id)
    
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Your Have Been Logged Out! Thanks For Stopping By ")
    return redirect(url_for('login'))
    

   
@app.route('/search')
def search(): 
    q = request.args.get('q')
    
    if q:
        posts = Posts.query.filter(Posts.title.contains(q) |
        Posts.content.contains(q))
    else:
        posts = Posts.query.all()
        
    return render_template("posts.html",
                                    posts=posts)
    
         