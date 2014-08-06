#Author: Wasim Thabraze
#License: MIT
#You can do anything with the code as long as you give the credits. :)

import webapp2
import jinja2
from google.appengine.ext import db
import os
import requests
import json
import sys
sys.path.insert(0,'libs')
from bs4 import BeautifulSoup

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

initial_reputation = 200

#DataStore
class Userdata(db.Model):
    userid = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    blog = db.LinkProperty(required=True)
    email = db.EmailProperty(required=True)
    location = db.StringProperty(required=True)
    avatar_url = db.LinkProperty(required=True)
    html_url = db.LinkProperty(required=True)
    followers = db.IntegerProperty(required=True)
    following = db.IntegerProperty(required=True)
    followers_url = db.LinkProperty(required=True)
    following_url = db.LinkProperty(required=True)
    repos_url = db.LinkProperty(required=True)
    created_at = db.StringProperty(required=True)
    updated_at = db.StringProperty(required=True)


class Repodata(db.Model):
    owner_name = db.StringProperty(required=True)
    own_repo_name = db.StringProperty(required=True)
    languages = db.StringProperty()
    forks = db.IntegerProperty(required=True)
    stars = db.IntegerProperty(required=True)
    html_url = db.LinkProperty(required=True)
    homepage = db.StringProperty()
    description = db.StringProperty()

def Userrepos(self,r_url):
    res = requests.get(str(r_url))
    repo_data = json.loads(res.content)
    for i in repo_data:
        if not i['fork'] and not i['private']:
            own_repo_name = i['name']
            html_url = i['html_url']
            owner_name = i['owner']['login']
            languages = i['language']
            forks = i['forks']
            stars = i['stargazers_count']
            homepage = i['homepage']
            description = i['description']
            repo_instance = Repodata(own_repo_name=own_repo_name,owner_name=owner_name,forks=forks,html_url=html_url,stars=stars,languages=languages,homepage=str(homepage),description=description)
            repo_instance.put()
    





class MainHandler(BaseHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        userid = self.request.get('userid')
        user_api_url = 'https://api.github.com/users/'+str(userid)
        r = requests.get(user_api_url)
        data = json.loads(r.content)

        #data needs to be parsed now!
        name = data['name']
        avatar_url = data['avatar_url']
        html_url = data['html_url']
        blog = data['blog']
        email = data['email']
        location = data['location']
        public_repos = data['public_repos']
        followers = data['followers']
        following = data['following']
        repos_url = data['repos_url']
        followers_url = data['followers_url']
        following_url = data['following_url']
        created_at = data['created_at']
        updated_at = data['updated_at']
        Userrepos(self,repos_url)

        #user data needs to be stored in the google data store now!
        user_instance = Userdata(name=name,created_at=created_at,updated_at=updated_at,userid=userid,avatar_url=avatar_url,blog=blog,email=email,repos_url=repos_url,followers=followers,following=following,following_url=following_url,followers_url=followers_url,location=location,html_url=html_url)
        user_instance.put()

        
        

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
