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
.. module:: tests
	:synopsis: Basic test of tools to make sure simple tools chain together properly

.. moduleauthor:: Jaedyn K. Draper
"""

from __future__ import unicode_literals, division, print_function

from csbuild._testing.functional_test import FunctionalTest

class BasicToolTest(FunctionalTest):
	"""Basic tool test"""
	# pylint: disable=invalid-name
	def test(self):
		"""Basic tool test"""
		self.assertMakeSucceeds("-v")
		for i in range(1, 11):
			self.assertFileContents("./intermediate/{}.second".format(i), str(i*2))
		self.assertFileContents("./out/Foo.third", "110")

	def testRebuild(self):
		"""Test that --rebuild works"""
		self.assertMakeSucceeds("-v")
		self.assertMakeSucceeds("--rebuild", "-v")
		for i in range(1, 11):
			self.assertFileContents("./intermediate/{}.second".format(i), str(i*2))
		self.assertFileContents("./out/Foo.third", "110")
