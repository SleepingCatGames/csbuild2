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
.. module:: msvc_cpp_compiler
	:synopsis: msvc compiler tool for C++

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import os

from .cpp_compiler_base import CppCompilerBase
from ..common.msvc_tool_base import MsvcToolBase
from ..common.tool_traits import HasDebugLevel, HasOptimizationLevel

DebugLevel = HasDebugLevel.DebugLevel
OptimizationLevel = HasOptimizationLevel.OptimizationLevel

class MsvcCppCompiler(MsvcToolBase, CppCompilerBase):
	"""
	MSVC compiler tool implementation.
	"""
	supportedPlatforms = {"Windows"}
	supportedArchitectures = {"x86", "x64"}
	outputFiles = {".obj"}


	####################################################################################################################
	### Methods implemented from base classes
	####################################################################################################################

	def __init__(self, projectSettings):
		MsvcToolBase.__init__(self, projectSettings)
		CppCompilerBase.__init__(self, projectSettings)

	def _getEnv(self, project):
		return self.vcvarsall.env

	def _getOutputFiles(self, project, inputFile):
		outputPath = os.path.join(project.GetIntermediateDirectory(inputFile), os.path.splitext(os.path.basename(inputFile.filename))[0])
		outputFiles = ["{}.obj".format(outputPath)]

		if self._debugLevel in [DebugLevel.ExternalSymbols, DebugLevel.ExternalSymbolsPlus]:
			outputFiles.append("{}.pdb".format(outputPath))
			if self._debugLevel == DebugLevel.ExternalSymbolsPlus:
				outputFiles.append("{}.idb".format(outputPath))

		return tuple(outputFiles)

	def _getCommand(self, project, inputFile, isCpp):
		compilerPath = os.path.join(self.vcvarsall.binPath, "cl.exe")
		extraFlags = self._cxxFlags if isCpp else self._cFlags
		cmd = [compilerPath]  \
			+ self._getDefaultArgs() \
			+ self._getPreprocessorArgs() \
			+ self._getDebugArgs() \
			+ self._getOptimizationArgs() \
			+ self._getRuntimeLinkageArgs() \
			+ self._getIncludeDirectoryArgs() \
			+ extraFlags \
			+ self._getOutputFileArgs(project, inputFile) \
			+ [inputFile.filename]
		return [arg for arg in cmd if arg]

	def SetupForProject(self, project):
		MsvcToolBase.SetupForProject(self, project)
		CppCompilerBase.SetupForProject(self, project)


	####################################################################################################################
	### Internal methods
	####################################################################################################################

	def _getDefaultArgs(self):
		args = ["/nologo", "/c", "/Oi", "/GS"]
		if self._optLevel == OptimizationLevel.Disabled:
			args.append("/RTC1")
		return args

	def _getDebugArgs(self):
		arg = {
			DebugLevel.EmbeddedSymbols: "/Z7",
			DebugLevel.ExternalSymbols: "/Zi",
			DebugLevel.ExternalSymbolsPlus: "/ZI",
		}
		return [arg.get(self._debugLevel, "")]

	def _getOptimizationArgs(self):
		arg = {
			OptimizationLevel.Size: "/O1",
			OptimizationLevel.Speed: "/O2",
			OptimizationLevel.Max: "/Ox",
		}
		return [arg.get(self._optLevel, "/Od")]

	def _getRuntimeLinkageArgs(self):
		arg = "/{}{}".format(
			"MT" if self._staticRuntime else "MD",
			"d" if self._debugRuntime else ""
		)
		return [arg]

	def _getPreprocessorArgs(self):
		defineArgs = ["/D{}".format(d) for d in self._defines]
		undefineArgs = ["/U{}".format(u) for u in self._undefines]
		return defineArgs + undefineArgs

	def _getIncludeDirectoryArgs(self):
		args = ["/I{}".format(directory) for directory in self._includeDirectories]
		return args

	def _getOutputFileArgs(self, project, inputFile):
		outputPath = os.path.join(project.GetIntermediateDirectory(inputFile), os.path.splitext(os.path.basename(inputFile.filename))[0])
		args = ["/Fo{}".format("{}.obj".format(outputPath))]

		if self._debugLevel in [DebugLevel.ExternalSymbols, DebugLevel.ExternalSymbolsPlus]:
			args.append("/Fd{}".format("{}.pdb".format(outputPath)))

		return args