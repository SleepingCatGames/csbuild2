# Copyright (C) 2016 Jaedyn K. Draper
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
.. module:: java_archiver_base
	:synopsis: Base class for Java archivers.

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import os
import csbuild

from abc import ABCMeta, abstractmethod

from ..common.java_tool_base import JavaToolBase

from ... import commands, log
from ..._utils import ordered_set
from ..._utils.decorators import MetaClass

def _ignore(_):
	pass

@MetaClass(ABCMeta)
class JavaArchiverBase(JavaToolBase):
	"""
	Base class for Java archivers.

	:param projectSettings: A read-only scoped view into the project settings dictionary
	:type projectSettings: toolchain.ReadOnlySettingsView
	"""
	inputGroups = { ".class" }
	outputFiles = { ".jar" }

	################################################################################
	### Initialization
	################################################################################

	def __init__(self, projectSettings):
		self._entryPointClass = projectSettings.get("javaEntryPointClass", "")

		JavaToolBase.__init__(self, projectSettings)


	################################################################################
	### Static makefile methods
	################################################################################

	@staticmethod
	def SetJavaEntryPointClass(cls):
		"""
		Set the entry point class for a Java application.

		:param cls: Entry point class in the form: <package>.<class_name>
		:type cls: str
		"""
		csbuild.currentPlan.SetValue("javaEntryPointClass", cls)


	################################################################################
	### Public API
	################################################################################

	def GetJavaEntryPointClass(self):
		"""
		Get the entry point class for the Java application.

		:return: Java application entry point class.
		:rtype: str
		"""
		return self._entryPointClass



	################################################################################
	### Methods that may be implemented by subclasses as needed
	################################################################################

	def _getEnv(self, project):
		_ignore(project)
		return None


	################################################################################
	### Abstract methods that need to be implemented by subclasses
	################################################################################

	@abstractmethod
	def _getOutputFiles(self, project):
		"""
		Get the set of output files that will be created from archiving a projects

		:param project: project being linked
		:type project: project.Project
		:return: tuple of files that will be produced from linking
		:rtype: tuple[str]
		"""
		return tuple([""])

	@abstractmethod
	def _getCommand(self, project, inputFiles):
		"""
		Get the command to link the provided set of files for the provided project

		:param project: Project to link
		:type project: project.Project
		:param inputFiles: files being linked
		:type inputFiles: input_file.InputFile
		:return: Command to execute, broken into a list, as would be provided to subrpocess functions
		:rtype: list
		"""
		return []


	################################################################################
	### Base class methods containing logic shared by all subclasses
	################################################################################

	def RunGroup(self, inputProject, inputFiles):
		"""
		Execute a group build step. Note that this method is run massively in parallel with other build steps.
		It is NOT thread-safe in ANY way. If you need to change shared state within this method, you MUST use a
		mutex.

		:param inputProject:
		:type inputProject: csbuild._build.project.Project
		:param inputFiles: List of files to build
		:type inputFiles: list[input_file.InputFile]
		:return: tuple of files created by the tool - all files must have an extension in the outputFiles list
		:rtype: tuple[str]
		"""
		log.Linker("Archiving {}.jar...", inputProject.outputName)

		returncode, _, _ = commands.Run(self._getCommand(inputProject, inputFiles), env=self._getEnv(inputProject))
		if returncode != 0:
			raise csbuild.BuildFailureException(inputProject, inputFiles)
		return self._getOutputFiles(inputProject)
