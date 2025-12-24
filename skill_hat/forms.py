from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from core.models import Category


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
