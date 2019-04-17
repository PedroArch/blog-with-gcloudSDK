#!/usr/bin/env python2.7

import os
import webapp2
import jinja2
from google.appengine.ext import db
import datetime

# Getting the template directory
template_dir = os.path.join(os.path.dirname(__file__), "templates")

# Starting the Jinja2 Environment
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# Main Handler
class Handler(webapp2.RequestHandler):

    # shortcut for writing the outputs easily
    def write(self, *a, **params):
        self.response.out.write(*a, **params)

    # transform html file in a string to render
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    # render the page
    def render(self, template, **params):
        self.write(self.render_str(template, **params))

# Class that creates the database table
class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

# Main Page Handler
class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 10")
        self.render("mainpage.html", posts=posts)

# PostPage Handler
class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path("Post", int(post_id))
        post = db.get(key)

        # Checking if there is a post with this key
        if not post:
            self.error(404)
            return
        else:
            self.render("permalink.html", post=post)

# NewPost Page Handler
class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        # Checking if user has filled all fields
        if subject and content:
            post = Post(subject=subject, content=content)
            post.put()
            self.redirect("/blog/%s" % str(post.key().id()))

        else:
            error = "we need both a subject and some content!"
            self.render("newpost.html", error=error, subject=subject, content=content)


# End of File

# Webserver start
app = webapp2.WSGIApplication([("/", MainPage),
                               ("/newpost", NewPost),
                               ("/blog/([0-9]+)", PostPage)],
                              debug=True)
