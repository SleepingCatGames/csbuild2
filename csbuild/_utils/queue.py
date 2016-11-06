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
.. module:: queue
	:synopsis: Lock-free queue

.. moduleauthor:: Jaedyn K. Draper
"""

from __future__ import unicode_literals, division, print_function

import threading
from collections import deque

class Queue(object):
	"""
	Specialized version of queue.Queue tailored to a smaller feature set to reduce unnecessary locking and contention
	"""
	def __init__(self):
		self._deque = deque()
		self._lock = threading.Lock()
		self._condition = threading.Condition(self._lock)

	def Put(self, item):
		"""
		Put an item into the queue
		:param item: whatever
		:type item: any
		"""
		with self._lock:
			self._deque.append(item)
			self._condition.notify()

	def Get(self):
		"""
		Get an item out of the queue
		:raises IndexError: If nothing is in the queue
		:return: Whatever was put into the queue
		:rtype: any
		"""
		return self._deque.popleft()

	def GetBlocking(self):
		"""
		Get an item out of the queue, blocking if there is nothing to get.
		:return: Whatever was put into the queue
		:rtype: any
		"""
		while True:
			with self._lock:
				try:
					return self._deque.popleft()
				except IndexError:
					pass
				self._condition.wait()
