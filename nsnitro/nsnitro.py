""" Citrix Netscaler Nitro API accessor """

import urllib, urllib2
from nsutil import *

__version__ = "0.0.2"

class NSNitro:
        """ Main class """

        __ip      = "1.2.3.4"
        __user  = "api_user"
        __password    = "api_user"
        __baseurl     = "http://1.2.3.4/nitro/v1/config/"
        __sessionid   = ""
        __loggedin    = False
        __initialized = False
        __contenttype = "application/x-www-form-urlencoded"
        __postheaders = {'Cookie' : 'sessionid='+__sessionid, 'Content-type' : __contenttype}

        def __init__(self, ip, user, password, useSSL=False):
                """ Contructor: ip - LB ip, user - LB username, pass - LB password """
                self.__ip = ip
                self.__user = user
                self.__password = password
                self.__baseurl = "%s://%s/nitro/v1/config/" % ('https' if useSSL else 'http',ip)
                self.__initialized = True

        def get_url(self):
                """ Returns base url for nitro API. Mostly useful for debugging """
                if not self.__initialized:
                        raise NSNitroError("Not initialized.")
                return self.__baseurl

        def get_sessionid(self):
                """ Returns sessionID that LB gave us after logging in """
                if not self.__initialized or not self.__loggedin:
                        raise NSNitroError("Not initialized or not logged in.")

                return self.__sessionid

        def login(self):
                """ Logins to the LB using the credentials give to constructor """
                if not self.__initialized:
                        raise NSNitroError("Not initialized.")

                payload = {"object":json.dumps({"login":{"username":self.__user,"password":self.__password}})}
                try:
                        nsresponse = self.post(payload)
                        if nsresponse.failed:
                                raise NSNitroError(nsresponse.message)

                        self.__sessionid = nsresponse.get_response_field('sessionid')
                        self.__postheaders = {'Cookie' : 'sessionid='+self.__sessionid, 'Content-type' : self.__contenttype}
                        self.__loggedin = True
                        return True

                except SyntaxError:
                        raise NSNitroError("Could not parse LB response.")
                except urllib2.URLError, ue:
                        raise NSNitroError("Error logging in!" + ue.message)

        def post(self, payload):
                try:
                        payload_encoded = urllib.urlencode(payload)

                        req = urllib2.Request(self.__baseurl, payload_encoded, self.__postheaders)
                        response = urllib2.urlopen(req)

                except urllib2.HTTPError, e:
                        raise NSNitroError("Could not send post request: %s, %s" % (e.code, e.message))

                nsresponse = NSNitroResponse(response.read())
                if nsresponse.failed:
                        raise NSNitroError(nsresponse.message)
                return nsresponse

        def put(self, payload):
                try:
                        opener = urllib2.build_opener(urllib2.HTTPHandler)
                        request = urllib2.Request(self.__baseurl, json.dumps(payload))
                        request.add_header('Cookie', 'sessionid='+self.__sessionid)
                        request.get_method = lambda: 'PUT'
                        response = opener.open(request)

                except urllib2.HTTPError, e:
                        raise NSNitroError("Could not send put request: %s, %s" % (e.code, e.message))

                nsresponse = NSNitroResponse(response.read())
                if nsresponse.failed:
                        raise NSNitroError(nsresponse.message)
                return nsresponse

        def get(self, url):
                try:
                        opener = urllib2.build_opener()
                        opener.addheaders.append(('Cookie', 'sessionid='+self.__sessionid))
                        response = opener.open(url)

                except urllib2.HTTPError, e:
                        print "Got reponse code: %s from the server" % e.code
                        raise NSNitroError("Could not get resource: %s, %s" % (e.code, e.message))

                nsresponse = NSNitroResponse(response.read())
                if nsresponse.failed:
                        raise NSNitroError(nsresponse.message)

                return nsresponse

        def delete(self, url):
                try:
                        opener = urllib2.build_opener()
                        req = urllib2.Request(url)
                        req.add_header('Cookie', 'sessionid='+self.__sessionid)
                        req.get_method = lambda: 'DELETE'
                        response = urllib2.urlopen(req)

                except urllib2.HTTPError, e:
                        raise NSNitroError("Could not send delete request: %s, %s" % (e.code, e.message))

                nsresponse = NSNitroResponse(response.read())
                if nsresponse.failed:
                        raise NSNitroError(nsresponse.message)
                return nsresponse

        def logout(self):
                try:
                    opener = urllib2.build_opener()
                    req = urllib2.Request(self.__baseurl)
                    req.add_header('Cookie','sessionid='+self.__sessionid)
                    req.add_header('logout','{}')
                    response = urllib2.urlopen(req)
                except urllib2.HTTPError,e:
                    raise NSNitroError("Could not send logout request: %s, %s" % (e.code, e.message))

                nsresponse = NSNitroResponse(response.read())
                if nsresponse.failed:
                        raise NSNitroError(nsresponse.message)
                del self.__sessionid

                return nsresponse.get_json_response()
