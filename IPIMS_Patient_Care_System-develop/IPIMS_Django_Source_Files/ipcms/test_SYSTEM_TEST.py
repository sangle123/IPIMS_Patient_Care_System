from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.test.client import Client as client
from ipcms.models import TempPatientData, Doctor, Patient, PatientHealthConditions, PatientAppt, Alert, PermissionsRole, EMedication, LabReport, LabTech, AddMedicalHistory
from pprint import pprint
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import AnonymousUser, User
import time
from ipcms.views import PatientPortalView, HealthConditionsView, SuccessTestView, GenerateStatsView,ViewAllPatientData
from django.views import generic

#Function to output color codes of the efficiency of the response time for each of the features in the IPIMS
def calculateResponseEfficiency(output_time):
	if (output_time < .006):
		return '\033[1;32mVERY GOOD\033[0m'
	elif (output_time < .01):
		return '\033[1;32mGOOD\033[0m'
	elif (output_time < .15):
		return '\033[1;37mDECENT\033[0m'
	else:
		return '\033[1;31mNEEDS TO BE QUICKER\033[0m'

def separator():
	print '\t\t---------------------------------------------------------'

class Test_SystemComplianceTest(TestCase):


	def setUp(self):

		#Factory used to help with requests
		self.factory = RequestFactory()

		#Build HSP member to upload reports for patient
		self.hsp_user = User.objects.create(username="hsp1", password="hsp1")
		self.hsp_user_permission = PermissionsRole.objects.create(role = "staff",user = self.hsp_user)

		#Build Doctor member to allow appointment scheduling in the system
		self.doctor_user = User.objects.create(username="doc1", password="doc1")
		self.doctor_obj = Doctor.objects.create(doctor_first_name="Ryan", doctor_last_name="Schachte", doctor_type="Neurologist", doctor_user=self.doctor_user)
		self.doctor_permission = PermissionsRole.objects.create(role = "doctor",user = self.doctor_user)

		#Save objects into the test database
		self.hsp_user.save()
		self.doctor_obj.save()
		self.doctor_user.save()
		self.doctor_permission.save()
		self.hsp_user_permission.save()

		self.patient_user = User.objects.create(username="pat_user_test", password="pat_pass_test")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application = TempPatientData.objects.create(
			user = self.patient_user,
			first_name = "John",
			last_name = "Larsen",
			ssn = 600418394,
			allergies = "Soda",
			address = "2417 E. Laurel St. Mesa, AZ 85213",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "jacob@jacob.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "other"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object = Patient.objects.create(
			fill_from_application = self.fill_patient_application,
			user = self.patient_user,
			approved = 1
			)

		#Implement a permission role access to the patient
		self.patient_permission = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user
			)



		self.patient_user.save()
		self.fill_patient_application.save()
		self.patient_object.save()
		self.patient_permission.save()

	#Build lab member to upload reports for patient
		self.lab_staff_user = User.objects.create(username="labstaff1", password="labstaff1")
		self.lab_staff_user_permission = PermissionsRole.objects.create(role = "lab",user = self.lab_staff_user)

		self.lab_staff_user.save()
		self.lab_staff_user_permission.save()

		self.lab_staff_tech = LabTech.objects.create(
			lab_first_name = "Lab_Guy",
			lab_last_name = "Lab_Last_Name",
			lab_user = self.lab_staff_user
			)

		self.lab_staff_tech.save()



	def test_PatientFeature(self):
		TOTAL_PATIENT_FEATURE_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR REGISTRATION FEATURE\n-----------------------------------------------------------\033[0m\n'

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Patient Registration")

		#Run the registration code here
		#Build the user in the system

		response_time_begin = time.time()

		self.patient_user = User.objects.create(username="pat_user_1", password="pat_pass_1")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application = TempPatientData.objects.create(
			user = self.patient_user,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "NONE",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "NONE",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johnson@johnson.com",
			data_sent = "1",
			race = "white",
			income = "$0-$10,000"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object = Patient.objects.create(
			fill_from_application = self.fill_patient_application,
			user = self.patient_user,
			approved = 0
			)

		#Implement a permission role access to the patient
		self.patient_permission = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user
			)

		self.patient_user.save()
		self.fill_patient_application.save()
		self.patient_object.save()
		self.patient_permission.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_PATIENT_FEATURE_TIME += response_time

		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Updating Medical History")

		#Upload an associated medical report for the patient

		response_time_begin = time.time()

		patient_medical_history_upload = AddMedicalHistory.objects.create(
			allergies="Dogs, Flees",
			medical_conditions="Heart Pain",
			patient=self.patient_object
			)
		patient_medical_history_upload.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_PATIENT_FEATURE_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Uploading and Storing Medical Records")
		response_time_begin = time.time()

		#Build the user in the system

		#Upload an associated medical report for the patient
		patient_medical_history_upload = AddMedicalHistory.objects.create(
			allergies="Dogs, Flees",
			medical_conditions="Heart Pain, Back Pain, Shoulder",
			patient=self.patient_object
			)
		patient_medical_history_upload.save()

		#Update and store medical data
		patient_medical_history_upload.medical_conditions = patient_medical_history_upload.medical_conditions + ", head pain"

		patient_medical_history_upload.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_PATIENT_FEATURE_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Approving Patient Application Request")

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		self.patient_object.approved = 1
		self.patient_object.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin
		TOTAL_PATIENT_FEATURE_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_PATIENT_FEATURE_TIME)

	def test_ScheduleApptFeature(self):

		TOTAL_SCHEDULE_APPT_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR SCHEDULE FEATURE\n-----------------------------------------------------------\033[0m\n'

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Schedule Appointment")

		#Build the user in the system
		response_time_begin = time.time()

		self.patient_health_conditions = PatientHealthConditions.objects.create(

			user = self.patient_object,
			nausea_level = 10,
			hunger_level = 8,
			anxiety_level = 1,
			stomach_level = 3,
			body_ache_level = 1,
			chest_pain_level = 4
			)
		self.patient_health_conditions.save()

		#Schedule an appointment
		medical_appointment_1 = PatientAppt.objects.create(
			date = "02/20/2016",
			doctor = self.doctor_obj,
			pain_level = 10,
			medical_conditions = "chest pain and stomach issues",
			allergies = self.fill_patient_application.allergies,
			user = self.patient_object,
			current_health_conditions = self.patient_health_conditions
			)
		medical_appointment_1.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("View Appointment")

		#Build the user in the system
		response_time_begin = time.time()

		#Query the appointment for viewing
		find_appt = PatientAppt.objects.filter(user=self.patient_object).get()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Manage Appointment")

		#Build the user in the system
		response_time_begin = time.time()

		#Query the appointment for viewing
		find_appt = PatientAppt.objects.filter(user=self.patient_object).get()

		find_appt.nausea_level = 1
		find_appt.stomach_level = 5
		find_appt.chest_pain_level = 7
		find_appt.anxiety_level = 3
		find_appt.body_ache_level = 1
		find_appt.save()

		#Appt updated

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_SCHEDULE_APPT_TIME)

	def test_UpdateHealthConditionsFeature(self):

		TOTAL_SCHEDULE_APPT_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR UPDATE HEALTH CONDITIONS FEATURE\n-----------------------------------------------------------\033[0m\n'

		separator()

		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Create Health Conditions")

		#Build the user in the system
		response_time_begin = time.time()

		#Create the health conditions of the patient
		self.patient_health_conditions = PatientHealthConditions.objects.create(

			user = self.patient_object,
			nausea_level = 10,
			hunger_level = 8,
			anxiety_level = 1,
			stomach_level = 3,
			body_ache_level = 1,
			chest_pain_level = 4
			)
		self.patient_health_conditions.save()

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Update Health Conditions")

		#Build the user in the system
		response_time_begin = time.time()

		#Get the conditions
		health_conds = PatientHealthConditions.objects.filter(user = self.patient_object).get()

		#Patient retrieved
		self.patient_health_conditions.nausea_level = 0
		self.patient_health_conditions.hunger_level = 1
		self.patient_health_conditions.anxiety_level = 6
		self.patient_health_conditions.stomach_level = 5
		self.patient_health_conditions.body_ache_level = 2
		self.patient_health_conditions.chest_pain_level = 5

		self.patient_health_conditions.save()

		#Patient health conditions updated successfully

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Send Manual Alert IPIMS")

		#Build the user in the system
		response_time_begin = time.time()

		current_patient = Patient.objects.filter(user=request.user).get()

		#patient gathered

		current_patient.alertSent = 1
		current_patient.save()

		#alert sent successfully

		#Load the patient portal
		request = self.factory.get(reverse_lazy('SuccessTestView'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = SuccessTestView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin

		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Send Automatic IPIMS Alert")

		#Build the user in the system
		response_time_begin = time.time()

		existent_conditions = PatientHealthConditions.objects.filter(user = self.patient_object).get()
		existent_conditions.delete()

		#Create the health conditions of the patient
		self.patient_health_conditions = PatientHealthConditions.objects.create(

			user = self.patient_object,
			nausea_level = 10,
			hunger_level = 10,
			anxiety_level = 10,
			stomach_level = 10,
			body_ache_level = 10,
			chest_pain_level = 4
			)
		self.patient_health_conditions.save()

		#IPIMS alert sent

		#load alert sent to portal
		#Load the patient portal
		request = self.factory.get(reverse_lazy('Portal'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = PatientPortalView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Now load the actual portal view after registration
		response_time = time.time() - response_time_begin


		TOTAL_SCHEDULE_APPT_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_SCHEDULE_APPT_TIME)


	def test_ServiceToDoctorsFeature(self):

		TOTAL_SERVICE_TO_DOCTORS_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR SERVICE TO DOCTORS FEATURE\n-----------------------------------------------------------\033[0m\n'
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Testing Valid Load For Analysis of:")
		print '\t\t\t+ \033[1;33mEnsure the relevant doctor can view the appointments\033[0m'
		print '\t\t\t+ \033[1;33mAbility for doctor/nurse to update the health conditions\033[0m'
		print '\t\t\t+ \033[1;33mAbility for doctor to resolve a patient case\033[0m'
		print '\t\t\t+ \033[1;33mAbility for doctor to prescribe medications\033[0m'
		print '\t\t\t+ \033[1;33mAbility for doctor to view patient lab records\033[0m'
		separator()

		#Build the user in the system
		response_time_begin = time.time()
		self.patient_user3 = User.objects.create(username="pat3", password="pat3")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application3 = TempPatientData.objects.create(
			user = self.patient_user3,
			first_name = "John",
			last_name = "Larsen",
			ssn = 600418394,
			allergies = "Soda",
			address = "2417 E. Laurel St. Mesa, AZ 85213",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "jacob@jacob.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "other"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object3 = Patient.objects.create(
			fill_from_application = self.fill_patient_application3,
			user = self.patient_user3,
			approved = 1
			)

		#Implement a permission role access to the patient
		self.patient_permission3 = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user3
			)

		self.patient_user3.save()
		self.fill_patient_application3.save()
		self.patient_object3.save()
		self.patient_permission3.save()


		#Update the health conditions of the patient
		self.patient_health_conditions3 = PatientHealthConditions.objects.create(

			user = self.patient_object3,
			nausea_level = 10,
			hunger_level = 8,
			anxiety_level = 1, 
			stomach_level = 3,
			body_ache_level = 1,
			chest_pain_level = 4
			)
		self.patient_health_conditions3.save()

		relevant_appt = PatientAppt.objects.create(
			date = "03/14/2015",
			doctor= self.doctor_obj,
			pain_level = 10,
			medical_conditions="n/a",
			allergies="cats",
			user = self.patient_object3,
			current_health_conditions=self.patient_health_conditions3,


			)
		relevant_appt.save()
		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_DOCTORS_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		current_appt = PatientAppt.objects.filter(user=self.patient_object3).get()
		current_appt.pain_level = 0
		current_appt.save()

		self.assertEqual(0, current_appt.pain_level)


		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_DOCTORS_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		self.patient_permission3.role = "staff"
		self.patient_permission3.save()
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user3
		response = GenerateStatsView(request)

		self.assertEqual(response.status_code, 200)

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_DOCTORS_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		e_med_maker = EMedication.objects.create(
			patient = self.patient_object3,
			medication_name = "xanax",
			prescribed_by_doctor=self.doctor_obj
			)

		e_med_maker.save()

		#Navigate back to the control panel
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user3
		response = PatientPortalView(request)

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_DOCTORS_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()
		new_lab_report = LabReport.objects.create(
			lab_patient = self.patient_object3,
			lab_results = "positive",
			lab_test = "Blood Tests",
			lab_notes = "seek medical attention",
			lab_tech = self.lab_staff_tech
			)

		new_lab_report.save()
		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_DOCTORS_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))
		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_SERVICE_TO_DOCTORS_TIME)


	def test_ServiceToStaffFeature(self):

		TOTAL_SERVICE_TO_STAFF_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR SERVICE TO STAFF FEATURE\n-----------------------------------------------------------\033[0m\n'


		separator()


		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("retrieval of patient information")
		response_time_begin = time.time()

		current_patient = Patient.objects.filter(user=self.patient_user).get()



		#temp staff change to test valid page viewing for all patient data
		self.lab_staff_user_permission = "staff"

		request = self.factory.get(reverse_lazy('ViewAllPatientData'))
		request.user = self.lab_staff_user
		response = ViewAllPatientData(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		self.assertContains(response, current_patient.fill_from_application.first_name)

		response_time = time.time() - response_time_begin
		TOTAL_SERVICE_TO_STAFF_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))


		separator()


		#Testing valid ability to load all the users in the datbase

		self.patient_user2 = User.objects.create(username="pat_user_test2", password="pat_pass_test2")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application2 = TempPatientData.objects.create(
			user = self.patient_user2,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600418394,
			allergies = "Soda",
			address = "2417 E. Laurel St. Mesa, AZ 85213",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "jacob1@jacob.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "other"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object2 = Patient.objects.create(
			fill_from_application = self.fill_patient_application2,
			user = self.patient_user2,
			approved = 1
			)

		#Implement a permission role access to the patient
		self.patient_permission = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user2
			)

		self.patient_user2.save()
		self.fill_patient_application2.save()
		self.patient_object2.save()
		self.patient_permission.save()


		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("retrieval of all patients")
		response_time_begin = time.time()
		# ViewAllPatientData


		patient_1 = Patient.objects.all()[:1].get()
		patient_2 = Patient.objects.all()[1:2].get()



		request = self.factory.get(reverse_lazy('ViewAllPatientData'))
		request.user = self.lab_staff_user
		response = ViewAllPatientData(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		TOTAL_SERVICE_TO_STAFF_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		self.assertContains(response, patient_1.fill_from_application.first_name)
		self.assertContains(response, patient_1.fill_from_application.last_name)
		self.assertContains(response, patient_2.fill_from_application.first_name)
		self.assertContains(response, patient_2.fill_from_application.last_name)

		patient_query_test = Patient.objects.filter(user=self.patient_user).get()



		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("view patient e-medication")
		response_time_begin = time.time()

		emed = EMedication.objects.create(

			patient = patient_query_test,
			medication_name = "xanax",
			prescribed_by_doctor = self.doctor_obj
			)

		emed.save()





		current_emed = EMedication.objects.filter(patient = patient_query_test).get()

		TOTAL_SERVICE_TO_STAFF_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()


		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("update medical history")
		response_time_begin = time.time()


		med_adder = AddMedicalHistory.objects.create(
			allergies = "kittens",
			medical_conditions = "none",
			patient = patient_query_test
			)

		med_adder.save()



		TOTAL_SERVICE_TO_STAFF_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()



	def test_ServiceToLabRecordsFeature(self):

		TOTAL_SERVICE_TO_LAB_TIME = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR SERVICE TO LAB FEATURE\n-----------------------------------------------------------\033[0m\n'

		separator()

		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Creation of Lab Record")

		response_time_begin = time.time()

		new_lab_report = LabReport.objects.create(
			lab_patient = self.patient_object,
			lab_results = "positive",
			lab_test = "Blood Tests",
			lab_notes = "seek medical attention",
			lab_tech = self.lab_staff_tech
			)

		new_lab_report.save()

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_LAB_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Viewing of Lab Record")

		current_lab_record = LabReport.objects.filter(lab_patient = self.patient_object).get()

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_LAB_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		current_lab_record = LabReport.objects.filter(lab_patient = self.patient_object).get()

		self.assertEqual("positive", current_lab_record.lab_results)

		current_lab_record.lab_results = "negative"

		self.assertEqual("negative", current_lab_record.lab_results)

		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Editing of Lab Record")

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_LAB_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		lab_removal = LabReport.objects.filter(lab_patient = self.patient_object).get()
		lab_removal.delete()

		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Removal of Lab Record")

		response_time = time.time() - response_time_begin

		TOTAL_SERVICE_TO_LAB_TIME += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_SERVICE_TO_LAB_TIME)

	def test_GenerationHealthStatsFeature(self):

		TOTAL_STATS_FEATURE = 0

		print '\033[1;45m\n----------------------------------------------------------\nSYSTEM TEST FOR STATISTICAL ANALYSIS FEATURE\n-----------------------------------------------------------\033[0m\n'

		#Need to basically query all of the data for the patients in the database and then load the page and see if the response is good
		#Instantiate the objects here

		separator()
		print '\t\t- \033[1;33mFeature Name:\033[0m %s'%("Testing Valid Load For Analysis of:")
		print '\t\t\t+ \033[1;33mAnalysis of Health Outcomes\033[0m'
		print '\t\t\t+ \033[1;33mTracking of Admission Rates\033[0m'
		print '\t\t\t+ \033[1;33mAnalysis of Types of Patients\033[0m'
		print '\t\t\t+ \033[1;33mAnalysis of Patient Populations\033[0m'
		#Build the user in the system
		response_time_begin = time.time()

		self.patient_user1 = User.objects.create(username="pat_user_test1", password="pat_pass_test1")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application1 = TempPatientData.objects.create(
			user = self.patient_user1,
			first_name = "John",
			last_name = "Larsen",
			ssn = 600418394,
			allergies = "Soda",
			address = "2417 E. Laurel St. Mesa, AZ 85213",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "jacob1@jacob.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "other"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object1 = Patient.objects.create(
			fill_from_application = self.fill_patient_application1,
			user = self.patient_user1,
			approved = 1
			)

		#Implement a permission role access to the patient
		self.patient_permission = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user1
			)

		self.patient_user1.save()
		self.fill_patient_application1.save()
		self.patient_object1.save()
		self.patient_permission.save()


		self.patient_user2 = User.objects.create(username="pat_user_test2", password="pat_pass_test2")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application2 = TempPatientData.objects.create(
			user = self.patient_user2,
			first_name = "John",
			last_name = "Larsen",
			ssn = 600418394,
			allergies = "Soda",
			address = "2417 E. Laurel St. Mesa, AZ 85213",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "jacob1@jacob.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "other"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object2 = Patient.objects.create(
			fill_from_application = self.fill_patient_application2,
			user = self.patient_user2,
			approved = 1
			)

		#Implement a permission role access to the patient
		self.patient_permission = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user2
			)

		self.patient_user2.save()		
		self.fill_patient_application2.save()
		self.patient_object2.save()
		self.patient_permission.save()

		#Load the stats page
		request = self.factory.get(reverse_lazy('GenerateStats'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = GenerateStatsView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)


		response_time = time.time() - response_time_begin

		TOTAL_STATS_FEATURE += response_time
		print '\t\t- \033[1;33mResponse Time:\033[0m %.3f seconds'%(response_time)
		print '\t\t- \033[1;33mReliability Rating:\033[0m %s'%(calculateResponseEfficiency(response_time))

		separator()

		print '\033\n[44mTOTAL TIME: %.5f seconds\033[0m'%(TOTAL_STATS_FEATURE)
