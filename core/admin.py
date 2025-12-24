from django.contrib import admin
from .models import (
    Category, Skill, UserProfile, Worker, Service, 
    WorkPortfolio, Booking, Review, Message, Notification
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'city', 'created_at']
    list_filter = ['user_type', 'city']
    search_fields = ['user__username', 'user__email', 'phone']


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


class WorkPortfolioInline(admin.TabularInline):
    model = WorkPortfolio
    extra = 1


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'location', 'rating', 'total_jobs', 'is_verified', 'is_available']
    list_filter = ['is_verified', 'is_available', 'categories', 'location']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'role', 'location']
    filter_horizontal = ['categories', 'skills']
    inlines = [ServiceInline, WorkPortfolioInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'worker', 'price', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    search_fields = ['name', 'worker__user__username']


@admin.register(WorkPortfolio)
class WorkPortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'worker', 'completed_date', 'created_at']
    search_fields = ['title', 'worker__user__username']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'worker', 'status', 'scheduled_date', 'estimated_price', 'created_at']
    list_filter = ['status', 'scheduled_date', 'created_at']
    search_fields = ['client__username', 'worker__user__username', 'title']
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['worker', 'client', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['worker__user__username', 'client__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'content']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']
