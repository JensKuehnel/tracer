# -*- coding: utf-8 -*-
# restart.py
# Defines RestartView
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

from tracer.views import View
from tracer.views.blocks import BlocksView


class RestartView(View):

	def render(self):

		def get_content(filter_result):
			return "\n".join(["	   " + daemon.name for daemon,result in self.args.daemons if result is filter_result])

		blocks = [
			{
				"title": "  * These daemons/services have been restarted",
				"content": get_content(True)
			},
			{
				"title": "  * These daemons/services failed to be restarted",
				"content": get_content(False)
			},
			{
				"title": "  * These daemons/services must be manually restarted",
				"content": get_content(None)
			}
		]

		view = BlocksView(self.out)
		view.assign("blocks", blocks)
		view.render()
