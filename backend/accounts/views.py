from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=request.data.get('email'))

            if user.role == 'caregiver':
                from caregivers.models import CaregiverProfile
                try:
                    verification_status = CaregiverProfile.objects.get(pk=user.pk).verification_status
                except CaregiverProfile.DoesNotExist:
                    verification_status = CaregiverProfile.VerificationStatus.PENDING

                if verification_status != CaregiverProfile.VerificationStatus.VERIFIED:
                    # Tokens were already issued by super().post(); blacklist the refresh
                    # token immediately so a blocked caregiver can't still use it.
                    try:
                        RefreshToken(response.data['refresh']).blacklist()
                    except TokenError:
                        pass
                    if verification_status == CaregiverProfile.VerificationStatus.REJECTED:
                        detail = 'Your caregiver application was rejected. Contact support for more information.'
                    else:
                        detail = 'Your account is pending admin verification. You will be able to log in once approved.'
                    return Response(
                        {'detail': detail, 'verification_status': verification_status},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            response.data['user'] = UserSerializer(user).data
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'})
        except TokenError:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
