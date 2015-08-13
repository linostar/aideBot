#!/usr/bin/env python3

#    AideBot IRC help bot
#    Copyright (C) 2015  Linostar <linux.anas@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import re

import yaml
import irc.client
import irc.bot

from aidelib import data_processing, flood_control


class CustomConnection(irc.client.ServerConnection):
	def privmsg(self, target, text):
		flood_event = flood_control.FloodControl.get_event(1)
		flood_event.wait()
		super().privmsg(target, text)

	def notice(self, target, text):
		flood_event = flood_control.FloodControl.get_event(1)
		flood_event.wait()
		super().notice(target, text)


class CustomReactor(irc.client.Reactor):
	def server(self):
		c = CustomConnection(self)
		with self.mutex:
			self.connections.append(c)
		return c


class CustomSimpleIRCClient(irc.client.SimpleIRCClient):
	def __init__(self):
		self.reactor = CustomReactor()
		self.connection = self.reactor.server()
		self.dcc_connections = []
		self.reactor.add_global_handler("all_events", self._dispatcher, -10)
		self.reactor.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)


class CustomSingleServerIRCBot(irc.bot.SingleServerIRCBot, CustomSimpleIRCClient):
	def __init__(self, server_list, nickname, realname, reconnection_interval=60, **connect_params):
		irc.bot.SingleServerIRCBot.__init__(self, server_list, nickname, realname, reconnection_interval=60)


class AideBot(CustomSingleServerIRCBot):
	channel = ""

	def __init__(self, config_file):
		self.read_config(config_file)
		self.channel = self.config['channel']
		self.data = data_processing.Data()
		self.flood = flood_control.FloodControl()
		CustomSingleServerIRCBot.__init__(self, [(self.config['server'], self.config['port'])],
		self.config['nick'], self.config['realname'])

	def read_config(self, filename):
		if not os.path.exists(filename):
			print('Error: config.yml could not be found.')
			sys.exit(1)
		with open(filename, 'r') as config_fd:
			self.config = yaml.load(config_fd)

	def on_welcome(self, c, e):
		if self.config['nspass']:
			self.connection.privmsg("nickserv", "identify {}".format(self.config['nspass']))
		c.join(self.channel)


def main():
	print("AideBot is running. To stop the bot, press Ctrl+C.")
	bot = AideBot("conf/config.yml")
	bot.start()

if __name__ == "__main__":
	main()
