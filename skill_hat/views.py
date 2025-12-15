from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm, RegisterForm


def home(request):
    # Create default worker data
    default_workers = [
        {
            'id': 1,
            'name': 'Jahid Hasan',
            'role': 'Cleaning Expert',
            'price': '500',
            'rating': '4.8 (120 reviews)',
            'location': 'Dhaka',
            'photo': {'url': '/static/images/jihad.jpg'}
        },
        {
            'id': 2,
            'name': 'Kawser Ahmed',
            'role': 'Plumber',
            'price': '600',
            'rating': '4.9 (95 reviews)',
            'location': 'Chittagong',
            'photo': {'url': '/static/images/kawser.jpg'}
        },
        {
            'id': 3,
            'name': 'Sanaullah Khan',
            'role': 'Electrician',
            'price': '700',
            'rating': '4.7 (80 reviews)',
            'location': 'Sylhet',
            'photo': {'url': '/static/images/sanaullah.jpg'}
        },
        {
            'id': 4,
            'name': 'Rahman Ali',
            'role': 'Carpenter',
            'price': '550',
            'rating': '4.6 (110 reviews)',
            'location': 'Dhaka',
            'photo': {'url': '/static/images/jihad.jpg'}
        }
    ]
    
    data = {
        'name': 'kawser',
         'age': 23,
         'gender': 'male',
         'default_workers': default_workers,
    }
    return render(request, 'pages/homepage.html', data)



def login_view(request):
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
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'pages/login_page.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Skill-হাট!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegisterForm()
    
    return render(request, 'pages/register_page.html', {'form': form})


def profile_view(request, worker_id):
    # Get worker data from the default workers list with full profile information
    default_workers = [
        {
            'id': 1,
            'name': 'Jahid Hasan',
            'role': 'Cleaning Expert',
            'price': '500',
            'rating': '4.8',
            'location': 'Dhaka',
            'photo': '/static/images/jihad.jpg',
            'experience': 8,
            'jobs_completed': 320,
            'review_count': 120,
            'response_time': 'Within 2 hours',
            'description': 'I\'m a professional Cleaning Expert with over 8 years of experience in providing high-quality cleaning services. I specialize in residential and commercial cleaning, deep cleaning, and post-construction cleaning. My commitment to excellence ensures that every project is completed to the highest standards with attention to detail.',
            'skills': ['Deep Cleaning', 'Residential Cleaning', 'Commercial Cleaning', 'Post-Construction Cleaning', 'Eco-Friendly Methods', 'Time Management', 'Attention to Detail'],
            'featured_services': [
                {'name': 'Deep Clean', 'price': '5000', 'image': '/static/images/jihad.jpg'},
                {'name': 'Regular Clean', 'price': '2000', 'image': '/static/images/jihad.jpg'},
            ],
            'recent_works': [
                {'title': 'Office Deep Clean', 'description': 'Completed with excellence', 'image': '/static/images/jihad.jpg'},
                {'title': 'Home Cleaning', 'description': 'Satisfied clients', 'image': '/static/images/jihad.jpg'},
                {'title': 'Post-Construction', 'description': 'Professional finish', 'image': '/static/images/jihad.jpg'},
            ]
        },
        {
            'id': 2,
            'name': 'Kawser Ahmed',
            'role': 'Plumber',
            'price': '600',
            'rating': '4.9',
            'location': 'Chittagong',
            'photo': '/static/images/kawser.jpg',
            'experience': 10,
            'jobs_completed': 450,
            'review_count': 95,
            'response_time': 'Within 1 hour',
            'description': 'I\'m an experienced Plumber with 10 years in the industry. I handle all types of plumbing jobs including installations, repairs, maintenance, and emergency services. I use only quality materials and provide reliable, efficient solutions for residential and commercial properties.',
            'skills': ['Pipe Installation', 'Leak Repair', 'Drain Cleaning', 'Water Heater Service', 'Emergency Repair', 'Maintenance', 'PVC & Copper Pipes'],
            'featured_services': [
                {'name': 'Emergency Repair', 'price': '1000', 'image': '/static/images/kawser.jpg'},
                {'name': 'Pipe Installation', 'price': '3000', 'image': '/static/images/kawser.jpg'},
            ],
            'recent_works': [
                {'title': 'Bathroom Plumbing', 'description': 'Complete installation', 'image': '/static/images/kawser.jpg'},
                {'title': 'Kitchen Repairs', 'description': 'Leak fixed quickly', 'image': '/static/images/kawser.jpg'},
                {'title': 'Water System', 'description': 'Full replacement done', 'image': '/static/images/kawser.jpg'},
            ]
        },
        {
            'id': 3,
            'name': 'Sanaullah Khan',
            'role': 'Electrician',
            'price': '700',
            'rating': '4.7',
            'location': 'Sylhet',
            'photo': '/static/images/sanaullah.jpg',
            'experience': 12,
            'jobs_completed': 380,
            'review_count': 80,
            'response_time': 'Within 2 hours',
            'description': 'Certified Electrician with 12 years of professional experience. I provide comprehensive electrical services including installations, repairs, upgrades, and maintenance for residential and commercial clients. Safety and quality are my top priorities.',
            'skills': ['Wiring Installation', 'Panel Repair', 'Circuit Breaker Service', 'Lighting Design', 'Safety Inspection', 'Power Outlet Installation', 'Industrial Electrical'],
            'featured_services': [
                {'name': 'Wiring Installation', 'price': '4000', 'image': '/static/images/sanaullah.jpg'},
                {'name': 'Panel Service', 'price': '2000', 'image': '/static/images/sanaullah.jpg'},
            ],
            'recent_works': [
                {'title': 'Home Rewiring', 'description': 'Complete new wiring', 'image': '/static/images/sanaullah.jpg'},
                {'title': 'Light Installation', 'description': 'Modern lighting setup', 'image': '/static/images/sanaullah.jpg'},
                {'title': 'Safety Inspection', 'description': 'All systems passed', 'image': '/static/images/sanaullah.jpg'},
            ]
        },
        {
            'id': 4,
            'name': 'Rahman Ali',
            'role': 'Carpenter',
            'price': '550',
            'rating': '4.6',
            'location': 'Dhaka',
            'photo': '/static/images/jihad.jpg',
            'experience': 9,
            'jobs_completed': 290,
            'review_count': 110,
            'response_time': 'Within 3 hours',
            'description': 'Skilled Carpenter with 9 years of experience in custom woodwork and furniture making. I specialize in creating beautiful and functional pieces from design to installation. I work with various wood types and finishes to match your style and budget.',
            'skills': ['Custom Furniture', 'Cabinet Making', 'Wood Finishing', 'Door & Window Installation', 'Renovation Work', 'Design Consultation', 'Quality Craftsmanship'],
            'featured_services': [
                {'name': 'Custom Furniture', 'price': '8000', 'image': '/static/images/jihad.jpg'},
                {'name': 'Cabinet Making', 'price': '6000', 'image': '/static/images/jihad.jpg'},
            ],
            'recent_works': [
                {'title': 'Bedroom Set', 'description': 'Custom design created', 'image': '/static/images/jihad.jpg'},
                {'title': 'Kitchen Cabinet', 'description': 'Modern finish applied', 'image': '/static/images/jihad.jpg'},
                {'title': 'Door Installation', 'description': 'Professional fit', 'image': '/static/images/jihad.jpg'},
            ]
        }
    ]
    
    # Find worker by id
    worker = next((w for w in default_workers if w['id'] == worker_id), None)
    
    if worker is None:
        messages.error(request, 'Worker not found.')
        return redirect('home')
    
    return render(request, 'pages/profile.html', {'worker': worker})



