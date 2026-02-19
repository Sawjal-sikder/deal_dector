from rest_framework import serializers # type: ignore
from service.models import SelectedSupermarket


class SelectedSupermarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedSupermarket
        fields = ['id', 'user', 'supermarket_id']
        read_only_fields = ['id','user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email
        return representation


class SelectedSupermarketBulkCreateSerializer(serializers.Serializer):
    supermarket_id = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )

    def create(self, validated_data):
        user = self.context['request'].user
        ids = validated_data['supermarket_id']

        # Delete all previous selections
        SelectedSupermarket.objects.filter(user=user).delete()

        # Create new selections
        created = SelectedSupermarket.objects.bulk_create([
            SelectedSupermarket(user=user, supermarket_id=sid)
            for sid in ids
        ])

        return created