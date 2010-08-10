#
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description:
#

"""

"""


import getpass
import urllib, urllib2
import urlparse
from HTMLParser import HTMLParser
import sys
import os
import logging
import re


class SSOHTMLParser(HTMLParser):
    """
    Simple html parser which understand what is needed to show the current
    version of the SSO login page. End parsing at <\html>, which is in
    current version of login page inside <noscript> before other stuff on page.
    Asks form inputs of types text and password from the user.
    The data is saved in varables inside class
    """
    def __init__(self, *argv, **kwargs):
        self.username_func = kwargs.pop('username_func',None)
        self.password_func = kwargs.pop('password_func',None)
        HTMLParser.__init__(self, *argv, **kwargs)
        self.html_end = False
        self.httpdata = {}
        self.input_requested = False
        self.input_entered = False
        self.method = ''
        self.action = ''
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.html_end:
            return
        if tag == 'br':
            print
        elif tag == 'form':
            self.action = attrs.get('action')
            self.method = attrs.get('method')
        elif tag == 'input':
            inputtype = attrs.get('type', 'text')
            if inputtype == 'hidden':
                # Should the username be also overridable
                self.httpdata[attrs.get('name')] = attrs.get('value')
            if inputtype == 'password':
                self.input_requested = True
                data = self.password_func()
                if data:
                    self.input_entered = True
                self.httpdata[attrs.get('name')] = data
            if inputtype == 'text':
                self.input_requested = True
                data = self.username_func()
                if data:
                    self.input_entered = True
                self.httpdata[attrs.get('name')] = data
            if inputtype == 'submit':
                self.httpdata['submit'] = attrs.get('value')

    def handle_endtag(self, tag):
        if self.html_end:
            return
        if tag == 'tr':
            print
        if tag == 'title':
            print
        if tag == 'html':
            self.html_end = True

    def handle_data(self, data):
        if self.html_end:
            return
        if data.strip():
            print data.strip(),

class CarbonAuthHandler(urllib2.AbstractHTTPHandler):
    handler_order = 600
    def __init__(self):
        urllib2.AbstractHTTPHandler.__init__(self)
        self.auth_count = 0
        self.auth_max = 5
        self.username = ""
        self.password = ""
        self.username_func = None
        self.password_func = None
        
    
    def add_username_func(self, username_func):
        """
        Add password getting function
        """
        self.username_func = username_func

    def add_password_func(self, password_func):
        """
        Add password getting function
        """
        self.password_func = password_func

    def get_username(self):
        """
        Add password getting function
        """
        if self.auth_count == 0  and self.username_func:            
            return self.username_func()
        else:
            self.username = raw_input("Username: ")
            return self.username 
            
    def get_password(self):
        """
        Add password getting function
        """
        if self.auth_count == 0 and self.password_func:            
            return self.password_func()
        else:
            self.password = getpass.getpass()
            return self.password

    def https_response(self, request, response):
        """
        Catches responses which are from sso login page and asks for the
        information from the command line and posts it.
        After posting urllib2 takes care of following redirects back to
        original page.
        """
        if (re.match('login.*\.europe\.nokia\.com', request.get_host())):
            if self.auth_count > self.auth_max:
                print "Authentication failed!"
                return response
            sso_parser = SSOHTMLParser(username_func=self.get_username, password_func=self.get_password)
            sso_parser.feed(response.read())
            self.auth_count += 1
            
            # !sso_parser.input_requested when we have posted the form and
            # are reading the redirect back. We don't want to handle that
            if sso_parser.input_requested:
                if not sso_parser.input_entered:
                    # By entering empty username and password you get
                    # out of infinite invalid login loop
                    # Only bad thing that the SSO login page doesen't
                    # tell you that login failed, only shows the same text
                    # again
                    raise urllib2.URLError("No login data entered")
                newurl = urlparse.urljoin(request.get_full_url(), sso_parser.action)
                ssoreq = urllib2.Request(newurl,
                                         urllib.urlencode(sso_parser.httpdata),
                                         origin_req_host=request.get_origin_req_host(),
                                         unverifiable=True,
                                         )
                return self.parent.open(ssoreq)
        return response

    def http_response(self, request, response):
        """
        Catches responses which are from normal carbon authenticatoin page and uses set password if found
        or asks for the information from the command line and posts it.
        After posting urllib2 takes care of following redirects back to
        original page.
        """    
        if response.code == 200 and (re.match('.*/extauth/login/?.*', request.get_full_url())):
            if self.auth_count > self.auth_max:
                raise urllib2.HTTPError("Authentication failed!")
            
            loginreq = urllib2.Request(request.get_full_url(),
                                     urllib.urlencode({ 'username' : self.get_username(), 
                                                        'password' : self.get_password(),
                                                        'submit' : 'login'}
                                                      ),
                                     origin_req_host=request.get_origin_req_host(),
                                     unverifiable=True,
                                     )
            self.auth_count += 1
            return self.parent.open(loginreq)
        else:            
            return response
