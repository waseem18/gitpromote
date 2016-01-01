
import webapp2
import jinja2
import requests
import os
import sys
import time
import logging
import urllib2
import json
import re
from operator import itemgetter
from datetime import datetime
from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import mail



template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)



def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
 
        try:
            # Dispatch the request!
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

 
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))


class ToNotify(db.Model):
    email = db.StringProperty()



class Main(BaseHandler):
    def get(self):
        self.render('index.html')
    def post(self):
        email = self.request.get('email')
        if email:
            instance = ToNotify(key_name=email,email=email)
            instance.put()
            self.render('thankyou.html')
        else:
            self.render('index.html')






config = {}
config['webapp2_extras.sessions'] = {'secret_key': ' ','cookie_args':{'max_age':86400}}


app = webapp2.WSGIApplication([
    ('/',Main)
],config=config, debug=True)
