from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Skill, Worker, Service, WorkPortfolio


class Command(BaseCommand):
    help = 'Seeds the database with initial categories, skills, and sample workers'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create Categories
        categories_data = [
            {'name': 'Cleaning', 'name_bn': 'পরিষ্কার', 'slug': 'cleaning', 'icon': 'fa-broom'},
            {'name': 'Plumbing', 'name_bn': 'প্লাম্বিং', 'slug': 'plumbing', 'icon': 'fa-wrench'},
            {'name': 'Electrical', 'name_bn': 'ইলেকট্রিক্যাল', 'slug': 'electrical', 'icon': 'fa-bolt'},
            {'name': 'Carpentry', 'name_bn': 'কার্পেন্টারি', 'slug': 'carpentry', 'icon': 'fa-hammer'},
            {'name': 'Painting', 'name_bn': 'পেইন্টিং', 'slug': 'painting', 'icon': 'fa-paint-roller'},
            {'name': 'Gardening', 'name_bn': 'বাগান', 'slug': 'gardening', 'icon': 'fa-leaf'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')
        
        # Create Skills for each category
        skills_data = {
            'cleaning': ['Deep Cleaning', 'Residential Cleaning', 'Commercial Cleaning', 'Post-Construction Cleaning', 'Carpet Cleaning'],
            'plumbing': ['Pipe Installation', 'Leak Repair', 'Drain Cleaning', 'Water Heater Service', 'Emergency Repair'],
            'electrical': ['Wiring Installation', 'Panel Repair', 'Lighting', 'Safety Inspection', 'Power Outlet Installation'],
            'carpentry': ['Custom Furniture', 'Cabinet Making', 'Door Installation', 'Wood Finishing', 'Renovation Work'],
            'painting': ['Interior Painting', 'Exterior Painting', 'Wall Texturing', 'Color Consultation', 'Spray Painting'],
            'gardening': ['Lawn Maintenance', 'Tree Trimming', 'Plant Installation', 'Irrigation Systems', 'Landscape Design'],
        }
        
        for cat_slug, skill_names in skills_data.items():
            for skill_name in skill_names:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    category=categories[cat_slug]
                )
                if created:
                    self.stdout.write(f'  Created skill: {skill_name}')
        
        # Create sample workers
        workers_data = [
            {
                'username': 'jahid.hasan@example.com',
                'email': 'jahid.hasan@example.com',
                'first_name': 'Jahid',
                'last_name': 'Hasan',
                'password': 'worker123',
                'worker': {
                    'role': 'Cleaning Expert',
                    'bio': 'Professional Cleaning Expert with over 8 years of experience in providing high-quality cleaning services.',
                    'experience_years': 8,
                    'hourly_rate': 500,
                    'location': 'Dhaka',
                    'service_areas': 'Dhaka, Mirpur, Uttara, Gulshan',
                    'rating': 4.8,
                    'total_reviews': 120,
                    'total_jobs': 320,
                    'response_time': 'Within 2 hours',
                    'is_verified': True,
                    'categories': ['cleaning'],
                }
            },
            {
                'username': 'kawser.ahmed@example.com',
                'email': 'kawser.ahmed@example.com',
                'first_name': 'Kawser',
                'last_name': 'Ahmed',
                'password': 'worker123',
                'worker': {
                    'role': 'Plumber',
                    'bio': 'Experienced Plumber with 10 years in the industry. I handle all types of plumbing jobs.',
                    'experience_years': 10,
                    'hourly_rate': 600,
                    'location': 'Chittagong',
                    'service_areas': 'Chittagong, Agrabad, Nasirabad',
                    'rating': 4.9,
                    'total_reviews': 95,
                    'total_jobs': 450,
                    'response_time': 'Within 1 hour',
                    'is_verified': True,
                    'categories': ['plumbing'],
                }
            },
            {
                'username': 'sanaullah.khan@example.com',
                'email': 'sanaullah.khan@example.com',
                'first_name': 'Sanaullah',
                'last_name': 'Khan',
                'password': 'worker123',
                'worker': {
                    'role': 'Electrician',
                    'bio': 'Certified Electrician with 12 years of professional experience in electrical services.',
                    'experience_years': 12,
                    'hourly_rate': 700,
                    'location': 'Sylhet',
                    'service_areas': 'Sylhet, Zindabazar, Amberkhana',
                    'rating': 4.7,
                    'total_reviews': 80,
                    'total_jobs': 380,
                    'response_time': 'Within 2 hours',
                    'is_verified': True,
                    'categories': ['electrical'],
                }
            },
            {
                'username': 'rahman.ali@example.com',
                'email': 'rahman.ali@example.com',
                'first_name': 'Rahman',
                'last_name': 'Ali',
                'password': 'worker123',
                'worker': {
                    'role': 'Carpenter',
                    'bio': 'Skilled Carpenter with 9 years of experience in custom woodwork and furniture making.',
                    'experience_years': 9,
                    'hourly_rate': 550,
                    'location': 'Dhaka',
                    'service_areas': 'Dhaka, Dhanmondi, Mohammadpur',
                    'rating': 4.6,
                    'total_reviews': 110,
                    'total_jobs': 290,
                    'response_time': 'Within 3 hours',
                    'is_verified': False,
                    'categories': ['carpentry'],
                }
            },
            {
                'username': 'farhan.khan@example.com',
                'email': 'farhan.khan@example.com',
                'first_name': 'Farhan',
                'last_name': 'Khan',
                'password': 'worker123',
                'worker': {
                    'role': 'Painter',
                    'bio': 'Professional painter specializing in interior and exterior painting with 7 years experience.',
                    'experience_years': 7,
                    'hourly_rate': 450,
                    'location': 'Dhaka',
                    'service_areas': 'Dhaka, Banani, Baridhara',
                    'rating': 4.5,
                    'total_reviews': 75,
                    'total_jobs': 200,
                    'response_time': 'Within 4 hours',
                    'is_verified': True,
                    'categories': ['painting'],
                }
            },
            {
                'username': 'amin.hassan@example.com',
                'email': 'amin.hassan@example.com',
                'first_name': 'Amin',
                'last_name': 'Hassan',
                'password': 'worker123',
                'worker': {
                    'role': 'Garden Expert',
                    'bio': 'Garden specialist with expertise in lawn maintenance, landscaping, and plant care.',
                    'experience_years': 6,
                    'hourly_rate': 400,
                    'location': 'Khulna',
                    'service_areas': 'Khulna, Boyra, Sonadanga',
                    'rating': 4.4,
                    'total_reviews': 60,
                    'total_jobs': 150,
                    'response_time': 'Within 3 hours',
                    'is_verified': False,
                    'categories': ['gardening'],
                }
            },
        ]
        
        for worker_data in workers_data:
            # Check if user exists
            user, created = User.objects.get_or_create(
                username=worker_data['username'],
                defaults={
                    'email': worker_data['email'],
                    'first_name': worker_data['first_name'],
                    'last_name': worker_data['last_name'],
                }
            )
            
            if created:
                user.set_password(worker_data['password'])
                user.save()
                self.stdout.write(f'  Created user: {user.get_full_name()}')
            
            # Update profile type
            user.profile.user_type = 'worker'
            user.profile.save()
            
            # Create worker profile
            wd = worker_data['worker']
            worker, w_created = Worker.objects.get_or_create(
                user=user,
                defaults={
                    'role': wd['role'],
                    'bio': wd['bio'],
                    'experience_years': wd['experience_years'],
                    'hourly_rate': wd['hourly_rate'],
                    'location': wd['location'],
                    'service_areas': wd['service_areas'],
                    'rating': wd['rating'],
                    'total_reviews': wd['total_reviews'],
                    'total_jobs': wd['total_jobs'],
                    'response_time': wd['response_time'],
                    'is_verified': wd['is_verified'],
                }
            )
            
            if w_created:
                # Add categories
                for cat_slug in wd['categories']:
                    worker.categories.add(categories[cat_slug])
                self.stdout.write(f'  Created worker profile: {worker}')
                
                # Create sample services
                Service.objects.create(
                    worker=worker,
                    name=f'{wd["role"]} Service - Basic',
                    description=f'Basic {wd["role"].lower()} service package',
                    price=wd['hourly_rate'] * 2,
                    duration='2-3 hours',
                    is_featured=True
                )
                Service.objects.create(
                    worker=worker,
                    name=f'{wd["role"]} Service - Premium',
                    description=f'Premium {wd["role"].lower()} service with extended features',
                    price=wd['hourly_rate'] * 5,
                    duration='4-6 hours',
                    is_featured=False
                )
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
