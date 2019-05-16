# coding: utf-8

from rest_framework import serializers

from .models import Usages, Resources, Kakeibos, SharedKakeibos


class UsagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ("name", "is_expense",)


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = ("name", "is_saving")


class KakeibosSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer()
    move_to = ResourcesSerializer()
    move_from = ResourcesSerializer()

    class Meta:
        model = Kakeibos
        fields = ('date', 'fee', 'way', 'usage', 'move_to', 'move_from', 'memo')


class SharedKakeibosSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer()
    class Meta:
        model = SharedKakeibos
        fields = ('date', 'fee', 'paid_by', 'usage', 'memo')