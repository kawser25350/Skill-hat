from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'workers', views.WorkerViewSet, basename='worker')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'portfolio', views.PortfolioViewSet, basename='portfolio')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('auth/login/', views.LoginView.as_view(), name='api-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api-logout'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='api-change-password'),
    
    # Profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='api-profile'),
    path('profile/worker/', views.MyWorkerProfileView.as_view(), name='api-worker-profile'),
    
    # Worker reviews (public)
    path('workers/<int:worker_id>/reviews/', views.WorkerReviewsView.as_view(), name='worker-reviews'),
    
    # Dashboard
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    
    # Router URLs
    path('', include(router.urls)),
]
