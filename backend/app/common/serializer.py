from sqlalchemy.inspection import inspect
from typing import Any, List, Optional, Union


class BaseSerializer:
    def __init__(self, instance: any, many: bool = False):
        self.many = many
        self.instance = instance

    @property
    def data(self):
        if self.instance:
            return None
        
        if self.many:
            return [self.to_representation(obj) for obj in self.instance]
        
        return self.to_representation(self.instance)
    
    def to_representation(self, obj):
        raise NotImplementedError("Serializer must implement to_representation")
    

class ModelSerializer(BaseSerializer):
    class meta:
        model = None
        fields = None
        exclude = None

    def get_fields(self):
        mapper = inspect(self.Meta.model)
        column_names = [c.key for c in mapper.columns]

        if self.Meta.fields:
            return self.Meta.fields
        
        if self.Meta.exclude:
            return [name for name in column_names if name not in self.Meta.exclude]

        return column_names

    def to_representation(self, obj):
        result = {}
        fields = self.get_fields()
        for name in fields:
            value = getattr(obj, name)

            if isinstance(value, (list, dict)):
                result[name] = value
                continue

            if hasattr(value, "isoformat"):
                result[name] = value.isoformat()
                continue

            result[name] = value

        return result