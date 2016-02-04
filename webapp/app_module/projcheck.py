import flask
from apiclient.discovery import build
from flask import Flask, session,render_template,request


def proj_check():
    '''
    Checks to see if active project is set. If not, then route to a select project page with session cookie to return back
    :param return_path:
    :return:
    '''
    if session.get("active_proj"):
        return 1
    return None

def get_active_proj(return_path):
    '''
    sends to set project, sets session var so that project_select returns back
    :param return_path:
    :return:
    '''
    session['returnpath']=return_path
    return flask.redirect(flask.url_for('project_select'))

def get_proj(oauth2):
    '''
    gets all projects for active account
    :param oauth2:
    :return:
    '''
    proj_service = build('cloudresourcemanager','v1beta1',credentials=oauth2.credentials)
    projects_raw=proj_service.projects().list().execute()
    if projects_raw:
        session['projects'] = [i['projectId'] for i in projects_raw['projects']]
        session['projectlist']=[{'id':i['projectId'],'name':i['name']} for i in projects_raw['projects']]
    else:
        session['projects']='None'
    return
