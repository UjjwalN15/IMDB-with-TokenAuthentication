from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .validators import validate_password, contact_validator
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300, validators=[MinLengthValidator(8), validate_password])
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    age = models.IntegerField()
    username = models.CharField(max_length=300, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')])
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=10, help_text="Enter a 10-digit contact number", validators=[contact_validator])
    name = models.CharField(max_length=600, blank=True, editable=False)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        self.name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        Watchlist.objects.filter(user=self).delete()
        super().delete(*args, **kwargs)


    def __str__(self):
        return self.email

class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    
    def __str__(self):
        return self.name
    

class Movies(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_year = models.DateField()
    active = models.BooleanField(default=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='movies')
    added_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    @property
    def rating(self):
        avg_rating = self.reviews.aggregate(average=Avg('ratings'))['average']
        return avg_rating if avg_rating is not None else 3.5
    
class Reviews(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=200)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, related_name='reviews')
    ratings = models.FloatField()
    comment = models.TextField()
    added_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (self.movie.title + ' => ' + str(self.ratings)+ '  rating')
    
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, related_name='watchlist')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
    def __str__(self):
        return self.movie.title