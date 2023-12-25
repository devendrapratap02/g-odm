def transform_to_lower_case(value) -> str:
	return_value = value
	if value and isinstance(value, str):
		return_value = value.lower()

	return return_value


def transform_na_to_none(value) -> None:
	na_value = "na"
	return_value = value
	lower_case_value = transform_to_lower_case(value)
	if not value or lower_case_value == na_value:
		return_value = None

	return return_value


def transform_invalid_ref_to_none(value) -> None:
	ref_value = "#ref!"
	return_value = value
	lower_case_value = transform_to_lower_case(value)
	if not value or lower_case_value == ref_value:
		return_value = None

	return return_value


def transform_tags_to_tags(value):
	if not value:
		return ""

	value: str = value
	start_index = value.find("[")
	end_index = value.find("]")

	if start_index == -1 or end_index == -1 or start_index > end_index:
		return value

	list_as_string = value[start_index + 1:end_index]
	if not list_as_string:
		return ""
	list_split = list_as_string.split(",")
	list_strip_quotes = [item.strip('"\'') for item in list_split]
	list_filter_empty = list(filter(lambda item: not not item.strip(), list_strip_quotes))
	return ",".join(list_filter_empty)
