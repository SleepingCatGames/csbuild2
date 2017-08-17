# Copyright (C) 2017 Jaedyn K. Draper
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
.. module:: sitecustomize
	:synopsis: Hacky stuff for getting pycharm test runners to work

.. moduleauthor:: Jaedyn K. Draper
"""

from __future__ import unicode_literals, division, print_function

import os
import sys

# Copied from csbuild._utils because we can't import that before we set environ, and we need this to do that
if sys.version_info[0] >= 3:
	def PlatformString(inputStr):
		"""
		In the presence of unicode_literals, get an object that is type str in both python2 and python3.
		:return: str representation of inputStr
		:rtype: str
		"""
		if isinstance(inputStr, str):
			return inputStr
		return inputStr.decode("UTF-8")
else:
	def PlatformString(inputStr):
		"""
		In the presence of unicode_literals, get an object that is type str in both python2 and python3.
		:return: str representation of inputStr
		:rtype: str
		"""
		if isinstance(inputStr, str):
			return inputStr
		return inputStr.encode("UTF-8")

edit_done = False


def PathHook(_):
	"""
	Hacks around some stuff to make sure things are properly set up when running with jetbrains test runner
	instead of run_unit_tests.py
	"""
	global edit_done
	if edit_done:
		raise ImportError
	try:
		argv = sys.argv
	except AttributeError:
		pass
	else:
		edit_done = True
		if argv[0].endswith('_jb_unittest_runner.py'):
			import signal
			import time

			def _exitsig(sig, _):
				if sig == signal.SIGINT:
					log.Error("Keyboard interrupt received. Aborting test run.")
				else:
					log.Error("Received terminate signal. Aborting test run.")
				os._exit(sig)  # pylint: disable=protected-access


			signal.signal(signal.SIGINT, _exitsig)
			signal.signal(signal.SIGTERM, _exitsig)

			os.environ[PlatformString("CSBUILD_RUNNING_THROUGH_PYTHON_UNITTEST")] = PlatformString("1")
			os.environ[PlatformString("CSBUILD_NO_AUTO_RUN")] = PlatformString("1")
			sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
			os.environ[PlatformString("PYTHONPATH")] = os.pathsep.join(sys.path)
			os.chdir(os.path.dirname(os.path.abspath(__file__)))

			sys.modules['__main__'].__file__ = ''

			from csbuild import log
			from csbuild._utils import shared_globals, terminfo

			shared_globals.startTime = time.time()

			shared_globals.colorSupported = terminfo.TermInfo.SupportsColor()
			shared_globals.showCommands = True
	raise ImportError # let the real import machinery do its work

sys.path_hooks[:0] = [PathHook]
