from rest_framework import serializers # type: ignore
from service.models import SelectedSupermarket

class SelectedSupermarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedSupermarket
        fields = ['id', 'user', 'supermarket_id']
        read_only_fields = ['id','user']
        
    def validate_supermarket_id(self, value):
        user = self.context['request'].user
        exising_supermarket_id = SelectedSupermarket.objects.filter(user=user, supermarket_id=value).exists()
        
        if exising_supermarket_id:
            raise serializers.ValidationError("This supermarket is already in your selected list.")
        return value        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email
        return representation