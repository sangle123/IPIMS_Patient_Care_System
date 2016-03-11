from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

#This class will also contain the list of names of the doctors who work for the hospital
class Doctor(models.Model):
	doctor_first_name = models.CharField(max_length=256, default="")
	doctor_last_name = models.CharField(max_length=256, default="")
	doctor_type = models.CharField(max_length=256, choices=[('Gynecologist', 'Gynecologist'), ('Neurologist', 'Neurologist'), ('Therapist', 'Therapist'), ('Allergist', 'Allergist'), ('Cardiologist', 'Cardiologist'), ('Dermatologist', 'Dermatologist'), ('Oncologist', 'Oncologist'), ('ENT', 'ENT'), ('Plastic Surgeon', 'Plastic Surgeon'), ('Psychiatrist', 'Psychiatrist'), ('Urologist','Urologist'), ('Podiatrist', 'Podiatrist')], default="Select Doctor Type")
	doctor_user = models.OneToOneField(User, unique=True, blank=False, default="", null=False)

	def __unicode__(self):
		return "Dr. " + str(self.doctor_first_name.title()) + ' ' + str(self.doctor_last_name.title()) + ' - ' + str(self.doctor_type.title())

class LabTech(models.Model):
	lab_first_name = models.CharField(max_length=256, default="")
	lab_last_name = models.CharField(max_length=256, default="")
	lab_user = models.OneToOneField(User, unique=True, blank=False, default="", null=False)

	def __unicode__(self):
		return str(self.lab_first_name) + ' ' + str(self.lab_last_name)

class PermissionsRole(models.Model):
	role = models.CharField(max_length=256, choices=[('admin', 'admin'), ('nurse', 'nurse'), ('staff', 'staff'), ('doctor', 'doctor'), ('patient', 'patient'), ('lab', 'lab')])
	user = models.OneToOneField(User, unique=True,  blank=True, default="")

	def __unicode__(self):
		return str(self.role)

#This is the mediator for the data that is submitted by the user to the HSP staff
#The data is stored and if the HSP staff approves the patient, then the data will be stored into a patient class
class TempPatientData(models.Model):

	user = models.OneToOneField(User,unique=True,null=True,default="")
	email_address = models.CharField(max_length=256, blank=False)
	first_name = models.CharField(max_length=256, default="")
	last_name = models.CharField(max_length=256, default="")
	age = models.IntegerField(default = 18, blank=False)
	gender = models.CharField(max_length=256, choices=[('male','Male'), ('female', 'Female'), ('other', 'Other'), ('prefer not to say', 'Prefer Not To Say')], default='Select a gender', blank = False)
	race = models.CharField(max_length=256, choices=[('white', 'White'), ('american_indian_alaskan_native', 'American Indian or Alaskan Native'),('hawaiian', 'Native Hawaiian or Other Pacific Islander'),('black', 'Black or African American'),('asian', 'Asian'), ('other', 'Other')], default="Other")
	income = models.CharField(max_length=256, choices=[('$0-$10,000', '$0-$10,000'), ('$10,001-$30,000', '$10,001-$30,000'), ('$30,001-$60,000', '$30,001-$60,000'),('$60,001-$85,000', '$60,001-$85,000'), ('$85,001-$110,000', '$85,001-$110,000'), ('$110,001+', '$110,001+'), ('Prefer Not To Say', 'Prefer Not To Say')], default='Prefer Not To Say', blank=False)
	phone_number = PhoneNumberField(blank = True, default="")
	# DOB = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
	DOB = models.CharField(max_length=255, blank=True, null=True)
	ssn = models.IntegerField(blank=True)
	allergies = models.CharField(max_length=256, default="")
	address = models.CharField(max_length=256, default="")
	medications = models.CharField(max_length=256, default="")
	insurance_provider =models.CharField(max_length=256, blank=False)
	insurance_policy_number = models.IntegerField(blank=True)
	data_sent = models.IntegerField(default=0)


	def __unicode__(self):
		return (str(self.first_name) + " " + str(self.last_name) + " " + str(self.email_address))

#This patient model will extend the user class so we can add the associated medical data for the user
class Patient(models.Model):

	fill_from_application = models.OneToOneField(TempPatientData,unique=True,null=True,default="")
	user = models.OneToOneField(User, unique=True,  blank=True, default="", null=True)
	approved = models.IntegerField(default=0, null=False)
	alertSent = models.IntegerField(default=0, null=False)
	date_created = models.CharField(default="9-20-1995", null=True, max_length=20)


	def __unicode__(self):
		return 'Email: ' + str(self.user) + ' First Name: ' + str(self.fill_from_application.first_name) + ' Last Name: ' + str(self.fill_from_application.last_name)

class PatientHealthConditions(models.Model):

	user = models.OneToOneField(Patient, unique=False, blank=True, default="")

	nausea_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	hunger_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	anxiety_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	stomach_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	body_ache_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	chest_pain_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], default=0)
	def __unicode__(self):
		return str(self.user.user.username)

#Class for the patients to schedule appointments for their associated doctor
class PatientAppt(models.Model):
	date = models.CharField(max_length=1000, unique=True)
	doctor = models.ForeignKey(Doctor, unique=False, default=-1)
	pain_level = models.IntegerField(validators=[MinValueValidator(0),
                                       MaxValueValidator(10)], blank=False)
	medical_conditions = models.CharField(max_length=1000, default="None")
	allergies = models.CharField(max_length=1000, default="None")
	user = models.ForeignKey(Patient, unique=False, blank=True, default="")
	current_health_conditions = models.ForeignKey(PatientHealthConditions, unique=False, blank=True, default="", null=True)
	resolved = models.IntegerField(default=0, blank=True)

	def __unicode__(self):
		return str(self.doctor)

#Class that is responsible for housing all of the alerts that are submitted by the user
class Alert(models.Model):
	alert_level = models.IntegerField(default=0, null=False)
	alert_patient = models.OneToOneField(Patient, unique = True, null = True)
	alert_description = models.CharField(max_length=255, default="", null = True, unique=False)

class EMedication(models.Model):
	patient = models.ForeignKey(Patient, null=False, default='', blank=False)
	medication_name = models.CharField(max_length=255, default = '', blank=False, null=False)
	medication_quantity = models.IntegerField(default=0, blank=True, null=True)
	reminder = models.IntegerField(default=0)
	prescribed_by_doctor = models.ForeignKey(Doctor, default="0")

class LabReport(models.Model):
	lab_patient = models.ForeignKey(Patient, default = "0")
	lab_results = models.CharField(max_length=255, choices=[('positive', 'Positive'), ('negative', 'Negative')])
	lab_test = models.CharField(max_length=255, choices=[('Blood pressure screening', 'Blood pressure screening'), ('C-reactive protein test', 'C-reactive protein test'), ('Colonoscopy', 'Colonoscopy'), ('Diabetes risk tests', 'Diabetes risk tests'), ('Pap smear', 'Pap smear'), ('Skin cancer exam', 'Skin cancer exam'), ('Blood Tests', 'Blood Tests')])
	lab_notes = models.TextField(default="Insert Notes For Lab Test")
	lab_tech = models.ForeignKey(LabTech, default="")

class AddMedicalHistory(models.Model):
	allergies = models.CharField(max_length=255, default="")
	medical_conditions = models.CharField(max_length=255, default="")
	patient = models.ForeignKey(Patient, default="")

