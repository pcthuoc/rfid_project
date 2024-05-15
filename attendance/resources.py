from import_export import resources
from .models import Student

class PersonResource(resources.ModelResource):
    class Meta:
        model = Student