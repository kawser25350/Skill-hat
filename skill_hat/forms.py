from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Category, Booking, Service
from datetime import date, timedelta


class LoginForm(forms.Form):
    """Login form for both customers and workers"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        })
    )
    keep_logged_in = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Keep me logged in'
    )


class CustomerRegisterForm(UserCreationForm):
    """Registration form for Customers - simple signup"""
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name',
            'autocomplete': 'name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (optional)',
            'autocomplete': 'tel'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        label='Confirm Password'
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to the terms and conditions'
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data['full_name']
        user.first_name = full_name.split()[0]
        user.last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        if commit:
            user.save()
        return user


class WorkerRegisterForm(UserCreationForm):
    """Registration form for Workers - includes professional details"""
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name',
            'autocomplete': 'name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'autocomplete': 'tel'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        label='Confirm Password'
    )
    
    # Worker-specific fields
    role = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Cleaning Expert, Plumber, Electrician'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        empty_label='Select your service category'
    )
    hourly_rate = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hourly Rate (৳)',
            'min': '50'
        })
    )
    location = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Location (e.g., Dhaka, Mirpur)'
        })
    )
    experience_years = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Years of Experience',
            'min': '0'
        })
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell customers about your skills and experience...',
            'rows': 3
        })
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to the terms and conditions'
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'password1', 'password2', 
                  'role', 'category', 'hourly_rate', 'location', 'experience_years', 'bio', 'photo')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data['full_name']
        user.first_name = full_name.split()[0]
        user.last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        if commit:
            user.save()
        return user


# Keep old RegisterForm for backward compatibility
RegisterForm = CustomerRegisterForm


class BookingForm(forms.ModelForm):
    """Booking form for customers to book workers"""
    
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat(),
        })
    )
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
        })
    )
    
    class Meta:
        model = Booking
        fields = ['title', 'description', 'location', 'phone', 'scheduled_date', 'scheduled_time', 'service']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for your booking (e.g., "Kitchen Deep Cleaning")'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your requirements in detail...',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full address where service is needed'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact phone number',
                'pattern': '[0-9]{11}'
            }),
            'service': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, worker=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker
        
        if worker:
            # Filter services to only show this worker's services
            self.fields['service'].queryset = Service.objects.filter(worker=worker, is_active=True)
            self.fields['service'].empty_label = 'Select a service package (optional)'
            self.fields['service'].required = False
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < date.today():
            raise forms.ValidationError('Please select a future date.')
        return scheduled_date
    
    def save(self, commit=True, client=None):
        booking = super().save(commit=False)
        
        if client:
            booking.client = client
        
        if self.worker:
            booking.worker = self.worker
            
            # Set estimated price based on service or hourly rate
            if booking.service:
                booking.estimated_price = booking.service.price
            else:
                booking.estimated_price = self.worker.hourly_rate * 2  # Default 2 hours
        
        if commit:
            booking.save()
        
        return booking
