# coding: utf-8

from rest_framework import serializers
from datetime import datetime
from .models import Usages, Resources, Kakeibos, SharedKakeibos, CreditItems, Credits, Event
from .models import CronKakeibo, CronShared, UsualRecord


class UsagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usages
        fields = ('pk', "name", "is_expense",)


class ResourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = ('pk', "name", "is_saving")


class KakeibosSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)
    move_to = ResourcesSerializer(read_only=True)
    move_to_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True, allow_empty=True, allow_null=True)
    move_from = ResourcesSerializer(read_only=True)
    move_from_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True, allow_empty=True, allow_null=True)

    def create(self, validated_data):
        # usage
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['usage'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        # move_to
        validated_data['move_to'] = validated_data.get('move_to_uid', None)
        del validated_data['move_to_uid']
        # move_from
        validated_data['move_from'] = validated_data.get('move_from_uid', None)
        del validated_data['move_from_uid']
        # return
        return Kakeibos.objects.create(**validated_data)

    class Meta:
        model = Kakeibos
        fields = (
            'pk', 'date', 'fee', 'way', 'usage',
            'move_to', 'move_from', 'memo',
            'usage_uid', 'move_to_uid', 'move_from_uid'
        )


class SharedKakeibosSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)

    def create(self, validated_data):
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['user'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        return SharedKakeibos.objects.create(**validated_data)

    class Meta:
        model = SharedKakeibos
        fields = ('pk', 'date', 'fee', 'paid_by', 'usage', 'memo', 'usage_uid')


class CreditItemsSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)

    def create(self, validated_data):
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['user'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        return CreditItems.objects.create(**validated_data)

    class Meta:
        model = CreditItems
        fields = ('pk', 'name', 'usage', 'usage_uid')


class CreditsSerializer(serializers.ModelSerializer):
    credit_item = CreditItemsSerializer()

    class Meta:
        model = Credits
        fields = ('pk', 'date', 'debit_date', 'fee', 'credit_item', 'memo', )


class CronKakeiboSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)
    move_to = ResourcesSerializer(read_only=True)
    move_to_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True,
                                                     allow_empty=True, allow_null=True)
    move_from = ResourcesSerializer(read_only=True)
    move_from_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True,
                                                       allow_empty=True, allow_null=True)

    def create(self, validated_data):
        # usage
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['usage'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        # move_to
        validated_data['move_to'] = validated_data.get('move_to_uid', None)
        del validated_data['move_to_uid']
        # move_from
        validated_data['move_from'] = validated_data.get('move_from_uid', None)
        del validated_data['move_from_uid']
        # return
        return CronKakeibo.objects.create(**validated_data)

    class Meta:
        model = CronKakeibo
        fields = ('pk', 'fee', 'way', 'usage', 'move_to', 'move_from', 'memo', 'usage_uid', 'move_from_uid', 'move_to_uid')


class CronSharedSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)

    def create(self, validated_data):
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['user'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        return CronShared.objects.create(**validated_data)

    class Meta:
        model = CronShared
        fields = ('pk', 'fee', 'paid_by', 'usage', 'usage_uid', 'memo')


class UsualRecordSerializer(serializers.ModelSerializer):
    usage = UsagesSerializer(read_only=True)
    usage_uid = serializers.PrimaryKeyRelatedField(queryset=Usages.objects.all(), write_only=True)
    move_to = ResourcesSerializer(read_only=True)
    move_to_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True,
                                                     allow_empty=True, allow_null=True)
    move_from = ResourcesSerializer(read_only=True)
    move_from_uid = serializers.PrimaryKeyRelatedField(queryset=Resources.objects.all(), write_only=True,
                                                       allow_empty=True, allow_null=True)

    def create(self, validated_data):
        # usage
        validated_data['usage'] = validated_data.get('usage_uid', None)
        if validated_data['usage'] is None:
            raise serializers.ValidationError("usage not found.")
        del validated_data['usage_uid']
        # move_to
        validated_data['move_to'] = validated_data.get('move_to_uid', None)
        del validated_data['move_to_uid']
        # move_from
        validated_data['move_from'] = validated_data.get('move_from_uid', None)
        del validated_data['move_from_uid']
        # return
        return UsualRecord.objects.create(**validated_data)

    class Meta:
        model = UsualRecord
        fields = (
            'pk', 'fee', 'way', 'usage',
            'move_to', 'move_from', 'memo',
            'icon', 'usage_uid', 'move_from_uid', 'move_to_uid'
        )


class EventSerializer(serializers.ModelSerializer):
    kakeibos = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('pk', "name", "date", "memo", "detail", "sum_plan", "is_active", "kakeibos")

    def get_kakeibos(self, obj):
        try:
            res = KakeibosSerializer(
                Kakeibos.objects.all().filter(event=Event.objects.get(id=obj.id)),
                many=True
            ).data
        except Exception as e:
            res = None
        finally:
            return res