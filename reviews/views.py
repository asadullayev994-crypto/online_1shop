

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from reviews.models import Review
from reviews.serializers import ReviewSerializer, ReviewUpdateSerializer


class ProductReviewListView(APIView):
   

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_product(self, slug):
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None

    def get(self, request, slug):
        product = self.get_product(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        reviews = Review.objects.filter(
            product=product, is_approved=True
        ).select_related("user").order_by("-created_at")

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slug):
        product = self.get_product(slug)
        if not product:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["product"] = product.pk

        serializer = ReviewSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, request, review_id):
        try:
            return Review.objects.get(pk=review_id, user=request.user)
        except Review.DoesNotExist:
            return None

    def put(self, request, review_id):
        review = self.get_object(request, review_id)
        if not review:
            return Response({"error": "Sharh topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_200_OK)

    def delete(self, request, review_id):
        review = self.get_object(request, review_id)
        if not review:
            return Response({"error": "Sharh topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"message": "Sharh o'chirildi."}, status=status.HTTP_200_OK)


class AdminReviewListView(APIView):
   

    permission_classes = [IsAdminUser]

    def get(self, request):
        reviews = Review.objects.filter(is_approved=False).select_related(
            "user", "product"
        ).order_by("-created_at")
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminReviewApproveView(APIView):
   

    permission_classes = [IsAdminUser]

    def get_object(self, review_id):
        try:
            return Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return None

    def post(self, request, review_id):
        review = self.get_object(review_id)
        if not review:
            return Response({"error": "Sharh topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        review.is_approved = True
        review.save(update_fields=["is_approved"])
        return Response({"message": "Sharh tasdiqlandi."}, status=status.HTTP_200_OK)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        if not review:
            return Response({"error": "Sharh topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"message": "Sharh o'chirildi."}, status=status.HTTP_200_OK)