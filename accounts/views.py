from django.shortcuts import render
from django.shortcuts import render
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.serializer import UserSerializer
# Create your views here.


class UserDetailAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(instance=request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
