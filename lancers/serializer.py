# coding: utf-8
from django.contrib.auth import get_user_model
from rest_framework import serializers
from datetime import datetime
from .models import Client, Opportunity, OpportunityWork, Category, Service


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    def create(self, validated_data):
        client = Client(**validated_data)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        client.save_from_shell(u)
        return client

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        instance.save_from_shell(u)
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        category = Category(**validated_data)
        u = self.context['request'].user
        # u = get_user_model().objects.first()
        category.save_from_shell(u)
        return category

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        instance.save_from_shell(u)
        return instance


class OpportunitySerializer(serializers.ModelSerializer):

    client_name = serializers.ReadOnlyField(source="client.name")
    client_type = serializers.ReadOnlyField(source="client.client_type")
    client_name_slack = serializers.ReadOnlyField(source="client.name_slack")
    category_name = serializers.ReadOnlyField(source="category.name")
    sub_categories = CategorySerializer(many=True, read_only=True)
    working_time = serializers.ReadOnlyField(source="get_working_time")
    unit_val = serializers.ReadOnlyField(source="get_unit_val")

    class Meta:
        model = Opportunity
        fields = '__all__'

    def create(self, validated_data):
        opportunity = Opportunity(**validated_data)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        opportunity.save_from_shell(u)
        return opportunity

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        instance.save_from_shell(u)
        return instance


class OpportunityWorkSerializer(serializers.ModelSerializer):
    opportunity_name = serializers.ReadOnlyField(source="opportunity.name")
    opportunity_type = serializers.ReadOnlyField(source="opportunity.type")
    opportunity_status = serializers.ReadOnlyField(source="opportunity.status")

    class Meta:
        model = OpportunityWork
        fields = '__all__'

    def create(self, validated_data):
        opportunitywork = OpportunityWork(**validated_data)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        if not opportunitywork.working_time \
                and opportunitywork.datetime_start \
                and opportunitywork.datetime_end:
            opportunitywork.working_time = int((opportunitywork.datetime_end-opportunitywork.datetime_start).seconds/60)
        # save_from_shell
        opportunitywork.save_from_shell(u)
        return opportunitywork

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        # u = get_user_model().objects.first()
        u = self.context['request'].user
        instance.save_from_shell(u)
        return instance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'