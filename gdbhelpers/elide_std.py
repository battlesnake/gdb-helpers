import gdb
from gdb.FrameDecorator import FrameDecorator
import re
import os

stdstr = '[stdlib internal]'

def simplify_name(s):
	s = re.sub(r'\bstd::', '', s)
	s = re.sub(r'\bbasic_string<char, char_traits<char>, allocator<char> >', 'string', s)
	s = re.sub(r' allocator<[^>]+> >', ' >', s)
	if s.startswith('_'):
		return stdstr
	return s

class Decorator(FrameDecorator):
	def __init__(self, fobj):
		super(Decorator, self).__init__(fobj)
		self._fobj = fobj
		self._elided = []
		self._std = False

	def elided(self):
		return self._elided

	def function(self):
		return simplify_name(self._fobj.function()) if self._std else self._fobj.function()

	def frame_args(self):
		return None if self._std and self.function() == stdstr else self._fobj.frame_args()

	def filename(self):
		return os.path.basename(self._fobj.filename()) if self._std else self._fobj.filename()

class ElideStdFilter(object):
	def __init__(self):
		self.name = "elide_std"
		self.priority = 2
		self.enabled = True
		gdb.frame_filters[self.name] = self

	def filter(self, frame_iter):
		res = []
		last = None
		for frame in frame_iter:
			dec = Decorator(frame)
			if dec.filename().startswith('/usr') and last:
				dec._std = True
				last._elided.append(dec)
			else:
				res.append(dec)
			last = dec
		return res

ElideStdFilter()
