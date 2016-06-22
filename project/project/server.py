#from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol
from twisted.protocols.basic import LineReceiver

from twisted.python import log
from twisted.web.client import getPage
from twisted.application import service, internet

import time
import datetime
import logging
import re
import sys
import json

GOOGLE_API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
GOOGLE_API_KEY = "AIzaSyCkw_HbOwiI30J19GBoQyFRSmdLTYyM7Qo"

PORTS = {
			"Alford": 8000, 
			"Bolden": 8001, 
			"Hamilton": 8002, 
			"Parker": 8003, 
			"Powell": 8004
}

FLIST = {
		"Alford": ["Parker", "Powell"], 
		"Bolden": ["Parker", "Powell"], 
		"Hamilton": ["Parker"], 
		"Parker": ["Alford", "Bolden", "Hamilton"], 
		"Powell": ["Alford", "Bolden"]
}

class ProxyServer(LineReceiver):
	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.factory.numConnections += 1
		logging.info("Connection made. Total: {0}".format(self.factory.numConnections))

	def connectionLost(self, reason):
		self.factory.numConnections -= 1
		logging.info("Connection lost. Total: {0}".format(self.factory.numConnections))

	def lineReceived(self, line):
		logging.info("Line received: {0}".format(line))
		words = line.split(" ")

		if (words[0] == "AT") and (len(words) == 6):
			self.handle_AT(words[1:])

		elif (words[0] == "IAMAT") and (len(words) == 4):
			self.handle_IAMAT(words[1:])

		elif (words[0] == "WHATSAT") and (len(words) == 4):
			self.handle_WHATSAT(words[1:])

		else:
			logging.error("Invalid command: {0}".format(line))
			self.transport.write("? " + line + "\n")


	def handle_AT(self, message):
		SID, timeDiff, CID, location, CTS = message

		# Check client's timestamp to prevent unnecessary flooding
		if (CID in self.factory.clients) and (CTS <= self.factory.clients[CID]["CTS"]):
			# The incoming update is outdated; stop further flooding
			logging.info("Outdated/duplicate location update from {0}".format(SID))
			return

		# Update client info
		self.logClient(CID)
		self.factory.clients[CID] = {"SID": SID, "timeDiff": timeDiff, "location": location, "CTS": CTS}

		# Send update location to friends 
		self.sendLocationUpdate(CID)


	def handle_IAMAT(self, message):
		CID, location, CTS = message

		# Calculate time difference
		timeDiff = time.time() - float(CTS)

		# Update timestamp format
		timeDiffStr = "+{0}".format(timeDiff) if timeDiff >= 0 else timeDiff

		# Update client info
		self.logClient(CID)
		self.factory.clients[CID] = {"SID": self.factory.SID, "timeDiff": timeDiffStr, "location": location, "CTS": CTS}

		# Reply client's command
		self.reply(CID)
		
		# Send update location to friends
		self.sendLocationUpdate(CID)


	def handle_WHATSAT(self, message):
		CID, radius, limit = message

		# Check if client exists
		if not (CID in self.factory.clients):
			# Client does not exist
			logging.info("Requested client does not exist, stupid!")
			return

		location = re.sub(r'[-]', ' -', self.factory.clients[CID]["location"])
		locationParts = re.sub(r'[+]', ' +', location).split() 

		# Contact Google Places API and Reply client's command
		API_URL = "{0}key={1}&location={2},{3}&radius={4}".format(GOOGLE_API_URL, GOOGLE_API_KEY, locationParts[0], locationParts[1], radius)
		API_response = getPage(API_URL)
		API_response.addCallback(callback = lambda x:(self.printData(x, CID, limit)))

		logging.info("Sent Google Places API request to {0}".format(API_URL))


	def printData(self, jsonData, CID, limit):
		logging.info("Google Places API response: {0}".format(jsonData))

		data = json.loads(jsonData)
		results = data['results']
		data['results'] = results[0:int(limit)]
		jsonData = json.dumps(data, indent=4)

		response = "{0}\n{1}\n\n".format(self.createLocationUpdate(CID), jsonData)
		logging.info("{0}'s response: {1}".format(self.factory.SID, response))
		self.transport.write(response)


	def createLocationUpdate(self, CID):
		client = self.factory.clients[CID]
		return "AT {0} {1} {2} {3} {4}".format(client["SID"], client["timeDiff"], CID, client["location"], client["CTS"])


	def sendLocationUpdate(self, CID):
		# Send client info to friends
		# list: friend -> port
		locUpdate = self.createLocationUpdate(CID)
		logging.info("Location update by {0}: {1}".format(self.factory.SID, locUpdate))

		for friend in self.factory.friendsList:
			reactor.connectTCP('localhost', PORTS[friend], ProxyClientFactory(locUpdate))
			logging.info("Location update sent from {0} to {1}".format(self.factory.SID, friend))


	def reply(self, CID):
		locUpdate = self.createLocationUpdate(CID)
		logging.info("{0}'s response: {1}".format(self.factory.SID, locUpdate))
		self.transport.write(locUpdate + "\n")

	def logClient(self, CID):
		if CID in self.factory.clients:
			logging.info("Updated existing client: {0}".format(CID))
		else:
			logging.info("Added new client: {0}".format(CID))

		
class ProxyServerFactory(protocol.ServerFactory):
	def __init__(self, SID):
		self.SID = SID
		# SID -> Port No
		self.friendsList = FLIST[self.SID]
		self.clients = {}
		self.numConnections = 0
		filename = self.SID + "_" + re.sub(r'[:T]', '_', datetime.datetime.utcnow().isoformat().split('.')[0]) + ".log"
		logging.basicConfig(filename = filename, level=logging.DEBUG)
		logging.info("{0}:{1} server started".format(self.SID, PORTS[self.SID]))

	def buildProtocol(self, addr):
		return ProxyServer(self)

	def stopFactory(self):
		logging.info("{0} server shutdown".format(self.SID))


class ProxyClient(LineReceiver):
	def __init__(self, factory):
		self.factory = factory

	def connectionMade(self):
		self.sendLine(self.factory.message)
		self.transport.loseConnection()


class ProxyClientFactory(protocol.ClientFactory):
	def __init__(self, message):
		self.message = message

	def buildProtocol(self, addr):
		return ProxyClient(self)


def main():
	if len(sys.argv) != 2:
		print "Error: incorrect number of arguments"
		exit()

	reactor.listenTCP(PORTS[sys.argv[1]], ProxyServerFactory(sys.argv[1]))
	reactor.run()


if __name__ == '__main__':
	main()

