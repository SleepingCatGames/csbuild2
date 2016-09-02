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
.. module:: make
	:synopsis: Makefile for this test

.. moduleauthor:: Jaedyn K. Draper
"""

from __future__ import unicode_literals, division, print_function

import csbuild
from csbuild.toolchain import Tool
import os

class AddDoubles(Tool):
	"""
	Simple base class
	"""
	supportedArchitectures={"foo", "bar"}

class Doubler(AddDoubles):
	"""
	Simple tool that opens a file, doubles its contents numerically, and writes a new file.
	"""
	inputFiles = {".first"}

	outputFiles = {".second"}

	def Run(self, project, inputFile):
		with open(inputFile.filename, "r") as f:
			value = int(f.read())
		value *= 2
		outFile = os.path.join(project.intermediateDir, os.path.splitext(os.path.basename(inputFile.filename))[0] + ".second")
		with open(outFile, "w") as f:
			f.write(str(value))
		return outFile

class Adder(AddDoubles):
	"""
	Simple tool that opens multiple doubled files and adds their contents together numerically, outputting a final file.
	"""
	inputGroups = {".second"}
	outputFiles = {".third"}

	def RunGroup(self, project, inputFiles):
		value = 0
		for inputFile in inputFiles:
			with open(inputFile.filename, "r") as f:
				value += int(f.read())
		outFile = os.path.join(project.outputDir, project.outputName + ".third")
		with open(outFile, "w") as f:
			f.write(str(value))
		return outFile

csbuild.RegisterToolchain("AddDoubles", "foo", Doubler, Adder)
csbuild.RegisterToolchain("AddDoubles2", "foo", Doubler, Adder)
csbuild.RegisterToolchain("AddDoubles3", "foo", Doubler, Adder)
csbuild.RegisterToolchain("AddDoubles4", "foo", Doubler, Adder)

csbuild.RegisterToolchainGroup("FirstTwo", "AddDoubles", "AddDoubles2")
csbuild.RegisterToolchainGroup("MiddleTwo", "AddDoubles2", "AddDoubles3")
csbuild.RegisterToolchainGroup("LastTwo", "AddDoubles3", "AddDoubles4")

csbuild.SetDefaultToolchain("AddDoubles")

with csbuild.Project("TestProject", "."):
	with csbuild.MultiContext(csbuild.ToolchainGroup("FirstTwo", "MiddleTwo"), csbuild.Target("debug"), csbuild.Architecture("foo")):
		csbuild.SetIntermediateDirectory("intermediate/FirstThree/{targetName}/{architectureName}/{toolchainName}")

	with csbuild.MultiContext(csbuild.ToolchainGroup("MiddleTwo", "LastTwo"), csbuild.Target("release"), csbuild.Architecture("bar")):
		csbuild.SetOutputDirectory("out/LastThree/{targetName}/{architectureName}/{toolchainName}")

	with csbuild.MultiContext(csbuild.Toolchain("AddDoubles"), csbuild.Architecture("foo")):
		csbuild.SetOutput("{architectureName}Foo", csbuild.ProjectType.Application)

	csbuild.SetOutput("Foo", csbuild.ProjectType.Application)
