#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")
    
def get_remote_ip(host):
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        return 0
    return remote_ip

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        #print("Connecting")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        #print("Sending")
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        #print("Receiving..")
        self.socket.settimeout(1)
        fulldata = ''
        done = False
        method = 'utf-8'
        while(True):
            data = None
            try:
                data = self.socket.recv(1024)
            except Exception:
                break
            if not data:
                break
            decoded = data.decode(method)
            fulldata += decoded
            if "charset=" in decoded:
                charset = decoded.index("charset=")
                method = decoded[charset+8:decoded[charset:].index('\n')+charset]
        return fulldata

    def GET(self, url, args=None):
        body = ''
        if '//' in url:
            addr = urllib.parse.urlparse(url)
            route = addr.netloc
            if ':' in route:
                route = route[:route.index(':')]
            path = addr.path
            if addr.port:
                port = addr.port
            else:
                port = 80
        else:
            host = get_remote_ip(url)
            route = url
            port = 80
            path = ''
        try:
            self.connect(route,port)
        except Exception:
            code = 404
            print(code)
            return HTTPResponse(code, body)
        if (not path):
            path = '/'
        payload = 'GET '+path+' HTTP/1.1\r\n'
        payload += 'HOST: '+route+'\r\n'
        payload += 'Accept: */* \r\n'
        payload += '\r\n'
        self.sendall(payload)
        
        returnValues = self.recvall()
        self.close()
        body = returnValues
    
        if 'HTTP/1.1 ' in returnValues:
            index = returnValues.index('HTTP/1.1 ')
            if index < 10:
                code = int(returnValues[index+9:index+12])
        elif '404' in returnValues:
            code = 404
        elif '200' in returnValues:
            code = 200
        elif '301' in returnValues:
            code = 301
            
        index1 = body.index('\r\n\r\n')
        index2 = index1 + 4
        body = body[index2:]
        if code != 404:
            print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        body = ''
        if '//' in url:
            addr = urllib.parse.urlparse(url)
            route = addr.netloc
            if ':' in route:
                route = route[:route.index(':')]
            path = addr.path
            if addr.port:
                port = addr.port
            else:
                port = 80
        else:
            host = get_remote_ip(url)
            route = url
            port = 80
            path = ''
        try:
            self.connect(route,port)
        except Exception:
            code = 404
            print(code)
            return HTTPResponse(code, body)
        if (not path):
            path = '/'
        data = ''
        if args:
            for arg in args:
                data = data +'&'+ arg +'='+ args[arg]
            data = data[1:]
        payload = 'POST '+path+' HTTP/1.1\r\n'
        payload += 'HOST: '+route+'\r\n'
        payload += 'Content-Type: application/x-www-form-urlencoded'
        payload += 'Accept: */* \r\n'
        payload += 'Content-Length: '+str(len(data))
        payload += '\r\n\r\n'
        payload += data+'\r\n\r\n'
        #print('---------------------------')
        #print(payload+'\n\n')
        self.sendall(payload)
        
        returnValues = self.recvall()
        self.sendall(data)
        self.close()
        body = returnValues
    
        if 'HTTP/1.1 ' in returnValues:
            index = returnValues.index('HTTP/1.1 ')
            if index < 10:
                code = int(returnValues[index+9:index+12])
        elif '404' in returnValues:
            code = 404
        elif '200' in returnValues:
            code = 200
        elif '301' in returnValues:
            code = 301
        else:
            code = 404
        index1 = body.index('\r\n\r\n')
        index2 = index1 + 4
        body = body[index2:]
        if code != 404:
            print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
