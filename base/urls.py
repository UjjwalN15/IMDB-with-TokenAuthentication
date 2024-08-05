from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('movies/', MoviesApiViewSet.as_view({'get': 'list', 'post':'create'}), name='movies'),
    path('movies/<int:pk>/', MoviesApiViewSet.as_view({'get': 'retrieve', 'put':'update','patch': 'partial_update', 'delete':'destroy'}),name='movies_detail'),
    path('platform/', PlatformApiViewSet.as_view({'get': 'list', 'post':'create'}), name='platform'),
    path('platform/<int:pk>/', PlatformApiViewSet.as_view({'get':'retrieve','put':'update','patch':'partial_update','delete':'destroy'}), name='platform_detail'),
    path('reviews/', ReviewsApiViewSet.as_view({'post':'create'}), name='reviews'),
    path('reviews/<int:pk>/', ReviewsApiViewSet.as_view({'put':'update','patch':'partial_update','delete':'destroy'}), name='reviews_detail'),
    path('movies/<int:pk>/reviews/', ReviewsApiViewSetDetails.as_view(), name='movie_review'),
    path('register/', register, name='register'),
    path('verify/', VerifyOTP.as_view(), name='verify'),
    path('login/', Login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('watchlist/', WatchlistViewSet.as_view(), name='watchlist'),
    path('add_to_watchlist/<int:pk>/', add_to_watchlist, name='add_to_watchlist'),
    path('view_watchlist/',view_watchlist, name='view_watchlist'),
    path('delete_watchlist/<int:pk>/',delete_watchlist, name='delete_watchlist'),
]