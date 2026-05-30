from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "user_email", "user_full_name", "product", "rating",
            "title", "comment", "is_approved", "created_at",
        ]
        read_only_fields = ["is_approved", "created_at", "user_email", "user_full_name"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate_comment(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Izoh kamida 5 ta belgi bo'lishi kerak.")
        return value.strip() if value else value

    def validate(self, attrs):
        request = self.context.get("request")
        product = attrs.get("product")
        if Review.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError("Siz bu mahsulotga allaqachon sharh yozdingiz.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate_comment(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Izoh kamida 5 ta belgi bo'lishi kerak.")
        return value.strip() if value else value