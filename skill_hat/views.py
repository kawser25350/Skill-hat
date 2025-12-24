from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.db import transaction
from django.views.decorators.http import require_POST
from .forms import LoginForm, CustomerRegisterForm, WorkerRegisterForm
from core.models import Category, Worker, Service, Skill, Booking, UserProfile


def home(request):
    """Homepage with categories and featured workers"""
    from django.db.models import Count
    
    # Get categories with worker count
    categories = list(Category.objects.filter(is_active=True).annotate(
        workers_count=Count('workers', filter=Q(workers__is_available=True))
    ))
    
    # Create category batches for carousel (4 categories per slide)
    batch_size = 4
    category_batches = [categories[i:i+batch_size] for i in range(0, len(categories), batch_size)] if categories else []
    
    default_workers = Worker.objects.filter(is_available=True).order_by('-rating', '-total_jobs')[:8]
    
    # Convert workers to template-friendly format
    workers_data = []
    for worker in default_workers:
        workers_data.append({
            'id': worker.id,
            'name': worker.user.get_full_name() or worker.user.username,
            'role': worker.role,
            'category': worker.categories.first().slug if worker.categories.exists() else '',
            'price': float(worker.hourly_rate),
            'rating': worker.rating,
            'reviews': worker.total_reviews,
            'location': worker.location,
            'photo': worker.photo_url
        })
    
    data = {
        'user': request.user if request.user.is_authenticated else None,
        'categories': categories,
        'category_batches': category_batches,
        'default_workers': workers_data,
    }
    return render(request, 'pages/homepage.html', data)


def search_results(request):
    """Search workers by category, location, price, rating"""
    category = request.GET.get('category', '').lower()
    location = request.GET.get('location', '').lower()
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    rating = request.GET.get('rating', '')
    sort_by = request.GET.get('sort', 'relevance')
    
    # Start with all available workers
    workers_qs = Worker.objects.filter(is_available=True)
    
    # Filter by category
    if category and category != 'choose category':
        workers_qs = workers_qs.filter(
            Q(categories__slug__iexact=category) | Q(categories__name__icontains=category)
        )
    
    # Filter by location
    if location:
        workers_qs = workers_qs.filter(
            Q(location__icontains=location) | Q(service_areas__icontains=location)
        )
    
    # Filter by price range
    if min_price:
        try:
            workers_qs = workers_qs.filter(hourly_rate__gte=int(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            workers_qs = workers_qs.filter(hourly_rate__lte=int(max_price))
        except ValueError:
            pass
    
    # Filter by rating
    if rating:
        try:
            workers_qs = workers_qs.filter(rating__gte=float(rating))
        except ValueError:
            pass
    
    # Sort results
    if sort_by == 'price_low':
        workers_qs = workers_qs.order_by('hourly_rate')
    elif sort_by == 'price_high':
        workers_qs = workers_qs.order_by('-hourly_rate')
    elif sort_by == 'rating':
        workers_qs = workers_qs.order_by('-rating')
    else:
        workers_qs = workers_qs.order_by('-rating', '-total_jobs')
    
    # Convert to template-friendly format
    workers_data = []
    for worker in workers_qs.distinct():
        workers_data.append({
            'id': worker.id,
            'name': worker.user.get_full_name() or worker.user.username,
            'role': worker.role,
            'category': worker.categories.first().slug if worker.categories.exists() else '',
            'price': float(worker.hourly_rate),
            'rating': worker.rating,
            'reviews': worker.total_reviews,
            'location': worker.location,
            'photo': worker.photo_url
        })
    
    # Get all active categories for filter dropdown
    all_categories = Category.objects.filter(is_active=True)
    
    data = {
        'user': request.user if request.user.is_authenticated else None,
        'workers': workers_data,
        'total_results': len(workers_data),
        'categories': all_categories,
        'category': category if category else '',
        'location': location if location else '',
        'min_price': min_price if min_price else '',
        'max_price': max_price if max_price else '',
        'rating': rating if rating else '',
        'sort_by': sort_by,
    }
    return render(request, 'pages/search_results.html', data)



def login_view(request):
    """User login view - works for both customers and workers"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get the next URL to redirect after login
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate using email
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    
                    # Check user type and redirect accordingly
                    try:
                        profile = user.profile
                        user_type = profile.user_type
                    except UserProfile.DoesNotExist:
                        user_type = 'client'
                    
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    
                    # Redirect to next URL if provided, otherwise dashboard
                    next_url = request.POST.get('next', '')
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'pages/login_page.html', {'form': form, 'next': next_url})


def customer_register_view(request):
    """Customer registration view - simple signup for people who want to hire workers"""
    if request.user.is_authenticated:
        return redirect('home')
    
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                
                # Create UserProfile as customer
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.user_type = 'client'
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()
                
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to Skill-হাট!')
                
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomerRegisterForm()
    
    return render(request, 'pages/customer_register.html', {'form': form, 'next': next_url})


def worker_register_view(request):
    """Worker registration view - for people who want to offer services"""
    if request.user.is_authenticated:
        return redirect('home')
    
    categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = WorkerRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                
                # Create UserProfile as worker (no profile_image for workers - use Worker.profile_photo instead)
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.user_type = 'worker'
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()
                
                # Create Worker profile
                worker = Worker.objects.create(
                    user=user,
                    role=form.cleaned_data['role'],
                    bio=form.cleaned_data.get('bio', ''),
                    hourly_rate=form.cleaned_data['hourly_rate'],
                    location=form.cleaned_data['location'],
                    experience_years=form.cleaned_data.get('experience_years') or 0,
                    is_available=True,
                )
                
                # Add category
                category = form.cleaned_data['category']
                worker.categories.add(category)
                
                # Handle photo - save to Worker.profile_photo only
                if 'photo' in request.FILES:
                    worker.profile_photo = request.FILES['photo']
                    worker.save()
                
                login(request, user)
                messages.success(request, 'Registration successful! Your worker profile is now active!')
                return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = WorkerRegisterForm()
    
    return render(request, 'pages/worker_register.html', {'form': form, 'categories': categories})


def register_view(request):
    """Registration choice page - choose between customer and worker"""
    if request.user.is_authenticated:
        return redirect('home')
    
    next_url = request.GET.get('next', '')
    return render(request, 'pages/register_page.html', {'next': next_url})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def profile_view(request, worker_id):
    """Worker profile view using real database"""
    worker = get_object_or_404(Worker, id=worker_id)
    services = worker.services.filter(is_active=True)
    portfolio = worker.portfolio.all()[:6]
    reviews = worker.reviews.all()[:10]
    
    # Get skills
    skills = list(worker.skills.values_list('name', flat=True))
    if not skills:
        # Get skills from category if worker hasn't added specific skills
        for category in worker.categories.all():
            skills.extend(list(category.skills.values_list('name', flat=True)[:5]))
    
    worker_data = {
        'id': worker.id,
        'name': worker.user.get_full_name() or worker.user.username,
        'role': worker.role,
        'price': str(int(worker.hourly_rate)),
        'rating': str(worker.rating),
        'location': worker.location,
        'photo': worker.photo_url,
        'experience': worker.experience_years,
        'jobs_completed': worker.total_jobs,
        'review_count': worker.total_reviews,
        'response_time': worker.response_time,
        'description': worker.bio,
        'is_verified': worker.is_verified,
        'skills': skills[:7],
        'featured_services': [
            {
                'name': service.name,
                'price': str(int(service.price)),
                'image': service.image.url if service.image else worker.photo_url
            } for service in services.filter(is_featured=True)[:2]
        ],
        'recent_works': [
            {
                'title': work.title,
                'description': work.description[:50] if work.description else '',
                'image': work.image.url if work.image else worker.photo_url
            } for work in portfolio
        ],
        'reviews': [
            {
                'client_name': review.client.get_full_name() or review.client.username,
                'rating': review.rating,
                'comment': review.comment,
                'date': review.created_at
            } for review in reviews
        ]
    }
    
    # Add default services if none exist
    if not worker_data['featured_services']:
        worker_data['featured_services'] = [
            {'name': f'{worker.role} - Basic', 'price': str(int(worker.hourly_rate * 2)), 'image': worker.photo_url},
            {'name': f'{worker.role} - Premium', 'price': str(int(worker.hourly_rate * 5)), 'image': worker.photo_url},
        ]
    
    # Add default recent works if none exist
    if not worker_data['recent_works']:
        worker_data['recent_works'] = [
            {'title': 'Recent Project 1', 'description': 'Completed with excellence', 'image': worker.photo_url},
            {'title': 'Recent Project 2', 'description': 'Satisfied client', 'image': worker.photo_url},
        ]
    
    return render(request, 'pages/profile.html', {
        'worker': worker_data,
        'user': request.user if request.user.is_authenticated else None,
    })


@login_required
def dashboard_view(request):
    """User dashboard - view orders, manage profile, become a worker"""
    user = request.user
    
    # Check if user is a worker
    try:
        worker = Worker.objects.get(user=user)
        is_worker = True
    except Worker.DoesNotExist:
        worker = None
        is_worker = False
    
    # Get user profile
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Get all categories and skills for the become worker form
    categories = Category.objects.filter(is_active=True)
    all_skills = Skill.objects.all()
    
    # Stats for dashboard
    if is_worker:
        # Worker stats - orders received
        bookings = Booking.objects.filter(worker=worker).order_by('-created_at')
        pending_orders = bookings.filter(status='pending').count()
        in_progress_orders = bookings.filter(status='in_progress').count()
        completed_orders = bookings.filter(status='completed').count()
        total_orders = bookings.count()
        total_earnings = sum(b.service.price for b in bookings.filter(status='completed') if b.service)
        
        stats = {
            'total_bookings': total_orders,
            'pending_bookings': pending_orders,
            'in_progress_bookings': in_progress_orders,
            'completed_jobs': completed_orders,
            'total_earnings': total_earnings,
            'rating': worker.rating,
            'total_reviews': worker.total_reviews,
        }
    else:
        # Client stats - orders placed
        bookings = Booking.objects.filter(client=user).order_by('-created_at')
        pending_orders = bookings.filter(status='pending').count()
        in_progress_orders = bookings.filter(status='in_progress').count()
        completed_orders = bookings.filter(status='completed').count()
        total_orders = bookings.count()
        
        stats = {
            'total_bookings': total_orders,
            'pending_bookings': pending_orders,
            'in_progress_bookings': in_progress_orders,
            'completed_bookings': completed_orders,
        }
    
    context = {
        'user': user,
        'profile': profile,
        'is_worker': is_worker,
        'worker': worker,
        'bookings': bookings[:20],  # Last 20 bookings
        'stats': stats,
        'categories': categories,
        'all_skills': all_skills,
    }
    
    # Render different dashboard based on user type
    if is_worker:
        return render(request, 'pages/worker_dashboard.html', context)
    else:
        return render(request, 'pages/customer_dashboard.html', context)


@login_required
@require_POST
def update_profile_view(request):
    """Update user profile"""
    user = request.user
    
    with transaction.atomic():
        # Update user info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        
        # Check if user is a worker
        try:
            worker = Worker.objects.get(user=user)
            is_worker = True
        except Worker.DoesNotExist:
            worker = None
            is_worker = False
        
        # Handle profile photo upload - save to Worker.profile_photo for workers, UserProfile.profile_image for customers
        if 'profile_image' in request.FILES:
            if is_worker:
                worker.profile_photo = request.FILES['profile_image']
            else:
                profile.profile_image = request.FILES['profile_image']
        
        profile.save()
        
        # If user is a worker, update worker info too
        if is_worker:
            worker.location = request.POST.get('address', worker.location)
            worker.save()
    
    messages.success(request, 'Profile updated successfully!')
    return redirect('dashboard')


@login_required
@require_POST
def become_worker_view(request):
    """Convert a regular user to a worker"""
    user = request.user
    
    # Check if already a worker
    if Worker.objects.filter(user=user).exists():
        messages.warning(request, 'You are already registered as a worker!')
        return redirect('dashboard')
    
    # Get form data
    role = request.POST.get('role', '')
    bio = request.POST.get('bio', '')
    hourly_rate = request.POST.get('hourly_rate', 15)
    location = request.POST.get('location', '')
    experience_years = request.POST.get('experience_years', 0)
    
    # Handle both single category and multiple categories
    category_id = request.POST.get('category')
    category_ids = request.POST.getlist('categories')
    if category_id:
        category_ids.append(category_id)
    
    skill_ids = request.POST.getlist('skills')
    
    # Create worker profile
    worker = Worker.objects.create(
        user=user,
        role=role,
        bio=bio,
        hourly_rate=hourly_rate,
        location=location,
        experience_years=experience_years or 0,
        is_available=True,
    )
    
    # Handle photo upload
    if 'photo' in request.FILES:
        worker.profile_photo = request.FILES['photo']
        worker.save()
    
    # Add categories
    if category_ids:
        categories = Category.objects.filter(id__in=category_ids)
        worker.categories.set(categories)
    
    # Add skills
    if skill_ids:
        skills = Skill.objects.filter(id__in=skill_ids)
        worker.skills.set(skills)
    
    messages.success(request, 'Congratulations! You are now registered as a worker. Start getting orders!')
    return redirect('dashboard')


@login_required
@require_POST
def update_worker_profile_view(request):
    """Update worker-specific profile details"""
    user = request.user
    
    try:
        worker = Worker.objects.get(user=user)
    except Worker.DoesNotExist:
        messages.error(request, 'You are not registered as a worker.')
        return redirect('dashboard')
    
    with transaction.atomic():
        # Update user info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        
        # Update profile phone
        try:
            profile = user.profile
            profile.phone = request.POST.get('phone', profile.phone)
            profile.save()
        except UserProfile.DoesNotExist:
            pass
        
        # Update worker info
        worker.role = request.POST.get('role', worker.role)
    worker.bio = request.POST.get('bio', worker.bio)
    worker.hourly_rate = request.POST.get('hourly_rate', worker.hourly_rate)
    worker.location = request.POST.get('location', worker.location)
    worker.experience_years = request.POST.get('experience_years', worker.experience_years)
    worker.is_available = request.POST.get('is_available') == 'on'
    
    # Handle photo upload
    if 'photo' in request.FILES:
        worker.profile_photo = request.FILES['photo']
    
    worker.save()
    
    # Update categories
    category_ids = request.POST.getlist('categories')
    if category_ids:
        categories = Category.objects.filter(id__in=category_ids)
        worker.categories.set(categories)
    
    # Update skills
    skill_ids = request.POST.getlist('skills')
    if skill_ids:
        skills = Skill.objects.filter(id__in=skill_ids)
        worker.skills.set(skills)
    
    messages.success(request, 'Worker profile updated successfully!')
    return redirect('dashboard')


@login_required
@require_POST
def booking_action_view(request, booking_id):
    """Handle booking actions (accept, decline, complete)"""
    user = request.user
    action = request.POST.get('action', '')
    
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permissions
    try:
        worker = Worker.objects.get(user=user)
        is_worker = booking.worker == worker
    except Worker.DoesNotExist:
        is_worker = False
    
    is_client = booking.client == user
    
    if not is_worker and not is_client:
        messages.error(request, 'You do not have permission to modify this booking.')
        return redirect('dashboard')
    
    # Handle actions
    if action == 'accept' and is_worker:
        booking.status = 'confirmed'
        messages.success(request, 'Booking accepted!')
    elif action == 'decline' and is_worker:
        booking.status = 'cancelled'
        messages.info(request, 'Booking declined.')
    elif action == 'start' and is_worker:
        booking.status = 'in_progress'
        messages.success(request, 'Work started!')
    elif action == 'complete' and is_worker:
        booking.status = 'completed'
        messages.success(request, 'Job marked as completed!')
    elif action == 'cancel' and is_client:
        booking.status = 'cancelled'
        messages.info(request, 'Booking cancelled.')
    
    booking.save()
    return redirect('dashboard')



