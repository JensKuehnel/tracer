from .__meta__ import *
from tracer.controllers.restart import RestartController


class TestRestart(unittest.TestCase):

	def test_no_sudo(self):
		"""
		RestartController requires root to run, no need to append executed helpers with sudo
		"""
		daemons = [
			MockDaemon("sudo_restart", ["sudo service restart daemon"]),
			MockDaemon("sudoless_restart", ["service restart daemon"]),
			MockDaemon("daemon_containing_sudo", ["sudo service restart sudodaemon"])
		]

		# Assert that the call_helper never has to call sudo
		def mock_call_helper(helper):
			self.assertFalse(helper.startswith("sudo "))

		RestartController.restart_daemons(daemons, call_helper=mock_call_helper)

	def test_restart(self):
		"""
		Test the RestartController.restart_daemons method
		"""
		daemons = [
			MockDaemon("should_succeed_one", ["sudo should_succeed"]),
			MockDaemon("should_succeed_two", ["sudo should_succeed",
											  "sudo second_unused_helper"]),
			MockDaemon("should_fail", ["sudo fail"]),
			MockDaemon("unrestartable", [])
		]

		# Emulate service restarting
		def mock_call_helper(helper):
			return helper == "should_succeed"

		# Restart each of the daemons and get the result dict
		restarted_daemons = RestartController.restart_daemons(daemons, call_helper=mock_call_helper)

		# Test that each daemon has a result
		self.assertEquals(len(daemons), len(restarted_daemons))

		# Test that each daemon was correctly reported as restarted, failed or un-restartabe
		for daemon, result in restarted_daemons.items():
			if "succeed" in daemon.name():
				self.assertTrue(result)
			elif "fail" in daemon.name():
				self.assertFalse(result)
			else:
				self.assertTrue(result is None)


class MockDaemon(object):
	_name = None
	_helpers = []

	def __init__(self, name, helpers):
		self._name = name
		self._helpers = helpers

	def name(self):
		return self._name

	def helpers(self):
		return self._helpers