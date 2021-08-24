import json
import os

import gspread
from gspread.client import Client
from gspread.models import Spreadsheet

_g_sheet: Client
_worksheets = {}

ENV_SYSTEM_KEY_PATH = "GODM_AUTH_KEY_PATH"


def authenticate(key_object: object = None, key_path: str = None):
	"""Authenticates the access token against the Google Sheet API

	Args:
		key_object (object, optional): JSON Object contains the whole generated access key. Defaults to None.
		key_path (str, optional): Path of the Access key file. Defaults to None.

	If none of the parameters are passed, it will look for ENV variable named GODM_AUTH_KEY_PATH to look for file path
	"""

	if not key_object or not isinstance(key_object, object):
		if not key_path or not os.path.exists(key_path):
			key_path = os.environ.get(ENV_SYSTEM_KEY_PATH)
			key_object = json.load(open(key_path))

	global _g_sheet
	_g_sheet = gspread.service_account_from_dict(key_object)


def get_sheet(sheet_name: str) -> Spreadsheet:
	"""Fetches the Google Sheet object from already cached list or else creates the new object and store in catch

	Args:
		sheet_name (str): Sheet name

	Returns:
		:class:`gspread.models.Spreadsheet`: instance
	"""

	if not _g_sheet:
		authenticate()

	if not _worksheets.get(sheet_name, None):
		_worksheets[sheet_name] = _g_sheet.open(sheet_name)

	return _worksheets.get(sheet_name)


def load_sheet(sheet_name: str, alias: str = "default"):
	"""Load the Google Sheet object for later use. It creates the :class:`gspread.models.Spreadsheet` instance
	and catches it along with alias name as well

	Args:
		sheet_name (str): Google Sheet Tab Name
		alias (str, optional): Addition name to catch the instance. Defaults to "default".
	"""
	if not _g_sheet:
		authenticate()

	_worksheets[sheet_name] = _g_sheet.open(sheet_name)

	if alias:
		_worksheets[alias] = _worksheets[sheet_name]
