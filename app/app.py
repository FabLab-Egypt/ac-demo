#!/usr/bin/env python2.7
# -*- charset: utf8 -*-

import json

from helpers import redirect_url
from storage import Storage, Member, AuthExpired
depo = Storage('dumy_depo.json')


from flask import Flask, request, render_template, Response, abort, redirect
app = Flask(__name__)
app.config.from_object('config')

OK           = 200
BAD_REQUEST  = 400
UNAUTHORIZED = 401
INVALID      = 403
NOT_FOUND    = 404
NOT_ALLOWED  = 405
TOKEN_EXPIRED = 419 #498

class TokenExpiredInvalid(Exception):
    pass

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/doc/')
@app.route('/docs/')
def docs():
    return render_template('docs.html')

@app.route('/users/rm/<usr_mobile>')
def remove_record(usr_mobile):
    print depo.rm(usr_mobile)
    return redirect(redirect_url('list_panel'))

@app.route('/users/block/<usr_mobile>')
def block_record(usr_mobile):
    print depo.disable(usr_mobile)
    return redirect(redirect_url('list_panel'))

@app.route('/users/unblock/<usr_mobile>')
def unblock_record(usr_mobile):
    print depo.enable(usr_mobile)
    return redirect(redirect_url('list_panel'))

@app.route('/users/add/', methods=['GET', 'POST'])
def signup_panel():
    error = None
    if request.method == 'POST':
        kys = ['user-name', 'user-email', 'user-mobile']
        if (set(kys) & set(request.form.keys()) ) == set(kys):
            if depo.addAndSave(request.form):
                return Response('Recored Saved', content_type='text/plain; charset=utf-8'), OK
            else:
                return Response('Recored Duplicated, Not Saving', content_type='text/plain; charset=utf-8'), INVALID
        return abort(BAD_REQUEST)
    return render_template('signup_panel.html')

@app.route('/users/list/')
def list_panel():
    print len(depo.getObject())
    return render_template('registered_list.html', users_data=depo.getObject())

@app.route('/users/list/members')
def list_panel_members():
    members_lst = []
    for usr in depo.getObject():
        if usr['user-rfid']:
            members_lst.append(usr)
    return render_template('registered_list.html', users_data=members_lst)

@app.route('/users/list/visitors')
def list_panel_visitors():
    visitors_lst = []
    for usr in depo.getObject():
        if not usr['user-rfid']:
            visitors_lst.append(usr)
    return render_template('registered_list.html', users_data=visitors_lst)

@app.route('/a/')
@app.route('/a/<token>')
def authenticate_token(token=None):
    print '>> toke:', token
    if token:
        usr_rec = None
        rspnd = 'name: {}\n\remail: {}\n\rmobile: {}\n\rtype: {}'
        if token[:2] == '01' and len(token.replace('-','')) == 11:
            print '>> lookup Visitor Base'
            usr_rec = depo.lookup_visitor(token)
            print ">> ", usr_rec
            if isinstance(usr_rec, Member):
                return abort(NOT_ALLOWED)
        else:
            print '>> lookup Members Base'
            usr_rec = depo.lookup_members(token)

        if usr_rec:
            if isinstance(usr_rec, dict):
                user_type = 'member' if usr_rec['user-rfid'] else 'visitor'
                rspnd = rspnd.format(usr_rec['user-name'],usr_rec['user-email'],usr_rec['user-mobile'],user_type)
                return Response(rspnd, content_type='text/plain; charset=utf-8')
            elif isinstance(usr_rec, AuthExpired):
                abort(UNAUTHORIZED)
        else:
            abort(NOT_FOUND)
    return abort(BAD_REQUEST)


@app.errorhandler(NOT_FOUND)
def not_found(error):
    return Response('Not Found', content_type='text/plain; charset=utf-8'), NOT_FOUND

@app.errorhandler(NOT_ALLOWED)
def not_allowed(error):
    return Response('Not Allowed', content_type='text/plain; charset=utf-8'), NOT_ALLOWED

@app.errorhandler(BAD_REQUEST)
def bad_request(error):
    return Response('Bad Request', content_type='text/plain; charset=utf-8'), BAD_REQUEST

@app.errorhandler(UNAUTHORIZED)
def unauthorized(error):
    return Response('Unauthorized: Token Expired/Invalid', content_type='text/plain; charset=utf-8'), UNAUTHORIZED

@app.errorhandler(TokenExpiredInvalid)
def token_expired(error):
    return Response('Token Expired/Invalid', content_type='text/plain; charset=utf-8'), TOKEN_EXPIRED

if __name__ == '__main__':
    app.run(port=app.config['PORT'])
