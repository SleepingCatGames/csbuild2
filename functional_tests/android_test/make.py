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

.. moduleauthor:: Brandon Bare
"""

from __future__ import unicode_literals, division, print_function

import csbuild
import os

# csbuild.SetAndroidNdkRootPath("/opt/google/android-ndk-r16b")
# csbuild.SetAndroidSdkRootPath("/home/bbare/dev/support/android-sdk")

csbuild.SetOutputDirectory("out")

with csbuild.Project("hello_world", "hello_world"):
	csbuild.SetAndroidTargetSdkVersion(26)
	csbuild.SetAndroidManifestFilePath(os.path.join("hello_world", "AndroidManifest.xml"))
	csbuild.UseDefaultAndroidNativeAppGlue(True)
	csbuild.SetSupportedToolchains("android-gcc")
	csbuild.SetOutput("hello_world", csbuild.ProjectType.Application)
