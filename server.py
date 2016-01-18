#  coding: utf-8 
import SocketServer, os, sys, mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Michael Stensby
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class RequestHandler():

	BASE_PATH = "./www"
	HTTP_OK = "200 OK\n"
	HTTP_404 = "404 Not found\n\n"
	HTTP_301 = "301 Moved Permanently\r\n"
	
	def __init__(self, data):
		self.requestType = data[0]
		self.path = data[1]
		self.http = data[2]
		self.ipAddr = data[6]
		self.fullPath = self.BASE_PATH + self.path
		self.mimeType = mimetypes.guess_type(self.fullPath)[0]
	

	# check to see if file requested exists
	def exists(self):
		# check to see if file requested higher than server directory
		if (os.path.abspath(self.fullPath).startswith(os.path.abspath(self.BASE_PATH))):
			return os.path.exists(self.fullPath)
		return False
		
	# 404	
	def notFound(self,server):
		server.request.sendall(self.http + " " + self.HTTP_404)
		server.request.sendall("<html lang=en><title>Error 404 Not Found</title>")
		server.request.sendall("<b><body>404 Page not found</body></b>\n\n")
		
	#301	
	def redirect(self, server):
		server.request.sendall(self.http + " " + self.HTTP_301)
		server.request.sendall("Location: " + self.path + "/" + "\r\n \r\n")
		self.returnIndex(server)
		
	#200	
	def returnPage(self,server):
		server.request.sendall(self.http + " " + self.HTTP_OK + "Content-Type: " + self.mimeType + "\n\n")
		with open(self.fullPath) as file:
			server.request.sendall(file.read())
	
	# return /index.html for / requests
	def returnIndex(self,server):
		self.fullPath = self.fullPath+ "/index.html"
		self.mimeType = mimetypes.guess_type(self.fullPath)[0]
		self.returnPage(server)
		
	def requestHandle(self,server):
		if(self.exists()):
			if (self.mimeType != None):
				self.returnPage(server)
			elif (self.mimeType == None):
				if (self.path[-1] == "/"):
					self.returnIndex(server)
				else:
					self.redirect(server)
			else:
				self.notFound(server)

		else:
			self.notFound(server)
	

class MyWebServer(SocketServer.BaseRequestHandler):
   
	
	def handle(self):
		self.data = self.request.recv(1024).strip()
		data = self.data.split()
		#print ("Got a request of: %s\n" % self.data)
		
		handler = RequestHandler(data)
		handler.requestHandle(self)
		
		
						
if __name__ == "__main__":
	HOST, PORT = "localhost", 8080

	SocketServer.TCPServer.allow_reuse_address = True
	# Create the server, binding to localhost on port 8080
	server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
