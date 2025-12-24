from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Service categories like Cleaning, Plumbing, etc."""
    name = models.CharField(max_length=100)
    name_bn = models.CharField(max_length=100, blank=True, help_text="Bengali name")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Category image for carousel")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Skills that workers can have"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='skills')

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile for all users"""
    USER_TYPE_CHOICES = [
        ('client', 'Client'),
        ('worker', 'Worker'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"


class Worker(models.Model):
    """Worker/Expert profile with all details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    categories = models.ManyToManyField(Category, related_name='workers')
    skills = models.ManyToManyField(Skill, related_name='workers', blank=True)
    
    # Professional info
    role = models.CharField(max_length=100, help_text="e.g., Cleaning Expert, Plumber")
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Location
    location = models.CharField(max_length=200)
    service_areas = models.TextField(blank=True, help_text="Areas where worker provides service")
    
    # Stats
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    total_jobs = models.PositiveIntegerField(default=0)
    response_time = models.CharField(max_length=50, default="Within 2 hours")
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # Media
    profile_photo = models.ImageField(upload_to='workers/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-total_jobs']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role}"
    
    @property
    def photo_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        return None


class Service(models.Model):
    """Services offered by workers"""
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True, help_text="e.g., 2-3 hours")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.worker}"


class WorkPortfolio(models.Model):
    """Portfolio/Recent works of workers"""
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='portfolio')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/')
    completed_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Work Portfolios"

    def __str__(self):
        return f"{self.title} - {self.worker}"


class Booking(models.Model):
    """Booking/Order between client and worker"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Booking details
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    
    # Pricing
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.client.username} → {self.worker}"


class Review(models.Model):
    """Reviews for workers"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.client.username} for {self.worker} - {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update worker's average rating
        worker = self.worker
        reviews = worker.reviews.all()
        if reviews.exists():
            worker.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            worker.total_reviews = reviews.count()
            worker.save()


class Message(models.Model):
    """Messages between client and worker"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class Notification(models.Model):
    """Notifications for users"""
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('message', 'Message'),
        ('review', 'Review'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
