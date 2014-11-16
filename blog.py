import os

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader('template_dir'),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_to_string(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(**kwargs)

    def render(self, template, **kwargs):
        return self.write(self.render_to_string(template, **kwargs))

class BlogHandler(Handler):
    def get(self):
        self.response.out.write("Hello, world!")

app = webapp2.WSGIApplication([('/blog', BlogHandler)], debug=True)