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
.. module:: java_compiler_base
	:synopsis: Basic class for Java compilers.

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import csbuild
import os
import subprocess
import threading

from abc import ABCMeta, abstractmethod

from ..common.java_tool_base import JavaToolBase

from ... import commands, log
from ..._utils import ordered_set
from ..._utils.decorators import MetaClass

def _ignore(_):
	pass

@MetaClass(ABCMeta)
class JavaCompilerBase(JavaToolBase):
	"""
	Base class for Java compilers.

	:param projectSettings: A read-only scoped view into the project settings dictionary
	:type projectSettings: toolchain.ReadOnlySettingsView
	"""
	inputGroups = { ".java" }
	outputFiles = { ".class" }

	_lock = threading.Lock()

	################################################################################
	### Initialization
	################################################################################

	def __init__(self, projectSettings):
		self._srcPaths = projectSettings.get("javaSrcPaths", ordered_set.OrderedSet())
		self._classPaths = projectSettings.get("javaClassPaths", ordered_set.OrderedSet())

		JavaToolBase.__init__(self, projectSettings)


	################################################################################
	### Static makefile methods
	################################################################################

	@staticmethod
	def AddJavaSourcePaths(*dirs):
		"""
		Add directories in which to search for Java source files.

		:param dirs: List of directories.
		:type dirs: str
		"""
		csbuild.currentPlan.UnionSet("javaSrcPaths", [os.path.abspath(directory) for directory in dirs])

	@staticmethod
	def AddJavaClassPaths(*dirs):
		"""
		Add directories in which to search for compiled Java classes.

		:param dirs: List of directories.
		:type dirs: str
		"""
		csbuild.currentPlan.UnionSet("javaClassPaths", [os.path.abspath(directory) for directory in dirs])


	################################################################################
	### Public API
	################################################################################

	def GetJavaSourcePaths(self):
		"""
		Get the list of Java source file directories.

		:return: Class directories
		:rtype: ordered_set.OrderedSet[str]
		"""
		return self._srcPaths

	def GetJavaClassPaths(self):
		"""
		Get the list of Java class directories.

		:return: Class directories
		:rtype: ordered_set.OrderedSet[str]
		"""
		return self._classPaths


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
	def _getOutputFiles(self, project, inputFiles, classRootPath):
		"""
		Get the set of output files that will be created from compiling a project.

		:param project: Project being compiled.
		:type project: project.Project

		:param inputFiles: Files being compiled.
		:type inputFiles: input_file.InputFile

		:return: Tuple of files that will be produced from compiling.
		:rtype: tuple[str]
		"""
		return tuple([""])

	@abstractmethod
	def _getCommand(self, project, inputFiles, classRootPath):
		"""
		Get the command to compile the provided set of files for the provided project

		:param project: Project being compiled.
		:type project: project.Project

		:param inputFiles: Files being compiled.
		:type inputFiles: input_file.InputFile

		:param classRootPath: Root path for the compiled class files.
		:type classRootPath: str

		:return: Command to execute, broken into a list, as would be provided to subprocess functions.
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

		:param inputProject: Project being built.
		:type inputProject: csbuild._build.project.Project

		:param inputFiles: List of files to build.
		:type inputFiles: list[input_file.InputFile]

		:return: Tuple of files created by the tool - all files must have an extension in the outputFiles list.
		:rtype: tuple[str]
		"""
		log.Build(
			"Compiling Java files for {}: [{}]",
			inputProject.outputName,
			", ".join(
				sorted([f.filename for f in inputFiles])
			)
		)

		# Create the class root intermediate directory.
		classRootPath = os.path.join(inputProject.intermediateDir, self._classRootDirName)
		if not os.access(classRootPath, os.F_OK):
			# Put a lock on the directory just in case something else happens to be trying to create it at the same time.
			with JavaCompilerBase._lock:
				if not os.access(classRootPath, os.F_OK):
					os.makedirs(classRootPath)

		returncode, _, _ = commands.Run(self._getCommand(inputProject, inputFiles, classRootPath), env=self._getEnv(inputProject))
		if returncode != 0:
			raise csbuild.BuildFailureException(inputProject, inputFiles)

		outputFiles = self._getOutputFiles(inputProject, inputFiles, classRootPath)

		# If the project generated no class files, flag that as an error.
		if not outputFiles:
			log.Error("Project {} generated no class files".format(inputProject.outputName))

		return outputFiles