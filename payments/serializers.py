from rest_framework import serializers

from payments.models import Payment, PaymentMethod, PaymentStatus


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "order", "method", "method_display", "status",
            "status_display", "amount", "currency",
            "transaction_id", "provider", "paid_at", "created_at",
        ]
        read_only_fields = [
            "status", "transaction_id", "paid_at", "created_at",
            "status_display", "method_display",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("To'lov summasi 0 dan katta bo'lishi kerak.")
        return value

    def validate_method(self, value):
        allowed = [m.value for m in PaymentMethod]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Noto'g'ri to'lov usuli. Qabul qilinadi: {', '.join(allowed)}"
            )
        return value

    def validate(self, attrs):
        order = attrs.get("order")
        if order:
            existing = Payment.objects.filter(
                order=order,
                status=PaymentStatus.PAID,
            ).exists()
            if existing:
                raise serializers.ValidationError(
                    {"order": "Bu buyurtma uchun to'lov allaqachon amalga oshirilgan."}
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class PaymentListSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "order", "method_display", "status_display",
            "amount", "currency", "paid_at", "created_at",
        ]