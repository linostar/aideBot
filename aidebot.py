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
	def privmsg(self, target, text, priority=1):
		flood_event = flood_control.FloodControl.get_event(priority)
		flood_event.wait()
		super().privmsg(target, text)

	def notice(self, target, text, priority=1):
		flood_event = flood_control.FloodControl.get_event(priority)
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

	def on_pubmsg(self, c, e):
		detected = re.match(r"\!(help(\s+.+)?)", e.arguments[0], re.IGNORECASE)
		if detected:
			if not detected.group(2):
				command = ""
			else:
				command = detected.group(2).strip().lower()
			self.execute(e.source.nick, command)

	def on_privmsg(self, c, e):
		detected = re.match(r"\!(help(\s+.+)?)", e.arguments[0], re.IGNORECASE)
		if detected:
			if not detected.group(2):
				command = ""
			else:
				command = detected.group(2).strip().lower()
			self.execute(e.source.nick, command)

	def execute(self, source, command):
		if not command:
			self.connection.privmsg(source, "Help is available for the following topics/commands:")
			self.connection.privmsg(source, ", ".join(sorted(self.data.topics.keys())))
			return
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command
			args = ""
		else:
			cmd = command[0:first_space]
			args = command[first_space:].lstrip()
		if cmd in self.data.topics:
			if isinstance(self.data.topics[cmd], dict):
				if not args and args not in self.data.topics[cmd]:
					subs = [cmd + " " + s for s in self.data.topics[cmd].keys()]
					self.connection.notice(source, "There is only help available for " +
						"\x02{}\x02.".format(", ".join(subs)))
				elif not args and args in self.data.topics[cmd] and len(self.data.topics[cmd]) > 1:
					subs = [cmd + " " + s for s in self.data.topics[cmd].keys() if s]
					self.connection.privmsg(source, self.data.topics[cmd][args])
					self.connection.privmsg(source, "There is also help available for " +
						"\x02{}\x02.".format(", ".join(subs)))
				elif args in self.data.topics[cmd]:
					self.connection.privmsg(source, self.data.topics[cmd][args])
				else:
					self.connection.notice(source, ("There is no help available for \x02{}" +
						" {}\x02.").format(cmd, args))
			else:
				self.connection.privmsg(source, self.data.topics[cmd])
		else:
			self.connection.notice(source, "There is no help available for \x02{}\x02."
				.format(cmd))


def main():
	print("AideBot is running. To stop the bot, press Ctrl+C.")
	bot = AideBot("conf/config.yml")
	bot.start()

if __name__ == "__main__":
	main()
