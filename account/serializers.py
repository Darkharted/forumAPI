from rest_framework import serializers

from .models import CustomUser
from .tasks import send_activation_code
from django.core.mail import send_mail


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=4, required=True, write_only=True
    )
    password_confirmation = serializers.CharField(
        min_length=4, required=True,
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'email', 'password',
            'password_confirmation'
        )

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirmation = attrs.pop('password_confirmation')
        if password != password_confirmation:
            msg_ = (
                "Passwords do not match"
            )
            raise serializers.ValidationError(msg_)
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        send_activation_code(
            user.email, user.activation_code
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=4, required=True)
    new_password = serializers.CharField(min_length=4, required=True)
    new_password_confirm = serializers.CharField(min_length=4, required=True)

    def validate_old_password(self, old_pass):
        request = self.context.get('request')
        user = request.user

        if not user.check_password(old_pass):
            raise serializers.ValidationError('Вы ввели неправильный старый пароль')

        return old_pass

    def validate(self, attrs):
        old_pass = attrs.get('old_password')
        new_pass1 = attrs.get('new_password')
        new_pass2 = attrs.get('new_password_confirm')

        if new_pass1 != new_pass2:
            raise serializers.ValidationError('Новые пароли не совпадают')

        if old_pass == new_pass1:
            raise serializers.ValidationError('Новый и старый пароль не могут быть одинаковыми')
        return attrs

    def set_new_password(self):
        new_pass = self.validated_data.get('new_pass')
        user = self.context.get('request').user
        user.set_password(new_pass)
        user.save()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')

        return email

    def send_verification_email(self):
        email = self.validated_data.get('email')
        user = CustomUser.objects.get(email=email)
        user.create_activation_code()
        send_mail(
            'Забыли пароль',
            f'Ваш код для активации для начала изменения пароля - {user.activation_code}',
            'test@gmail.com',
            [user.email]
        )


class ForgotPassCompleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=4, required=True)
    password_confirmation = serializers.CharField(min_length=4, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password1 = attrs.get('password')
        password2 = attrs.get('password_confirmation')
        code = attrs.get('code')

        if not CustomUser.objects.filter(email=email, activation_code=code).exists():
            raise serializers.ValidationError("Данные не найдены")
        if password1 != password2:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def set_new_password(self):
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        user = CustomUser.objects.get(email=email)
        user.set_password(password)
        user.save()
