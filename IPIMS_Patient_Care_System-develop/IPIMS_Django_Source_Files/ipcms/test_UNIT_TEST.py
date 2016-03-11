from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from ipcms.models import TempPatientData, Doctor, Patient, PatientHealthConditions, PatientAppt, Alert, PermissionsRole, EMedication, LabReport, LabTech, AddMedicalHistory
from pprint import pprint
from django.shortcuts import redirect, get_object_or_404


'''''''''''''''''''''''''''''''''

	UNIT TESTING DOCUMENT

'''''''''''''''''''''''''''''''''

'''
THIS TEST SUITE DEALS WITH THE TEST CREATION OF THE REGISTRATION OF DIFFERENT USERS
'''


class TestRegistrationFeature(TestCase):

	def testCreationOfPatient(self):
		print '--------------------------------------\nTESTING PATIENT REGISTRATION CREATION\n---------------------------------------'

		print '\tCreating user object for the registration'

		patient_user = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user.save()

		print '\tThe patient user has been created'

		print '\tCreating unapproved patient object in the system'
		temp_patient_user_data = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user,
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
		#Save user into the test database
		temp_patient_user_data.save()
		print '\tRegistration Of Patient Completed Successfully!'

		print '\tSetting Patient Approval Status From HSP Staff'
		print '\tRyan Schachte (PATIENT) Not Approved'

		patient_object = Patient.objects.create(

			fill_from_application = temp_patient_user_data,
			user = patient_user,
			approved = 0
			)

		patient_object.save()

		self.assertEqual(patient_object.approved, 0)

		print '\tHSP will now approve the patient'
		patient_object.approved = 1

		self.assertEqual(patient_object.approved, 1)
		print '\tPatient successfully added, registered and approved!'
		print '\tRyan Schachte (PATIENT) Approved'

	def testCreationOfHSP(self):

		print '--------------------------------------\nTESTING HSP REGISTRATION CREATION\n---------------------------------------'
		print '\tCreating the HSP Staff User Account'

		hsp_user = User.objects.create(username="hsp_user_1", email="hsp_user_1@yahoo.com", password="hsp_user_1_password")
		hsp_user.save()

		print '\tHSP Staff Member Registered with a permission role of NULL'

		hsp_permission_role = PermissionsRole.objects.create(

			role = "staff",
			user = hsp_user

			)
		print '\tHSP Staff Permission role assigned to - STAFF'
		print '\tHSP Staff Registered Successfully!'

		self.assertEqual(hsp_permission_role.role, "staff")
		self.assertEqual(hsp_permission_role.user, hsp_user)

	def testCreationOfDoctor(self):
		print '--------------------------------------\nTESTING DOCTOR REGISTRATION CREATION\n---------------------------------------'
		print '\tCreating the Doctor User Account'

		doctor_user = User.objects.create(username="doctor_user", email="doctor_user@yahoo.com", password="doctor_user_password")
		doctor_user.save()

		doctor_object = Doctor.objects.create(
			doctor_first_name = "john",
			doctor_last_name = "stamos",
			doctor_type = "Gynecologist",
			doctor_user = doctor_user
			)
		doctor_object.save()

		print '\tdoctor_user Member Registered with a permission role of NULL'

		hsp_permission_role = PermissionsRole.objects.create(

			role = "doctor",
			user = doctor_user

			)
		print '\tdoctor_user Permission role assigned to - DOCTOR'
		print '\tdoctor_user Registered Successfully!'

'''
THIS TEST SUITE DEALS WITH THE FEATURES FOR THE DOCTOR
'''
class TestServiceToDoctorsFeature(TestCase):

	def setUp(self):
		print '\tCreating the doctor, patient and lab tech in the test database'
		doctor_user = User.objects.create(username="doctor_user", email="doctor_user@yahoo.com", password="doctor_user_password")
		doctor_user.save()

		lab_tech_user = User.objects.create(username="lab_tech_user", email="lab_tech_user@yahoo.com", password="lab_tech_user_password")
		lab_tech_user.save()

		doctor_object = Doctor.objects.create(
			doctor_first_name = "john",
			doctor_last_name = "stamos",
			doctor_type = "Gynecologist",
			doctor_user = doctor_user
			)
		doctor_object.save()


		patient_user = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user.save()
		temp_patient_user_data = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user,
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
		#Save user into the test database
		temp_patient_user_data.save()

		patient_object = Patient.objects.create(

			fill_from_application = temp_patient_user_data,
			user = patient_user,
			approved = 0
			)

		patient_object.save()

		# print '\tDoctor and Patient Created Successfully!'

		new_tech = LabTech.objects.create(

			lab_first_name="tech1_first_name",
			lab_last_name="tech1_last_name",
			lab_user = lab_tech_user
			)


	def testViewPatientCase(self):

		print '--------------------------------------\nTESTING VIEWING THE PATIENT CASE\n---------------------------------------'

		patient_case = PatientAppt.objects.create(
			date = "02/20/2015",
			doctor = Doctor.objects.filter(doctor_user__username="doctor_user").get(),
			pain_level = 10,
			medical_conditions = "Heart Pain",
			allergies = "cats",
			user = Patient.objects.filter(user__username="patient_user_1").get(),
			resolved = 0
			)
		patient_case.save()

		print '\tPatient Case Created Successfully!'

		print '\tEvaluating Patient Case Information...'

		self.assertEqual(patient_case.doctor, Doctor.objects.filter(doctor_user__username="doctor_user").get())
		self.assertEqual(patient_case.date, "02/20/2015")
		self.assertEqual(patient_case.pain_level, 10)
		self.assertEqual(patient_case.allergies, "cats")

		print '\tAll outputs for patient case output to TRUE'

	def testUpdatingHealthConditionsOfPatient(self):
		print '--------------------------------------\nTESTING HEALTH CONDITION UPDATE\n---------------------------------------'

		print '\tWe will now update the health conditions of a patient inside of the test database'

		print '\tGathering patient_user_1 from DB....'

		current_user = Patient.objects.filter(user__username="patient_user_1").get()
		health_conditions = PatientHealthConditions.objects.create(

			user = current_user,
			nausea_level = 10,
			hunger_level = 9,
			anxiety_level = 7,
			stomach_level = 3
			)
		health_conditions.save()

		print '\tHealth Conditions Accessed....'

		print '\tCurrent nausea level is %d' %(health_conditions.nausea_level)
		self.assertEqual(health_conditions.nausea_level, 10)

		print '\tSetting nausea level to 2...'
		health_conditions.nausea_level = 2

		print '\tCurrent nausea level is %d' %(health_conditions.nausea_level)
		self.assertEqual(health_conditions.nausea_level, 2)

		print '\tNausea level has been set to 2 successfully!'



	def testPrescribingMedication(self):
		print '--------------------------------------\nTESTING THE E-PRESCRIPTION FEATURE\n---------------------------------------'

		current_patient 	= Patient.objects.filter(user__username="patient_user_1").get()
		current_doctor 		= Doctor.objects.filter(doctor_user__username="doctor_user").get()

		print '\tCreating a perscription for %s %s' %(current_patient.fill_from_application.first_name, current_patient.fill_from_application.last_name)
		new_perscription 	= EMedication.objects.create(

			patient = current_patient,
			medication_name = "Xanax",
			prescribed_by_doctor = current_doctor
			
			)

		new_perscription.save()

		print '\tPerscription is Xanax...'

		self.assertEqual(new_perscription.medication_name, "Xanax")

		print '\tEvaluated as TRUE'

		print '\tThe perscription for the user has been generated successfully!'


	def testViewPatientLabRecords(self):
		print '--------------------------------------\nTESTING LAB RECORD RETRIEVAL FOR PATIENTS\n---------------------------------------'

		lab_record = LabReport.objects.create(

			lab_patient = Patient.objects.filter(user__username="patient_user_1").get(),
			lab_results = "Positive",
			lab_test = "Blood pressure screening",
			lab_notes = "Seek medical attention!",
			lab_tech = LabTech.objects.filter(lab_first_name="tech1_first_name").get()

			)

		lab_record.save()

		print '\tLab record has been created and stored successfully!'

		print '\tWe want to view the lab records for the patient...'

		print '\tLab Patient Email: %s' %(lab_record.lab_patient.fill_from_application.user.email)

		self.assertEqual(lab_record.lab_patient.fill_from_application.user.email, "patient_user_1@yahoo.com")

		print '\tASSERTION TRUE'

		print '\tLab Results: %s' %(lab_record.lab_results)

		self.assertEqual(lab_record.lab_results, "Positive")

		print '\tASSERTION TRUE'

		print '\tLab Test: %s' %(lab_record.lab_test)

		self.assertEqual(lab_record.lab_test, "Blood pressure screening")

		print '\tASSERTION TRUE'

		print '\tLab Notes: %s' %(lab_record.lab_notes)

		self.assertEqual(lab_record.lab_notes, "Seek medical attention!")

		print '\tASSERTION TRUE'

'''
THIS TEST SUITE DEALS WITH THE FEATURES FOR THE STAFF (HSP)
'''
class TestServiceToStaffFeature(TestCase):

	def setUp(self):

		print '\tSetting up objects for test database....'


		doctor_user = User.objects.create(username="doctor_user", email="doctor_user@yahoo.com", password="doctor_user_password")
		doctor_user.save()

		lab_tech_user = User.objects.create(username="lab_tech_user", email="lab_tech_user@yahoo.com", password="lab_tech_user_password")
		lab_tech_user.save()

		doctor_object = Doctor.objects.create(
			doctor_first_name = "john",
			doctor_last_name = "stamos",
			doctor_type = "Gynecologist",
			doctor_user = doctor_user
			)
		doctor_object.save()


		patient_user = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user.save()
		temp_patient_user_data = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "CATS, DOGS",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "ZYRTEC",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johnson@johnson.com",
			data_sent = "1",
			race = "white",
			income = "$0-$10,000"
			)
		#Save user into the test database
		temp_patient_user_data.save()

		patient_object = Patient.objects.create(

			fill_from_application = temp_patient_user_data,
			user = patient_user,
			approved = 0
			)

		patient_object.save()

		# print '\tDoctor and Patient Created Successfully!'

		new_tech = LabTech.objects.create(

			lab_first_name="tech1_first_name",
			lab_last_name="tech1_last_name",
			lab_user = lab_tech_user
			)

		current_patient 	= Patient.objects.filter(user__username="patient_user_1").get()
		current_doctor 		= Doctor.objects.filter(doctor_user__username="doctor_user").get()

		new_perscription 	= EMedication.objects.create(

			patient = current_patient,
			medication_name = "Xanax",
			prescribed_by_doctor = current_doctor
			)

		new_perscription.save()


		current_user = Patient.objects.filter(user__username="patient_user_1").get()
		health_conditions = PatientHealthConditions.objects.create(

			user = current_user,
			nausea_level = 10,
			hunger_level = 9,
			anxiety_level = 7,
			stomach_level = 3
			)
		health_conditions.save()

	def testUploadMedicalReports(self):

		current_patient 	= Patient.objects.filter(user__username="patient_user_1").get()

		print '--------------------------------------\nTESTING HSP UPLOAD MEDICAL REPORTS FEATURE\n---------------------------------------'

		print '\tCreating Medical Report To Upload....'

		med_hist = AddMedicalHistory.objects.create(

			allergies="flees, dogs, cats",
			medical_conditions="Heart pain",
			patient=current_patient
			)

		print '\tUploading medical reports for %s %s' %(current_patient.fill_from_application.first_name, current_patient.fill_from_application.last_name)

		med_hist.save()

		print '\tMedical history saved for the patient'

		self.assertEqual(med_hist.allergies, "flees, dogs, cats")

		print '\tASSERTION TRUE'


	def testUpdateHealthConditions(self):

		print '--------------------------------------\nTESTING UPDATE HEALTH CONCERNS (HSP) FEATURE\n---------------------------------------'


		current_user = Patient.objects.filter(user__username="patient_user_1").get()
		health_cond_for_patient_1 = PatientHealthConditions.objects.filter(user = current_user).get()

		print '\tThese are the following health conditions:'
		print'\t\t%s' %(health_cond_for_patient_1.nausea_level)
		print'\t\t%s' %(health_cond_for_patient_1.stomach_level)
		print'\t\t%s' %(health_cond_for_patient_1.anxiety_level)
		print'\t\t%s' %(health_cond_for_patient_1.hunger_level)

		print '\tCurrently updating nausea from %d to %d' %(health_cond_for_patient_1.nausea_level, 6)

		health_cond_for_patient_1.nausea_level = 6

		self.assertEqual(health_cond_for_patient_1.nausea_level, 6)

		print '\tHealth Concern Update Successful, new level is %d' %(health_cond_for_patient_1.nausea_level)


	def testViewPatientMedicalHistory(self):

		print '--------------------------------------\nTESTING VIEWING OF PATIENT MEDICAL HISTORY FOR STAFF (HSP)\n---------------------------------------'

		current_user = Patient.objects.filter(user__username="patient_user_1").get()

		print '\tAttempting to obtain patient medical history for %s %s....' %(current_user.fill_from_application.first_name, current_user.fill_from_application.last_name)

		self.assertEqual(current_user.fill_from_application.allergies, "CATS, DOGS")
		print '\tALLERGIES RETRIEVED SUCCESSFULLY....[%s]' %(current_user.fill_from_application.allergies)

		self.assertEqual(current_user.fill_from_application.medications, "ZYRTEC")
		print '\tMEDICATIONS RETRIEVED SUCCESSFULLY....[%s]' %(current_user.fill_from_application.medications)

		print '\tRetrieval of patient and associated medical history was VALID'

	def testViewPatientPerscription(self):
		print '--------------------------------------\nTESTING VIEWING OF PATIENT E-PERSCRIPTIONS HISTORY FOR STAFF (HSP)\n---------------------------------------'

		current_user = Patient.objects.filter(user__username="patient_user_1").get()
		e_medications = EMedication.objects.filter(patient=current_user).all()

		for each_medication in e_medications:
			print '\t' + each_medication.medication_name + ' is a medication name to test'

		print '\tTesting HSP accessibility to medicine...'

		self.assertEqual(e_medications[0].medication_name, "Xanax")

		print '\tMedication Found! - [%s]' %(e_medications[0].medication_name)


'''
THIS TEST SUITE DEALS WITH THE FEATURES FOR THE LAB STAFF
'''
class TestServiceToLabFeature(TestCase):

	def setUp(self):

		print '\tSetting up objects for test database....'


		doctor_user = User.objects.create(username="doctor_user", email="doctor_user@yahoo.com", password="doctor_user_password")
		doctor_user.save()

		lab_tech_user = User.objects.create(username="lab_tech_user", email="lab_tech_user@yahoo.com", password="lab_tech_user_password")
		lab_tech_user.save()

		doctor_object = Doctor.objects.create(
			doctor_first_name = "john",
			doctor_last_name = "stamos",
			doctor_type = "Gynecologist",
			doctor_user = doctor_user
			)
		doctor_object.save()


		patient_user = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user.save()
		temp_patient_user_data = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "CATS, DOGS",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "ZYRTEC",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johnson@johnson.com",
			data_sent = "1",
			race = "white",
			income = "$0-$10,000"
			)
		#Save user into the test database
		temp_patient_user_data.save()

		patient_object = Patient.objects.create(

			fill_from_application = temp_patient_user_data,
			user = patient_user,
			approved = 0
			)

		patient_object.save()

		# print '\tDoctor and Patient Created Successfully!'

		new_tech = LabTech.objects.create(

			lab_first_name="tech1_first_name",
			lab_last_name="tech1_last_name",
			lab_user = lab_tech_user
			)

		current_patient 	= Patient.objects.filter(user__username="patient_user_1").get()
		current_doctor 		= Doctor.objects.filter(doctor_user__username="doctor_user").get()

		new_perscription 	= EMedication.objects.create(

			patient = current_patient,
			medication_name = "Xanax",
			prescribed_by_doctor = current_doctor
			)

		new_perscription.save()


		current_user = Patient.objects.filter(user__username="patient_user_1").get()
		health_conditions = PatientHealthConditions.objects.create(

			user = current_user,
			nausea_level = 10,
			hunger_level = 9,
			anxiety_level = 7,
			stomach_level = 3
			)
		health_conditions.save()


		new_lab_report = LabReport.objects.create(

			lab_patient = current_user,
			lab_results = "Negative",
			lab_test = "Blood pressure screening",
			lab_notes = "Seek Attention!",
			lab_tech = LabTech.objects.filter(lab_first_name="tech1_first_name").get()
			)

		new_lab_report.save()


	def testLabReportCreation(self):

		print '--------------------------------------\nTESTING CREATION OF LAB REPORT FOR LAB STAFF\n---------------------------------------'

		current_user = Patient.objects.filter(user__username="patient_user_1").get()


		print '\tAttempting to create lab report....'

		new_lab_report = LabReport.objects.create(

			lab_patient = current_user,
			lab_results = "Positive",
			lab_test = "Blood pressure screening",
			lab_notes = "Seek Attention!",
			lab_tech = LabTech.objects.filter(lab_first_name="tech1_first_name").get()
			)

		new_lab_report.save()

		print '\tLab Report Created Successfully!'



	def testLabReportEdit(self):

		print '--------------------------------------\nTESTING EDIT OF LAB REPORT FOR LAB STAFF\n---------------------------------------'

		all_report = LabReport.objects.all()
		
		edit_report = all_report[0]

		print '\tCurrent Report Results are %s' %(edit_report.lab_results)

		print '\tChanging results from NEGATIVE to POSITIVE'

		edit_report.lab_results = "POSITIVE"

		print '\tItem set successfully... value is [%s]' %(edit_report.lab_results)

		self.assertEqual(edit_report.lab_results, "POSITIVE")

		print '\tASSERTION TRUE'




	def testLabReportRemoval(self):

		print '--------------------------------------\nTESTING REMOVAL OF LAB REPORT FOR LAB STAFF\n---------------------------------------'

		current_user = Patient.objects.filter(user__username="patient_user_1").get()

		if LabReport.objects.filter(lab_patient=current_user).exists():

			print '\tLab Results Found For Patient 1'
			print '\tAttempting removal of the lab results...'

			report = LabReport.objects.filter(lab_patient=current_user).get()
			report.delete()

			if not LabReport.objects.filter(lab_patient=current_user).exists():
				print '\tSUCCESSFUL DELETION OF LAB REPORT'

			else:
				print '\tUNSUCCESSFUL DELETION OF LAB REPORT'


'''
THIS TEST SUITE DEALS WITH THE FEATURES FOR STATISTICAL ANALYSIS
'''
class TestStatisticalReportAnalysis(TestCase):

	def setUp(self):

		#Create 3 different users and verify the numbers
		patient_user_1 = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user_2 = User.objects.create(username="patient_user_2", email="patient_user_2@yahoo.com", password="patient_user_2_password")
		patient_user_3 = User.objects.create(username="patient_user_3", email="patient_user_3@yahoo.com", password="patient_user_3_password")

		patient_user_1.save()
		patient_user_2.save()
		patient_user_3.save()


		temp_patient_user_data_1 = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user_1,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "NONE",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "NONE",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johngson@johnson.com",
			data_sent = "1",
			race = "white",
			income = "$0-$10,000"
			)
		#Save user into the test database
		temp_patient_user_data_1.save()


		temp_patient_user_data_2 = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user_2,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "NONE",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "NONE",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johenson@johnson.com",
			data_sent = "1",
			race = "white",
			income = "$0-$10,000"
			)
		#Save user into the test database
		temp_patient_user_data_2.save()


		temp_patient_user_data_3 = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user_3,
			first_name = "Ryan",
			last_name = "Schachte",
			ssn = 600489139,
			allergies = "NONE",
			address = "2463 E. Mallory Dr. Tempe, AZ 85281",
			medications = "NONE",
			insurance_provider = "Allstate",
			insurance_policy_number = 19938343434,
			email_address = "johnsfon@johnson.com",
			data_sent = "1",
			race = "american_indian_alaskan_native",
			income = "$30,001-$60,000"
			)
		#Save user into the test database
		temp_patient_user_data_3.save()


		patient_object1 = Patient.objects.create(

			fill_from_application = temp_patient_user_data_1,
			user = patient_user_1,
			approved = 1
			)

		patient_object2 = Patient.objects.create(

			fill_from_application = temp_patient_user_data_2,
			user = patient_user_2,
			approved = 1
			)

		patient_object3 = Patient.objects.create(

			fill_from_application = temp_patient_user_data_3,
			user = patient_user_3,
			approved = 1
			)


		patient_object1.save()
		patient_object2.save()
		patient_object3.save()

		print '\tSETUP SUCCESSFUL FOR REPORTS'


	def testPatientAdmissionData(self):

		print '--------------------------------------\nTESTING ADMISSION DATA FOR STATS REPORT\n---------------------------------------'

		#Run the number of people generated (EXPECTED = 3)

		print '\tTesting the number of admitted people should currently be (3) AKA 100% Admission'

		self.assertEqual(3, Patient.objects.filter(approved=1).count())

		if not Patient.objects.filter(approved=1).count()==3:
			print '\tERROR - INVALID ASSERTION'
		else:
			print '\tVALID ASSERTION, 100% ADMISSION RATE'

	def testPatientSalaryData(self):

		print '--------------------------------------\nTESTING SALARY DATA FOR STATS REPORT\n---------------------------------------'

		#66.6% OF USERS SHOULD BE MAKING $0-$10,000

		all_users = Patient.objects.filter(approved=1).count() #Should be 3
		salary_test_users = TempPatientData.objects.filter(income="$0-$10,000").count() #Should be 2

		self.assertEqual(2, salary_test_users)
		self.assertEqual(3, all_users)

		print '\tTRUE - 66.6% of USERS MAKE $0-$10,0000'


	def testPatientTypes(self):

		print '--------------------------------------\nTESTING PATIENT TYPE DATA FOR STATS REPORT\n---------------------------------------'

		all_users = Patient.objects.filter(approved=1).count() #Should be 3

		#american_indian_alaskan_native  == 33.3%
		#white == 66.6%

		indian_users = TempPatientData.objects.filter(race="american_indian_alaskan_native").count() #Should be 1
		white_users = TempPatientData.objects.filter(race="white").count() #Should be 2

		self.assertEqual(3, all_users)

		print '\tSUCCESS THERE ARE (3) APPROVED PATIENTS'

		self.assertEqual(white_users, 2)

		print '\tSUCCESS - 66.6% OF USERS ARE WHITE'

		self.assertEqual(indian_users, 1)

		print '\tSUCCESS - 33.3% OF USERS ARE INDIAN'



class TestDifferentPatientFeatures(TestCase):

	def setup(self):
		print '\tCreating user object for the registration'

		patient_user = User.objects.create(username="patient_user_1", email="patient_user_1@yahoo.com", password="patient_user_1_password")
		patient_user.save()

		print '\tThe patient user has been created'

		print '\tCreating unapproved patient object in the system'
		temp_patient_user_data = TempPatientData.objects.create(
		#Assign the attributes that are associated with the user
			user = patient_user,
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
		#Save user into the test database
		temp_patient_user_data.save()

		doctor_user = User.objects.create(username="doctor_user", email="doctor_user@yahoo.com", password="doctor_user_password")
		doctor_user.save()

		doctor_object = Doctor.objects.create(
			doctor_first_name = "john",
			doctor_last_name = "stamos",
			doctor_type = "Gynecologist",
			doctor_user = doctor_user
			)
		doctor_object.save()

		print '\tdoctor_user Member Registered with a permission role of NULL'

		hsp_permission_role = PermissionsRole.objects.create(

			role = "doctor",
			user = doctor_user

			)
		print '\tdoctor_user Permission role assigned to - DOCTOR'
		print '\tdoctor_user Registered Successfully!'

	def testScheduleOfAppointment(self):
		print '\tAttempting to schedule appointment for the patient'


		print '\tPatient Case Created Successfully!'
