

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from payments.models import Payment, PaymentStatus
from payments.serializers import PaymentSerializer, PaymentListSerializer


class PaymentListView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(
            user=request.user
        ).select_related("order").order_by("-created_at")
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PaymentSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        payment = serializer.save()
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentDetailView(APIView):
   

    permission_classes = [IsAuthenticated]

    def get_object(self, request, payment_id):
        try:
            return Payment.objects.get(pk=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return None

    def get(self, request, payment_id):
        payment = self.get_object(request, payment_id)
        if not payment:
            return Response({"error": "To'lov topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPaymentListView(APIView):
    

    permission_classes = [IsAdminUser]

    def get(self, request):
        payments = Payment.objects.all().select_related(
            "user", "order"
        ).order_by("-created_at")

      
        pay_status = request.query_params.get("status")
        if pay_status:
            payments = payments.filter(status=pay_status)

        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPaymentUpdateView(APIView):
   

    permission_classes = [IsAdminUser]

    def get_object(self, payment_id):
        try:
            return Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return None

    def put(self, request, payment_id):
        payment = self.get_object(payment_id)
        if not payment:
            return Response({"error": "To'lov topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status kiritilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        allowed = [s.value for s in PaymentStatus]
        if new_status not in allowed:
            return Response(
                {"error": f"Noto'g'ri status. Qabul qilinadi: {', '.join(allowed)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils import timezone
        update_fields = ["status"]

        payment.status = new_status
        if new_status == PaymentStatus.PAID:
            payment.paid_at = timezone.now()
            update_fields.append("paid_at")

        payment.save(update_fields=update_fields)
        return Response(
            {"message": f"To'lov statusi '{new_status}' ga o'zgartirildi."},
            status=status.HTTP_200_OK,
        )