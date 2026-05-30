

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from cart.serializers import CartSerializer, CartItemSerializer


class CartView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass
        return Response({"message": "Savat tozalandi."}, status=status.HTTP_200_OK)


class CartItemAddView(APIView):
   

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartItemSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        item = serializer.save()
        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, request, item_id):
        try:
            cart = Cart.objects.get(user=request.user)
            return CartItem.objects.get(pk=item_id, cart=cart)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return None

    def put(self, request, item_id):
        item = self.get_object(request, item_id)
        if not item:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get("quantity")
        if not quantity:
            return Response({"error": "Miqdor kiritilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({"error": "Miqdor son bo'lishi kerak."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({"error": "Miqdor 1 dan kam bo'lmasin."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > item.product.stock:
            return Response(
                {"error": f"Omborda faqat {item.product.stock} ta mavjud."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        item = self.get_object(request, item_id)
        if not item:
            return Response({"error": "Mahsulot topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message": "Mahsulot savatdan o'chirildi."}, status=status.HTTP_200_OK)