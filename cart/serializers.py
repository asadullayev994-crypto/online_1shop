from rest_framework import serializers

from cart.models import Cart, CartItem
from products.models import Product
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "total_price"]

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Mahsulot topilmadi.")
        if not product.is_available:
            raise serializers.ValidationError("Mahsulot mavjud emas yoki tugagan.")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Miqdor 1 dan kam bo'lmasin.")
        if value > 100:
            raise serializers.ValidationError("Bir vaqtda 100 tadan ko'p mahsulot qo'shib bo'lmaydi.")
        return value

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)
        try:
            product = Product.objects.get(pk=product_id)
            if quantity > product.stock:
                raise serializers.ValidationError(
                    {"quantity": f"Omborda faqat {product.stock} ta mavjud."}
                )
        except Product.DoesNotExist:
            pass
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_items"]