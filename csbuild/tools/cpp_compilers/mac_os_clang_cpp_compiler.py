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
.. module:: mac_os_clang_cpp_compiler
	:synopsis: Clang compiler tool for C++ specifically targeting macOS.

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

from .clang_cpp_compiler import ClangCppCompiler

from ..common.apple_tool_base import MacOsToolBase

class MacOsClangCppCompiler(MacOsToolBase, ClangCppCompiler):
	"""
	Clang compiler for macOS implementation
	"""

	####################################################################################################################
	### Methods implemented from base classes
	####################################################################################################################

	def __init__(self, projectSettings):
		MacOsToolBase.__init__(self, projectSettings)
		ClangCppCompiler.__init__(self, projectSettings)

	def SetupForProject(self, project):
		MacOsToolBase.SetupForProject(self, project)
		ClangCppCompiler.SetupForProject(self, project)

	def _getDefaultArgs(self, project):
		baseArgs = ClangCppCompiler._getDefaultArgs(self, project)
		return baseArgs + [
			"-mmacosx-version-min={}".format(self.macOsVersionMin)
		]