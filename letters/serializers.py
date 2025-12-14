from rest_framework import serializers
from .models import Letter, ModificationRequest

class LetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = '__all__'
        read_only_fields = ('sender',)


class ModificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModificationRequest
        fields = '__all__'
        read_only_fields = (
            'requested_by',
            'sender_approval',
            'receiver_approval',
            'status',
        )
