from godm import LoadPolicy
from godm.field import BooleanField, DateField, IntegerField, StringField
from godm.model import GModel


class Users(GModel):
	name = StringField(name="Name")
	age = IntegerField(name="Age")
	dob = DateField(name="DOB", format=DateField.MM_DD_YYYY, allow_empty=True, default_val="01/01/2010")
	is_family = BooleanField(name="Family")

	class Meta:
		sheet_name = "Test Sheet - GODM"
		tab_name = "Users"
		header_index = 1
		load_policy = LoadPolicy.LAZY

# a = Users.manager.filter(is_family=True)
# b = Users.manager.filter(age__lt=30)
# c = Users.manager.get(name="Devendra")
