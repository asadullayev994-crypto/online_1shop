from rest_framework import serializers
from categories.models import Category
 
 
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    full_path = serializers.CharField(read_only=True)
 
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "image", "full_path", "children"]
        read_only_fields = ["slug"]
 
    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data
 
    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Kategoriya nomi kamida 2 ta harf bo'lishi kerak.")
        return value
 
 
class CategoryShortSerializer(serializers.ModelSerializer):
    """Faqat asosiy ma'lumotlar — product ichida ishlatiladi"""
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
 
 
# ═══════════════════════════════════════
# products — serializers
# ═══════════════════════════════════════
from rest_framework import serializers
from products.models import Product, ProductImage, Status
 
 
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_main"]
 
    def validate_image(self, value):
        # Max 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Rasm hajmi 5MB dan oshmasin.")
        allowed = ["image/jpeg", "image/png", "image/webp"]
        if value.content_type not in allowed:
            raise serializers.ValidationError("Faqat JPEG, PNG yoki WEBP formatlar qabul qilinadi.")
        return value
 
 
class ProductListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun — qisqa"""
    main_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    category = CategoryShortSerializer(read_only=True)
 
    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "price", "discount_price",
            "current_price", "discount_percent", "stock",
            "status", "category", "main_image", "created_at",
        ]
 
    def get_main_image(self, obj):
        image = obj.images.filter(is_main=True).first()
        if image:
            return ProductImageSerializer(image).data
        return None
 
 
class ProductDetailSerializer(serializers.ModelSerializer):
    """Batafsil — bitta mahsulot uchun"""
    images = ProductImageSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    category = CategoryShortSerializer(read_only=True)
    seller_email = serializers.EmailField(source="seller.email", read_only=True)
 
    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "description", "price", "discount_price",
            "current_price", "discount_percent", "stock", "status",
            "is_available", "category", "seller_email", "images", "created_at",
        ]
        read_only_fields = ["slug", "created_at"]
 
 
class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Yaratish va yangilash uchun"""
    class Meta:
        model = Product
        fields = [
            "title", "description", "price", "discount_price",
            "stock", "status", "category",
        ]
 
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value
 
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Ombor miqdori manfiy bo'lmasin.")
        return value
 
    def validate_title(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Mahsulot nomi kamida 3 ta harf bo'lishi kerak.")
        return value
 
    def validate(self, attrs):
        price = attrs.get("price", getattr(self.instance, "price", None))
        discount_price = attrs.get("discount_price", getattr(self.instance, "discount_price", None))
        if discount_price and price and discount_price >= price:
            raise serializers.ValidationError({"discount_price": "Chegirmali narx asosiy narxdan kichik bo'lishi kerak."})
        return attrs
 
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["seller"] = request.user
        return super().create(validated_data)
 