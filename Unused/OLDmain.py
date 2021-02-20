import os, time, json, googlemaps, math
os.system("pip3 install -U selenium")
os.system("pip3 install geopy")
import geopy
from geopy.distance import geodesic

#sudo easy_install selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
options = webdriver.ChromeOptions();
config = {}
gmaps = None
driver = None





#used to get displayed incidents. Used like 2 times in GetAllIncidents
def getIncidentList(allIncidents):
	incidentList = []
	for incident in allIncidents:
		ic = incident.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_container')]")
		if ic.is_displayed():
			timestamp = ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_timestamp')]/h5[contains(@class, 'pp_incident_item_timestamp_day')]").text + ", " + ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_timestamp')]/h5[contains(@class, 'pp_incident_item_timestamp_time')]").text
			icd = ic.find_element_by_xpath("./div[contains(@class, 'pp_incident_item_description')]")
			iType = icd.find_element_by_xpath("./h2[contains(@class, 'pp_incident_item_description_title')]").text
			iLocation = icd.find_element_by_xpath("./h3[contains(@class, 'pp_incident_item_description_location')]").text
			incidentReport = {"time" : timestamp, "type" : iType, "location" : iLocation}
			incidentList.append(incidentReport)
	return incidentList


def GetAllIncidents(agencyName):
	incidentList = []
	driver.get(f"https://web.pulsepoint.org")
	time.sleep(2)
	#press that settings button. nevermind, don't do this, it just closes the menu
	#driver.find_element_by_id("pp_wa_navbar_search_button").click()
	print("Test")
	#select the agency
	dropdownInput = driver.find_element_by_id("pp_wa_drawer_search_multiple_agencies").find_element_by_xpath("./div[contains(@class, 'dhxcombo_material')]/input[contains(@class, 'dhxcombo_input')]")#
	dropdownInput.click()
	dropdownInput.send_keys(agencyName)
	dropdownInput.send_keys(Keys.RETURN)
	time.sleep(1)
	driver.find_element_by_xpath("//button[contains(text(), 'Display Incidents')]").click()
	time.sleep(6)
	allIncidents = driver.find_elements_by_class_name("pp_incident_item_dd")
	print("Getting active incidents")
	incidentList += getIncidentList(allIncidents)
	#now select the recent incident list
	driver.find_element_by_xpath("//a[contains(@class, 'pp_wa_tabs_icon icon-recent')]").click()
	time.sleep(5)
	print("Getting recent incidents")
	incidentList += getIncidentList(allIncidents)


	print(len(allIncidents))

		
	return incidentList



def ValidateLocations(locations):
	failed = 0
	for l in locations:
		#check if the location has coords already. unless its a regex or match location, and has no radius.
		if "coords" not in l and "radius" in l: #no coords, but we have a radius. Try to assign coordinates to it.
			if "address" in l:
				try:
					l['coords'] = getCoords(l['address'])
				except:
					failed += 1
					print("Could not geocode address.")
			else:
				print(l['name'], "has a set radius but no way of finding its coords.")
				failed += 1
	print(f"Location validation complete. {failed} failed address(es)")
	print(locations)


def getIncidentImportance(i):
	importanceResults = {}
	for l in config["locations"]:
		#try checking distance
		if 'coords' in l:
			try:
				importanceResults['dist'] = geodesic(i['coords'], l['coords'])
			except:
				pass
	print(importanceResults)


def main():
	global driver
	global gmaps
	global config
	#load the JSON config file
	try:
		with open("config.json", "r") as f:
			config = json.loads(f.read())
	except:
		print("Error loading JSON!")
	#initialize google maps
	try:
		gmaps = googlemaps.Client(key=config["apiKey"])
	except:
		print("Couldn't initialize google maps. Probably an invallid API key. This might break things!")
	#runs chromedriver in headless mode so you don't have to burn your eyes looking at it.
	if config['headless']:
		options.add_argument('headless');
	#do some validating for the locations
	ValidateLocations(config["locations"])
	#open the webdriver
	driver = webdriver.Chrome(executable_path=os.getcwd()+"/chromedriver", options=options) #macos
	#driver = webdriver.Chrome(options=options) #linux
	while True:
		incidents = GetAllIncidents(config['agencies'][0]['name'])
		#go through each incident, compare the address to our list of addresses
		for i in incidents:
			try:
				i['coords'] = getCoords(i['location'])
			except:
				print("could not geocode ", i['location'])
			getIncidentImportance(i)
		break



	time.sleep(3)
	driver.quit()

if __name__ == "__main__":
	main()




