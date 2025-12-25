from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from core.models import (
    Category, Skill, UserProfile, Worker, Service,
    WorkPortfolio, Booking, Review, Message, Notification
)


# ============ User & Auth Serializers ============

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'user_type', 'phone', 'address', 'city', 'profile_image', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(choices=['client', 'worker'], default='client')

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'full_name', 'user_type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already registered."})
        
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        user_type = validated_data.pop('user_type')
        validated_data.pop('password2')
        
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )
        
        # Update user profile type
        user.profile.user_type = user_type
        user.profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user info serializer"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# ============ Category & Skill Serializers ============

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']


class CategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    worker_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_bn', 'slug', 'icon', 'description', 'is_active', 'skills', 'worker_count']
    
    def get_worker_count(self, obj):
        return obj.workers.filter(is_available=True).count()


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight category serializer for lists"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']


# ============ Worker Serializers ============

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration', 'image', 'is_featured', 'is_active']
        read_only_fields = ['id']


class WorkPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPortfolio
        fields = ['id', 'title', 'description', 'image', 'completed_date']
        read_only_fields = ['id']


class WorkerListSerializer(serializers.ModelSerializer):
    """Lightweight worker serializer for lists"""
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    categories = CategoryListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Worker
        fields = [
            'id', 'name', 'role', 'location', 'rating', 'total_reviews', 
            'total_jobs', 'hourly_rate', 'is_verified', 'is_available', 'photo', 'categories'
        ]
    
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.profile_photo and hasattr(obj.profile_photo, 'url'):
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class WorkerDetailSerializer(serializers.ModelSerializer):
    """Full worker detail serializer"""
    user = UserSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    categories = CategoryListSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    portfolio = WorkPortfolioSerializer(many=True, read_only=True)
    
    class Meta:
        model = Worker
        fields = [
            'id', 'user', 'name', 'role', 'bio', 'experience_years', 'hourly_rate',
            'location', 'service_areas', 'rating', 'total_reviews', 'total_jobs',
            'response_time', 'is_verified', 'is_available', 'photo',
            'categories', 'skills', 'services', 'portfolio', 'created_at'
        ]
    
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.profile_photo and hasattr(obj.profile_photo, 'url'):
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class WorkerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating worker profiles"""
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all()
    )
    skills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), required=False
    )
    
    class Meta:
        model = Worker
        fields = [
            'role', 'bio', 'experience_years', 'hourly_rate', 
            'location', 'service_areas', 'response_time', 
            'is_available', 'profile_photo', 'categories', 'skills'
        ]


# ============ Booking Serializers ============

class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight booking serializer"""
    client_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'title', 'client_name', 'worker_name', 'status',
            'scheduled_date', 'scheduled_time', 'estimated_price', 'created_at'
        ]
    
    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username
    
    def get_worker_name(self, obj):
        return obj.worker.user.get_full_name() or obj.worker.user.username


class BookingDetailSerializer(serializers.ModelSerializer):
    """Full booking detail serializer"""
    client = UserSerializer(read_only=True)
    worker = WorkerListSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'worker', 'service', 'title', 'description',
            'location', 'scheduled_date', 'scheduled_time', 'estimated_price',
            'final_price', 'status', 'created_at', 'updated_at', 'completed_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    worker_id = serializers.IntegerField(write_only=True)
    service_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Booking
        fields = [
            'worker_id', 'service_id', 'title', 'description',
            'location', 'scheduled_date', 'scheduled_time', 'estimated_price'
        ]
    
    def create(self, validated_data):
        worker_id = validated_data.pop('worker_id')
        service_id = validated_data.pop('service_id', None)
        
        worker = Worker.objects.get(id=worker_id)
        service = Service.objects.get(id=service_id) if service_id else None
        
        booking = Booking.objects.create(
            client=self.context['request'].user,
            worker=worker,
            service=service,
            **validated_data
        )
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status"""
    class Meta:
        model = Booking
        fields = ['status', 'final_price']


# ============ Review Serializers ============

class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    client_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'booking', 'worker', 'client_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'worker', 'created_at']
    
    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    booking_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['booking_id', 'rating', 'comment']
    
    def validate_booking_id(self, value):
        try:
            booking = Booking.objects.get(id=value)
            if booking.status != 'completed':
                raise serializers.ValidationError("Can only review completed bookings.")
            if hasattr(booking, 'review'):
                raise serializers.ValidationError("This booking already has a review.")
            return value
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found.")
    
    def create(self, validated_data):
        booking_id = validated_data.pop('booking_id')
        booking = Booking.objects.get(id=booking_id)
        
        review = Review.objects.create(
            booking=booking,
            worker=booking.worker,
            client=self.context['request'].user,
            **validated_data
        )
        return review


# ============ Message Serializers ============

class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'booking', 'sender_name', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'is_read', 'created_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for sending messages"""
    class Meta:
        model = Message
        fields = ['receiver', 'booking', 'content']
    
    def create(self, validated_data):
        message = Message.objects.create(
            sender=self.context['request'].user,
            **validated_data
        )
        return message


# ============ Notification Serializers ============

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'link', 'created_at']
        read_only_fields = ['id', 'notification_type', 'title', 'message', 'link', 'created_at']
