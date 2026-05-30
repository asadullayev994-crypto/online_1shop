

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
   

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]