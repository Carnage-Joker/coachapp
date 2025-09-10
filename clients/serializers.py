# serializers.py
from rest_framework import serializers
from .models import Client, ClientInjury, ClientPreference, ClientEquipment, ClientBlock


class ClientInjurySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientInjury
        exclude = ('client',)  # <— don't require client from the request
        read_only_fields = ('id', 'created_at', 'updated_at')


class ClientPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPreference
        exclude = ('client',)
        read_only_fields = ('id', 'created_at', 'updated_at')


class ClientEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientEquipment
        exclude = ('client',)
        read_only_fields = ('id', 'created_at', 'updated_at')


class ClientSerializer(serializers.ModelSerializer):
    injuries = ClientInjurySerializer(many=True, required=False)
    preferences = ClientPreferenceSerializer(many=True, required=False)
    equipment = ClientEquipmentSerializer(many=True, required=False)

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        injuries = validated_data.pop('injuries', [])
        prefs = validated_data.pop('preferences', [])
        equip = validated_data.pop('equipment', [])
        client = Client.objects.create(**validated_data)
        for i in injuries:
            ClientInjury.objects.create(client=client, **i)
        for p in prefs:
            ClientPreference.objects.create(client=client, **p)
        for e in equip:
            ClientEquipment.objects.create(client=client, **e)
        return client


class ClientBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBlock
        fields = ("id", "name", "created_at", "updated_at", "block")
        read_only_fields = ("id", "created_at", "updated_at")
