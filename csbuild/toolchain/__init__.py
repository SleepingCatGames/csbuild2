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
.. package:: toolchain
	:synopsis: General-purpose toolchain infrastructure

.. moduleauthor:: Jaedyn K. Draper
"""

from __future__ import unicode_literals, division, print_function

import os
from .._utils import memo
from .._build import input_file

_eliminatePylintAbstractMethodCheck = True

def _ignore(_):
	pass

class Tool(object):
	"""
	Tool base class. Derive from this class to provide a tool for use in building things.

	Tool constructor should take at least one argument, which will be the project settings dictionary.
	Values in this dictionary which pertain to the tool in question can ONLY be accessed from within that tool -
	they are scoped. Thus, these values should be pulled out of the settings dict and stored as instance
	variables on the tool itself, and the projectSettings dict itself should NOT be held onto -
	this will ensure child classes of a tool can access all the data they need.

	:param projectSettings: A read-only scoped view into the project settings dictionary
	:type projectSettings: toolchain.ReadOnlySettingsView
	"""

	#: List of file extensions to be passed to Run as individual inputs.
	#  Run() will be called once per file as soon as each file is available to build
	#  Example: A C++ compiler would take individual inputs of types {".c", ".cc", ".cxx", ".cpp"}
	#  An empty string indicates a file with no extension
	inputFiles = set()

	#: List of file extensions to be passed to Run as a group input.
	#  Run() will be called only once all tools that output this type have finished running
	#  and will be called only once on the entire group.
	#  Example: A C++ linker would take group inputs of types {".o"} or {".obj"} depending on the platform
	#  An empty string indicates a file with no extension
	inputGroups = set()

	#: List of dependencies that will prevent Run() from being called if they're still being created,
	#  even if they're not taken as inputs.
	#  Example: A C++ compiler might add dependencies of type {".pch"} or {".gch"} to wait on a precompile step
	#  An empty string indicates a file with no extension
	dependencies = set()

	#: The file extensions of files created by this toolchain
	#  Example: A C++ compiler would have output files of type {".o"} or {".obj"} depending on the platform
	#  Or a C++ linker would have output files of type {".exe", ".dll", ".lib"} or {"", ".so", ".a"}
	#  An empty string indicates a file with no extension
	outputFiles = set()

	#: Indicates what output files (if any) must completed on dependencies
	#  before this tool is run on this project. Example: A C++ linker might need all dependencies to finish
	#  generating files of type {".dll", ".lib"} or {".so", ".a"} before running itself. Any projects in the
	#  dependency chain that generate files of that type will prevent this tool from running until it no longer
	#  has any valid inputs for tools that will generate that output, and the outputs have all been generated.
	crossProjectDependencies = set()

	#: Set of supported architectures. If this toolchain supports all possible --architecture arguments,
	#  set this value to None. An empty set implies it supports no architectures and can never be run.
	supportedArchitectures = set()

	#: Set of supported platforms. If this toolchain supports all possible platforms,
	#  set this value to None. An empty set implies it supports no platforms and can never be run.
	supportedPlatforms = None

	#: Set this to a positive non-zero value to prevent this tool from being run in parallel.
	#  This is a global setting; multiple instances of this tool will not run concurrently, even for different projects
	maxParallel = 0

	#: If this is True, this tool will be the only one to act on the input files passed to it, and they will not
	#  go to any other tool. If an input file passed to a tool marked exclusive should go to another tool, it may
	#  be returned as an output from Run or RunGroup to forward it to the next tool. Exclusive tools for a given input
	#  extension will always run before other tools for that input extension regardless of order in the toolchain;
	#  if multiple tools in a toolchain are marked exclusive, the input files will only be passed to the first one;
	#  however, if it outputs the same file type, its outputs will be passed to the second exclusive one, whose outputs
	#  can be passed to the third, and so on; outputs from the last exclusive tool will be passed to all non-exclusive
	#  tools accepting that file type.
	exclusive = False

	_initialized = False

	def __init__(self, projectSettings):
		pass

	def SetupForProject(self, project):
		"""
		Run project setup, if any, before building the project, but after all dependencies have been resolved.

		:param project: project being set up
		:type project: csbuild._build.project.Project
		"""
		pass

	@staticmethod
	def __static_init__():
		assert not Tool._initialized
		Tool._initialized = True

	def Run(self, inputProject, inputFile):
		"""
		Execute a single build step. Note that this method is run massively in parallel with other build steps.
		It is NOT thread-safe in ANY way. If you need to change shared state within this method, you MUST use a
		mutex.

		:param inputProject: project being built
		:type inputProject: csbuild._build.project.Project
		:param inputFile: File to build
		:type inputFile: input_file.InputFile
		:return: tuple of files created by the tool - all files must have an extension in the outputFiles list
		:rtype: tuple[str]
		:raises NotImplementedError: if the subclass defines inputFiles and does not implement it
		"""
		_ignore(inputProject)
		_ignore(inputFile)
		if _eliminatePylintAbstractMethodCheck:
			raise NotImplementedError()
		return ""

	def RunGroup(self, inputProject, inputFiles):
		"""
		Execute a group build step. Note that this method is run massively in parallel with other build steps.
		It is NOT thread-safe in ANY way. If you need to change shared state within this method, you MUST use a
		mutex.

		:param inputProject: project being built
		:type inputProject: csbuild._build.project.Project
		:param inputFiles: List of files to build
		:type inputFiles: list[input_file.InputFile]
		:return: tuple of files created by the tool - all files must have an extension in the outputFiles list
		:rtype: tuple[str]
		:raises NotImplementedError: if the subclass defines inputGroups and does not implement it
		"""
		_ignore(inputProject)
		_ignore(inputFiles)
		if _eliminatePylintAbstractMethodCheck:
			raise NotImplementedError()
		return ""

class CompileChecker(object):
	"""
	Class to implement various components of checking whether a file should be recompiled.
	"""
	def __init__(self):
		self.memo = memo.Memo()

	def ShouldRecompile(self, fileValue, baselineValue):
		"""
		Given a condensed value from all the input files and their dependencies,
		check against the baseline to determine if a recompile should be performed.

		:param fileValue: The condensed value for the file
		:type fileValue: any
		:param baselineValue: The baseline retrieved earlier
		:type baselineValue: any
		:return: whether or not to recompile the file
		:rtype: bool
		"""
		return fileValue > baselineValue

	def CondenseRecompileChecks(self, values):
		"""
		Condense a list of values into a single value. For example, in the default, a list of modification
		timestamps gets condensed into the most recent modification date.

		:param values: The values collected from GetRecompileValue() for a list of dependencies
		:type values: list
		:return: The condensed value
		:rtype: any
		"""
		return max(values)

	def GetRecompileValue(self, buildProject, inputFile):
		"""
		Get a value to be used to compute recompilability. In the default implementation, this is a last modification date.

		:param buildProject: Project encapsulating the files being built
		:type buildProject: csbuild._build.project.Project
		:param inputFile: The file to compute the value for
		:type inputFile: input_file.InputFile
		:return: The value to be used to compute recompilability
		:rtype: any
		"""
		_ignore(buildProject)
		return os.path.getmtime(inputFile.filename)

	def GetDependencies(self, buildProject, inputFile):
		"""
		Get a list of dependencies for a file.

		:param buildProject: Project encapsulating the files being built
		:type buildProject: csbuild._build.project.Project
		:param inputFile: The file to check
		:type inputFile: input_file.InputFile
		:return: List of files to depend on
		:rtype: list[str]
		"""
		_ignore(inputFile)
		_ignore(buildProject)
		return []

	def GetRecompileBaseline(self, buildProject, inputFiles):
		"""
		Get the baseline recompile value, typically the value for the intended output of the file.
		For example, with timestamps for a c++ toolchain, this would be the value of the .o/.obj file
		for a given .cpp input.

		A return value of None forces a recompile.

		:param buildProject: Project encapsulating the files being built
		:type buildProject: csbuild._build.project.Project
		:param inputFiles: List of input files
		:type inputFiles: ordered_set.OrderedSet[input_file.InputFile]
		:return: A baseline recompile value, or None to force recompile
		:rtype: any
		"""
		lastFiles = buildProject.GetLastResult(inputFiles)
		if lastFiles is not None:
			return min(
				[
					self.GetRecompileValue(buildProject, input_file.InputFile(outputFile)) if os.access(outputFile, os.F_OK) else 0
					for outputFile in lastFiles
				]
			)
		return None

	def __deepcopy__(self, copyMemo):
		copyMemo[id(self)] = self
		return self
