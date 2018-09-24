# -*- coding: utf-8 -*-
# restart.py
# Defines RestartController
#
# Copyright (C) 2016 Benjamin Roberts
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

from tracer.resources.tracer import Tracer
from tracer.resources.system import System
from tracer.resources.rules import Rules
from tracer.resources.applications import Applications
from tracer.resources.memory import dump_memory
from tracer.views.restart import RestartView
import sys
import os
import subprocess


class RestartController(object):

	# Dictionary of Applications to True (restarted), False (failed to restart) and None (no restart helper)
	restarted_daemons = None

	def __init__(self, args, call_helper=None):
		#TODO filter blacklisted packages from restart

		tracer = Tracer(
			System.package_manager(erased=args.erased),
			Rules,
			Applications,
			memory=dump_memory,
			erased=args.erased
		)

		daemons = tracer.trace_affected(user="root").filter_types([Applications.TYPES["DAEMON"]])

		if call_helper is None:
			call_helper = RestartController._call_helper
		else:
			call_helper = call_helper
		self.restarted_daemons = RestartController.restart_daemons(daemons, call_helper)

	def render(self):
		view = RestartView()
		view.assign("daemons", self.restarted_daemons)
		view.render()

		restart_failed = False in self.restarted_daemons.items()
		RestartController._exit(restart_failed=restart_failed)

	@staticmethod
	def restart_daemons(daemons, call_helper):
		"""
		Iterate through the list of daemons and restart them by calling the first available helper.
		Returns a dictionary of Applications to the result of their restart:
			+ True: restart succeeded
			+ False: restart failed
			+ None: not restarted (no handler)
		"""
		restarted_daemons = {}
		for daemon in daemons:
			helpers = daemon.helpers()

			if len(helpers) is 0:
				restarted_daemons[daemon] = None
			else:
				helper = helpers[0]
				if "sudo " in helper:
					helper = helper.replace("sudo ", "")

				restarted_daemons[daemon] = call_helper(helper)

		return restarted_daemons

	@staticmethod
	def _call_helper(helper):
		"""
		Call the helper string in order to restart a daemon.
		Exits if tracer is not running as root
		"""
		if os.geteuid() is not 0:
			RestartController._exit(no_root=True)

		with open(os.devnull, "w") as out:
			return subprocess.call(helper.split(" "), stdout=out, stderr=out) is 0

	@staticmethod
	def _exit(no_root=False, restart_failed=False):
		"""
		0 - Daemons restarted successfully
		201 - Not executed as root
		202 - Daemon restart failed
		"""
		if no_root:
			print("Must be root to restart daemons/services")
			sys.exit(201)
		elif restart_failed:
			print("Failed to restart all restartable daemons")
			sys.exit(202)
		else:
			sys.exit(0)





