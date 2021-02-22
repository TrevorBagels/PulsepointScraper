from PPSUtils import Utils
from geopy.distance import geodesic

class ImportanceChecker:
	def __init__(self, main):
		self.main = main
		self.checks = [TextBasedImportance, LocationbasedImportance]
	#this is what's used to determine incident importance
	def IsIncidentImportant(self, incident):
		iid = self.main.incidentID(incident)
		if iid not in self.main.data['analyzed']:
			self.main.data['analyzed'].append(iid)
		else:
			return False
		incident['significantLocation'] = None #this will be the name of a location in config.locations if we need to notify the user about it.
		#use each filter to perform analysis
		for check in self.checks:
			checkInstance = check(self.main, incident)
			for location in self.main.config['locations']:
				important = checkInstance.check(location)
				if important:
					incident["significantLocation"] = location['name']
					self.main.Events.OnIncidentAnalyzed(incident)
					return True
		self.main.Events.OnIncidentAnalyzed(incident)
		return False			
		
		
class TextBasedImportance:
	def __init__(self, main, incident):
		self.main = main
		self.incident = incident
	
	def check(self, l):
		if 'match' in l:
			matchString = self.removeChars(l['match'].lower()) #the monitored location matching string (if this is in the incident, then it's important)
			if matchString in self.removeChars(self.incident['address'].lower()): #there was a text match, this is important
				return True
		return False
	#makes it easier to match the strings by getting rid of unnecessary junk.
	def removeChars(self, txt, chars=",./?><()+=-_~!#"):
			newTxt = txt
			for x in chars:
				newTxt = newTxt.replace(x, "")
			return newTxt


class LocationbasedImportance:
	def __init__(self, main, incident):
		self.main = main
		self.incident = incident
		incident["dists"] = {}
		if self.main.gmaps != None:
			incident['coords'] = Utils.getCoords(incident['address'], main.gmaps)
	def check(self, l):#l = the location being checked. this should return true/false
		if self.main.gmaps == None: #no google maps, doing a location check is useless
			return False
		if 'coords' in l:
			self.incident['dists'][l['name']] = geodesic(self.incident['coords'], l['coords']).meters
			if self.incident["dists"][l['name']] <= l['radius']:#this incident has been declared important. Call the analysis finished event then return true.
				self.incident["significantLocation"] = l['name']
				return True
		return False