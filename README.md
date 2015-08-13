# AideBot
AideBot is a universal IRC help bot. When a user write (in public message or private message to the bot) a `!help` or a `!help topic`, the bot will respond with the appropriate line from a JSON file, where help data is stored.

The `!help` command itself can be customized and changed to something else by modifying `helpcommand` entry in the `conf/config.yml` file.

## How to Install
1. You need `Python3` and `pip3` installed on your system.

2. Run: `pip3 install -r requirements.txt`

3. Register the bot nick on the IRC network you want it to run on.

4. Copy `conf/config.example.yml` to `conf/config.yml` and change the configuration parameters according to your needs.

5. Finally, run: `python3 aidebot.py` and enjoy!

## How to add data to the bot

Open `data/data.json` with a text editor (or a JSON editor) and enter your help data there in JSON format. The file contains few sample data lines by default to demonstrate how simple topic/command help data and complex command help data should look like.
