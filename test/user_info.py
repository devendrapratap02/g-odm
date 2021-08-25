from godm.field import StringField, IntegerField, DateField
from godm.model import GModel


class Users(GModel):
	name = StringField(name="Name")
	age = IntegerField(name="Age")
	dob = DateField(name="DOB", format=DateField.MM_DD_YYYY, allow_empty=True, default_val="01/01/2010")
	is_family = StringField(name="Family")

	class Meta:
		sheet_name = "Test Sheet"
		tab_name = "Users"
		header_index = 4


a = Users.manager.filter(is_family="Yes")
a.first()
a.last()

b = Users.manager.get(age="29")
