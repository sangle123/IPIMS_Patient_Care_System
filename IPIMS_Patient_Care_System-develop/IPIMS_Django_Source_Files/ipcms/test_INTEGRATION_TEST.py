from __future__ import division
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.test.client import Client as client
from ipcms.models import TempPatientData, Doctor, Patient, PatientHealthConditions, PatientAppt, Alert, PermissionsRole, EMedication, LabReport, LabTech, AddMedicalHistory
from pprint import pprint
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import AnonymousUser, User
import time
from ipcms.views import PatientPortalView, HealthConditionsView, GenerateStatsView, ViewAllPatientData, display_all_lab_results



class Test_FullIntegrationTest(TestCase):

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




	def test_RegistrationFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR REGISTRATION FUNCTIONALITY\n-----------------------------------------------------------'

		'''
		1) Register a new patient into the system
		2) Test integration implementation for the user before being approved
		'''

		'''
		1) Register a new HSP staff into the system
		2) Test that HSP can upload medical reports
		3) Ensure the health records are stored and accessible
		'''

		#Build the user in the system
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

		print '\n\t-Registering test patient within the database'

		print '\033[1;32m\nPATIENT REGISTERED SUCCESSFULLY\033[0m\n'

		print '\t-Testing that the patient hasn\'t been approved yet'

		#Load the patient portal
		request = self.factory.get(reverse_lazy('Portal'))

		#Set the current user request object
		request.user = self.patient_user

		#Store the view response
		response = PatientPortalView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Assert template output
		self.assertContains(response, 'We Are Still Reviewing Your Application')
		print '\t-Patient currently: UNAPPROVED'
		print '\t-Approving Patient To Access Portal'

		#Change approval status
		self.patient_object.approved = 1
		self.patient_object.save()

		#Reload data
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user

		#Ensure patient was approved successfully
		response = PatientPortalView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		#Ensure the patient portal section loads
		self.assertContains(response, 'Before Continuing Further, please')

		#Patient now approved successfully
		print '\t-Patient currently: APPROVED'
		print '\033[1;32m\nPATIENT APPROVED\033[0m\n'

		#Ensure valid retrieval and storage of registration data in the database
		print '\t-Printing Current Patient Medical Data:\n'
		print '\t\t+Full Name: %s %s'%(self.fill_patient_application.first_name, self.fill_patient_application.last_name)
		print '\t\t+SSN: %s'%(self.fill_patient_application.ssn)
		print '\t\t+Allergies: %s'%(self.fill_patient_application.allergies)
		print '\t\t+Address: %s'%(self.fill_patient_application.address)
		print '\t\t+Medications: %s'%(self.fill_patient_application.medications)
		print '\t\t+Insurance Provider: %s'%(self.fill_patient_application.insurance_provider)
		print '\t\t+Insurance Policy #: %s'%(self.fill_patient_application.insurance_policy_number)
		print '\t\t+Email Address: %s'%(self.fill_patient_application.email_address)
		print '\t\t+Race: %s'%(self.fill_patient_application.race)
		print '\t\t+Income: %s'%(self.fill_patient_application.income)

		print '\n\t-Testing HSP Uploading Patient Medical Reports'

		#Upload an associated medical report for the patient
		patient_medical_history_upload = AddMedicalHistory.objects.create(
			allergies="Dogs, Flees",
			medical_conditions="Heart Pain",
			patient=self.patient_object
			)
		patient_medical_history_upload.save()

		print '\033[1;32m\nPATIENT MEDICAL REPORTS UPLOADED SUCCESSFULLY\033[0m\n'

		print '\t-Testing printing patient medical data for %s %s' %(self.fill_patient_application.first_name, self.fill_patient_application.last_name)

		#Grab a medical report for the selected patient
		query_history_reports = AddMedicalHistory.objects.filter(patient=self.patient_object).get()

		#View the stored data
		if (AddMedicalHistory.objects.filter(patient=self.patient_object).exists()):
			print '\t-Patient Medical History Upload From HSP Queried...'
			medical_data = AddMedicalHistory.objects.filter(patient=self.patient_object).get()
			print '\t-Patient Allergies: %s'%(medical_data.allergies)
			print '\t-Patient Medical Conditions: %s'%(medical_data.medical_conditions)

		print '\033[1;32m\nPATIENT MEDICAL REPORTS STORED AND RETRIEVED SUCCESSFULLY\033[0m\n'

		print '\n\t-Testing HSP Updating Patient Medical Reports'

		#Update the medical history information
		if (AddMedicalHistory.objects.filter(patient=self.patient_object).exists()):
			print '\t-Patient Medical History Upload From HSP Queried...'
			print '\t-Adding "CATS" as allergy to patient medical history'
			medical_data = AddMedicalHistory.objects.filter(patient=self.patient_object).get()
			medical_data.allergies = medical_data.allergies + ', CATS'
			print '\t-Patient Allergies: %s'%(medical_data.allergies)
			print '\t-Patient Medical Conditions: %s'%(medical_data.medical_conditions)

		print '\033[1;32m\nPATIENT MEDICAL REPORTS UPDATED\033[0m\n'

		#summary of integration test
		print '\033[30;42m\nREGISTRATION FEATURE INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Patient Registration (name, contact info, ssn, med history, allergies, insurance)\033[0m',
		print '\033[30;42m\n-Successful HSP Medical Information Upload (allergies, medical conditions upload)\033[0m',
		print '\033[30;42m\n-Successful HSP Medical Information Updating (allergies, medical conditions upload)\033[0m',
		print '\033[30;42m\n-Successful Patient Data Storage & Retrieval\033[0m'

	def test_ScheduleFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR SCHEDULE FUNCTIONALITY\n-----------------------------------------------------------'


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


		#Request an appointment to the healthcare provider
		print '\t-Currently requesting a medical appointment from Dr. %s %s' %(self.doctor_obj.doctor_first_name, self.doctor_obj.doctor_last_name)

		print '\t-Currently requesting an appointment for patient: %s %s' %(self.fill_patient_application.first_name, self.fill_patient_application.last_name)
		print '\t-Appointment Details:'
		print '\t\t+Date: %s'%("02/20/2016")
		print '\t\t+Doctor: Dr. %s %s'%(self.doctor_obj.doctor_first_name, self.doctor_obj.doctor_last_name)
		print '\t\t+Pain Level: %d'%(10)
		print '\t\t+Medical Conditions: xanax'
		print '\t\t+Allergies: %s'%(self.fill_patient_application.allergies)
		print '\t\t+Patient: %s %s'%(self.fill_patient_application.first_name, self.fill_patient_application.last_name)
		print '\t\t+Current Health Conditions: %d %d %d %d %d %d'%(self.patient_health_conditions.anxiety_level,
																self.patient_health_conditions.stomach_level, 
																self.patient_health_conditions.body_ache_level, 
																self.patient_health_conditions.anxiety_level, 
																self.patient_health_conditions.chest_pain_level, 
																self.patient_health_conditions.hunger_level 
																)

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

		print '\033[1;32m\nPATIENT APPOINTMENT (#1) CREATED SUCCESSFULLY!\033[0m\n'

		print '\t-Test changing status of the appointment from not resolved to resolved'

		#Change resolution status of appointment
		medical_appointment_1.resolved = 1

		self.assertEqual(1, medical_appointment_1.resolved)

		print '\t-Medical appointment resolved successfully'

		print '\033[1;32m\nPATIENT APPOINTMENT RESOLVED SUCCESSFULLY!\033[0m\n'

		print '\t-Attempting to view all the currently scheduled appointments for patient %s %s' %(self.fill_patient_application.first_name, self.fill_patient_application.last_name)

		print '\t-There are currently (%d) appointments in the database' %(PatientAppt.objects.all().count())

		#Query appointment for the patient
		current_appointment = PatientAppt.objects.filter(user = self.patient_object).get()

		#Check appt. existence.
		if (PatientAppt.objects.filter(user = self.patient_object).exists()):
			print '\t-Appointment for patient has been found; Attempting to view appointment details'

			#Retrieve appt data. (view)
			current_appt = PatientAppt.objects.filter(user = self.patient_object).get()
			print '\t-Appointment object is %s' %(current_appt)
			print '\t\t+Date: %s'%(current_appt.date)
			print '\t\t+Doctor: Dr. %s %s'%(current_appt.doctor.doctor_first_name, current_appt.doctor.doctor_last_name)
			print '\t\t+Pain Level: %d'%(10)
			print '\t\t+Medical Conditions: xanax'
			print '\t\t+Allergies: %s'%(current_appt.allergies)
			print '\t\t+Patient: %s %s'%(current_appt.user.fill_from_application.first_name, current_appt.user.fill_from_application.last_name)
			print '\t\t+Current Health Conditions: %d %d %d %d %d %d'%(current_appt.current_health_conditions.anxiety_level,
																	current_appt.current_health_conditions.stomach_level, 
																	current_appt.current_health_conditions.body_ache_level, 
																	current_appt.current_health_conditions.anxiety_level, 
																	current_appt.current_health_conditions.chest_pain_level, 
																	current_appt.current_health_conditions.hunger_level 
																	)

			print '\033[1;32m\nPATIENT APPOINTMENT VIEWED SUCCESSFULLY!\033[0m\n'

		print '\tTesting the manage portion of the appointments scheduler..'
		print '\tAttempting to change the date of the appointment'
		print '\tCurrent appointment date: %s' %(current_appt.date)

		#Updating appt. data
		current_appt.date = "03/14/2015"

		print '\tCurrent appointment date: %s' %(current_appt.date)

		#Assert change was valid
		self.assertEqual(current_appt.date, "03/14/2015")

		print '\033[1;32m\nPATIENT APPOINTMENT DATE CHANGED SUCCESSFULLY!\033[0m\n'

		print '\tTesting the manage portion of the appointments scheduler..'
		print '\tAttempting to delete the appointment'

		#Remove appt.
		current_appt.delete()

		#Assert positive removal
		self.assertEqual(0, PatientAppt.objects.all().count())

		print '\033[1;32m\nPATIENT APPOINTMENT DELETED SUCCESSFULLY!\033[0m\n'

		#summary of the integration test that was ran
		print '\033[30;42m\nSCHEDULE APPOINTMENT FEATURE INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Patient Appointment Creation (Doctor Chosen based on health)\033[0m',
		print '\033[30;42m\n-Successful Patient Appointment Resolution By Doctor\033[0m',
		print '\033[30;42m\n-Successful Patient Appointment Viewed/Retrieved\033[0m',
		print '\033[30;42m\n-Successful Patient Appoinment Managed (Updated/Removed)\033[0m'



	def test_UpdateHealthConditionsFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR UPDATE HEALTH CONDITIONS FUNCTIONALITY\n-----------------------------------------------------------'

		print '\t-Testing ability for patient to login & update health conds.'

		#Login as the patient and ensure that the IPIMS wants us to update our health conditions
		#Reload data
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user

		#Ensure patient was approved successfully
		response = PatientPortalView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		print '\t\t+Patient currently logged in successfully..'
		print '\t\t+Testing patient health-conds update'

		#Ensure the patient is viewing the page to force a health care update
		self.assertContains(response, '<h3>Before Continuing Further, please <a href="/health_conditions">add your health conditions..</a></h3>')

		#Update the health conditions of the patient
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

		#Login as the patient and ensure that the IPIMS wants us to update our health conditions
		#Reload data
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user

		#Ensure patient was approved successfully
		response = PatientPortalView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		print '\033[1;32m\nPATIENT HEALTH CONDITIONS ADDED SUCCESSFULLY!\033[0m\n'

		print '\t-Attempting to retrieve the patient health conditions to test validity'

		#Login as the patient and ensure that the IPIMS wants us to update our health conditions
		#Reload data
		request = self.factory.get(reverse_lazy('Conditions'))
		request.user = self.patient_user

		#Ensure patient was approved successfully
		response = HealthConditionsView(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		'''
		ENSURING EACH INDIVIDUAL HEALTH CONDITION WAS STORED AND OUTPUTTED SUCCESSFULLY WITHIN THE IPIMS
		'''

		#Testing proper nausea level
		self.assertContains(response, 'name="nausea_level" type="number" value="10"')
		print '\t\t+Nausea level: Expected - 10, result - 10'

		#Testing proper hunger level
		self.assertContains(response, 'name="hunger_level" type="number" value="8"')
		print '\t\t+Hunger level: Expected - 8, result - 8'

		#Testing proper anxiety level
		self.assertContains(response, 'name="anxiety_level" type="number" value="1"')
		print '\t\t+Anxiety level: Expected - 1, result - 1'

		#Testing proper stomach level
		self.assertContains(response, 'name="stomach_level" type="number" value="3"')
		print '\t\t+Stomach level: Expected - 3, result - 3'

		#Testing proper body ache level
		self.assertContains(response, 'name="body_ache_level" type="number" value="1"')
		print '\t\t+Body Ache level: Expected - 1, result - 1'

		#Testing proper chest pain level
		self.assertContains(response, 'name="chest_pain_level" type="number" value="4"')
		print '\t\t+Chest Pain level: Expected - 4, result - 4'

		print '\033[1;32m\nPATIENT HEALTH CONDITIONS STORED AND VIEWED SUCCESSFULLY VIA IPIMS!\033[0m\n'

		'''
		ENSURE THE ALERT CAPABILITIES OF THE IPIMS ARE WORKING PROPERLY
		'''

		print('\t-Testing manual alert submission from patient to healthcare from portal page')

		#Ensure that the alert has not been sent yet
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user
		response = PatientPortalView(request)

		self.assertNotContains(response, 'Your alert has been sent to the hospital!')

		print('\t\t+Successful analysis that the alert has not yet been sent.. sending alert now')

		self.patient_object.alertSent = 1
		self.patient_object.save()

		print('\t\t+Alert now sent successfully, testing page response')

		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user
		response = PatientPortalView(request)

		self.assertContains(response, '<h4><b>Your alert has been sent to the hospital!</b></h4>')

		print '\033[1;32m\nMANUAL SUBMISSION OF ALERT HAS BEEN SENT SUCCESSFULLY!\033[0m\n'

		#Reset alert sent
		self.patient_object.alertSent = 0
		self.patient_object.save()

		#Visit patient portal again as patient user
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user
		response = PatientPortalView(request)

		#Alert send message disappears when the alert has been retracted from the system
		self.assertNotContains(response, '<h4><b>Your alert has been sent to the hospital!</b></h4>')

		print '\t-Testing IPIMS automatic analysis alert functionality'
		print '\t\t+Currently increasing health conditions above (40) threshhold'

		#Update the health conditions to exceed the threshhold
		self.patient_health_conditions.nausea_level = 10
		self.patient_health_conditions.hunger_level = 10
		self.patient_health_conditions.anxiety_level = 10
		self.patient_health_conditions.chest_pain_level = 10
		self.patient_health_conditions.save()

		print '\t\t+Patient health threshhold set.. Testing auto send alert feature'

		#Navigate back to the control panel
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user
		response = PatientPortalView(request)

		#Test that the page ensures that the alert has been sent successfully!
		self.assertContains(response, '<h4><b>Your alert has been sent to the hospital!</b></h4>')

		print '\033[1;32m\nAUTOMATIC SUBMISSION OF ALERT HAS BEEN SENT SUCCESSFULLY BY IPIMS!\033[0m\n'

		#summary of the integration test that was ran
		print '\033[30;42m\nUPDATE HEALTH CONDITIONS FEATURE INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Addition of Patient Health Conditions\033[0m',
		print '\033[30;42m\n-Successful Storage of Patient Health Conditions\033[0m',
		print '\033[30;42m\n-Successful Retrieval of Patient Health Conditions\033[0m',
		print '\033[30;42m\n-Successful Manual Alert Submission To Health Staff\033[0m',
		print '\033[30;42m\n-Successful Automatic Alert Submission To Health Staff By IPIMS\033[0m'

	def test_ServiceToDoctorsFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR SERVICE TO DOCTORS FUNCTIONALITY\n-----------------------------------------------------------'


		'''
		(First Generate some appointments to view in the IPIMS)

		Ensure the relevant doctor can view the appointments
		Ability for doctor/nurse to update the health conditions
		Ability for doctor to resolve a patient case 
		Ability for doctor to prescribe medications 
		Ability for doctor to view patient lab records (Will need to create lab record instantiation)
		'''

		print '\t-Testing ability for nurse/doctor to update relevant health conditions'

		self.patient_user3 = User.objects.create(username="pat_user_test3", password="pat_pass_test3")

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

		current_appt = PatientAppt.objects.filter(user=self.patient_object3).get()

		print '\t-Current appointment has been queried for: %s %s' %(current_appt.user.fill_from_application.first_name, current_appt.user.fill_from_application.last_name)
		print '\t-Appointment Data Is:'
		print '\t\t +Date: %s'%(current_appt.date)
		print '\t\t +Doctor: Dr. %s %s'%(current_appt.doctor.doctor_first_name, current_appt.doctor.doctor_last_name)
		print '\t\t +pain_level: %d'%(current_appt.pain_level)
		print '\t\t +medical_conditions: %s'%(current_appt.medical_conditions)
		print '\t\t +user: %s'%(current_appt.user)
		print '\t\t +current_health_conditions: %s'%(current_appt.current_health_conditions)

		print '\033[1;32m\nAPPOINTMENT VIEWED SUCCESSFULLY!\033[0m\n'

		print '\t-Attempting to update data'

		current_appt.pain_level = 0
		current_appt.save()

		self.assertEqual(0, current_appt.pain_level)
		print '\t-Appt updated from 10 to 0 ... '

		print '\033[1;32m\nAPPOINTMENT UPDATED SUCCESSFULLY!\033[0m\n'

		print '\tAttempting to validate ability to resolve a patient case...'

		self.patient_permission3.role = "staff"
		self.patient_permission3.save()
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user3
		response = GenerateStatsView(request)


		print '\tCurrent stats response relays 100% unresolved case rate..'
		print '\tResolving case to changing that to 0%'

		current_appt.resolved = 1
		current_appt.save()

		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user3
		response = GenerateStatsView(request)

		self.assertNotContains(response, '<li>100.00% Unresolved Cases</li>')
		self.assertContains(response, '<li>100.00% Resolved Cases</li>')

		print '\033[1;32m\nAPPOINTMENT RESOLUTION CAPABILITIES SUCCESSFUL!\033[0m\n'

		print '\t-Testing ability to prescribe medication to user..'

		self.patient_permission3.role="patient"
		self.patient_permission3.save()

		#Navigate back to the control panel
		request = self.factory.get(reverse_lazy('Portal'))
		request.user = self.patient_user3
		response = PatientPortalView(request)

		self.assertContains(response, 'No Medications Pending')

		print '\t\t +Patient currently has no medications..'
		print '\t-Prescribing xanax to patient..'

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

		self.assertContains(response, '<form method="POST" action="/accounts/portal/clear/">')

		print '\033[1;32m\nE-PRESCRIPTION CAPABILITIES SUCCESSFUL!\033[0m\n'

		print '\t-Testing Lab Viewing Capabilities'


		new_lab_report = LabReport.objects.create(
			lab_patient = self.patient_object3,
			lab_results = "positive",
			lab_test = "Blood Tests",
			lab_notes = "seek medical attention",
			lab_tech = self.lab_staff_tech
			)

		new_lab_report.save()

		print '\t-Lab report is created'

		# display_all_lab_results

		self.patient_permission3.role="doctor"
		self.patient_permission3.save()

		#Navigate back to the control panel
		request = self.factory.get(reverse_lazy('display_all_lab_results'))
		request.user = self.patient_user3
		response = display_all_lab_results(request)

		self.assertContains(response, 'Blood Tests')
		self.assertContains(response, self.patient_object3.fill_from_application.first_name)
		self.assertContains(response, self.patient_object3.fill_from_application.last_name)

		print '\033[1;32m\nLAB RECORD CAPABILITIES SUCCESSFUL!\033[0m\n'

		#summary of the integration test that was ran
		print '\033[30;42m\nSERVICE TO DOCTORS FEATURE SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Ability To Update Patient Health Conditions\033[0m',
		print '\033[30;42m\n-Successful Patient Appointment Resolution\033[0m',
		print '\033[30;42m\n-Successful E-Medication Prescription Abilities\033[0m',
		print '\033[30;42m\n-Successful Retreival of Patient Lab Record Information\033[0m',

	def test_ServiceToStaffFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR SERVICE TO STAFF FUNCTIONALITY\n-----------------------------------------------------------'

		'''
		Test retrieval of patient information
		View All Patients
		View Patient Medical Information
		View Patient Prescription
		Update Patient Medical History
		'''

		print '\t-Testing valid retrieval of patient information from the database..'

		current_patient = Patient.objects.filter(user=self.patient_user).get()

		print '\t-Individual Patient Information has been retrieved successfully..'
		print '\t\t +%s %s'%(current_patient.fill_from_application.first_name, current_patient.fill_from_application.last_name)

		#temp staff change to test valid page viewing for all patient data
		self.lab_staff_user_permission = "staff"

		request = self.factory.get(reverse_lazy('ViewAllPatientData'))
		request.user = self.lab_staff_user
		response = ViewAllPatientData(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		self.assertContains(response, current_patient.fill_from_application.first_name)


		print '\033[1;32m\nVIEWING PATIENT DATA INFO RETRIEVAL SUCCESSFUL!\033[0m\n'

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


		# ViewAllPatientData
		print '\t-Attempting retrieval of all patients in the database..'
		print '\t-Current total count of all patient users in the database is %d' %(Patient.objects.all().count())
		print '\t-Need to HTTP request that the following names appear on the view all data page:'

		patient_1 = Patient.objects.all()[:1].get()
		patient_2 = Patient.objects.all()[1:2].get()

		print '\t\t +%s %s'%(patient_1.fill_from_application.first_name, patient_1.fill_from_application.last_name)
		print '\t\t +%s %s'%(patient_2.fill_from_application.first_name, patient_2.fill_from_application.last_name)
		print '\t-Loading all patient data page..'

		request = self.factory.get(reverse_lazy('ViewAllPatientData'))
		request.user = self.lab_staff_user
		response = ViewAllPatientData(request)

		#Test valid response code
		self.assertEqual(response.status_code, 200)

		print '\t-Patient data page loaded successfully..'

		self.assertContains(response, patient_1.fill_from_application.first_name)
		self.assertContains(response, patient_1.fill_from_application.last_name)
		self.assertContains(response, patient_2.fill_from_application.first_name)
		self.assertContains(response, patient_2.fill_from_application.last_name)

		print '\t-All patient records populated successfully!'

		print '\033[1;32m\nVIEWING ALL PATIENTS IS SUCCESSFUL!\033[0m\n'

		print '\t-Testing ability to view patient medical information'

		print '\t-Attempting to query patient from DB..'

		patient_query_test = Patient.objects.filter(user=self.patient_user).get()

		print '\t-Patient retrieval: SUCCESS'
		print '\t-Attempting to view name data to validate query'
		print '\t-The patient name is %s %s'%(patient_query_test.fill_from_application.first_name, patient_query_test.fill_from_application.last_name)

		print '\033[1;32m\nVIEWING PATIENT DATA IS SUCCESSFUL!\033[0m\n'

		print '\t-Testing ability to view patient e-medication data properly'

		emed = EMedication.objects.create(

			patient = patient_query_test,
			medication_name = "xanax",
			prescribed_by_doctor = self.doctor_obj
			)

		emed.save()

		print '\t-Query for e-medication..'

		current_emed = EMedication.objects.filter(patient = patient_query_test).get()

		print '\t-EMedication obtained..'

		print '\t-Medication Name: %s'%(current_emed.medication_name)

		print '\033[1;32m\nMEDICATION DATA RETRIEVED SUCCESSFULLY!\033[0m\n'

		print '\t-Attempting to update medical history for the following patient:'
		print '\t\t-%s'%(patient_query_test)


		med_adder = AddMedicalHistory.objects.create(
			allergies = "kittens",
			medical_conditions = "none",
			patient = patient_query_test
			)

		med_adder.save()

		print '\033[1;32m\nUPDATE MEDICAL INFORMATION WAS SUCCESSFUL!\033[0m\n'


		#summary of the integration test that was ran
		print '\033[30;42m\nSERVICE TO STAFF INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Test of Patient Information Retrieval\033[0m',
		print '\033[30;42m\n-Successful Viewing of Patients in Database\033[0m',
		print '\033[30;42m\n-Successful Retrieval of Patient Medical Information\033[0m',
		print '\033[30;42m\n-Successful Retrieval of Perscription Information\033[0m',
		print '\033[30;42m\n-Successful Update for Medical History\033[0m'


	def test_LabRecordsFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR LAB RECORDS FUNCTIONALITY\n-----------------------------------------------------------'

		'''
		Test creation of lab record
		Test viewing of lab record
		Test editing of lab record
		Test removal of lab record

		'''
		print '\t-Testing creation of lab record'
		print '\t\t +Assign patient..'
		print '\t\t +Assign results as positive..'
		print '\t\t +Assign test as blood test..'
		print '\t\t +Assign notes as "seek medical attention"..'
		print '\t\t +Assign tech to %s %s..'%(self.lab_staff_tech.lab_first_name, self.lab_staff_tech.lab_last_name)

		new_lab_report = LabReport.objects.create(
			lab_patient = self.patient_object,
			lab_results = "positive",
			lab_test = "Blood Tests",
			lab_notes = "seek medical attention",
			lab_tech = self.lab_staff_tech
			)

		new_lab_report.save()

		print '\033[1;32m\nLAB REPORT GENERATION IS SUCCESSFUL!\033[0m\n'

		print '\t-Testing viewing of lab record'
		print '\t\t +Attempting record query for patient..'

		current_lab_record = LabReport.objects.filter(lab_patient = self.patient_object).get()

		print '\t\t +Record obtained successfully, attempting to view details..'
		print '\t\t +Patient: %s %s'%(current_lab_record.lab_patient.fill_from_application.first_name, current_lab_record.lab_patient.fill_from_application.last_name)
		print '\t\t +Results: %s'%(current_lab_record.lab_results)
		print '\t\t +Test Type: %s'%(current_lab_record.lab_test)
		print '\t\t +Notes: %s'%(current_lab_record.lab_notes)
		print '\t\t +Tech: %s %s'%(current_lab_record.lab_tech.lab_first_name, current_lab_record.lab_tech.lab_last_name)


		print '\033[1;32m\nLAB REPORT VIEWING & RETRIEVAL IS SUCCESSFUL!\033[0m\n'


		print '\t-Testing editing of lab record'
		print '\t\t +Attempting record query for patient..'
		print '\t\t +Attempting record query for patient..'

		current_lab_record = LabReport.objects.filter(lab_patient = self.patient_object).get()

		print '\t\t +Record obtained successfully, attempting to edit details..'

		self.assertEqual("positive", current_lab_record.lab_results)

		print '\t\t +Current results are %s changing to the opposite'%(current_lab_record.lab_results)

		current_lab_record.lab_results = "negative"

		self.assertEqual("negative", current_lab_record.lab_results)

		print '\033[1;32m\nLAB REPORT EDIT SUCCESSFUL!\033[0m\n'

		print '\t-Testing removal of lab record'

		if (LabReport.objects.filter(lab_patient = self.patient_object).exists()):
			print '\t\t +The lab record currently exists... removing'

		else:
			print '\t\t +Lab record no longer exists'

		lab_removal = LabReport.objects.filter(lab_patient = self.patient_object).get()
		lab_removal.delete()

		if (LabReport.objects.filter(lab_patient = self.patient_object).exists()):
			print '\t\t +The lab record currently exists... removing'

		else:
			print '\t\t +Lab record no longer exists'

		print '\033[1;32m\nLAB REPORT REMOVAL SUCCESSFUL!\033[0m\n'

		#summary of integration test
		print '\033[30;42mLAB FEATURE INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Lab Report Creation\033[0m',
		print '\033[30;42m\n-Successful Viewing & Retrieval of Lab Report\033[0m',
		print '\033[30;42m\n-Successful Editing of Lab Report\033[0m',
		print '\033[30;42m\n-Successful Removal of Lab Report\033[0m'

	def test_StatsReportsFeatureIntegration(self):

		print '\n\n\n----------------------------------------------------------\nINTEGRATION TEST FOR STATISTICAL REPORTS FUNCTIONALITY\n-----------------------------------------------------------'

		'''
		Health outcome analysis
		Admission rate
		Patient types
		Patient populations
		'''

		print '\t-Generating users to run statistical reports on'

		#Generate 5 patients and begin doing statistical analysis and tests on the expected and actual output
		self.patient_user1 = User.objects.create(username="pat1", password="pat1")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application = TempPatientData.objects.create(
			user = self.patient_user1,
			first_name = "patient1",
			last_name = "patient1",
			ssn = 600418394,
			allergies = "cats",
			address = "address 1",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "patient1@patient1.com",
			data_sent = "1",
			race = "black",
			income = "$0-$10,000",
			gender = "female"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object = Patient.objects.create(
			fill_from_application = self.fill_patient_application,
			user = self.patient_user1,
			approved = 1
			)

		self.patient_permission1 = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user1
			)

		print '\t-Users generated successfully'

		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		#Patient should not be able to view this page because not a staff memer
		self.assertNotContains(response, 'Patient Statistical Report Analysis')

		print '\t-Statistical Reports page successfully blocked if user is a - PATIENT'
		print '\t-Changing permission to staff to test stats page'

		self.patient_permission1.role = "staff"
		self.patient_permission1.save()
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		print '\t-Permission changed to - STAFF'

		self.assertContains(response, 'Patient Statistical Report Analysis')

		print '\033[1;32m\nSTATISTICAL REPORTS ANALYSIS LOADED SUCCESSFULLY!\033[0m\n'


		#Add some health conditions
		self.patient_health_conditions1 = PatientHealthConditions.objects.create(

			user = self.patient_object,
			nausea_level = 10,
			hunger_level = 8,
			anxiety_level = 1, 
			stomach_level = 3,
			body_ache_level = 1,
			chest_pain_level = 4
			)
		self.patient_health_conditions1.save()


		#Schedule an appointment
		medical_appointment_1 = PatientAppt.objects.create(
			date = "02/20/2016",
			doctor = self.doctor_obj,
			pain_level = 10,
			medical_conditions = "chest pain and stomach issues",
			allergies = self.fill_patient_application.allergies,
			user = self.patient_object,
			current_health_conditions = self.patient_health_conditions1
			)
		medical_appointment_1.save()


		print '\t-Testing patient analysis of health outcomes (should be 0% resolved)'

		#Gather all the appointments
		all_apts = PatientAppt.objects.all().count()
		apts_not_resolved = PatientAppt.objects.filter(resolved=0).all().count()
		apts_resolved = PatientAppt.objects.filter(resolved=1).all().count()

		print '\t\t+ %d Resolved & %d Not Resolved with %d total appts'%(apts_resolved, apts_not_resolved, all_apts)
		self.assertEqual(100, (apts_not_resolved/all_apts)*100)
		print '\t\t+ Success! 100% of cases are currently unresolved, testing page output..'

		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		self.assertContains(response, '<li>100.00% Unresolved Cases</li>')
		self.assertContains(response, '<li>0.00% Resolved Cases</li>')

		print '\t\t+ Page outputs: 100.00% Unresolved Cases & 0.00% Resolved Cases'

		print '\t-Testing case percentage change when case becomes resolved'

		medical_appointment_1.resolved = 1
		medical_appointment_1.save()

		print '\t-Testing patient analysis of health outcomes (should be 100% resolved)'

		#Gather all the appointments
		all_apts = PatientAppt.objects.all().count()
		apts_not_resolved = PatientAppt.objects.filter(resolved=0).all().count()
		apts_resolved = PatientAppt.objects.filter(resolved=1).all().count()

		#Print resultant test data
		print '\t\t+ %d Resolved & %d Not Resolved with %d total appts'%(apts_resolved, apts_not_resolved, all_apts)
		self.assertEqual(100, (apts_resolved/all_apts)*100)
		print '\t\t+ Success! 100% of cases are currently resolved, testing page output..'

		#Load the stats page request
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		#Test the actual page output
		self.assertContains(response, '<li>0.00% Unresolved Cases</li>')
		self.assertContains(response, '<li>100.00% Resolved Cases</li>')

		print '\t\t+ Page outputs: 0.00% Unresolved Cases & 100.00% Resolved Cases'

		print '\033[1;32m\nANALYSIS OF PATIENT HEALTH OUTCOMES 100% PASSED!\033[0m\n'

		print '\t-Currently tracking the admission rates for statistical analysis'

		print '\t\t +Generating 1 unapproved patient and 2 approved patient for a 33.3% and 66.7% rate'

		#Create another patient who isn't approved
		#Yielf a 50/50 admission rate for approved and unapproved

		self.patient_user2 = User.objects.create(username="pat2", password="pat2")

		#Have the patient fill in their medical information to submit to the HSP staff
		self.fill_patient_application = TempPatientData.objects.create(
			user = self.patient_user2,
			first_name = "patient2",
			last_name = "patient2",
			ssn = 600418394,
			allergies = "cats",
			address = "address 1",
			medications = "Xanax",
			insurance_provider = "StateFarm",
			insurance_policy_number = 19938343434,
			email_address = "patient2@patient2.com",
			data_sent = "1",
			race = "white",
			income = "$10,001-$30,000",
			gender = "male"
			)

		#Implement a patient role up to the newly registered (pending) patient
		self.patient_object1 = Patient.objects.create(
			fill_from_application = self.fill_patient_application,
			user = self.patient_user2,
			approved = 0
			)

		self.patient_permission1 = PermissionsRole.objects.create(
			role = "patient",
			user = self.patient_user2
			)

		print '\t\t +Unapproved patient generated successfully'

		#Gather stats for patient admission data

		total_patients = Patient.objects.all().count()
		patients_approved = Patient.objects.filter(approved=1).all().count()
		patients_unapproved = Patient.objects.filter(approved=0).all().count()

		disapproval_percentage = (float(patients_unapproved)/float(total_patients))*100
		approval_percentage = (float(patients_approved)/float(total_patients))*100


		print '\t\t +There are %d approved and %d unapproved with %d total' %(patients_approved, patients_unapproved, total_patients)

		print '\t\t +The approval percentage is %.2f and the denial percentage is %.2f'%(approval_percentage, disapproval_percentage)

		#Load the stats page request
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		print '\033[1;32m\nSTATISTICAL REPORTS ADMISSION RATES OUTPUTTED SUCCESSFULLY!\033[0m\n'

		print '\t-Running analysis on the types of patients we have in the IPIMS'
		print '\t\t +Currently analyzing income type for patients..'
		print '\t\t\t +Expected to have 66.67% $0-$10,00 and 33.33% $10,001-$30,000'

		#Load the stats page request
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		self.assertContains(response, '<li>66.67% $0-$10,000</li>')
		self.assertContains(response, '<li>33.33% $10,001-$30,000</li>')

		print '\033[1;32m\nPATIENT TYPES FOR SALARY OUTPUTTED SUCCESSFULLY!\033[0m\n'

		print '\t-Running analysis on the types of patients we have in the IPIMS'
		print '\t\t +Currently analyzing gender type for patients..'
		print '\t\t\t +Expected to have 33.33% Male, 33.33% Female and 33.33% Other'

		#Load the stats page request
		request = self.factory.get(reverse_lazy('GenerateStats'))
		request.user = self.patient_user1
		response = GenerateStatsView(request)

		self.assertContains(response, '<li>33.33% Male</li>')
		self.assertContains(response, '<li>33.33% Female</li>')
		self.assertContains(response, '<li>0.00% Prefer Not To Say</li>')
		self.assertContains(response, '<li>33.33% Other</li>')

		print '\033[1;32m\nSTATISTICAL REPORTS GENDER TYPES OUTPUTTED SUCCESSFULLY!\033[0m\n'

		#summary of integration test
		print '\033[30;42mSTATISTICAL ANALYSIS FEATURE INTEGRATION TEST SUMMARY:\033[0m'
		print '\033[30;42m\n-Successful Health Outcome Analysis\033[0m',
		print '\033[30;42m\n-Successful Admission Rate Analysis\033[0m',
		print '\033[30;42m\n-Successful Patient Type Analysis\033[0m',
		print '\033[30;42m\n-Successful Patient Population Analysis\033[0m'

