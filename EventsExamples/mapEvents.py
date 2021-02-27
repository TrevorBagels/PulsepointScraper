
'''
This one creates a webmap of all the recent incidents
Note that this is an example of what you can do with the events class, and this requires changing some things for practical use

'''
import numpy as np
import pandas as pd
from notifiers import get_notifier
import folium
import haversine as hs
import json, datetime, random
#note that this code might be incompatible with match-based locations, but it can be easily patched by adding an if statement somewhere in this mess.

class Events:
    def __init__(self, main):
        self.savePath = "/Users/bagel/Library/Application Support/Übersicht/widgets/bagel.widget/"
        self.sw = [45.32616808642837, -122.99680708158327]
        self.ne = [45.62569517298938, -122.27091410482807]
        self.location = self.main.config['locations'][0]['coords'] #center point for the location
        self.logFileName = "Logs/" + str(datetime.datetime.now()).split(" ")[0] + "_" + str(random.randrange(1, 9999)) + ".log"
        self.main = main #reference to the main class
        self.incidents = []
        print(self.location)
        self.map = folium.Map(location=self.location, zoom_start=4, tiles="https://{s}.tile.jawg.io/jawg-matrix/{z}/{x}/{y}{r}.png?access-token=rZdfyevzxIdbsN9w6Vj7F3XIXkLO4IuXeksSMnFb8uByhftsBIHdSlCcpHVr16QR", attr="<a>somethin should go here</a>") #"https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        #these coords are the bottom left and top right points for the viewport
        self.drawLines = True
        self.main.sleep(3)
        
    def UpdateIncidentHTML(self):
        pass
    #called the moment a new incident is found
    def OnAnyIncidentFound(self, incident):
        print(f"Incident found at {incident['address']}.")
        pass
    #called when an agency is put into the queue.
    def OnAgencyEnterQueue(self, agency):
        print(f"Added agency {agency} to the queue.")
        pass
    def OnAnalysisStart(self):
        print(len(self.main.data['lastIncidents']), "incident(s) found. Performing analysis now...")
    #called after an incident is analyzed, prior to notifying you (if the program decides to notify you about this particular incident, that is.)
    def OnIncidentAnalyzed(self, incident):
        #determine marker icon
        incident['timeAnalyzed'] = str(datetime.datetime.now())
        self.incidents.append(incident)
        icon = "map-marker"
        icons = {
            "Medical Emergency": "heartbeat|blue",
            "Outside Fire": "fire|red",
            "Residential Fire": "home|red",
            "Vehicle Fire": "fire|red",
            "Illegal Fire": "fire|darkred",
            "Fire Alarm": " fire-extinguisher|red",
            "Interfacility Transfer":"bus",
            "Traffic Collision": "car|orange",
            "Odor Investigation": "|pink",
            "Hazardous Condition": "|pink",
            "Investigation": "question|darkgreen",
            "Lockout": "lock|darkblue",
            "Commercial Fire": "fire|red",
            "Carbon Monoxide": "smoke|gray",
            "Alarm": "alarm|darkblue",
            "Lift Assist": "plane|darkpurple",
            "Water Rescue": "tint|pink",
            "Public Service": "|cadetblue"
        }
        if incident['type'] in icons:
            icon = icons[incident['type']]
        
        if 'fire' in incident['type'].lower():
            icon = icons["Outside Fire"]
        color = "lightgreen"
        if len(icon.split("|")) == 2:
            a =  icon.split("|")
            color = a[1]
            icon = a[0]
        useIcon = folium.Icon(color=color, icon=icon, prefix='fa') #the icon to actually use
        #make a marker of this incident
        folium.Marker(icon=useIcon, location=incident['coords'], tooltip=incident['type'], popup=f'<p>{incident["time"]}<br>{incident["address"]}</p>').add_to(self.map)
        #draws a line to the nearest monitored location. looks pretty cool.
        if self.drawLines:
            p1 = incident['coords']
            closest = 0
            closestDist = 100000 #meters
            for l, i in zip(self.main.config['locations'], range(len(self.main.config['locations']))):
                if 'coords' in l:
                    dist = hs.haversine(l['coords'], incident['coords'])
                    if dist < closestDist:
                        closest = i
                        closestDist = dist
            points = [tuple(p1), tuple(self.main.config['locations'][closest]['coords'])]
            folium.PolyLine(points, color="red", weight=2.5, opacity=.3).add_to(self.map)
        pass

    def OnMainLoopEnd(self):#save the latest map
        self.map.fit_bounds([self.sw, self.ne])
        self.map.save(self.savePath + "map.html")
        self.main.sleep(1)
        #refresh the uberschit widget. commented out because most people probably don't use uberschit
        '''
        with open("/Users/bagel/Library/Application Support/Übersicht/widgets/bagel.widget/pulsepointmap.coffee", "r+") as f:
            f.write("")
        with open(self.logFileName, "w+") as f:
            f.write(json.dumps(self.incidents))
        '''
    def OnMainLoopStart(self):
        pass
    #currently sends a notification to pushover using the notifiers library
    def Notify(self, incident, location, importance):
        p = get_notifier("pushover")
        coords = "no coords found"
        locationAddress = "no address found"
        locationref = GetLocationByName(self.main, location)
        if "address" in locationref:
            locationAddress = locationref['address']
        if "coords" in incident:
            coords = str(incident['coords'])
        #MESAGE GOES HERE
        message = f"""{incident['type'].upper()} AT {location.upper()}
        Time: {incident['time']}
        Incident Address: {incident['address']} \t ({coords})
        Monitored location: {locationAddress}
        """
        p.notify(user=self.main.config["pushoverUser"], token=self.main.config['pushoverToken'], message=message)
        print("NOTIFICATION SENT")
        pass


def GetLocationByName(main, name):
    for x in main.config['locations']:
        if x['name'] == name:
            return x
    print(f'could not find location using name "{name}"')
