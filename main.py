#Author: Wasim Thabraze
#Product:gitpromote
#version: alpha
#License: MIT
#Mail me if you wish to speak to me about this project or to just say a Hi! I would humbly respond.:D
#Bug: Delete a repo which is deleted on github----->To be done in Beta version! 
#Logout user if there is a change in the session id stored in cookie!---->Bug traced and completely cleared.
import webapp2
import jinja2
import requests
import json
import os
from datetime import datetime
from google.appengine.ext import db
from webapp2_extras import sessions

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

#Base handler handles user sessions.
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
 
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
 
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()



class Userdata(db.Model):
    user_login_id = db.StringProperty()
    fullname = db.StringProperty()
    website = db.StringProperty()
    bio = db.StringProperty()
    email = db.StringProperty()
    location = db.StringProperty()
    avatar_url = db.LinkProperty()
    user_html_url = db.LinkProperty()
    followers = db.IntegerProperty()
    following = db.IntegerProperty()
    followers_url = db.LinkProperty()
    following_url = db.LinkProperty()
    repos_url = db.LinkProperty()
    created_at = db.StringProperty()
    updated_at = db.StringProperty()
    lang_tags= db.ListProperty(str)



class Repodata(db.Model):
    user_login_id = db.StringProperty(required=True)
    repo_name = db.StringProperty(required=True)
    language = db.StringProperty()
    forks = db.IntegerProperty(required=True)
    stars = db.IntegerProperty(required=True)
    repo_html_url = db.LinkProperty(required=True)
    homepage = db.StringProperty()
    description = db.StringProperty()

class PromotedRepos(db.Model):
   promoting_repo_name = db.StringProperty()
   promoting_user_name = db.StringProperty()
   promoting_user_fullname = db.StringProperty()
   people = db.StringProperty()
   promoted_time = db.DateTimeProperty(auto_now=True)
   promoting_repo_language = db.StringProperty()
   promoting_repo_forks = db.StringProperty()
   promoting_repo_stars = db.StringProperty()
   promoting_repo_description = db.StringProperty()




class MainHandler(BaseHandler):
  def get(self):
    #User id logged in. Renders Homepage of the logged in user!
    if self.session.get('user_login_id'):
        user_login_id = self.session.get('user_login_id')
        user_data = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :g",g=user_login_id)
        homepage_posts = db.GqlQuery("SELECT * FROM PromotedRepos ORDER BY promoted_time DESC LIMIT 50")
        template_values={'user_login_id':user_login_id,'homepage_posts':homepage_posts,'user_data':user_data}
        template = jinja_env.get_template('homepage.html')
        self.response.out.write(template.render(template_values))
    else:
        #User is not logged in. Renders Signup page!
        template_values={}
        template = jinja_env.get_template('index.html')
        self.response.out.write(template.render(template_values))



class Developer(BaseHandler):
    def get(self):
        url_queries = self.request.GET
        state = url_queries['state']
        code = url_queries['code']
        url = 'https://github.com/login/oauth/access_token?client_id=a454ac3fef0a7cde71df&client_secret=4029cf0da2c400aa755d818dcdda96be97fc94a4&redirect_uri=http://gitpromote.appspot.com/dev&code='+str(code)
        req = requests.post(url)
        req = str(req.content)
        access_token = ""
        i = 13
        while (req[i]!='&'):
            access_token = access_token + req[i]
            i = i + 1

        user_api_url = 'https://api.github.com/user?access_token='+str(access_token)
        user_json_data = requests.get(user_api_url)
        d = json.loads(user_json_data.content)
        user_login_id = d['login']
        q = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :w",w=user_login_id).fetch(limit=2)
        #if len(q)>0:
        #    self.redirect('http://gitpromote.appspot.com')
        #    return
        if 'name' in d:
            fullname = d['name']
        else:
            fullname=""

        self.session['user_login_id'] = user_login_id

        avatar_url = d['avatar_url']
        user_html_url = d['html_url']
        if 'blog' in d:
            website = d['blog']
        else:
            website=""
        if 'email' in d:
            email = d['email']
        else:
            email=""
        if 'location' in d:
            location = d['location']
        else:
            location=""
        public_repos = d['public_repos']
        bio=""
        followers = d['followers']
        following = d['following']
        repos_url = d['repos_url']
        followers_url = d['followers_url']
        following_url = d['following_url']
        created_at = d['created_at']
        updated_at = d['updated_at']

        lang = []
        res = requests.get(str(repos_url))
        repo_data = json.loads(res.content)
        for i in repo_data:
            if not i['fork'] and not i['private']:
                repo_name = i['name']
                repo_html_url = i['html_url']
                user_login_id = i['owner']['login']
                language = i['language']
                forks = i['forks']
                stars = i['stargazers_count']
                homepage = i['homepage']
                description = i['description']
                lang.append(language)
                if len(q)==0:
                    repo_instance = Repodata(key_name=repo_name,repo_name=repo_name,user_login_id=user_login_id,forks=forks,repo_html_url=repo_html_url,stars=stars,language=language,homepage=str(homepage),description=description)
                    repo_instance.put()

                if len(q)>0:
                    repo_instance = Repodata(key_name=repo_name,repo_name=repo_name,user_login_id=user_login_id,forks=forks,repo_html_url=repo_html_url,stars=stars,language=language,homepage=str(homepage),description=description)
                    repo_instance.put()
                    
        lang_list = list(set(lang))
        if None in lang_list:
            lang_list.remove(None)

        if len(q)>0:
            user_instance = Userdata(key_name=user_login_id,repos_url=repos_url,public_repos=public_repos,created_at=created_at,updated_at=updated_at,lang_tags=lang_list,fullname=fullname,user_login_id=user_login_id,avatar_url=avatar_url,user_html_url=user_html_url,website=website,email=email,location=location,following=following,followers=followers,following_url=following_url,followers_url=followers_url)
            user_instance.put()
            self.redirect('/user/'+str(user_login_id))
            
        if len(q)==0:
            user_instance = Userdata(key_name=user_login_id,repos_url=repos_url,bio=bio,public_repos=public_repos,created_at=created_at,updated_at=updated_at,lang_tags=lang_list,fullname=fullname,user_login_id=user_login_id,avatar_url=avatar_url,user_html_url=user_html_url,website=website,email=email,location=location,following=following,followers=followers,following_url=following_url,followers_url=followers_url)
            user_instance.put()
            self.redirect('/details')



class Details(BaseHandler):
    def get(self):
        user_login_id = self.session.get('user_login_id')
        user_info = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :v",v=user_login_id)
        template_values = {'user_info':user_info}
        template = jinja_env.get_template('extrainfo.html')
        self.response.out.write(template.render(template_values))   

class Redirecting(BaseHandler):
    def post(self):
        user_login_id = self.session.get('user_login_id')
        fullname = self.request.get('fullname')
        bio = self.request.get('bio')
        email = self.request.get('email')
        website=self.request.get('website')
        user_info = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :g",g=user_login_id)
        user_info.fullname = fullname
        user_info.bio = bio
        user_info.email = email
        user_info.website = website
        self.redirect('/user/'+user_login_id)

class ProfileHandler(BaseHandler):
  def get(self):
    #self.redirect('href="https://github.com/login/oauth/authorize?state=gitpromote&redirect_uri=http://gitpromote.appspot.com/dev&client_id=a454ac3fef0a7cde71df&scope=user')
    user_login_id = self.session.get('user_login_id')
    current_url = self.request.url
    userid = current_url.split('/')[4]
    qq = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :u",u=userid).fetch(limit=2)
    if len(qq)==0:
        self.response.out.write(userid+" has not yet created a profile on gitpromote. Invite him!")
        return
    user_info = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :a",a=userid)
    repo_info = db.GqlQuery("SELECT * FROM Repodata WHERE user_login_id= :b",b=userid)
    template_values = {
    'userid':userid,
    'user_login_id':user_login_id,
    'repo_info' :repo_info,
    'user_info':user_info
    }
    template = jinja_env.get_template('profilepage.html')
    self.response.out.write(template.render(template_values))


class Repository(BaseHandler):
  def get(self):
    user_login_id = self.session.get('user_login_id')
    current_url = self.request.url
    repo_enquired = current_url.split('/')[4]

    repo_info = db.GqlQuery("SELECT * FROM Repodata WHERE repo_name= :c",c=repo_enquired)
    user_info = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :x",x=user_login_id)
    #is_it_promoted = db.GqlQuery("SELECT * FROM PromotedRepos WHERE promoting_repo_name= :g",g=repo_enquired).fetch(limit=1)
    #if len(is_it_promoted)>0:
    #    pt = db.GqlQuery("SELECT promoted_time FROM PromotedRepos WHERE promoting_repo_name= :h",h=repo_enquired)
    #    ps = "Last promoted at: "
    #else:
    #    pt = ""
    #    ps = "Repository not yet promoted!"
    template_values = {
    #'pt':pt,
    #'ps':ps,
    'user_info':user_info,
    'user_login_id':user_login_id,
    'repo_info':repo_info
    }
    template = jinja_env.get_template('repo.html')
    self.response.out.write(template.render(template_values))


class Promote(BaseHandler):
    def post(self):
        people = self.request.get('rsval')
        promoting_repo_name = self.request.get('promoting_repo_name')
        promoting_user_name = self.request.get('promoting_user_name')
        promoting_user_fullname = db.GqlQuery("SELECT fullname FROM Userdata WHERE user_login_id= :l",l=promoting_user_name).get()
        promoting_user_fullname = promoting_user_fullname.fullname
        promoting_repo_language = self.request.get('promoting_repo_language')
        promoting_repo_forks = self.request.get('promoting_repo_forks')
        promoting_repo_stars = self.request.get('promoting_repo_stars')
        promoted_time = datetime.now()
        promoting_repo_description = self.request.get('promoting_repo_description')
        pr = PromotedRepos(key_name=promoting_repo_name,promoting_repo_stars=promoting_repo_stars,promoting_user_fullname=promoting_user_fullname,promoting_repo_description=promoting_repo_description,promoting_repo_forks=promoting_repo_forks,promoting_repo_language=promoting_repo_language,people=people,promoting_user_name=promoting_user_name,promoting_repo_name=promoting_repo_name,promoted_time=promoted_time)
        pr.put()
        self.redirect('http://gitpromote.appspot.com')

class Tag(BaseHandler):
    def get(self):
        current_url = self.request.url
        tag = current_url.split('/')[4]
        homepage_tagged_posts = db.GqlQuery("SELECT * FROM PromotedRepos WHERE promoting_repo_language= :e",e=tag)
        user_login_id = self.session.get('user_login_id')
        user_data = db.GqlQuery("SELECT * FROM Userdata WHERE user_login_id= :j",j=user_login_id)
        template_values = {
        'homepage_tagged_posts':homepage_tagged_posts,
        'user_data':user_data
        }
        template = jinja_env.get_template('homepage-tagged.html')
        self.response.out.write(template.render(template_values))


class Signout(BaseHandler):
  def get(self):
    if self.session.get('user_login_id'):
      del self.session['user_login_id']

    self.redirect('http://gitpromote.appspot.com')



config = {}
config['webapp2_extras.sessions'] = {'secret_key': 'some-secret-key-to-use','cookie_args':{'max_age':604800}}

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/dev',Developer),
                               ('/user/.*',ProfileHandler),
                               ('/red',Redirecting),
                               ('/details',Details),
                               ('/repo/.*',Repository),
                               ('/promote',Promote),
                               ('/tagged/.*',Tag),
                               ('/signout',Signout)
                            ], config=config, debug=True)
