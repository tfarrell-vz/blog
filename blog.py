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

class CookieHandler(Handler):
    def get(self):
        visits = self.request.cookies.get('visits', 0)
        if visits.isdigit():
            visits = int(visits) + 1
        else:
            visits = 0
        self.response.headers.add_header('Set-Cookie', 'visits=%s' % visits)

        if visits > 10000:
            self.write("You are the best ever!")
        else: 
            self.write("You've been here %s times!" % visits)

app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/(\d+)', PostHandler),
                               ('/blog/cookie', CookieHandler)
                               ], debug=True)