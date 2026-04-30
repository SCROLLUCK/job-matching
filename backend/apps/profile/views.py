from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileView(APIView):
    def get(self, request):
        profile = UserProfile.get()
        return Response(UserProfileSerializer(profile).data)

    def put(self, request):
        profile = UserProfile.get()
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
