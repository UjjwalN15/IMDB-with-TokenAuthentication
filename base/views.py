from django.shortcuts import render
from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from .emails import *
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .validators import CustomPasswordValidator
from rest_framework.authtoken.models import Token
# Create your views here.

class MoviesApiViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movies.objects.all()
    filterset_fields = ['platform','active']
    search_fields = ['title']
    
class MovieGenreApiView(viewsets.ModelViewSet):
    serializer_class = MovieGenreSerializer
    queryset = MovieGenre.objects.all()

class PlatformApiViewSet(viewsets.ModelViewSet):
    serializer_class = PlatformSerializer
    queryset = Platform.objects.all()
    filterset_fields = ['name']
    search_fields = ['name']
    
class ReviewsApiViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Reviews.objects.all()
    # send_email_for_review_added(serializer_class.data['email','movie.title','ratings'])
    def perform_create(self, serializer):
        review = serializer.save()  # Save the review and get the instance
        # Send email after review is successfully created
        send_email_for_review_added(review.email, review.movie.title, review.ratings)
      
class ReviewsApiViewSetDetails(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        movie_id = self.kwargs['pk']
        return Reviews.objects.filter(movie_id=movie_id)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        password = request.data.get('password')
        phone = request.data.get('phone')
        if User.objects.filter(phone=phone).exists():
            return Response({'phone': ['Phone number already exists.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Validate the password
            CustomPasswordValidator().validate(password)
            # If valid, hash the password
            hash_password = make_password(password)
            
            # Save the user instance
            user = serializer.save()
            user.password = hash_password
            user.save()
            send_otp_for_verification_email(serializer.data['email'])
            return Response({'message': 'Registration Successful. Please Check your email for Email Validation OTP'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # If password validation fails, return the errors
            return Response({'password': e.messages}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)
            
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                otp = serializer.validated_data.get('otp')
                
                user = User.objects.filter(email=email)
                if not user.exists():
                    return Response({
                        'status': 400,
                        'message': 'User not found',
                        'data': 'Invalid email address provided.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if user[0].otp != otp:
                    return Response({
                        'status': 400,
                        'message': 'Invalid OTP',
                        'data': 'The OTP you entered is incorrect.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user = user.first()
                user.is_email_verified = True
                user.save()
                
                return Response({
                    'status': 200,
                    'message': 'Account Verified',
                    'data': {'Email Verified. Now you can login by the email and password.'}
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 400,
                'message': 'Invalid data',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except KeyError as ke:
            return Response({
                'status': 500,
                'message': 'Missing key in serializer data',
                'data': str(ke)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({
                'status': 500,
                'message': 'Internal server error',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=email, password=password)
    if user is None:
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_404_NOT_FOUND)
    
    if not user.is_email_verified:
        return Response({'detail': 'Please verify your email to login.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)
        
@permission_classes([IsAuthenticated])
class LogoutView(APIView):
    def post(self, request, format=None):
        # Delete the token to force a logout
        request.user.auth_token.delete()
        return Response({"detail": "Logout Successful"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_watchlist(request,pk):
    try:
        movie = Movies.objects.get(pk=pk)
    except Movies.DoesNotExist:
        return Response({'error':'Movie not found.'},status=status.HTTP_404_NOT_FOUND)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    
    if created:
        send_mail_add_to_watchlist(request.user.email, movie.title)
        return Response({'message':f'{movie.title} added to watchlist.'},status=status.HTTP_201_CREATED)
    else:
        return Response({'message':f'{movie.title} already in watchlist.'},status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    movies = [item.movie for item in watchlist_items]
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_watchlist(request,pk):
    try:
        watchlist_item = Watchlist.objects.get(user=request.user, movie_id=pk)
    except Watchlist.DoesNotExist:
        return Response({'error':'Movie not found in watchlist.'},status=status.HTTP_404_NOT_FOUND)
    watchlist_item.delete()
    send_mail_delete_watchlist(request.user.email, watchlist_item.movie.title)
    return Response({'message':f'{watchlist_item.movie.title} deleted from watchlist.'},status=status.HTTP_204_NO_CONTENT)