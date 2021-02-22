class Utils:
	#this is what gets coords using google maps. You could get rid of all google maps stuff from main.py, and modify this to work with a different API if you'd like to use something else.
	def getCoords(address, gmaps):
		l = gmaps.geocode(address)[0]['geometry']['location']
		return [float(l["lat"]), float(l["lng"])]