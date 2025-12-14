from rest_framework import serializers
from .models import Letter, ModificationRequest

class LetterSerializer(serializers.ModelSerializer): # cite: uploaded:serializers.py
    class Meta:
        model = Letter # cite: uploaded:serializers.py
        fields = '__all__' # cite: uploaded:serializers.py
        read_only_fields = ('sender',) # cite: uploaded:serializers.py


class ModificationRequestSerializer(serializers.ModelSerializer): # cite: uploaded:serializers.py
    class Meta:
        model = ModificationRequest # cite: uploaded:serializers.py
        fields = '__all__' # cite: uploaded:serializers.py
        read_only_fields = ( # cite: uploaded:serializers.py
            'requested_by',
            'sender_approval',
            'receiver_approval',
            'status',
        )