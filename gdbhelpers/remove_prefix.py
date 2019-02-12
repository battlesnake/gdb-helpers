import gdb
from gdb.FrameDecorator import FrameDecorator
import re

prefix = [
	"Tests",
	"oc::mosaic",
	"oc",
	"std"
]

class SymbolWrapper(object):
	def __init__(self, frame, symval):
		self.symval = symval
		self.frame = frame

	def value(self):
		value = self.symval.value()
		if value != None:
			return value
		sym = self.symval.symbol()
		return sym.value(self.frame)

	def symbol(self):
		return self.symval.symbol()

class RemovePrefixDecorator(FrameDecorator):
	def __init__(self, fobj):
		super(RemovePrefixDecorator, self).__init__(fobj)
		self._fobj = fobj

	def function(self):
		name = self._fobj.function()
		name = re.sub(r'oc::mosaic::StatusCode<(\d+)>', '#\\1', name)
		for x in prefix:
			name = re.sub(r'\b' + x + '::', '', name)
		return name

	def wrap_symbol(self, symval):
		return SymbolWrapper(self.inferior_frame(), symval)

	def frame_args(self):
		args = self._fobj.frame_args()
		if args is None:
			return None
		return map(self.wrap_symbol, args)

class RemovePrefix(object):
	def __init__(self):
		self.name = "remove_prefix"
		self.priority = 1 # before colorizer
		self.enabled = True
		gdb.frame_filters[self.name] = self

	def filter(self, frame_iter):
		return map(RemovePrefixDecorator, frame_iter)

RemovePrefix()
