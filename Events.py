
'''
The functions in the instance class of Events are called by main.py during certain events. 
If you'd like to change how the notifications work, without falling into the dirty mess of my code, this is the place to do it.
'''
from notifiers import get_notifier
class Events:
    def __init__(self, main):
        self.main = main #reference to the main class
        pass

    
    #called the moment a new incident is found
    def OnAnyIncidentFound(self, incident):
        print(f"Incident found at {incident['address']}.")
        pass
    #called when an agency is put into the queue.
    def OnAgencyEnterQueue(self, agency):
        print(f"Added agency {agency} to the queue.")
        pass
    #called after an incident is analyzed, prior to notifying you (if the program decides to notify you about this particular incident, that is.)
    def OnIncidentAnalyzed(self, incident):
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
