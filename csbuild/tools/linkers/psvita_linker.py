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
.. module:: psvita_linker
	:synopsis: Implementation of the PSVita linker tool.

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import csbuild
import os

from .linker_base import LinkerBase

from ..common.sony_tool_base import PsVitaBaseTool, SonyBaseTool

from ... import log
from ..._utils import ordered_set, response_file, shared_globals

class PsVitaLinker(PsVitaBaseTool, LinkerBase):
	"""
	PSVita linker tool implementation.
	"""
	supportedArchitectures = { "arm" }

	inputGroups = { ".o" }
	outputFiles = { ".self", ".a", ".suprx" }
	crossProjectDependencies = { ".a", ".suprx" }

	def __init__(self, projectSettings):
		PsVitaBaseTool.__init__(self, projectSettings)
		LinkerBase.__init__(self, projectSettings)


	####################################################################################################################
	### Methods implemented from base classes
	####################################################################################################################

	def _getOutputFiles(self, project):
		return tuple({ os.path.join(project.outputDir, project.outputName + self._getOutputExtension(project.projectType)) })

	def _getCommand(self, project, inputFiles):
		if project.projectType == csbuild.ProjectType.StaticLibrary:
			useResponseFile = False
			cmdExe = self._getArchiverName()
			cmd = ["rcs"] \
				+ self._getCustomLinkerArgs() \
				+ self._getOutputFileArgs(project) \
				+ self._getInputFileArgs(inputFiles)
		else:
			useResponseFile = True
			cmdExe = self._getLinkerName()
			cmd = self._getDefaultArgs(project) \
				+ self._getCustomLinkerArgs() \
				+ self._getOutputFileArgs(project) \
				+ self._getInputFileArgs(inputFiles) \
				+ self._getLibraryPathArgs() \
				+ self._getStartGroupArgs() \
				+ self._getLibraryArgs() \
				+ self._getEndGroupArgs()

		if useResponseFile:
			responseFile = response_file.ResponseFile(project, "linker-{}".format(project.outputName), cmd)

			if shared_globals.showCommands:
				log.Command("ResponseFile: {}\n\t{}".format(responseFile.filePath, responseFile.AsString()))

			cmd = [cmdExe, "@{}".format(responseFile.filePath)]

		else:
			cmd = [cmdExe] + cmd

		return cmd

	def _findLibraries(self, project, libs):
		targetLibPath = os.path.join(self._psVitaSdkPath, "target", "lib")
		allLibraryDirectories = [x for x in self._libraryDirectories] + [targetLibPath]

		return SonyBaseTool._commonFindLibraries(allLibraryDirectories, libs)

	def _getOutputExtension(self, projectType):
		outputExt = {
			csbuild.ProjectType.SharedLibrary: ".suprx",
			csbuild.ProjectType.StaticLibrary: ".a",
		}.get(projectType, ".self")

		return outputExt


	####################################################################################################################
	### Internal methods
	####################################################################################################################

	def _getLinkerName(self):
		binPath = os.path.join(self._psVitaSdkPath, "host_tools", "build", "bin")
		exeName = "psp2ld.exe"

		return os.path.join(binPath, exeName)

	def _getArchiverName(self):
		binPath = os.path.join(self._psVitaSdkPath, "host_tools", "build", "bin")
		exeName = "psp2snarl.exe"

		return os.path.join(binPath, exeName)

	def _getDefaultArgs(self, project):
		args = []
		if project.projectType == csbuild.ProjectType.SharedLibrary:
			args.extend([
				"-oformat=prx",
				"-prx-stub-output-dir={}".format(project.outputDir),
			])
		return args

	def _getCustomLinkerArgs(self):
		return sorted(ordered_set.OrderedSet(self._linkerFlags))

	def _getOutputFileArgs(self, project):
		outFile = "{}".format(self._getOutputFiles(project)[0])
		if project.projectType == csbuild.ProjectType.StaticLibrary:
			return [outFile]
		return ["-o", outFile]

	def _getInputFileArgs(self, inputFiles):
		return [f.filename for f in inputFiles]

	def _getLibraryPathArgs(self):
		args = ["-L{}".format(os.path.dirname(lib)) for lib in self._actualLibraryLocations.values()]
		return args

	def _getLibraryArgs(self):
		libNames = [os.path.basename(lib) for lib in self._actualLibraryLocations.values()]
		args = []

		for lib in libNames:
			if lib.startswith("lib"):
				lib = lib[3:]

			args.append("-l{}".format(lib))

		return args

	def _getStartGroupArgs(self):
		return ["--start-group"]

	def _getEndGroupArgs(self):
		return ["--end-group"]
