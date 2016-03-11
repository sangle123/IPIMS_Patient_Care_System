from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from .models import Patient, PatientAppt, PatientHealthConditions, TempPatientData, EMedication, LabReport
from django.db import models
from django import forms

class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Patient Email Address"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password1',
            'password2',
            ButtonHolder(
                Submit('register', 'Register', css_class='btn-primary')
            )
        )

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Email Address"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            )
        )

class PatientForm(forms.ModelForm):
    user = forms.CharField(max_length=40)
    class Meta:
        model = Patient
        fields = '__all__'


class PatientApptForm(forms.ModelForm):
    class Meta:
        model = PatientAppt
        widgets = {
        'date': forms.TextInput(attrs={'placeholder': 'Selecting This Textbox Will Enable A Drop Down For Date & Time'}),
        'pain_level': forms.TextInput(attrs={'placeholder': 'Level Ranges from 0-10'}),
    }
        fields = '__all__'
        exclude = ['user', 'current_health_conditions']


class PatientHealthConditionsForm(forms.ModelForm):
    class Meta:
        model = PatientHealthConditions
        fields = '__all__'
        exclude = ['user']



class EMedicationForm(forms.ModelForm):
    class Meta:
        model = EMedication
        widgets = {
            'medication_name': forms.TextInput(attrs={'placeholder': 'Enter the name of the medication'}),
        }
        fields = '__all__'


class LabReportForm(forms.ModelForm):
    class Meta:
        model = LabReport
        # widgets = {
        #     'medication_name': forms.TextInput(attrs={'placeholder': 'Enter the name of the medication'}),
        # }
        fields = '__all__'



class TempPatientDataForm(forms.ModelForm):
    class Meta:
        model = TempPatientData
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Legal First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Legal Last Name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1(areacode)(phone-number)'}),
            'DOB': forms.TextInput(attrs={'placeholder': '01/01/2000'}),
            'ssn': forms.TextInput(attrs={'placeholder': '111223333'}),
            'allergies': forms.TextInput(attrs={'placeholder': 'Separate your allergies by commas'}),
            'medications': forms.TextInput(attrs={'placeholder': 'Separate your medications by commas'}),
            'insurance_policy_number': forms.TextInput(attrs={'placeholder': 'Valid Insurance Required'}),

        }
        fields = '__all__'
        exclude = ['user', 'data_sent', 'email_address']


