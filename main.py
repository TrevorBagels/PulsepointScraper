import os, time, json, googlemaps, math, sys
from geopy.distance import geodesic
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PPSUtils import Utils, Config
import Events

class Main:
	def __init__(self):
		self.data = {"agencies" : [], "queue" : [], "lastIncidents" : [], "analyzed" : [], "locations" : [] }
		self.config = None
		self.gmaps = None
		self.driver = None
		self.options = webdriver.ChromeOptions()
		self.LoadConfig()
		self.SetupChromedriver()
		self.os = "mac"
		self.Events = Events.Events(self)
		#load the webpage
		self.driver.get("https://web.pulsepoint.org")
		while True:
			self.MainLoop()
			'''
			try:
				self.MainLoop()
			except Exception as e:
				print(e)
				print("error occured. restarting browser...")
				self.sleep(5)
				self.driver.quit()
				print("quit browser!")
				self.sleep(1)
				self.driver = None
				self.SetupChromedriver()
				self.driver.get("https://web.pulsepoint.org")
				self.sleep(3)
			'''
			self.sleep(3)
	
	def sleep(self, sTime):
		return time.sleep(sTime * self.config['speed'])
	def exit(self):
		self.driver.quit()
		sys.exit()

	def WaitForID(self, id, timeout="default", crash=True):
		if timeout == "default":
			timeout = self.config['timeout']
		try:
			elementPresent = EC.presence_of_element_located((By.ID, id))
			WebDriverWait(self.driver, timeout).until(elementPresent)
			return True
		except TimeoutException:
			if crash:
				print(f"Timed out waiting for element #{id}. Try setting your timeout value in the config to something larger, or submit an issue to the repository.")
				self.exit()
			
			return False
	
	def GetIncidentsShown(self, incidents):
		incidentList = []
		for incident in incidents:
			ic = incident.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_container')]")
			if ic.is_displayed():
				timestamp = ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_timestamp')]/h5[contains(@class, 'pp_incident_item_timestamp_day')]").text + ", " + ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_timestamp')]/h5[contains(@class, 'pp_incident_item_timestamp_time')]").text
				icd = ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_description')]")
				iType = icd.find_element_by_xpath("./h2[contains(@class, 'pp_incident_item_description_title')]").text
				iLocation = icd.find_element_by_xpath("./h3[contains(@class, 'pp_incident_item_description_location')]").text
				incidentReport = {"time" : timestamp, "type" : iType, "address" : iLocation}
				if self.incidentID(incidentReport) not in self.data['analyzed']:
					incidentList.append(incidentReport)
					self.Events.OnAnyIncidentFound(incidentReport)
		return incidentList

	def incidentID(self, incident):
		return f"{incident['time']}_{incident['address']}_{incident['type']}"
	def isIncidentImportant(self, incident): #todo: move to a seperate module.
		iid = self.incidentID(incident)
		if iid not in self.data['analyzed']:
			self.data['analyzed'].append(iid)
		else:
			return False
		#analyze it and determine if it seems important and worthy of notifying the user about.
		#coords and stuff
		incident["dists"] = {}
		incident['significantLocation'] = None #this will be the name of a location in config.locations if we need to notify the user about it.
		if self.gmaps != None:
			incident['coords'] = Utils.getCoords(incident['address'], self.gmaps)
			#now measure distance
			for l in self.config['locations']:
				if 'coords' in l:
					incident['dists'][l['name']] = geodesic(incident['coords'], l['coords'])
					if Config.parse_measurement(str(incident["dists"][l['name']])) <= l['radius']:#this incident has been declared important. Call the analysis finished event then return true.
						incident["significantLocation"] = l['name']
						self.Events.OnIncidentAnalyzed(incident)
						return True
		#now try doing match/regex options
		def removeChars(txt, chars=",./?><()+=-_~!#"):#makes it easier to match the strings by getting rid of unnecessary junk.
			newTxt = txt
			for x in chars:
				newTxt = newTxt.replace(x, "")
			return newTxt
		for l in self.config['locations']:
			if 'match' in l:
				matchString = removeChars(l['match'].lower()) #the monitored location matching string (if this is in the incident, then it's important)
				if matchString in removeChars(incident['address'].lower()):
					#deem it important
					incident["significantLocation"] = l['name']
					self.Events.OnIncidentAnalyzed(incident)
					return True
		
		self.Events.OnIncidentAnalyzed(incident)
		


	def MainLoop(self):
		#region queue setup
		self.data['queue'] = [] #reset the queue, then re-determine it.
		for a in self.data["agencies"]:
			if float(a["lastScanned"]) < time.time() - float(a["frequency"]):
				self.data["queue"].append(a['name'])
				self.Events.OnAgencyEnterQueue(a['name'])
				a['lastScanned'] = time.time()
		#endregion
		if len(self.data['queue']) == 0:
			return
		#wait until ready.
		self.WaitForID("pp_wa_drawer_search_multiple_agencies")

		#make sure side menu is open. It usually is open the first time you use the site, but closes once it caches cookies or something.
		if self.driver.find_element_by_id("pp_wa_drawer_search_multiple_agencies").is_displayed() == False:
			self.driver.find_element_by_id("pp_wa_navbar_search_button").click() #now it is visible, and we can go about our business
			self.sleep(3)

		#region try to clear any agencies that were previously selected
		try:
			self.driver.find_element_by_xpath("//button[contains(@class, 'updatable_list_clear_button enabled')]").click()
		except Exception as e:
			pass
		#endregion
		#region Select agencies
		dropdownInput = self.driver.find_element_by_id("pp_wa_drawer_search_multiple_agencies").find_element_by_xpath("./div[contains(@class, 'dhxcombo_material')]/input[contains(@class, 'dhxcombo_input')]")
		dropdownInput.click()
		
		#select the agencies from the queue
		for agency in self.data['queue']:
			self.sleep(.2)
			#clear the field because this website doesn't do that automatically
			if self.os == "mac":
				dropdownInput.send_keys(Keys.COMMAND + "a")
			else:
				dropdownInput.send_keys(Keys.LEFT_CONTROL + "a")
			dropdownInput.send_keys(Keys.DELETE)
			self.sleep(.15)
			dropdownInput.send_keys(agency)
			dropdownInput.send_keys(Keys.RETURN)
			self.sleep(.05)
		#endregion
		self.sleep(.1)
		#agencies selected, display the incidents
		self.driver.find_element_by_xpath("//button[contains(text(), 'Display Incidents')]").click()
		#great, now we begin our search.
		self.data["lastIncidents"] = []
		self.sleep(2) #wait for stuff to load
		allIncidents = self.driver.find_elements_by_class_name("pp_incident_item_dd")
		#search active incidents
		self.data["lastIncidents"] += self.GetIncidentsShown(allIncidents)
		#recent incidents (if turned on)
		if self.config['ignoreRecent'] == False and len(self.data['analyzed']) == 0: #don't ignore recent, and this is the first time doing a check.
			self.driver.find_element_by_xpath("//a[contains(@class, 'pp_wa_tabs_icon icon-recent')]").click()
			self.sleep(4)
			self.data["lastIncidents"] += self.GetIncidentsShown(allIncidents)
		print(len(self.data['lastIncidents']), "incidents found. Performing analysis now...")
		if self.config['skipAnalysis']: #used for testing selenium without making any api calls to google maps
			print("Skipping analysis!")
			return

		for i in self.data['lastIncidents']:
			important = self.isIncidentImportant(i)
			if important:
				self.Events.Notify(i, i['significantLocation'], Events.GetLocationByName(self, i['significantLocation'])['importance'])
		print("Analysis complete!")
			
			
			
			
		

	#region setup

	def LoadAgencies(self):
		#setup data.agencies
		for agency in self.config['agencies']:
			freq = Config.parse_time(self.config["scanInterval"])
			if "scanInterval" in agency:
				freq = Config.parse_time(agency["scanInterval"])
			a = {"lastScanned": 0, "frequency": freq, "name": agency["name"]}
			self.data['agencies'].append(a)
				

	def LoadConfig(self): #eventually will be replaced with a very advanced configuration loader that I have yet to program.
		def validateLocations(locations):
			failed = 0
			for l in locations:
				#check if the location has coords already. unless its a regex or match location, and has no radius.
				if "address" in l and "coords" not in l: #no coords, but we have an address. Try to assign coordinates to it.
					if "address" in l:
						try:
							l['coords'] = Utils.getCoords(l['address'], self.gmaps)
						except Exception as e:
							print(e)
							failed += 1
							print(f"Could not geocode address {l['address']}.")
				if "radius" not in l:
					l['radius'] = Config.parse_measurement(self.config['radiusDefault'])
				else:
					l['radius'] = Config.parse_measurement(l['radius'])
				if "importance" not in l:
					l['importance'] = 1
				
			print(f"Location validation complete. {failed} failed address(es)")
			#print(locations)

		try:
			with open("config.json", "r") as f:
				self.config = json.loads(f.read())
		except:
			print("Error loading JSON! This is YOUR fault! (use a json validator and figure out what's wrong)")
			exit()
		self.InitGMaps()
		validateLocations(self.config['locations'])
		self.LoadAgencies()
		print("Configuration loaded")



	def InitGMaps(self):
		try:
			self.gmaps = googlemaps.Client(key=self.config["apiKey"])
		except:
			print("Google maps API key is invallid.")

	def SetupChromedriver(self):
		if self.config['headless']:
			self.options.add_argument('headless')
		self.driver = webdriver.Chrome(executable_path=os.getcwd()+"/Chrome/chromedriver", options=self.options) #macos
		#self.driver = webdriver.Chrome(options=options) #linux
	#endregion

if __name__ == "__main__":
	Main()



