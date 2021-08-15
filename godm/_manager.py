from .exceptions import EntityException, FieldException
from .iterator import EntityIterator


class GModelManager(object):

	def __init__(self, model):
		self.model = model

	def _filter_data_list(self, **kwargs):
		all_data = getattr(self.model, "_data")
		headers = getattr(self.model, "_headers")
		meta = getattr(self.model, "_meta")

		all_data_list = [i for i in range(all_data.row_count)]
		filter_data_list = []

		for key, val in list(kwargs.items()):
			filter_data_list = []
			field = meta.get(key)
			key_name = getattr(field, "_meta", {}).get("name")
			local_index = headers.index(key_name) + 1

			column_values = all_data.col_values(local_index)
			for index in all_data_list:
				value = column_values[index]
				if val == value:
					filter_data_list.append(index + 1)

			all_data_list = filter_data_list

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

	def get(self, **kwargs):

		filter_data_list = self._filter_data_list(**kwargs)
		print(filter_data_list)

		if len(filter_data_list) == 0:
			raise EntityException(f"Unable to find Entity {self.model}, {kwargs}")

		model_data = self._get_data_from_id(filter_data_list[0])

		return self.model(model_data)

	def filter(self, **kwargs):
		filter_data_list = self._filter_data_list(**kwargs)
		print(filter_data_list)

		return EntityIterator(self, filter_data_list)

	def get_entity_from_id(self, row_index):
		model_data = self._get_data_from_id(row_index)
		return self.model(model_data)
