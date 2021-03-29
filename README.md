### This is the old version of PulsepointScraper. Check out the new version, available [here](https://github.com/TrevorBagels/PulsepointScraperV2)



# PulsepointScraper (V1)
Get notifications about certain medical emergencies at custom locations (highly configurable)

**Works for MacOS, Linux, and Windows**


## Installation
1. Clone the repository `git clone https://github.com/TrevorBagels/PulsepointScraper.git`
2. Navigate to the new directory `cd PulsepointScraper`
3. Install requirements `pip3 install -r requirements.txt`
4. Make sure to configure before using!
#### Additional installation steps (linux)
* You may have to install chromedriver for things to work `sudo apt install chromium-chromedriver`. Sudo may or may not be necessary.
* Set `os` in `config.json` to `"linux"`
### Additional installation steps (windows)
* Download chromedriver from [here](https://chromedriver.chromium.org/downloads)
* Set `os` in `config.json` to "windows"


Unzip it and put chromedriver.exe into `PulsepointScraper/Drivers/`
## Configuration
Open config.json to start doing some configuration. You'll need to fill out the API keys for google maps and pushover, or things might not work properly. Everything else should work, but configuring the program is highly recommended if you intend to actually use it. Click [here](https://github.com/TrevorBagels/PulsepointScraper/wiki/Configuration) for more info on configuration. 

## Usage
Simply run `python3 main.py` and everything should work.
