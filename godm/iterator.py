from .exceptions import InvalidIndexException


class EntityIterator:

	def __init__(self, manager, filter_list):
		self._manager = manager
		self._filter_list = filter_list
		self._start_index = 0

	def __iter__(self):
		return self

	def __next__(self):
		if self._start_index < len(self._filter_list):
			entity_obj = self._manager.get_entity_from_id(self._filter_list[self._start_index])
			self._start_index += 1
			return entity_obj
		raise StopIteration

	def __getitem__(self, index):
		if type(index) is not int or index < 0 or index >= len(self._filter_list):
			raise InvalidIndexException()
		return self._manager.get_entity_from_id(self._filter_list[index])

	def first(self):
		return self.__getitem__(0)

	def last(self):
		return self.__getitem__(self.size() - 1)

	def nth(self, index):
		return self.__getitem__(index)

	def size(self):
		return len(self._filter_list)

	def reset(self):
		self._start_index = 0
