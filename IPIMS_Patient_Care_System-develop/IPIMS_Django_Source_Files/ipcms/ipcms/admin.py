from django.contrib import admin
from .forms import *
from .models import Patient, PatientAppt, PermissionsRole, Doctor, PatientHealthConditions, TempPatientData, Alert, EMedication, LabTech, LabReport,LabTech,AddMedicalHistory


#Add custom columns to appear inside of the database for the user
class PatientApptAdmin(admin.ModelAdmin):
	list_display = ('user', 'doctor', 'date', 'resolved')
	form = PatientApptForm

class PermissionsRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'role')

class DoctorAdmin(admin.ModelAdmin):
	list_display = ('doctor_first_name', 'doctor_last_name', 'doctor_type')

class PatientHealthConditionsAdmin(admin.ModelAdmin):
	form = PatientHealthConditionsForm

class TempPatientDataAdmin(admin.ModelAdmin):
	list_display=('first_name','last_name', 'gender')

class AlertAdmin(admin.ModelAdmin):
	list_display=('alert_level', 'alert_patient', 'alert_description')

class PatientAdmin(admin.ModelAdmin):
	list_display=('user', 'alertSent')
	# readonly_fields = ('created',)

class EMedicationAdmin(admin.ModelAdmin):
	list_display=('patient', 'medication_name')

class LabReportAdmin(admin.ModelAdmin):
	list_display=('lab_patient', 'lab_tech')


admin.site.register(Alert,AlertAdmin)
admin.site.register(AddMedicalHistory)
admin.site.register(LabTech)
admin.site.register(LabReport, LabReportAdmin)
admin.site.register(TempPatientData,TempPatientDataAdmin)
admin.site.register(PatientHealthConditions, PatientHealthConditionsAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(PatientAppt, PatientApptAdmin)
admin.site.register(PermissionsRole, PermissionsRoleAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(EMedication, EMedicationAdmin)


