# Copyright (C) 2013 Jaedyn K. Draper
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
.. module:: java_tool_base
	:synopsis: Abstract base class for Java tools.

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import csbuild
import os

from abc import ABCMeta

from ..._utils.decorators import MetaClass
from ...toolchain import Tool


@MetaClass(ABCMeta)
class JavaToolBase(Tool):
	"""
	Parent class for all tools targetting Java applications.

	:param projectSettings: A read-only scoped view into the project settings dictionary
	:type projectSettings: toolchain.ReadOnlySettingsView
	"""
	def __init__(self, projectSettings):
		Tool.__init__(self, projectSettings)

		self._javaHomePath = projectSettings.get("javaHomePath", "")

		# When no Java home path is explicitly provided, attempt to get it from the environment.
		if not self._javaHomePath:
			self._javaHomePath = os.getenv("JAVA_HOME", "")

		assert self._javaHomePath, "Java home path not provided or set through the JAVA_HOME environment variable."
		assert os.access(self._javaHomePath, os.F_OK), "Java home path does not exist: {}".format(self._javaHomePath)


	####################################################################################################################
	### Methods implemented from base classes
	####################################################################################################################

	def SetupForProject(self, project):
		Tool.SetupForProject(self, project)


	################################################################################
	### Static makefile methods
	################################################################################

	@staticmethod
	def SetJavaHomePath(path):
		"""
		Sets the path to the Java home.

		:param path: Java home path.
		:type path: str
		"""
		csbuild.currentPlan.SetValue("javaHomePath", os.path.abspath(path))
