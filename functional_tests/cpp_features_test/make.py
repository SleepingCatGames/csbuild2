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

from csbuild.tools.common.tool_traits import HasDebugLevel, HasOptimizationLevel

csbuild.SetOutputDirectory("out")

#TODO: Remove this once the issues with DebugLevel and OptimizationLevel not being usable through `csbuild` are fixed.
DebugLevel = HasDebugLevel.DebugLevel
OptimizationLevel = HasOptimizationLevel.OptimizationLevel

# pylint: disable=invalid-name,missing-docstring
def defineProjectSettings(projectName, debugLevel, optLevel, useStaticRuntime, useDebugRuntime, defines, undefines):
	#TODO: Disable the msvc compiler warning: D9025 : overriding '/DIMPLICIT_DEFINE' with '/UIMPLICIT_DEFINE'
	csbuild.SetDebugLevel(debugLevel)
	csbuild.SetOptimizationLevel(optLevel)
	csbuild.SetStaticRuntime(useStaticRuntime)
	csbuild.SetDebugRuntime(useDebugRuntime)
	csbuild.AddDefines("IMPLICIT_DEFINE", *defines)
	csbuild.AddUndefines(*undefines)
	csbuild.SetOutput(projectName, csbuild.ProjectType.Application)

with csbuild.Project("hello_world", "hello_world"):
	with csbuild.Target("nosymbols_noopt_dynamic_release"):
		defineProjectSettings(
			"hello_world",
			DebugLevel.Disabled,
			OptimizationLevel.Disabled,
			False,
			False,
          [],
          [],
		)
	with csbuild.Target("embeddedsymbols_sizeopt_static_release"):
		defineProjectSettings(
			"hello_world",
			DebugLevel.EmbeddedSymbols,
			OptimizationLevel.Size,
			True,
			False,
          ["EXPLICIT_DEFINE"],
          [],
		)
	with csbuild.Target("externalsymbols_speedopt_dynamic_debug"):
		defineProjectSettings(
			"hello_world",
			DebugLevel.ExternalSymbols,
			OptimizationLevel.Speed,
			False,
			True,
          [],
          ["IMPLICIT_DEFINE"],
		)
	with csbuild.Target("externalplussymbols_maxopt_static_debug"):
		defineProjectSettings(
			"hello_world",
			DebugLevel.ExternalSymbolsPlus,
			OptimizationLevel.Max,
			True,
			True,
			["EXPLICIT_DEFINE"],
			["IMPLICIT_DEFINE"],
		)
