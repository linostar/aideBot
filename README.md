# AideBot
A Universal IRC Help Bot.

## How to Install
1. You need `Python3` and `pip3` installed on your system.

2. Run: `pip3 install -r requirements.txt`

3. Register the bot nick on the IRC network you want it to run on.

4. Copy `conf/config.example.yml` to `conf/config.yml` and change the configuration parameters according to your needs.

5. Finally, run: `python3 aidebot.py` and enjoy!

## How to add data to the bot

Open `data/data.json` with a text editor (or a JSON editor) and enter your data there in JSON format. The file contains few sample data lines by default to demonstrate how simple topic/command help data and complex command help data should look like.
