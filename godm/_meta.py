from ._auth import get_sheet
from ._manager import GModelManager
from .exceptions import FieldException
from .field import Field


class GModelMeta(type):

	def __new__(mcs, *args, **kwargs):
		(name, bases, attrs) = args
		cls = super().__new__(mcs, *args, **kwargs)
		if name != "GModel":
			def _setup_attrs():
				class_meta = getattr(cls, "Meta")

				spreed_sheet = get_sheet(getattr(class_meta, "sheet_name", "default"))
				cls._data = spreed_sheet.worksheet(getattr(class_meta, "tab_name"))
				cls._headers = cls._data.row_values(getattr(class_meta, "header_index"))

				cls._meta = {}
				cls._errors = {}
				cls_annotations = {}
				for attr, obj in list(attrs.items()):
					# if not attr.startswith("__") and attr != "Meta" and not hasattr(obj, "__call__"):
					if isinstance(obj, Field):
						delattr(cls, attr)
						try:
							obj.validate(cls._headers)
						except FieldException as ex:
							cls._errors[attr] = str(ex)
						except Exception as ex:
							print(ex)
						else:
							cls._meta[attr] = obj
						cls_annotations[attr] = str

				setattr(cls, "__annotations__", cls_annotations)
			setattr(cls, "manager", GModelManager(cls, _setup_attrs))

		return cls
