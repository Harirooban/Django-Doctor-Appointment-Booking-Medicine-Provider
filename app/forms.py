from django import forms

from .models import products, Doctor ,Patient


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = products
        fields = ('name', 'description', 'price', 'image', 'categoryId')


class DoctorForm(forms.ModelForm):
    PhoneNumber = forms.RegexField(regex=r'^\+?1?\d{9,15}$')
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Doctor
        fields = ('DoctorName', 'PhoneNumber', 'SpecilistIn', 'EmailId', 'password')


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ('name', 'phone', 'Email', 'gender', 'DoctorName', 'Spec', 'EmailId', 'Date', 'Time', 'visit')


