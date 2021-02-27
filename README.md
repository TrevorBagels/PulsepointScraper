# PulsepointScraper
Get notifications about certain medical emergencies at custom locations (highly configurable)

## Installation
1. Clone the repository `git clone https://github.com/TrevorBagels/PulsepointScraper.git`
2. Navigate to the new directory `cd PulsepointScraper`
3. Install requirements `pip3 install -r requirements.txt`
4. Make sure to configure before using!
#### Additional installation steps (linux)
You may have to install chromedriver for things to work `sudo apt install chromium-chromedriver`. Sudo may or may not be necessary.

## Configuration
Open config.json to start doing some configuration. You'll need to fill out the API keys for google maps and pushover, or things might not work properly. Everything else should work, but configuring the program is highly recommended if you intend to actually use it. Click [here](https://github.com/TrevorBagels/PulsepointScraper/wiki/Configuration) for more info on configuration. 

## Usage
Simply run `python3 main.py` and everything should work.

**This has not yet been tested for windows.**

**Linux might have some problems, but in theory, it should work.**
