from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Skill, Worker, Service, WorkPortfolio, UserProfile
from django.core.files.base import ContentFile
from datetime import date, timedelta
import random
import requests
import os


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
        
        # Create sample workers (1 per category with Bangladeshi names and detailed bios)
        workers_data = [
            {
                'username': 'jahid.hasan@example.com',
                'email': 'jahid.hasan@example.com',
                'first_name': 'Jahid',
                'last_name': 'Hasan',
                'password': 'worker123',
                'worker': {
                    'role': 'Cleaning Expert',
                    'bio': 'আমি জাহিদ হাসান, ১০ বছরের অভিজ্ঞ পরিষ্কার বিশেষজ্ঞ। বাসা, অফিস এবং বাণিজ্যিক স্থান পরিষ্কারে দক্ষ। আধুনিক যন্ত্রপাতি ও পরিবেশবান্ধব পণ্য ব্যবহার করি। Professional cleaning expert with 10+ years experience in residential, commercial, and post-construction cleaning. Customer satisfaction is my top priority.',
                    'experience_years': 10,
                    'hourly_rate': 500,
                    'location': 'Dhaka',
                    'service_areas': 'Mirpur, Uttara, Gulshan, Banani, Dhanmondi',
                    'rating': 4.9,
                    'total_reviews': 245,
                    'total_jobs': 520,
                    'response_time': 'Within 1 hour',
                    'is_verified': True,
                    'categories': ['cleaning'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/32.jpg',
                    'portfolio': [
                        {
                            'title': 'Gulshan Luxury Apartment Deep Cleaning',
                            'description': 'Complete deep cleaning of a 3500 sq ft luxury apartment in Gulshan-2. Included carpet shampooing, kitchen degreasing, bathroom sanitization, and window cleaning.',
                            'image_url': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800',
                        },
                        {
                            'title': 'Corporate Office Cleaning - BGMEA Tower',
                            'description': 'Weekly commercial cleaning contract for 5-floor corporate office. Maintaining hygiene standards for 200+ employees workspace.',
                            'image_url': 'https://images.unsplash.com/photo-1527515545081-5db817172677?w=800',
                        },
                        {
                            'title': 'Post-Construction Cleanup - Bashundhara R/A',
                            'description': 'Complete post-construction cleaning for newly built 8-story residential building. Removed all debris, dust, and construction residue.',
                            'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
                        },
                    ]
                }
            },
            {
                'username': 'kawser.ahmed@example.com',
                'email': 'kawser.ahmed@example.com',
                'first_name': 'Kawser',
                'last_name': 'Ahmed',
                'password': 'worker123',
                'worker': {
                    'role': 'Master Plumber',
                    'bio': 'আমি কাউসার আহমেদ, ১৫ বছরের অভিজ্ঞ মাস্টার প্লাম্বার। জরুরি মেরামত, পাইপ ইনস্টলেশন, লিক সমাধানে দক্ষ। ২৪/৭ সেবা প্রদান করি। Master plumber with 15 years of experience. Expert in pipe installation, leak detection, and emergency repairs. Available 24/7 for urgent plumbing issues.',
                    'experience_years': 15,
                    'hourly_rate': 700,
                    'location': 'Chittagong',
                    'service_areas': 'Chittagong City, Agrabad, Nasirabad, GEC',
                    'rating': 4.9,
                    'total_reviews': 312,
                    'total_jobs': 680,
                    'response_time': 'Within 30 minutes',
                    'is_verified': True,
                    'categories': ['plumbing'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/45.jpg',
                    'portfolio': [
                        {
                            'title': 'Complete Bathroom Renovation - Nasirabad Villa',
                            'description': 'Full bathroom plumbing renovation including new pipes, fixtures, water heater installation, and modern shower system setup.',
                            'image_url': 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=800',
                        },
                        {
                            'title': 'Commercial Water Line Installation',
                            'description': 'Installed complete water supply system for a new 10-story commercial building in Agrabad. Including pumps, tanks, and distribution network.',
                            'image_url': 'https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=800',
                        },
                        {
                            'title': 'Emergency Pipe Leak Repair - GEC Circle',
                            'description': 'Emergency repair of major water pipe leak in residential building. Completed within 2 hours to prevent water damage.',
                            'image_url': 'https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=800',
                        },
                    ]
                }
            },
            {
                'username': 'sanaullah.khan@example.com',
                'email': 'sanaullah.khan@example.com',
                'first_name': 'Sanaullah',
                'last_name': 'Khan',
                'password': 'worker123',
                'worker': {
                    'role': 'Certified Electrician',
                    'bio': 'আমি সানাউল্লাহ খান, সার্টিফাইড ইলেকট্রিশিয়ান। ১৪ বছরের অভিজ্ঞতা নিয়ে বাসা ও অফিসের ইলেকট্রিক্যাল কাজ করি। নিরাপত্তা আমার প্রথম অগ্রাধিকার। Certified electrician with 14 years of experience. Expert in residential and commercial wiring, panel installation, and safety inspections. Licensed and insured.',
                    'experience_years': 14,
                    'hourly_rate': 750,
                    'location': 'Sylhet',
                    'service_areas': 'Sylhet City, Zindabazar, Amberkhana, Subid Bazar',
                    'rating': 4.8,
                    'total_reviews': 278,
                    'total_jobs': 590,
                    'response_time': 'Within 1 hour',
                    'is_verified': True,
                    'categories': ['electrical'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/67.jpg',
                    'portfolio': [
                        {
                            'title': 'Smart Home Wiring - Zindabazar Residence',
                            'description': 'Complete smart home electrical installation including automated lighting, smart switches, and home automation panel setup.',
                            'image_url': 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=800',
                        },
                        {
                            'title': 'Industrial Panel Installation - Tea Factory',
                            'description': 'Installed 3-phase industrial electrical panel for tea processing factory. Including safety systems and backup power integration.',
                            'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
                        },
                        {
                            'title': 'Solar System Installation - Amberkhana',
                            'description': '5KW solar panel system installation with inverter and battery backup for residential building. Reduced electricity bills by 70%.',
                            'image_url': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800',
                        },
                    ]
                }
            },
            {
                'username': 'rahman.mistri@example.com',
                'email': 'rahman.mistri@example.com',
                'first_name': 'Rahman',
                'last_name': 'Mistri',
                'password': 'worker123',
                'worker': {
                    'role': 'Master Carpenter',
                    'bio': 'আমি রহমান মিস্ত্রি, ১৮ বছরের অভিজ্ঞ মাস্টার কার্পেন্টার। কাস্টম ফার্নিচার, দরজা-জানালা, এবং কাঠের কাজে বিশেষজ্ঞ। ঐতিহ্যবাহী বাংলাদেশী কারিগরি জানি। Master carpenter with 18 years of experience. Expert in custom furniture, doors, windows, and traditional Bengali woodwork.',
                    'experience_years': 18,
                    'hourly_rate': 650,
                    'location': 'Dhaka',
                    'service_areas': 'Dhaka, Dhanmondi, Mohammadpur, Mirpur',
                    'rating': 4.9,
                    'total_reviews': 234,
                    'total_jobs': 510,
                    'response_time': 'Within 2 hours',
                    'is_verified': True,
                    'categories': ['carpentry'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/52.jpg',
                    'portfolio': [
                        {
                            'title': 'Custom Modular Kitchen - Dhanmondi',
                            'description': 'Designed and built complete modular kitchen with teak wood cabinets, granite countertop integration, and pull-out storage systems.',
                            'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800',
                        },
                        {
                            'title': 'Traditional Wooden Door Crafting',
                            'description': 'Hand-carved traditional Bangladeshi style main door with intricate floral patterns. Made from seasoned mahogany wood.',
                            'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',
                        },
                        {
                            'title': 'Complete Bedroom Furniture Set - Mirpur',
                            'description': 'Custom bedroom furniture including king-size bed, wardrobes, dressing table, and side tables. All made from premium Shegun wood.',
                            'image_url': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800',
                        },
                    ]
                }
            },
            {
                'username': 'farhan.khan@example.com',
                'email': 'farhan.khan@example.com',
                'first_name': 'Farhan',
                'last_name': 'Khan',
                'password': 'worker123',
                'worker': {
                    'role': 'Professional Painter',
                    'bio': 'আমি ফারহান খান, পেশাদার পেইন্টার। ১১ বছরের অভিজ্ঞতা নিয়ে বাসা ও অফিসের রং করি। টেক্সচার, ডিজাইনার ওয়াল, এবং ওয়াটারপ্রুফ পেইন্টিংয়ে দক্ষ। Professional painter with 11 years of experience. Expert in interior/exterior painting, textures, and waterproof coatings. Free color consultation available.',
                    'experience_years': 11,
                    'hourly_rate': 500,
                    'location': 'Dhaka',
                    'service_areas': 'All over Dhaka City, Banani, Baridhara',
                    'rating': 4.8,
                    'total_reviews': 198,
                    'total_jobs': 430,
                    'response_time': 'Within 2 hours',
                    'is_verified': True,
                    'categories': ['painting'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/28.jpg',
                    'portfolio': [
                        {
                            'title': 'Luxury Villa Exterior Painting - Baridhara',
                            'description': 'Complete exterior painting of 3-story luxury villa with weatherproof coating. Used premium Asian Paints with 10-year warranty.',
                            'image_url': 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=800',
                        },
                        {
                            'title': 'Designer Wall Texture - Banani Office',
                            'description': 'Created custom textured accent walls for corporate office reception. Italian texture finish with metallic highlights.',
                            'image_url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800',
                        },
                        {
                            'title': 'Kids Room Mural Painting - Gulshan',
                            'description': 'Hand-painted colorful mural for children bedroom featuring jungle theme with animals and trees.',
                            'image_url': 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=800',
                        },
                    ]
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
                    'bio': 'আমি আমিন হাসান, বাগান বিশেষজ্ঞ। ১০ বছরের অভিজ্ঞতা নিয়ে রুফটপ গার্ডেন, বাগান ডিজাইন, এবং গাছের যত্ন করি। জৈব বাগান করতে সাহায্য করি। Garden expert with 10 years of experience. Specializing in rooftop gardens, garden design, and plant care. Creating organic and sustainable gardens.',
                    'experience_years': 10,
                    'hourly_rate': 450,
                    'location': 'Khulna',
                    'service_areas': 'Khulna, Boyra, Sonadanga, Jessore',
                    'rating': 4.7,
                    'total_reviews': 178,
                    'total_jobs': 390,
                    'response_time': 'Within 2 hours',
                    'is_verified': True,
                    'categories': ['gardening'],
                    'profile_photo_url': 'https://randomuser.me/api/portraits/men/75.jpg',
                    'portfolio': [
                        {
                            'title': 'Rooftop Garden Design - Khulna City',
                            'description': 'Designed and implemented complete rooftop garden with vegetable beds, flower sections, and automated drip irrigation system.',
                            'image_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800',
                        },
                        {
                            'title': 'Commercial Landscape - Jessore Hotel',
                            'description': 'Complete landscape design for hotel entrance including lawn, flower beds, decorative plants, and pathway lighting.',
                            'image_url': 'https://images.unsplash.com/photo-1558904541-efa843a96f01?w=800',
                        },
                        {
                            'title': 'Organic Vegetable Garden - Boyra',
                            'description': 'Setup organic vegetable garden with raised beds, composting system, and seasonal planting schedule for year-round produce.',
                            'image_url': 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=800',
                        },
                    ]
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
            
            # Ensure profile exists and update type
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.user_type = 'worker'
            profile.save()
            
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
                
                # Download and save profile photo
                if 'profile_photo_url' in wd:
                    try:
                        response = requests.get(wd['profile_photo_url'], timeout=10)
                        if response.status_code == 200:
                            filename = f"{worker_data['first_name'].lower()}_{worker_data['last_name'].lower()}.jpg"
                            worker.profile_photo.save(filename, ContentFile(response.content), save=True)
                            self.stdout.write(f'    Downloaded profile photo for {worker}')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'    Could not download profile photo: {e}'))
                
                self.stdout.write(f'  Created worker profile: {worker}')
                
                # Create sample services
                Service.objects.create(
                    worker=worker,
                    name=f'{wd["role"]} Service - Basic',
                    description=f'Basic {wd["role"].lower()} service package. Includes consultation and standard service.',
                    price=wd['hourly_rate'] * 2,
                    duration='2-3 hours',
                    is_featured=True
                )
                Service.objects.create(
                    worker=worker,
                    name=f'{wd["role"]} Service - Premium',
                    description=f'Premium {wd["role"].lower()} service with extended features and priority support.',
                    price=wd['hourly_rate'] * 5,
                    duration='4-6 hours',
                    is_featured=False
                )
                
                # Create portfolio items
                if 'portfolio' in wd:
                    for i, portfolio_item in enumerate(wd['portfolio']):
                        try:
                            # Download portfolio image
                            response = requests.get(portfolio_item['image_url'], timeout=15)
                            if response.status_code == 200:
                                portfolio = WorkPortfolio.objects.create(
                                    worker=worker,
                                    title=portfolio_item['title'],
                                    description=portfolio_item['description'],
                                    completed_date=date.today() - timedelta(days=random.randint(30, 365))
                                )
                                filename = f"{worker_data['first_name'].lower()}_project_{i+1}.jpg"
                                portfolio.image.save(filename, ContentFile(response.content), save=True)
                                self.stdout.write(f'    Created portfolio: {portfolio_item["title"]}')
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'    Could not create portfolio item: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
