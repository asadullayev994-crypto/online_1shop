

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wishlist.models import Wishlist, WishlistItem
from wishlist.serializers import WishlistSerializer, WishlistItemSerializer


class WishlistView(APIView):
  

    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist.items.all().delete()
        except Wishlist.DoesNotExist:
            pass
        return Response({"message": "Sevimlilar tozalandi."}, status=status.HTTP_200_OK)


class WishlistItemAddView(APIView):
   

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WishlistItemSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        item = serializer.save()
        return Response(
            WishlistItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class WishlistItemDeleteView(APIView):
   

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            item = WishlistItem.objects.get(pk=item_id, wishlist=wishlist)
        except (Wishlist.DoesNotExist, WishlistItem.DoesNotExist):
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({"message": "Mahsulot sevimlilardan o'chirildi."}, status=status.HTTP_200_OK)