from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import ChangePasswordSerializer, ForgotPassCompleteSerializer, ForgotPasswordSerializer, \
    RegisterSerializer
from account import serializers


class RegisterView(APIView):

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                "Successfully registred!", 201
            )


class ActivationView(APIView):

    def get(self, request, email, activation_code):
        user = CustomUser.objects.filter(
            email=email,
            activation_code=activation_code
        ).first()
        msg_ = (
            "User does not exist",
            "Activated!"
        )
        if not user:
            return Response(msg_, 400)
        user.activation_code = ''
        user.is_active = True
        user.save()
        return Response(msg_[-1], 200)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}  # context мы пишем в словаре, что бы в serializer могли использовать request
        )
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Status: 200. Пароль успешно обновлён')


class ForgotPasswordView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.send_verification_email()
            return Response('Вам было выслано код активации на вашу почту для востановления пароля')


class ForgotPassCompleteView(APIView):

    def post(self, request):
        serializer = ForgotPassCompleteSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response('Пароль был успешно заменён')
