from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from .serializer import UserSerializer, VerifyAccountSerializer, LoginSerializer
from .emails import send_otp_via_email
from .models import User

class RegisterAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                # Hash the password before saving
                user.set_password(data['password'])
                user.save()
                send_otp_via_email(serializer.data['email'])
                return Response({
                    'status': 200,
                    'message': 'Registration successful. Please check your email.',
                    'data': serializer.data,
                })
            else:
                return Response({
                    'status': 400,
                    'message': 'Something went wrong',
                    'data': serializer.errors,
                })
        except Exception as e:
            print(e)
            return Response({
                'status': 500,
                'message': 'Internal Server Error',
            })

class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)

            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']
                
                user = User.objects.filter(email=email)
                if not user.exists():
                     return Response({
                        'status': 400,
                        'message': 'Invalid email',
                    })
                
                user = user.first()
                if user.otp != otp:
                     return Response({
                        'status': 400,
                        'message': 'Wrong OTP',
                    })

                user.is_verified = True
                user.save()

                return Response({
                    'status': 200,
                    'message': 'Account verified',
                })
            else:
                return Response({
                    'status': 400,
                    'message': 'Invalid data',
                    'data': serializer.errors,
                })

        except Exception as e:
            print(e)
            return Response({
                'status': 500,
                'message': 'Internal Server Error',
            })


class LoginAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']
                
                user = authenticate(email=email, password=password)
                
                if user is not None:
                    login(request, user)
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        'status': 200,
                        'message': 'Login successful',
                        'token': token.key,
                    })
                else:
                    return Response({
                        'status': 400,
                        'message': 'Invalid credentials',
                    })
            else:
                return Response({
                    'status': 400,
                    'message': 'Invalid data',
                    'data': serializer.errors,
                })
        except Exception as e:
            print(e)
            return Response({
                'status': 500,
                'message': 'Internal Server Error',
            })
