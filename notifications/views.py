

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import Notification, NotificationPreference
from notifications.serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(APIView):
  

    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

      
        unread = request.query_params.get("unread")
        if unread == "true":
            notifications = notifications.filter(is_read=False)

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response({"message": "Barcha bildirishnomalar o'chirildi."}, status=status.HTTP_200_OK)


class NotificationDetailView(APIView):
    

    permission_classes = [IsAuthenticated]

    def get_object(self, request, notification_id):
        try:
            return Notification.objects.get(pk=notification_id, user=request.user)
        except Notification.DoesNotExist:
            return None

    def post(self, request, notification_id):
        notification = self.get_object(request, notification_id)
        if not notification:
            return Response({"error": "Bildirishnoma topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        notification.mark_as_read()
        return Response({"message": "O'qilgan deb belgilandi."}, status=status.HTTP_200_OK)

    def delete(self, request, notification_id):
        notification = self.get_object(request, notification_id)
        if not notification:
            return Response({"error": "Bildirishnoma topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response({"message": "Bildirishnoma o'chirildi."}, status=status.HTTP_200_OK)


class NotificationReadAllView(APIView):
   

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )
        return Response({"message": "Barcha bildirishnomalar o'qilgan deb belgilandi."}, status=status.HTTP_200_OK)


class NotificationPreferenceView(APIView):
   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)