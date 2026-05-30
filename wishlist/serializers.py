from rest_framework import serializers

from products.models import Product
from products.serializers import ProductListSerializer
from wishlist.models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_id", "created_at"]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Mahsulot topilmadi.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        try:
            wishlist = Wishlist.objects.get(user=request.user)
        except Wishlist.DoesNotExist:
            return attrs
        if WishlistItem.objects.filter(
            wishlist=wishlist, product_id=attrs["product_id"]
        ).exists():
            raise serializers.ValidationError("Bu mahsulot allaqachon sevimlilar ro'yxatida.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = validated_data.pop("product_id")
        return WishlistItem.objects.create(
            wishlist=wishlist,
            product_id=product_id,
        )


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)
    total_count = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ["id", "items", "total_count"]

    def get_total_count(self, obj):
        return obj.items.count()