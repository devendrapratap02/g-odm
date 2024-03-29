from typing import TYPE_CHECKING, Callable

import gspread
from enum import Enum

from .exceptions import FieldException, ModelItemException
from .iterator import GIterator

if TYPE_CHECKING:
	from .field import Field
	from .model import GModel

class LoadPolicy(Enum):
    INIT = "init"
    LAZY = "lazy"

class GModelManager(object):

	def __init__(self, model: "GModel", setup_attrs:Callable):
		model_meta = getattr(model, "Meta")
		self.load_policy = getattr(model_meta, "load_policy")
		self.model = model
		self.setup = False
		self.__setup_attrs = setup_attrs
  
		print(f"load_policy: {self.load_policy}")

		if self.load_policy == LoadPolicy.INIT:
			self._setup_attrs()

	def _setup_attrs(self, reload = False):
		if not self.setup or reload:
			self.__setup_attrs()
			self.setup = True

	def _get_header_index(self):
		class_meta = getattr(self.model, "Meta")
		return getattr(class_meta, "header_index")

	def _filter_data_list(self, **kwargs):
		header_index = self._get_header_index()
		all_data: gspread.Worksheet = getattr(self.model, "_data")
		headers: list = getattr(self.model, "_headers")
		meta:dict[str, "Field"] = getattr(self.model, "_meta")

		filter_data_list = []

		for key, val in list(kwargs.items()):
			if "__" in key:
				field_key, operator = key.split("__")
			else:
				field_key, operator = key, "eq"
			filter_data_list = []
			field:Field = meta.get(field_key)
			key_name = getattr(field, "_meta", {}).get("name")
			local_index = headers.index(key_name) + 1

			godm_column_values = all_data.col_values(local_index)

			for index, column_value in enumerate(godm_column_values[header_index:]):
				index += header_index
				if field.match_value(val, column_value, operator):
					filter_data_list.append(index + 1)

		return filter_data_list

	def _get_data_from_id(self, row_index):
		all_data = getattr(self.model, "_data")
		headers = getattr(self.model, "_headers")
		meta = getattr(self.model, "_meta")

		data_keys = dict()
		data_index = dict()
		row_data = all_data.row_values(row_index)
		for index in range(len(headers)):
			data_keys[index] = row_data[index]
			data_index[headers[index]] = row_data[index]

		data = {**data_keys, **data_index}
		errors = dict()
		fields = dict()
		for field, field_obj in list(meta.items()):
			field_val = None
			try:
				field_val = field_obj.get_value(data)
			except FieldException as ex:
				errors.setdefault(field, str(ex))
			# TODO avoid using this Exception catch
			except Exception as ex:
				errors.setdefault(field, str(ex))

			fields.setdefault(field, field_val)

		return {
			"id": row_index + 1,
			"data": data,
			"errors": errors,
			"fields": fields
		}

	def reload_model(self):
		self._setup_attrs(reload=True)

	def initialise_model(self):
		if self.load_policy == LoadPolicy.LAZY:
			self._setup_attrs()

	def get(self, **kwargs) -> "GModel":
		self._setup_attrs()

		filter_data_list = self._filter_data_list(**kwargs)

		if len(filter_data_list) == 0:
			raise ModelItemException(f"Unable to find Entity {self.model}, {kwargs}")

		model_data = self._get_data_from_id(filter_data_list[0])

		return self.model(model_data)

	def filter(self, **kwargs):
		self._setup_attrs()

		filter_data_list = self._filter_data_list(**kwargs)

		return GIterator(self, filter_data_list)

	def get_entity_from_id(self, row_index):
		self._setup_attrs()

		model_data = self._get_data_from_id(row_index)
		return self.model(model_data)
