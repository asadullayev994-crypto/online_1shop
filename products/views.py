# products/views.py

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product, ProductImage
from products.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
)


class ProductListView(APIView):
   

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        products = Product.objects.filter(status="published").select_related(
            "category", "seller"
        ).prefetch_related("images")

       
        category_slug = request.query_params.get("category")
        if category_slug:
            products = products.filter(category__slug=category_slug)

      
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

      
        search = request.query_params.get("search")
        if search:
            products = products.filter(title__icontains=search)

      
        ordering = request.query_params.get("ordering", "-created_at")
        allowed_orderings = ["price", "-price", "created_at", "-created_at"]
        if ordering in allowed_orderings:
            products = products.order_by(ordering)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()
        return Response(
            ProductDetailSerializer(product).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):
   

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_object(self, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None

    def get(self, request, slug):
        product = self.get_object(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        product = self.get_object(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        # Faqat o'z mahsulotini yoki admin yangilay oladi
        if product.seller != request.user and not request.user.is_staff:
            return Response({"error": "Ruxsat yo'q."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductCreateUpdateSerializer(
            product, data=request.data, partial=True, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(ProductDetailSerializer(product).data, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        product = self.get_object(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if product.seller != request.user and not request.user.is_staff:
            return Response({"error": "Ruxsat yo'q."}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({"message": "Mahsulot o'chirildi."}, status=status.HTTP_200_OK)


class ProductImageView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None

    def post(self, request, slug):
        product = self.get_object(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if product.seller != request.user and not request.user.is_staff:
            return Response({"error": "Ruxsat yo'q."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductImageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, slug, image_id):
        product = self.get_object(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if product.seller != request.user and not request.user.is_staff:
            return Response({"error": "Ruxsat yo'q."}, status=status.HTTP_403_FORBIDDEN)

        try:
            image = ProductImage.objects.get(pk=image_id, product=product)
        except ProductImage.DoesNotExist:
            return Response({"error": "Rasm topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        image.delete()
        return Response({"message": "Rasm o'chirildi."}, status=status.HTTP_200_OK)


class MyProductsView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(seller=request.user).prefetch_related("images")
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)