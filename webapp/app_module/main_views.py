# noinspection PyPackageRequirements
"""`main` is the top level module for your Flask application."""
import json
import string
import random
# Import the Flask Framework
from flask import Flask, session,render_template,request,g
import flask

# appengine stuff
import httplib2
import apiclient
from apiclient import discovery
from apiclient.discovery import build
from apiclient.errors import HttpError
# oauth stuff -- probably needs to be imported wherever @oauth2.required is used
from oauth2client import client
from oauth2client.client import AccessTokenRefreshError
from oauth2client import flask_util
from oauth2client.flask_util import UserOAuth2

#import locally accessable modules
from app_module import app
from app_module.valid import validator # checks for validation
from app_module.projcheck import get_proj # gets list of projects

from compute_request import ComputeInfo

from google.appengine.api import urlfetch


#TODO: FIx this line -- make it more secure, perhaps have Python generate a random number to use
app.config['SECRET_KEY']=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


# Set permissions and permission request
# First, scope:
scope=['https://www.googleapis.com/auth/bigquery',
        'https://www.googleapis.com/auth/plus.me',
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/cloud-platform.read-only',
        'email',
        'https://www.googleapis.com/auth/userinfo.profile']

# Now, setup the oauth2 request
# The service key should be a oauth2 client id file as granted under APIs and credentials at https://console.developers.google.com/apis/credentials
oauth2=UserOAuth2(app,client_secrets_file="./GeneralAdmin_Webapp_OAUTH.json",scopes=scope)


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# Baseline Defaults
# set the admin project -- this will be referenced at various points in the app
admin_project='admin-project'
default_zone='us-central1-f'


@app.route('/')
@oauth2.required
def hello():
    """Return a friendly HTTP greeting."""
    # proj_service = build('cloudresourcemanager','v1beta1',credentials=oauth2.credentials)
    # projects_raw=proj_service.projects().list().execute()
    # if projects_raw:
    #     session['projects'] = [i['projectId'] for i in projects_raw['projects']]
    # else:
    #     session['projects']='None'
    get_proj(oauth2)
    # Change next line to determine the project whose membership is tested for access
    test_project = 'PROJECT TO TEST FOR VALIDATION'
    if test_project in session['projects']:
        session['validated'] = 1
        return render_template('index.html')
    else:
        [session.pop('validated') if session.get("validated") else None]
        flask.abort(403)
        # This looks like it works swimmingly.


# This is a brief helper script that will allow us to use an @validator decorator to ensure that members that are not in the required group are not given access to webapp pages




@app.route('/test.html')
@validator
def testing_page():
    out = """
    This page has a bunch of stuff on it that is used for testing
    <p> {}
    <p> {}
    """.format(session.get('validated',0),session['projects'])


    return out


@app.route("/temptest.html")
@validator
def temptest():
    return flask.redirect(flask.url_for("project_select"))

@app.route("/active_project")
@validator
def project_select():
    if not session.get("projects"):
        get_proj(oauth2) # attempt to get projects if not present in session. 
                         # TODO 01-13-2016 00:32 put error handling here
    msg=flask.get_flashed_messages()
    return render_template("projectform.html")



@app.route('/active_project',methods=['POST'])
@validator
def project_select_pull_in():
    b=request.form['project']
    session['active_proj']=b
    if session.get("returnpath"):
        return flask.redirect(flask.url_for(session['returnpath']))
    else:
        return flask.redirect('/')


# @app.route("/compute_request_pt1")
# @validator
# def compute_req():
#     return session['active_proj']

# @app.route('/oauth2callback')
# def info():
#   if oauth2.email!='trcook@gmail.com':
#       redirect(url_for('404'))
#   else:
#       return "you made it!! {}".format(oauth2.email)

# Setup the unauthorized handler


@app.errorhandler(403)
def page_not_found(e):
    """Return a custom 404 error."""
    return "Hey Bozo. You don't belong here -- scramo.", 403


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500




@app.route('/login')
def login():
    if session.get('validated'):
        session.pop('validated')
    return flask.redirect(oauth2.authorize_url('/'))

@app.route("/logout")
@oauth2.required
def logout():
    if session.get('validated'):
        session.pop('validated')
    try:
        oauth2.credentials.revoke(httplib2.HTTP())
        'credentials.revoke success'
        # oauth2.credentials.revoke(httplib2.Http())
    # session.clear()
    except:
        print 'credentials.revoke did not work'
        pass
    try:
        urlfetch.Fetch(url=oauth2.credentials.revoke_uri + '?token=' + oauth2.credentials.access_token,method=urlfetch.GET)
        print 'flask redirect success'
    except:
        print 'flask.redirect did not work'
        pass
    # except:
    #     # flask.redirect(credentials.revoke_uri + '?token=' + credentials.access_token)
    #     return '''
    #     <p>Problems loging out. Probably due to changes in the app.
    #     <p>Try logging in again and then logging out:
    #     <a href='/login'>click here</a>
    #     '''
    session.clear() # needed because oauth is storing oauth2 creds in session.

    return 'later duder'



@app.route("/reset")
def reset_ses():
    if session.get("active_proj"):
        session.pop("active_proj")
    if session.get("projectlist"):
        session.pop("projectlist")
    if session.get("validated"):
        session.pop("validated")
    return 'go back'


@app.before_request
def session_defaults():
    print 'before_request'
    if not 'admin_project' in session:
        session['admin_project']=admin_project
    if not 'zone' in session:
        session['zone']=default_zone
    if not ('projectlist' in session or request.endpoint or request.endpoint == 'login'):
        print '{}'.format(str(request.endpoint))
        print 'proj list not found'
        try:
             get_proj(oauth2)
        except:
             return flask.redirect('/')



@app.errorhandler(AccessTokenRefreshError)
def handle_invalid_grant(e):
    print 'hello'
    return flask.redirect('/login')