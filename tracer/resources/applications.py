#-*- coding: utf-8 -*-
# applications.py
# Manager for applications file
#
# Copyright (C) 2014 Jakub Kadlčík
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from __future__ import absolute_import

from bs4 import BeautifulSoup, element
from tracer.paths import DATA_DIR, USER_CONFIG_DIRS
from tracer.resources.exceptions import PathNotFound
from tracer.resources.lang import _
from os.path import dirname


class Applications:

	DEFINITIONS = map(lambda x: x + "/applications.xml", [DATA_DIR] + USER_CONFIG_DIRS)

	TYPES = {
		"DAEMON"       :  "daemon",
		"STATIC"       :  "static",
		"SESSION"      :  "session",
		"APPLICATION"  :  "application"
	}
	DEFAULT_TYPE = TYPES["APPLICATION"]
	_apps = None

	def __init__(self):
		pass

	@staticmethod
	def find(app_name):
		if not Applications._apps:
			Applications._load_definitions()

		for app in Applications._apps:
			if app.name == app_name:
				#app.setdefault('type', Applications.DEFAULT_TYPE)
				#app.setdefault('helper', Applications._helper(app))
				return app

		return Application({"name" : app_name, "type" : Applications.DEFAULT_TYPE, "helper" : None})

	@staticmethod
	def all():
		if not Applications._apps:
			Applications._load_definitions()

		return Applications._apps

	@staticmethod
	def _load_definitions():
		Applications._apps = []
		for file in Applications.DEFINITIONS:
			try: Applications._load(file)
			except PathNotFound as ex:
				if not dirname(file) in USER_CONFIG_DIRS:
					raise ex

	@staticmethod
	def _load(file):
		try:
			f = open(file)
			soup = BeautifulSoup(f.read())

			for child in soup.applications.children:
				if not isinstance(child, element.Tag):
					continue

				if child.name == "app":
					application = Application(child.attrs)
					if application in Applications._apps:
						i = Applications._apps.index(application)
						Applications._apps[i].update(application)
					else:
						application.setdefault('type', Applications.DEFAULT_TYPE)
						application.setdefault('helper', Applications._helper(application))
						Applications._apps.append(application)

				if child.name == "group":
					for app in child.findChildren():
						application = Application(app.attrs)
						application.update(child.attrs)
						if application in Applications._apps:
							i = Applications._apps.index(application)
							Applications._apps[i].update(application)
						else:
							application.setdefault('type', Applications.DEFAULT_TYPE)
							application.setdefault('helper', Applications._helper(application))
							Applications._apps.append(application)

			f.close()

		except IOError:
			raise PathNotFound('DATA_DIR')

	@staticmethod
	def _helper(app):
		if app.type == Applications.TYPES["DAEMON"]:
			return "service {0} restart".format(app.name)

		elif app.type == Applications.TYPES["STATIC"]:
			return _("static_restart")

		elif app.type == Applications.TYPES["SESSION"]:
			return _("session_restart")

		return None


class Application:

	"""
	Represent the application defined in `applications.xml`

	Attributes
	----------
	name : str
	type : str
		See `Applications.TYPES` for possible values
	helper : str
		Describes how to restart the applications
	"""

	_attributes = None

	def __init__(self, attributes_dict):
		self._attributes = attributes_dict

	def __eq__(self, other):
		return isinstance(other, Application) and self.name == other.name

	def __getattr__(self, item):
		return self._attributes[item]

	def __len__(self):
		return len(self._attributes)

	def __contains__(self, item):
		return item in self._attributes

	def __str__(self):
		return "<Application: " + self._attributes["name"] + ">"

	def __repr__(self):
		return self.__str__() + "\n"

	def setdefault(self, key, value):
		self._attributes.setdefault(key, value)

	def update(self, values):
		if isinstance(values, Application):
			values = values._attributes
		self._attributes.update(values)
