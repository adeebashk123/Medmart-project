from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Medicine,health_Product,meduser1,Contact
from django.contrib.auth.forms import AuthenticationForm
class MedUserForm(UserCreationForm):
    class Meta:
        model = meduser1
        fields = ['username', 'fname', 'lname', 'email1', 'phoneno1', 'address1', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(MedUserForm, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
       
        self.fields['password1'].widget.attrs.update({'maxlength': '100'})
        self.fields['password2'].widget.attrs.update({'maxlength': '100'})

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))



class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'price', 'company_name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medicine name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(MedicineForm, self).__init__(*args, **kwargs)

        self.fields['image'].widget.attrs.update({'class': 'form-control'})
class HealthProductForm(forms.ModelForm):
    class Meta:
        model = health_Product
        fields = '__all__' 
        
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.TextInput(attrs={'class': 'form-control'}),
        }