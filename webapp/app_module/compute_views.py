# noinspection PyPackageRequirements
"""`main` is the top level module for your Flask application."""

import json
# Import the Flask Framework
from flask import Flask, session,render_template,request,g
import flask
# appengine stuff
import httplib2
import apiclient
from apiclient import discovery
from apiclient.discovery import build
from apiclient.errors import HttpError

#import locally accessable modules
from app_module import app
from app_module.valid import validator # checks for validation
from app_module.projcheck import proj_check,get_active_proj,get_proj
from app_module.main_views import oauth2
from apiclient.discovery import build
from compute_request import ComputeRequest,ComputeInfo

from app_module.name_generator.name_generator import word_gen


@app.route("/compute_request")
@oauth2.required()
@validator
def compute_req():
    if not proj_check():
        return get_active_proj('compute_req')
    session.pop('returnpath') if session.get('returnpath') else ''# removes 'returnpath if set'
    # g.computers=compute_instances(session['active_proj'],'us-central1-f',oauth2)
    g.compute_info=ComputeInfo(session['admin_project'],session['zone'],oauth2)
    g.computers=g.compute_info.compute_machine_types
    g.inst_name=word_gen()
    #g.computers=compute_instances(session['active_proj'],'us-central1-f',oauth2)
    session['imageslist']=g.compute_info.compute_images
    return render_template('compute_request_config.html')


# setup the url to recieve submitted form

@app.route("/compute_request",methods=['POST'])
@oauth2.required()
@validator
def compute_req_pull_in():
    mT=request.form['machineType']
    dimage=request.form['disk_image']
    inst_name=request.form['inst_name']
    computerequest=ComputeRequest('request_template/compute_request.json',metadata={'namo':'tom'},machine_type=mT,disk_image=dimage,inst_name=inst_name)
    session['computerequest']=computerequest.request
    computerequest.execute(cred=oauth2)
    # del(g.computerequest)
    # b=ComputeRequest('static/compute_request.json',metadata={'name':'tom'})
    # computers=compute_instances(session['active_proj'],'us-central1-f',oauth2)
    return flask.redirect(flask.url_for('compute_list_get'))


@app.route('/compute_list')
@oauth2.required()
@validator
def compute_list_get():
    # TODO change this into a form to query for specific things or set project/subproject.
    computerinfo=ComputeInfo(session['admin_project'],session['zone'],oauth2)
    g.instances=computerinfo.compute_instances
    return render_template('instances_list.html')