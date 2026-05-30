

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderCancelSerializer,
)


class OrderListView(APIView):
  

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related(
            "items", "items__product"
        ).order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, request, order_id):
        try:
            return Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_id):
        order = self.get_object(request, order_id)
        if not order:
            return Response({"error": "Buyurtma topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderCancelView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, request, order_id):
        try:
            return Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return None

    def post(self, request, order_id):
        order = self.get_object(request, order_id)
        if not order:
            return Response({"error": "Buyurtma topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderCancelSerializer(order, data={}, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(
            {"message": "Buyurtma bekor qilindi."},
            status=status.HTTP_200_OK,
        )


class AdminOrderListView(APIView):
    

    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.all().select_related("user").prefetch_related(
            "items", "items__product"
        ).order_by("-created_at")

        order_status = request.query_params.get("status")
        if order_status:
            orders = orders.filter(status=order_status)

        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminOrderUpdateView(APIView):
  

    permission_classes = [IsAdminUser]

    def get_object(self, order_id):
        try:
            return Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return None

    def put(self, request, order_id):
        order = self.get_object(order_id)
        if not order:
            return Response({"error": "Buyurtma topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status kiritilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        from orders.models import Status
        allowed = [s.value for s in Status]
        if new_status not in allowed:
            return Response(
                {"error": f"Noto'g'ri status. Qabul qilinadi: {', '.join(allowed)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save(update_fields=["status"])
        return Response(
            {"message": f"Status '{new_status}' ga o'zgartirildi."},
            status=status.HTTP_200_OK,
        )