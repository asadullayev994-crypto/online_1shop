from rest_framework import serializers

from cart.models import Cart
from orders.models import Order, OrderItem, Status
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "total_price"]

    def get_total_price(self, obj):
        return obj.total_price


class OrderListSerializer(serializers.ModelSerializer):
  
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "status_display", "total_price", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
  
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "status", "status_display", "total_price",
            "shipping_address", "note", "can_cancel",
            "items", "created_at",
        ]

    def get_can_cancel(self, obj):
        return obj.can_cancel


class OrderCreateSerializer(serializers.ModelSerializer):


    class Meta:
        model = Order
        fields = ["shipping_address", "note"]

    def validate_shipping_address(self, value):
        value = value.strip() if value else value
        if not value:
            raise serializers.ValidationError("Yetkazish manzili kiritilishi shart.")
        if len(value) < 10:
            raise serializers.ValidationError("Manzil kamida 10 ta belgi bo'lishi kerak.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Savatingiz bo'sh.")
        if not cart.items.exists():
            raise serializers.ValidationError("Savatingiz bo'sh.")
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        cart = Cart.objects.get(user=user)
        total_price = cart.total_price

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            **validated_data,
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.current_price,
            )

        cart.items.all().delete()
        return order


class OrderCancelSerializer(serializers.ModelSerializer):
  

    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        if not self.instance.can_cancel:
            raise serializers.ValidationError(
                "Faqat 'Kutilmoqda' holatidagi buyurtmani bekor qilish mumkin."
            )
        return attrs

    def update(self, instance, validated_data):
        instance.status = Status.CANCELLED
        instance.save(update_fields=["status"])
        return instance