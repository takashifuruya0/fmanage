# coding: utf-8
from django.contrib.auth import get_user_model
from rest_framework import serializers
from datetime import datetime
from .models import Client, Opportunity, OpportunityWork, Category


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    def create(self, validated_data):
        client = Client(**validated_data)
        u = get_user_model().objects.first()
        client.save_from_shell(u)
        return client


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        category = Category(**validated_data)
        u = get_user_model().objects.first()
        category.save_from_shell(u)
        return category


class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'

    def create(self, validated_data):
        opportunity = Opportunity(**validated_data)
        u = get_user_model().objects.first()
        opportunity.save_from_shell(u)
        return opportunity


class OpportunityWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityWork
        fields = '__all__'

    def create(self, validated_data):
        opportunitywork = OpportunityWork(**validated_data)
        u = get_user_model().objects.first()
        opportunitywork.save_from_shell(u)
        return opportunitywork
