import re



def seperate_string_number(string):
    previous_character = string[0]
    groups = []
    newword = string[0]
    for x, i in enumerate(string[1:]):
        if i.isalpha() and previous_character.isalpha():
            newword += i
        elif (i.isnumeric() or i == ".") and (previous_character.isnumeric() or previous_character == "."):
            newword += i
        else:
            groups.append(newword)
            newword = i

        previous_character = i

        if x == len(string) - 2:
            groups.append(newword)
            newword = ''
    return groups

class Utils:
	#this is what gets coords using google maps. You could get rid of all google maps stuff from main.py, and modify this to work with a different API if you'd like to use something else.
	def getCoords(address, gmaps):
		l = gmaps.geocode(address)[0]['geometry']['location']
		return [float(l["lat"]), float(l["lng"])]

timeValuesSeconds = {"":1, "s": 1, "m": 60, "h": 60*60, "d": 60*60*24, "W": 60*60*24*7, "M": 60*60*24*7*30, "Y": 60*60*24*365}
measurementValuesMeters = {"":1, "me": 1, "m": 1, "km": 1000, "ft": 3.280839895, "mi": 1000 * 0.621371}
class Config:
	def parse_time(txt):
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * timeValuesSeconds[value[1]]

	def parse_measurement(txt): #returns meters
		txt = txt.replace(" ", "")
		value = seperate_string_number(txt)
		return float(value[0]) * measurementValuesMeters[value[1]]

	'''def parse_time(txt): #returns seconds
		txt = txt.replace(" ", "")
		value = re.split('(\d+)',txt)
		return float(value[1]) * timeValuesSeconds[value[2]]
	def parse_measurement(txt): #returns meters
		txt = txt.replace(" ", "")
		value = re.split('(\d+)',txt)
		return float(value[1]) * measurementValuesMeters[value[2]]'''
		

