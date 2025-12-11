from django.http import HttpResponse
from django.shortcuts import render


def login_view(request):
    # Create default worker data
    default_workers = [
        {
            'name': 'Jahid Hasan',
            'role': 'Cleaning Expert',
            'price': '500',
            'rating': '4.8 (120 reviews)',
            'location': 'Dhaka',
            'photo': {'url': '/static/images/jihad.jpg'}
        },
        {
            'name': 'Kawser Ahmed',
            'role': 'Plumber',
            'price': '600',
            'rating': '4.9 (95 reviews)',
            'location': 'Chittagong',
            'photo': {'url': '/static/images/kawser.jpg'}
        },
        {
            'name': 'Sanaullah Khan',
            'role': 'Electrician',
            'price': '700',
            'rating': '4.7 (80 reviews)',
            'location': 'Sylhet',
            'photo': {'url': '/static/images/sanaullah.jpg'}
        },
        {
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
