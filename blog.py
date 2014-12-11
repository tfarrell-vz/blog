import re
import os
import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_to_string(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(**kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_to_string(template, **kwargs))

class Post(db.Model):
    subject = db.StringProperty()
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class User(db.Model):
    user_id = db.StringProperty()
    password = db.StringProperty()
    email = db.EmailProperty()

class BlogHandler(Handler):
    def get(self, posts=[]):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC").fetch(25)
        self.render('index.html', posts=posts)


class NewPostHandler(Handler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            blog_post = Post(subject=subject, content=content)
            blog_post.put()

            post_id = blog_post.key().id()

            self.redirect('/blog/%s' % post_id)

class PostHandler(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        posts = []
        posts.append(post)
        
        self.render('index.html', posts=posts)

# Verification functions for the signup
# Return boolean values context to render error messages
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)

EMAIL_RE =re.compile(r"^[\S]+@[\S]+\.[\S]+")
def valid_email(email):
    return EMAIL_RE.match(email)

def passwords_match(password, verify):
    if password != verify:
        return False
    else:
        return True

class SignupHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = {}
        if not valid_username(username):
            errors['username_error'] = "Error: That's not a valid username."
        if not valid_password(password):
            errors['password_error'] = "That wasn't a valid password."
        if not passwords_match(password, verify):
            errors['passwords_mismatch_error'] = "Your passwords didn't match."
        if email:
            if not valid_email(email):
                errors['email_error'] = "That's not a valid email."

        self.render('signup.html', username=username, **errors)

        if not errors:
            if email:
                new_user = User(user_id=username, password=password, email=email)
            else:
                new_user = User(user_id=username, password=password)
            new_user.put()

            self.response.headers.add_header('Set-Cookie', 'user_id=%s' % str(username))
            return self.redirect('/blog/welcome')

class SuccessHandler(Handler):
    def get(self):
        username = self.request.cookies.get('user_id')
        self.render('welcome.html', username=username)

class UserListHandler(Handler):
    def get(self, posts=[]):
        users = db.GqlQuery("SELECT * FROM User").fetch(25)
        self.render('userlist.html', users=users)    


app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/(\d+)', PostHandler),
                               ('/blog/userlist', UserListHandler),
                               ('/blog/signup', SignupHandler),
                               ('/blog/welcome', SuccessHandler),
                               ], debug=True)