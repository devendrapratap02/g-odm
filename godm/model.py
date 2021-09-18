import json
import datetime
from ._manager import GModelManager
from ._meta import GModelMeta


class GModel(object, metaclass=GModelMeta):
	manager = GModelManager

	def __init__(self, data):
		fields = data.get("fields", {})
		for field, field_val in list(fields.items()):
			setattr(self, field, field_val)
		setattr(self, "id", data.get("id"))
		setattr(self, "_data", data.get("data"))
		setattr(self, "_errors", data.get("errors"))

	def __init_subclass__(cls, **kwargs):
		return super(GModel).__init_subclass__(**kwargs)

	def __repr__(self):
		return json.dumps(self.to_json())

	def to_json(self):
		data = dict()
		_meta = getattr(self, "_meta", {})
		data["id"] = getattr(self, "id")
		for key in _meta:
			val = getattr(self, key, None)
			if isinstance(val, datetime.datetime):
				val = str(val)
			data[key] = val

		return data

	def get_errors(self):
		return getattr(self, "_errors", None)

	def get_raw_data(self):
		return getattr(self, "_data")

	def get_raw_value(self, field):
		all_fields = getattr(self, "_meta", {})
		field_obj = all_fields.get(field)
		field_obj_meta = getattr(field_obj, "_meta", {})
		field_column_name = field_obj_meta.get("name")

		return self.get_raw_data().get(field_column_name)
