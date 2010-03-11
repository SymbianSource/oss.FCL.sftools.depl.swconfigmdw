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

import SimpleHTTPServer
import SocketServer
import threading
import httplib
import os
import simplejson
import urllib
import urlparse
import posixpath
import cgi
from StringIO import StringIO

class SimpleWebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        self.action = ''

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        (action,path) = self.translate_path(self.path)
        
        if action == 'list_resources':
            return self.list_directory(path)
        elif action == 'get_resource':
            return self.get_resource(path) 
        else:
            self.send_error(404, "File not found")
            return None

    def get_resource(self,path):
        f = None
        ctype = self.guess_type(path)
        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        try:
            f = open(path, mode)
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        files = []
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            files.append(displayname)
        
        f.write(simplejson.dumps(files))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        @return: action,path
        """
        # abandon query parameters
        action = ''
        path = urlparse.urlparse(path)[2]
        path = path.lstrip('/')
        splittedpath = path.split('/')
        if len(splittedpath) > 1:
            action = splittedpath[1]
            path   = "/".join(splittedpath[2:])
            path = posixpath.normpath(urllib.unquote(path))
            words = path.split('/')
            words = filter(None, words)
            path = os.getcwd()
            for word in words:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir): continue
                path = os.path.join(path, word)
        return (action,path)
        

class SimpleWebServer(threading.Thread):
    def __init__(self, folder=".", port=8000):
        super(SimpleWebServer,self).__init__()
        self.PORT    = port
        self.folder  = folder
        self.handler = SimpleWebHandler
        self.httpd   = SocketServer.TCPServer(("localhost", self.PORT), self.handler)
        self.active  = False
        print "serving at port", self.PORT
 
    def run(self):
        # minimal web server.  serves files relative to the
        # current directory.
        os.chdir(self.folder)
        self.active = True
        while self.active:
            self.httpd.handle_request()
        return 0

    def stop(self):
        self.active = False
        conn = httplib.HTTPConnection('localhost', self.PORT)
        conn.request("GET", "/")
        r1 = conn.getresponse()
        print r1.status, r1.reason

if __name__ == '__main__':
    server = SimpleWebServer()
    server.start()
