import json
from datetime import datetime
from functools import update_wrapper, partial
from typing import Callable

from .exceptions import FieldException
from .transformers import transform_invalid_ref_to_none, transform_na_to_none, transform_tags_to_tags


class Field(object):
	class TransformDecorator(object):
		def __init__(self, decorated):
			update_wrapper(self, decorated)
			self.decorated = decorated

		def __call__(self, field_obj, headers):
			field_obj: Field = field_obj
			field_meta: dict = getattr(field_obj, "_meta")
			field_lookup_name = field_meta.get("name")
			field_value = headers.get(field_lookup_name)

			for transform in field_meta.get("pre_transform"):
				field_value = transform(field_value)

			headers.setdefault(f"{field_lookup_name}_transform", field_value)

			try:
				value = self.decorated(field_obj, headers)
			except Exception:
				raise
			else:
				for transform in field_meta.get("post_transform"):
					value = transform(value)

			return value

		def __get__(self, obj, obj_type):
			return partial(self.__call__, obj)

	def __init__(self, name: str = None, index: int = -1, allow_empty_or_null: bool = False, default_val: object = None,
	             pre_transform: list = None, post_transform: list = None, **others):

		if not pre_transform or type(pre_transform) is not list:
			pre_transform = []

		if not post_transform or type(post_transform) is not list:
			post_transform = []

		self._meta = dict({
			"name": name, "index": index, "allow_empty_or_null": allow_empty_or_null, "default_val": default_val,
			"pre_transform": [transform_invalid_ref_to_none, transform_na_to_none] + pre_transform,
			"post_transform": post_transform,
			**others
		})

	def get_value(self, data):
		transform_key = self._meta.get("name") + "_transform"
		non_transform = self._meta.get("name")
		if transform_key in data:
			return_value = data.get(transform_key)
		else:
			return_value = data.get(non_transform)

		return return_value

	def validate(self, headers):
		name = self._meta.get("name")
		index = self._meta.get("index")

		if isinstance(self, CustomField):
			to_value = self._meta.get("to_value")
			if not hasattr(to_value, "__call__"):
				raise FieldException("field was not callable")
			return

		field_checks = []
		if not name and not index:
			raise FieldException("No attributes are provided")
		if type(name) is not str:
			field_checks.append("name attr value is not string")
		if type(index) is not int:
			field_checks.append("index attr value is not int")

		if len(field_checks) == 2:
			raise FieldException(field_checks)

		# empty the field check list
		field_checks[:] = []
		if name and name in headers:
			index = headers.index(name)
		else:
			field_checks.append(f"name attribute [{name}] was not found in header list")

		if index in range(len(headers)):
			name = headers[index]
		else:
			field_checks.append(f"index attribute was out of range. [given: {index}], [header_size: {len(headers)}]")

		if len(field_checks) == 2:
			raise FieldException(field_checks)

		self._meta["name"] = name
		self._meta["index"] = index

	def __repr__(self):
		data = dict()
		for field_name, field_itself in self._meta.items():
			field_value = field_itself.__name__ if type(field_itself).__name__ == "type" else field_itself
			if type(field_itself) is list:
				field_value = []
				for transform in field_itself:
					field_value.append(transform.__name__)
			data.setdefault(field_name, field_value)

		return json.dumps(data)


class StringField(Field):

	@Field.TransformDecorator
	def get_value(self, data):
		transform_key = self._meta.get("name") + "_transform"
		non_transform = self._meta.get("name")

		transform_value = data.get(transform_key)
		non_transform_value = data.get(non_transform)

		if not transform_value and not non_transform_value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				raise FieldException("null or empty was found and no default is set")

		if not transform_value:
			if non_transform_value in ["NA", "na", "#ref!", "#REF!"]:
				value = transform_value
			else:
				value = non_transform_value
		else:
			value = transform_value

		if not value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				raise FieldException("null or empty was found and no default is set")

		return str(value)


class IntegerField(Field):

	@Field.TransformDecorator
	def get_value(self, data) -> int:

		value = super(IntegerField, self).get_value(data)
		if not value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				raise FieldException("null or empty was found and no default is set")
		try:
			value = float(value)
		except ValueError:
			raise
		else:
			return int(value)


class DecimalField(Field):

	@Field.TransformDecorator
	def get_value(self, data) -> float:
		value = super(DecimalField, self).get_value(data)
		if not value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				FieldException("null or empty was found and no default is set")

		try:
			value = float(value)
		except ValueError:
			raise FieldException("Not a Number: {}".format(value))
		else:
			return value


class BooleanField(Field):

	@Field.TransformDecorator
	def get_value(self, data):
		value = super(BooleanField, self).get_value(data)
		if not value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				FieldException("null or empty was found and no default is set")
		return type(value) is str and value.lower() == "true"


class DateField(Field):
	DD_MM_YYYY = "%d/%m/%Y"
	MM_DD_YYYY = "%m/%d/%Y"

	def __init__(self, date_format: str = MM_DD_YYYY, **kwargs):
		kwargs.setdefault("date_format", date_format)

		super().__init__(**kwargs)

	@Field.TransformDecorator
	def get_value(self, data):
		value = super(DateField, self).get_value(data)
		if not value:
			if self._meta.get("allow_empty_or_null"):
				return self._meta.get("default_val")
			else:
				FieldException("null or empty was found and no default is set")

		date_format = self._meta.get("date_format", DateField.MM_DD_YYYY)
		try:
			datetime.strptime(value, date_format)
		except ValueError:
			raise FieldException("Invalid Date Format: {}".format(value))
		else:
			return value


class ListField(Field):

	def __init__(self, delimiter: str = ",", item_type: object = str, **kwargs):
		kwargs.setdefault("delimiter", delimiter)
		kwargs.setdefault("item_type", item_type)
		kwargs.setdefault("pre_transform", [transform_tags_to_tags])

		super(ListField, self).__init__(**kwargs)

	@Field.TransformDecorator
	def get_value(self, data):
		value = super(ListField, self).get_value(data)
		if not value and self._meta.get("allow_empty_or_null"):
			return self._meta.get("default_val", [])

		delimiter = self._meta.get("delimiter", ",")
		item_type = self._meta.get("item_type", str)
		value_list = [ele.strip().strip('"\'') for ele in value.split(delimiter)]

		transform_method = str
		if item_type is int:
			transform_method = self._to_int
		elif item_type is float:
			transform_method = self._to_decimal

		final_list = [transform_method(item) for item in value_list]
		return final_list

	def _to_int(self, val):
		val = self._to_decimal(val)
		return int(val)

	def _to_decimal(self, val):
		type_of = self._meta.get("item_type", float)
		try:
			val = float(val)
		except ValueError:
			raise FieldException(f"Not all the items are of same type: {type_of}, value {val}")
		else:
			return val

	def validate(self, headers):
		super(ListField, self).validate(headers)
		item_type = self._meta.get("item_type")
		if item_type not in [int, float, str]:
			self._meta.setdefault("item_type", str)
			print(
				f"Valid item_type options for ListFields are int, float, str, but given: {item_type}. Reset to default: str")


class CustomField(Field):

	def __init__(self, to_value: Callable = lambda data: None, **kwargs):
		kwargs.setdefault("to_value", to_value)
		super(CustomField, self).__init__(**kwargs)

	def get_value(self, data):
		method: Callable = self._meta.get("to_value")
		return method(data)
