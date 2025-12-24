from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend

from core.models import (
    Category, Skill, UserProfile, Worker, Service,
    WorkPortfolio, Booking, Review, Message, Notification
)
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer, LoginSerializer,
    ChangePasswordSerializer, UserUpdateSerializer,
    CategorySerializer, CategoryListSerializer, SkillSerializer,
    WorkerListSerializer, WorkerDetailSerializer, WorkerCreateUpdateSerializer,
    ServiceSerializer, WorkPortfolioSerializer,
    BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    ReviewSerializer, ReviewCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    NotificationSerializer
)
from .permissions import IsOwnerOrReadOnly, IsWorkerOwner, IsBookingParticipant


# ============ Auth Views ============

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Registration successful!',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'message': 'Login successful!',
                    'user': UserSerializer(user).data,
                    'profile': UserProfileSerializer(user.profile).data,
                    'token': token.key
                })
            else:
                return Response(
                    {'error': 'Invalid email or password.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'Logged out successfully.'})


class ChangePasswordView(generics.UpdateAPIView):
    """Change password endpoint"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Wrong old password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully.'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update current user profile"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user.profile
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Update user info if provided
        user_data = {}
        if 'first_name' in request.data:
            user_data['first_name'] = request.data['first_name']
        if 'last_name' in request.data:
            user_data['last_name'] = request.data['last_name']
        
        if user_data:
            for key, value in user_data.items():
                setattr(request.user, key, value)
            request.user.save()
        
        return Response(serializer.data)


# ============ Category Views ============

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Category list and detail endpoints"""
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    @action(detail=True, methods=['get'])
    def workers(self, request, slug=None):
        """Get workers in a category"""
        category = self.get_object()
        workers = category.workers.filter(is_available=True)
        serializer = WorkerListSerializer(workers, many=True, context={'request': request})
        return Response(serializer.data)


# ============ Worker Views ============

class WorkerViewSet(viewsets.ModelViewSet):
    """Worker CRUD endpoints"""
    queryset = Worker.objects.filter(is_available=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'role', 'location', 'bio']
    ordering_fields = ['rating', 'hourly_rate', 'total_jobs', 'created_at']
    filterset_fields = ['categories', 'location', 'is_verified']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkerListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return WorkerCreateUpdateSerializer
        return WorkerDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsWorkerOwner()]
    
    def perform_create(self, serializer):
        # Check if user already has a worker profile
        if hasattr(self.request.user, 'worker_profile'):
            raise serializers.ValidationError("You already have a worker profile.")
        
        serializer.save(user=self.request.user)
        
        # Update user profile type
        self.request.user.profile.user_type = 'worker'
        self.request.user.profile.save()
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get worker reviews"""
        worker = self.get_object()
        reviews = worker.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """Get worker services"""
        worker = self.get_object()
        services = worker.services.filter(is_active=True)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search workers with filters"""
        queryset = self.get_queryset()
        
        # Category filter
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(
                Q(categories__slug=category) | Q(categories__name__icontains=category)
            )
        
        # Location filter
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(
                Q(location__icontains=location) | Q(service_areas__icontains=location)
            )
        
        # Price range filter
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(hourly_rate__gte=min_price)
        if max_price:
            queryset = queryset.filter(hourly_rate__lte=max_price)
        
        # Rating filter
        min_rating = request.query_params.get('rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        
        # Sorting
        sort_by = request.query_params.get('sort', 'rating')
        if sort_by == 'price_low':
            queryset = queryset.order_by('hourly_rate')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-hourly_rate')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort_by == 'jobs':
            queryset = queryset.order_by('-total_jobs')
        
        serializer = WorkerListSerializer(queryset.distinct(), many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class MyWorkerProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update current user's worker profile"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WorkerCreateUpdateSerializer
        return WorkerDetailSerializer
    
    def get_object(self):
        return self.request.user.worker_profile


# ============ Service Views ============

class ServiceViewSet(viewsets.ModelViewSet):
    """Service CRUD for workers"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'worker_profile'):
            return self.request.user.worker_profile.services.all()
        return Service.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(worker=self.request.user.worker_profile)


# ============ Portfolio Views ============

class PortfolioViewSet(viewsets.ModelViewSet):
    """Portfolio CRUD for workers"""
    serializer_class = WorkPortfolioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'worker_profile'):
            return self.request.user.worker_profile.portfolio.all()
        return WorkPortfolio.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(worker=self.request.user.worker_profile)


# ============ Booking Views ============

class BookingViewSet(viewsets.ModelViewSet):
    """Booking CRUD endpoints"""
    permission_classes = [IsAuthenticated, IsBookingParticipant]
    
    def get_queryset(self):
        user = self.request.user
        
        # Workers see bookings where they're the worker
        if hasattr(user, 'worker_profile'):
            worker_bookings = Booking.objects.filter(worker=user.worker_profile)
            client_bookings = Booking.objects.filter(client=user)
            return (worker_bookings | client_bookings).distinct()
        
        # Clients see their own bookings
        return Booking.objects.filter(client=user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        if self.action == 'create':
            return BookingCreateSerializer
        if self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        return BookingDetailSerializer
    
    def perform_create(self, serializer):
        booking = serializer.save()
        
        # Create notification for worker
        Notification.objects.create(
            user=booking.worker.user,
            notification_type='booking',
            title='New Booking Request',
            message=f'{booking.client.get_full_name() or booking.client.username} requested a booking.',
            link=f'/bookings/{booking.id}/'
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Worker accepts booking"""
        booking = self.get_object()
        if booking.worker.user != request.user:
            return Response({'error': 'Only the worker can accept.'}, status=403)
        
        booking.status = 'accepted'
        booking.save()
        
        # Notify client
        Notification.objects.create(
            user=booking.client,
            notification_type='booking',
            title='Booking Accepted',
            message=f'{booking.worker.user.get_full_name()} accepted your booking.',
            link=f'/bookings/{booking.id}/'
        )
        
        return Response({'message': 'Booking accepted.'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark booking as completed"""
        booking = self.get_object()
        if booking.worker.user != request.user:
            return Response({'error': 'Only the worker can complete.'}, status=403)
        
        booking.status = 'completed'
        from django.utils import timezone
        booking.completed_at = timezone.now()
        booking.save()
        
        # Update worker stats
        worker = booking.worker
        worker.total_jobs += 1
        worker.save()
        
        return Response({'message': 'Booking completed.'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel booking"""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        
        return Response({'message': 'Booking cancelled.'})


# ============ Review Views ============

class ReviewViewSet(viewsets.ModelViewSet):
    """Review CRUD endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(client=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer


class WorkerReviewsView(generics.ListAPIView):
    """Get reviews for a specific worker"""
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        worker_id = self.kwargs.get('worker_id')
        return Review.objects.filter(worker_id=worker_id)


# ============ Message Views ============

class MessageViewSet(viewsets.ModelViewSet):
    """Message endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """Get list of conversations"""
        user = request.user
        messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('-created_at')
        
        # Get unique conversation partners
        conversations = {}
        for msg in messages:
            partner = msg.receiver if msg.sender == user else msg.sender
            if partner.id not in conversations:
                conversations[partner.id] = {
                    'user': UserSerializer(partner).data,
                    'last_message': msg.content,
                    'last_message_time': msg.created_at,
                    'unread_count': Message.objects.filter(
                        sender=partner, receiver=user, is_read=False
                    ).count()
                }
        
        return Response(list(conversations.values()))
    
    @action(detail=False, methods=['get'])
    def with_user(self, request):
        """Get messages with a specific user"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver_id=other_user_id)) |
            (Q(sender_id=other_user_id) & Q(receiver=request.user))
        ).order_by('created_at')
        
        # Mark as read
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


# ============ Notification Views ============

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """Notification endpoints"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.request.user.notifications.all()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read.'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({'message': 'All marked as read.'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = request.user.notifications.filter(is_read=False).count()
        return Response({'unread_count': count})


# ============ Dashboard Views ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for current user"""
    user = request.user
    
    if hasattr(user, 'worker_profile'):
        worker = user.worker_profile
        bookings = Booking.objects.filter(worker=worker)
        
        return Response({
            'type': 'worker',
            'total_bookings': bookings.count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'completed_jobs': worker.total_jobs,
            'rating': worker.rating,
            'total_reviews': worker.total_reviews,
            'total_earnings': bookings.filter(status='completed').aggregate(
                total=models.Sum('final_price')
            )['total'] or 0
        })
    else:
        bookings = Booking.objects.filter(client=user)
        
        return Response({
            'type': 'client',
            'total_bookings': bookings.count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'completed_bookings': bookings.filter(status='completed').count(),
        })
