#for parsing contacts from a csv file (macos) (remove the first line of the csv file if you get an error)
#done by selecting all contacts and dropping them into a Numbers spreadsheet, and then exporting to csv.
#eventually will be replaced by automatic importing of icloud contacts
locationDefault = ["Portland", "OR"] #because that's where I'm from
import csv
from os import stat
with open('../contacts.csv', newline='') as f:
	reader = csv.DictReader(f)
	locations = []
	for row in reader:
		if row["Address : home : Street"] == "":
			continue
		name = row["First name"].strip() + " " + row["Last name"].strip()
		street = row["Address : home : Street"].strip() 
		city = row["Address : home : City"].strip()
		state = row["Address : home : State"].strip()
		if city == "":
			city = locationDefault[0]
		if state == "":
			state = locationDefault[1]
		address = street + ", " + city +", " + state
		locations.append({"name": name, "address": address, "importance": 2, "radius": "150m"})
	print(locations)#you'll have to replace "'" with '"' after putting it into the json file, and that's pretty much it. 
