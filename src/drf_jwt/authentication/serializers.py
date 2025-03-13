from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Username already exists"
            )
        ],
    )

    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        refresh = RefreshToken.for_user(user)
        return {
            "message": "User created successfully",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        try:
            token = RefreshToken(refresh_token)
            return {"access": str(token.access_token)}
        except Exception:
            raise serializers.ValidationError(
                {"error": "Invalid or expired refresh token"}
            )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        if not refresh_token:
            raise serializers.ValidationError({"error": "needed refresh token"})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError(
                {"error": "Invalid or expired refresh token"}
            )

        return {"success": "way out is successful"}
