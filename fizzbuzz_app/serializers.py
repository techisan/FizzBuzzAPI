from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import FizzBuzzRequest

def non_empty_validator(value):
    if value is None or (isinstance(value, str) and value.strip() == ''):
        raise serializers.ValidationError("This field is required and cannot be empty.")

class FizzBuzzRequestSerializer(serializers.Serializer):
    int1 = serializers.IntegerField(min_value=1, required=True)
    int2 = serializers.IntegerField(min_value=1, required=True)
    limit = serializers.IntegerField(min_value=1, required=True)
    str1 = serializers.CharField(max_length=255, required=True, validators=[non_empty_validator])
    str2 = serializers.CharField(max_length=255, required=True, validators=[non_empty_validator])

    def validate_int1(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("int1 must be a number.")
        return value

    def validate_int2(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("int2 must be a number.")
        return value

    def validate_limit(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("limit must be a number.")
        return value

    def validate_str1(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("str1 must be a string.")
        if not value.isalpha():
            raise serializers.ValidationError("str1 must be alphabetical only.")
        return value

    def validate_str2(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("str2 must be a string.")
        if not value.isalpha():
            raise serializers.ValidationError("str2 must be alphabetical only.")
        return value
    
    def validate(self, data):
        # Ensure that all required parameters are present
        required_params = {'int1', 'int2', 'limit', 'str1', 'str2'}
        missing_params = required_params - set(data.keys())
        empty_params = {param for param, value in data.items() if not value}

        error_dict = {}

        if missing_params:
            error_dict.update({param: [f"{param.capitalize()} is required."] for param in missing_params})

        if empty_params:
            error_dict.update({param: [f"{param.capitalize()} cannot be empty."] for param in empty_params})

        if error_dict:
            raise serializers.ValidationError(error_dict)

        return data

    class Meta:
        model = FizzBuzzRequest
        fields = '__all__'
