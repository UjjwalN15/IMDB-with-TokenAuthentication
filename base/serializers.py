from rest_framework import serializers
from .models import *
from .validators import validate_password, contact_validator
from django.core.exceptions import ValidationError

class PlatformSerializer(serializers.ModelSerializer):
    # For Hyperlinked movies
    # movies = serializers.HyperlinkedRelatedField(view_name='movies_detail',  # Name of the view that provides the URL for Movies many=True,read_only=True
    # many=True, read_only=True)
    movies = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Platform
        fields = '__all__'
        
class ReviewSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['movie'] = instance.movie.title if instance.movie else None
        return representation
    class Meta:
        model = Reviews
        fields = ['id','movie', 'email', 'full_name','ratings','comment','added_date']
        
    def validate_ratings(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Ratings should be between 1 and 10")
        return value
    
class MovieGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieGenre
        fields = '__all__'
class MovieSerializer(serializers.ModelSerializer):
    # platform = serializers.StringRelatedField()
    # genre = serializers.StringRelatedField(many=True, read_only=True)
    genre = serializers.PrimaryKeyRelatedField(queryset=MovieGenre.objects.all(), many=True)
    rating = serializers.ReadOnlyField()
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['platform'] = instance.platform.name if instance.platform else None
        representation['genre'] = [genre.name for genre in instance.genre.all()]  # Display genre names in output
        return representation
    class Meta:
        model = Movies
        fields = ['id','title','description','rating','release_year','genre','active','link','platform','added_date','updated_date']
    # platform = PlatformSerializer()
    
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(required=True, validators=[contact_validator])

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'name', 'age', 'gender', 'address', 'phone', 'is_email_verified')

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class WatchlistSerializer(serializers.ModelSerializer):
    movie = serializers.CharField(source='movie.title', read_only=True)  # Assuming you have a MovieSerializer

    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'added_on']