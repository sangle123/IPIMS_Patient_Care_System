from __future__ import absolute_import
from django.views import generic
from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from .forms import RegistrationForm, LoginForm, PatientForm, PatientHealthConditionsForm, TempPatientDataForm, EMedicationForm, LabReportForm
from django.template import RequestContext
from django.views.generic import ListView
from .models import PermissionsRole, Patient, PatientHealthConditions, TempPatientData, Alert,PatientAppt, Doctor, EMedication, LabReport, AddMedicalHistory
from .forms import RegistrationForm, LoginForm, PatientForm, PatientHealthConditionsForm, TempPatientDataForm, EMedicationForm
from django.template import RequestContext
from django.views.generic import ListView
from .models import PermissionsRole, Patient, PatientHealthConditions, TempPatientData, Alert,PatientAppt, Doctor, EMedication
from django.shortcuts import render_to_response
from .forms import PatientApptForm
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404,redirect
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
import datetime

#from django.shortcuts import redirect, get_object_or_404

STAFF_APPROVAL_ROLES = ('admin', 'doctor', 'staff', 'nurse', 'lab')


def AlertSender(request):
	#This method should be responsible for sending an alert to the doctor and HSP staff when the patient requests and alert to be sent

	# #print ('inside alert sender')
	patient_model = Patient.objects.get(user__username=request.user.username)
	health_conditions_model = PatientHealthConditions.objects.get(user=patient_model)
	patient_data_information = TempPatientData.objects.get(user__username=request.user.username)

	total_health_condition_level =  (health_conditions_model.nausea_level +
									health_conditions_model.hunger_level +
									health_conditions_model.anxiety_level+
									health_conditions_model.stomach_level+
									health_conditions_model.body_ache_level+
									health_conditions_model.chest_pain_level)



	#If this is a post method requested by the user, then execute the following logic
	if request.method == 'POST':

		desc = request.POST.get('desc')

		if desc is None:
			desc = "NO DESCRIPTION"

		#instantiate an alert model for the user
		alert_model = Alert(alert_patient = patient_model, alert_description = desc, alert_level = total_health_condition_level)
		patient_model.alertSent = 1
		patient_model.save()
		alert_model.save()

	# return render(request, '/accounts/portal/')
	return redirect(reverse('Portal'))

'''
Homepage to display the main control panel or HomePage based on user authentication
'''

def HomePageView(request):



	#Model Definitions & Declarations
	permissionModel = PermissionsRole
	patientModel = Patient

	#temp data for the user has been found
	tempDataFound = 0

	#Assign default permission role
	permissionRoleForUser = 'pending'
	medications_for_patient = ""

	#Assign a default approval rating
	approval = 0

	#Assign a default authentication boolean
	authenticated = False

	# approvalSwitch = 0

	#Check to see if the user has logged into the system or not
	if request.user.is_authenticated():

		#Boolean to ensure valid request authentication
		authenticated = True

		#Attempt a DB query on the request object
		if permissionModel.objects.filter(user__username=request.user.username)[:1].exists():

			#If request object from query exists, create a variable assignment on that object
			permissionRoleForUser = permissionModel.objects.filter(user__username=request.user.username)[:1].get()

			#If the logged in person is a patient, grab request object, make a query and grab the approval integer
			if patientModel.objects.filter(user__username=request.user.username)[:1].exists():

				#Get an integer declaraction for the approval of the user
				approvalSwitch = patientModel.objects.filter(user__username=request.user.username)[:1].get()

			#If the person is a hospital member, then they will automatically be considered approved
			if (permissionRoleForUser.role in STAFF_APPROVAL_ROLES):
				approval = 1
			else:
				if patientModel.objects.filter(user__username=request.user.username)[:1].exists():
					approval = approvalSwitch.approved
				else:
					approval = 0

	#Under the instance that the user is not authenticated
	else:
		permissionRoleForUser = ""



	return render( request, 'index.html', {'permissionModel': permissionModel, 'user': request.user, 'roles': permissionRoleForUser, 'approval': approval, 'authenticated': authenticated})


'''''''''''''''''''''''''''''''''''''''''''''''''''
Basic success page response rendering for the user
'''''''''''''''''''''''''''''''''''''''''''''''''''

class SuccessPageView(generic.TemplateView):
	template_name = 'accounts/success.html'

def SuccessTestView(request):
	return render(request, 'accounts/success.html')


'''''''''''''''''''''''''''''''''''''''''''''''''''
Sign up view used to register a user into the system
'''''''''''''''''''''''''''''''''''''''''''''''''''

class SignUpView(generic.CreateView):

	form_class = RegistrationForm
	model = User
	template_name = 'register.html'
	success_url = reverse_lazy('Success')


'''''''''''''''''''''''''''''''''''''''''''''''''''
Login view for the user to redirect into the patient/admin portal
'''''''''''''''''''''''''''''''''''''''''''''''''''

class LoginView(generic.FormView):
	form_class = LoginForm
	success_url = reverse_lazy('Portal')
	template_name = 'login.html'

	def form_valid(self, form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
			login(self.request, user)
			return super(LoginView, self).form_valid(form)
		else:
			return self.invalid(form)

def PatientPortalView(request):
	# template_name = 'home.html'
	#Model Definitions & Declarations
	permissionModel = PermissionsRole
	patientModel = Patient
	userModel = User
	tempModel = TempPatientData
	conditions_complete = False
	patient_model = Patient
	conditions_model = PatientHealthConditions
	alert_model = Alert

	approvalSwitch = 0

	#Assign default permission role
	permissionRoleForUser = 'pending'
	medications_for_patient = ''

	#Assign a default approval rating
	approval = 0

	#Assign a default authentication boolean
	authenticated = False

	patient = -1

	total_health_condition_level = 0

	#If user has already sent an alert request
	alert_sent = 0

	#Check to see if the user has logged into the system or not
	if request.user.is_authenticated():

		if patient_model.objects.filter(user=request.user.id)[:1].exists():
			patient = patient_model.objects.filter(user=request.user.id)[:1].get()

			if Alert.objects.filter(alert_patient=patient)[:1].exists():
				alert_sent = 1
				patient.alertSent = 1
				patient.save()
			else:
				alert_sent = patient.alertSent

		if conditions_model.objects.filter(user=patient)[:1].exists():
			conditions_complete = True
			patient_conditions = conditions_model.objects.filter(user=patient)[:1].get()

			total_health_condition_level =  (patient_conditions.nausea_level +
											patient_conditions.hunger_level +
											patient_conditions.anxiety_level+
											patient_conditions.stomach_level+
											patient_conditions.body_ache_level+
											patient_conditions.chest_pain_level)


			if (total_health_condition_level >= 40 and alert_sent == 0 and not Alert.objects.filter(alert_patient=patient)[:1].exists()):
				patient.alertSent = 1
				alert_sent = 1
				alert_model = Alert(alert_patient = patient, alert_description = 'SENT BY HOSPITAL SYSTEM', alert_level = total_health_condition_level)
				alert_model.save()
				patient.save()

			if (total_health_condition_level < 40 and alert_sent == 0):
				if Alert.objects.filter(alert_patient=patient)[:1].exists():
					alert_model = Alert.objects.filter(alert_patient=patient)[:1].get()
					alert_model.delete()

			#If there is no alert for the user, set the status to 0
			if not Alert.objects.filter(alert_patient=patient)[:1].exists() and patient_model.objects.filter(user__username=request.user.username)[:1].exists():
				patient.alertSent = 0
				patient.save()

			#If there health conditions are
			if (total_health_condition_level < 40 and alert_sent == 1):
				if Alert.objects.filter(alert_patient=patient)[:1].exists():
					alert_model = Alert.objects.filter(alert_patient=patient)[:1].get()
					if alert_model.alert_description == 'SENT BY HOSPITAL SYSTEM':
						# alert_model = alert_model.objects.filter(alert_patient=patient)[:1].get()
						alert_model.delete()
						patient.alertSent = 0
						patient.save()

			#If there health conditions are
			if (total_health_condition_level > 40 and alert_sent == 1 and not Alert.objects.filter(alert_patient=patient)[:1].exists()):
				if Alert.objects.filter(alert_patient=patient)[:1].exists():
					patient.alertSent = 1
					alert_sent = 1
					alert_model = Alert(alert_patient = patient, alert_description = 'SENT BY HOSPITAL SYSTEM', alert_level = total_health_condition_level)
					alert_model.save()
					patient.save()



		#Boolean to ensure valid request authentication
		authenticated = True

		#Attempt a DB query on the request object
		if permissionModel.objects.filter(user=request.user.id)[:1].exists():

			#If request object from query exists, create a variable assignment on that object
			permissionRoleForUser = permissionModel.objects.filter(user=request.user.id)[:1].get()

			#If the logged in person is a patient, grab request object, make a query and grab the approval integer
			if patientModel.objects.filter(user=request.user.id)[:1].exists():

				#Get an integer declaraction for the approval of the user
				approvalSwitch = patientModel.objects.filter(user=request.user.id)[:1].get()

			#If the person is a hospital member, then they will automatically be considered approved
			if (permissionRoleForUser.role in STAFF_APPROVAL_ROLES):
				approval = 1
			else:
				approval = approvalSwitch.approved

	#Under the instance that the user is not authenticated
	else:
		permissionRoleForUser = ""

	tempUserInformation = ""
	if tempModel.objects.filter(user=request.user.id)[:1].exists():
		tempUserInformation = tempModel.objects.filter(user=request.user)[:1].get()

	form = TempPatientDataForm()

	if request.method == "POST":

		form = TempPatientDataForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.user = request.user
			instance.data_sent = 1
			instance.email_address = request.user.username
			instance.save()
			return HttpResponseRedirect('formsuccess')

	#Get an array for allergies
	if not request.user.username == "admin" and approval == 1 and permissionRoleForUser.role == 'patient':

		if tempUserInformation.allergies is not None:
			allergens = tempUserInformation.allergies.split(",")

		if tempUserInformation.medications is not None:
			med_conditions = tempUserInformation.medications.split(",")
	else:
		allergens = ""
		med_conditions =""

	alerts_count = Alert.objects.all().count()

	doc_name = ''
	appts = ''
	if (not permissionRoleForUser == 'pending' and permissionRoleForUser.role == 'doctor'):

		doc_obj = Doctor.objects.filter(doctor_user=request.user).get()

		doc_name = doc_obj.doctor_first_name + ' ' + doc_obj.doctor_last_name

		appts = PatientAppt.objects.filter(doctor=doc_obj, resolved=0).count()

		if appts == 0:
			appts = 'No Appointments'

	current_patient = ''

	if (not tempUserInformation == ''):
		if (Patient.objects.filter(fill_from_application=tempUserInformation).exists()):
			current_patient = Patient.objects.filter(fill_from_application=tempUserInformation).get()

	#Query all the people that have alert sent
	get_all_unapproved_patients = TempPatientData.objects.filter(data_sent=1).all()

	unapproved_patient_list = []
	temp_patient_data_list = []


	for each_patient in get_all_unapproved_patients:
		if (not Patient.objects.filter(fill_from_application = each_patient).exists()):
			unapproved_patient_list.append(each_patient)

	unapproved_count = len(unapproved_patient_list)

	if not permissionRoleForUser == "pending":
		if permissionRoleForUser.role == 'patient':
			patient_date_time_set = Patient.objects.filter(fill_from_application__user=request.user).get()
			#print patient_date_time_set.date_created
			if patient_date_time_set.date_created == '9-20-1995':
				d = datetime.date.today()
				user_date_add = datetime.datetime.now()
				#print ' is now'
				patient_date_time_set.date_created = user_date_add
				patient_date_time_set.save()
				#print patient_date_time_set.date_created
				#print 'SET'

	if not permissionRoleForUser == "pending":
		if permissionRoleForUser.role == 'patient':

			#Query the medication pickups for the patient
			medications_for_patient = EMedication.objects.filter(reminder=0, patient__user=request.user).all()
			#print medications_for_patient

			if len(medications_for_patient) == 0:
				medications_for_patient = "No Medications Pending"

	context = {

		'form': form,
		'permissionModel': permissionModel,
		'user': request.user,
		'roles': permissionRoleForUser,
		'approval': approval,
		'authenticated': authenticated,
		'conditions_complete': conditions_complete,
		'temp_user_data': tempUserInformation,
		'allergens': allergens,
		'med_conditions':med_conditions,
		'alert_sent':alert_sent,
		'alerts_count':alerts_count,
		'doc_name' : doc_name,
		'appts' : appts,
		'current_patient' : current_patient,
		'unapproved_patient_list' : unapproved_patient_list,
		'unapproved_count' : unapproved_count,
		'medications_for_patient' : medications_for_patient

	}

	return render(request, 'portal.html', context)

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
View that is responsible for rendering the patient scheduling system for the user
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def ScheduleView(request):

	title = "Appointment Schedule"
	form = PatientApptForm(request.POST or None)
	patient_model = Patient

	patient = patient_model.objects.filter(user__username=request.user.username)[:1].get()

	conditions_complete = False

	conditions_model = PatientHealthConditions
	if (conditions_model.objects.filter(user=patient)[:1].exists()):
		conditions_complete = True
		patient_conditions = conditions_model.objects.filter(user=patient)[:1].get()

	if form.is_valid():
		instance = form.save(commit=False)
		instance.patient = patient
		instance.user = patient
		instance.current_health_conditions = patient_conditions
		instance.save()
		return HttpResponseRedirect('formsuccess')

	context = {
		"form": form,
		"template_title": title,
		"conditions_complete": conditions_complete
	}
	return render(request, 'schedule.html', context)

def HealthConditionsView(request):

	title = "Health Conditions"
	form = PatientHealthConditionsForm(request.POST or None)

	conditions_model = PatientHealthConditions
	patient_model = Patient

	data_exists = False

	#Check if the health conditions already exist within the database
	if patient_model.objects.filter(user__username=request.user.username)[:1].exists():
		patient = patient_model.objects.filter(user__username=request.user.username)[:1].get()

		if conditions_model.objects.filter(user=patient)[:1].exists():
			instance = conditions_model.objects.filter(user=patient)[:1].get()
			form = PatientHealthConditionsForm(instance=instance)
			data_exists = True

	if request.method == "POST":

		if conditions_model.objects.filter(user=patient)[:1].exists():
			instance = conditions_model.objects.filter(user=patient)[:1].get()
			form = PatientHealthConditionsForm(request.POST, instance=instance)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.user = patient
			instance.save()
			return HttpResponseRedirect('formsuccess')


	context = {
		"form": form,
		"template_title": title
	}

	return render(request, 'healthconditions.html', context)

#View that allows the admin user or employee to search for a patient
def PatientSearch(request):

	user_has_been_located = False

	patient_model = Patient #Perform queries on the database model that holds all the patient information

	search_data_list = ""

	patient_found = ''

	#Grab the post param information so that you can perform iteration logic through the database on the searchable customer
	if request.method == "POST":
		search_data = request.POST.get("search_data", "") #store the data of the user search information into a variable that you can parse
		db_search_type = request.POST.get("db_search_type", "")

		search_data_list = search_data.split(" ") #If there is more than one entry in the search bar, parse it as necessary

		#Check to see if the inputted email matches any of the patient emails in the databases
		if db_search_type == "email":
			if patient_model.objects.filter(fill_from_application__email_address__iexact=search_data_list[0]).exists():
				patient_found = patient_model.objects.filter(fill_from_application__email_address__iexact=search_data_list[0]).get()
				search_data_list.append(patient_found)
				user_has_been_located = True

		elif db_search_type == "firstlast":
			if patient_model.objects.filter(fill_from_application__first_name__iexact=search_data_list[0]).exists() and patient_model.objects.filter(fill_from_application__last_name__iexact=search_data_list[1]).exists():
				patient_found = patient_model.objects.filter(fill_from_application__first_name__iexact=search_data_list[0], fill_from_application__last_name__iexact=search_data_list[1]).all()
				search_data_list.append(patient_found)
				user_has_been_located = True

	if search_data_list == "":

		context = {

			'search_data': 'none',
			'located': user_has_been_located
		}

	elif user_has_been_located == True:


		context = {

			'search_data': search_data_list,
			'temp_user_data': patient_found,
			'located': user_has_been_located
		}

	else:

		context = {

			'search_data': search_data_list,
			'temp_user_data': patient_found,
			'located': user_has_been_located
		}

	return render(request, 'search.html', context)

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
View that forces request object to log out of the system
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def DeleteUser(request):

	patient_model = Patient

	if request.method == "POST":
		pk_id = request.POST.get("pk", "")
		if patient_model.objects.filter(id=pk_id).exists():
			found_patient_object = patient_model.objects.filter(id=pk_id).get()
			found_patient_object.delete()

	context = {

		'pk_id': pk_id
	}

	return render(request, 'deleted.html', context)

def EmergencyAlerts(request):

	#Model Definitions & Declarations
	permissionModel = PermissionsRole
	patientModel = Patient
	userModel = User
	tempModel = TempPatientData
	conditions_complete = False
	patient_model = Patient
	conditions_model = PatientHealthConditions
	alert_model = Alert

	#Check to see if the user has logged into the system or not
	if request.user.is_authenticated():

		#Boolean to ensure valid request authentication
		authenticated = True

		#Attempt a DB query on the request object
		if permissionModel.objects.filter(user__username=request.user.username)[:1].exists():

			#If request object from query exists, create a variable assignment on that object
			permissionRoleForUser = permissionModel.objects.filter(user__username=request.user.username)[:1].get()

			#If the person is a hospital member, then they will automatically be considered approved
			if (permissionRoleForUser.role in STAFF_APPROVAL_ROLES):
				approval = 1
			else:
				approval = 0

	#Under the instance that the user is not authenticated
	else:
		permissionRoleForUser = ""

	alerts_count = Alert.objects.all().count()
	all_alerts = Alert.objects.all()

	context = {

		'roles': permissionRoleForUser,
		'alerts_count':alerts_count,
		'alerts': all_alerts
	}

	return render(request, 'view_alerts.html', context)


#This is the view that is going to be used to update the account information for the user
def UpdateAccountView(request):
	title = "Update Account Information"
	form = TempPatientDataForm(request.POST or None)
	patient_model = Patient


	patient = patient_model.objects.filter(user=request.user)[:1].get()

	if (TempPatientData.objects.filter(user=request.user)[:1].exists()):

		instance = TempPatientData.objects.filter(user=request.user)[:1].get()
		form = TempPatientDataForm(instance = instance)

	if request.method == "POST":

		TPD = TempPatientData.objects.filter(user=request.user)[:1].get()

		if (not TPD is None):
			instance = TempPatientData.objects.filter(user=request.user)[:1].get()

			# form = TempPatientDataForm(request.POST, instance = instance)

		form = TempPatientDataForm(request.POST, instance = TPD)
		if form.is_valid():

			form.save()

		return HttpResponseRedirect('/accounts/portal/update_account/')


	context = {
		"form": form,
		"template_title": title
	}
	return render(request, 'update_account.html', context)

def CreateEmployeeView(request):

	#Grab the post parameters for the following data

	if request.method == "POST":
		user_name = request.POST.get('username')
		password = request.POST.get('password')
		staff_type = request.POST.get('staff_type')
		role = request.POST.get('role')

	user_model = User

#This view is responsible for quering all the currently existent appts for a user in the database and displaying the data to the page
def ApptView(request):

	current_appts_list = []

	#First you need to get the current patient to associate the patient with the appts
	current_patient = Patient.objects.filter(user=request.user)[:1].get()

	#Now you need to find all the appts that are associated with the current user who is logged in
	if (PatientAppt.objects.filter(user=current_patient)[:1].exists()):
		current_appts = PatientAppt.objects.filter(user=current_patient).all()
		for appts in current_appts:
			current_appts_list.append(appts)

	context = {

		'current_appts_list': current_appts_list,
		'current_patient': current_patient
	}

	return render(request, 'view_appts.html', context)

def view_ApptHistory(request):

	current_appts_list = []

	#First you need to get the current patient to associate the patient with the appts
	current_patient = Patient.objects.filter(user=request.user)[:1].get()

	#Now you need to find all the appts that are associated with the current user who is logged in
	if (PatientAppt.objects.filter(user=current_patient)[:1].exists()):
		current_appts = PatientAppt.objects.filter(user=current_patient).all()
		for appts in current_appts:
			current_appts_list.append(appts)

	context = {

		'current_appts_list': current_appts_list,
		'current_patient': current_patient

	}

	return render(request, 'view_ApptHistory.html', context)

def GenerateStatsView(request):


	roles = PermissionsRole.objects.filter(user=request.user.id)[:1].get()
	# roles = "doctor"

	#GENDER
	total_patients = TempPatientData.objects.filter().count()

	num_males = (float(TempPatientData.objects.filter(gender='male').count())/float(total_patients))*100
	num_females = (float(TempPatientData.objects.filter(gender='female').count())/float(total_patients))*100
	num_other = (float(TempPatientData.objects.filter(gender='other').count())/float(total_patients))*100
	num_PNTS = (float(TempPatientData.objects.filter(gender='prefer not to say').count())/float(total_patients))*100
	num_males = format(num_males, '.2f')
	num_females = format(num_females, '.2f')
	num_other = format(num_other, '.2f')
	num_PNTS = format(num_PNTS, '.2f')

	#RACE
	num_white = (float(TempPatientData.objects.filter(race='white').count())/float(total_patients))*100
	num_white = format(num_white, '.2f')
	num_indian = (float(TempPatientData.objects.filter(race='american_indian_alaskan_native').count())/float(total_patients))*100
	num_indian = format(num_indian, '.2f')
	num_hawaiian = (float(TempPatientData.objects.filter(race='hawaiian').count())/float(total_patients))*100
	num_hawaiian = format(num_hawaiian, '.2f')
	num_black = (float(TempPatientData.objects.filter(race='black').count())/float(total_patients))*100
	num_black = format(num_black, '.2f')
	num_asian = (float(TempPatientData.objects.filter(race='asian').count())/float(total_patients))*100
	num_asian = format(num_asian, '.2f')
	num_other_race = (float(TempPatientData.objects.filter(race='other').count())/float(total_patients))*100
	num_other_race = format(num_other_race, '.2f')


	#INCOME
	num_1 = (float(TempPatientData.objects.filter(income='$0-$10,000').count())/float(total_patients))*100
	num_1 = format(num_1, '.2f')
	num_2 = (float(TempPatientData.objects.filter(income='$10,001-$30,000').count())/float(total_patients))*100
	num_2 = format(num_2, '.2f')
	num_3 = (float(TempPatientData.objects.filter(income='$30,001-$60,000').count())/float(total_patients))*100
	num_3 = format(num_3, '.2f')
	num_4 = (float(TempPatientData.objects.filter(income='$60,001-$85,000').count())/float(total_patients))*100
	num_4 = format(num_4, '.2f')
	num_5 = (float(TempPatientData.objects.filter(income='$85,001-$110,000').count())/float(total_patients))*100
	num_5 = format(num_5, '.2f')
	num_6 = (float(TempPatientData.objects.filter(income='$110,001+').count())/float(total_patients))*100
	num_6 = format(num_6, '.2f')
	num_7 = (float(TempPatientData.objects.filter(income='Prefer Not To Say').count())/float(total_patients))*100
	num_7 = format(num_7, '.2f')

	#AGE
	age_1 = (float(TempPatientData.objects.filter(age__range=(0,19)).count())/float(total_patients))*100
	age_1 = format(age_1, '.2f')

	age_2 = (float(TempPatientData.objects.filter(age__range=(19,45)).count())/float(total_patients))*100
	age_2 = format(age_2, '.2f')

	age_3 = (float(TempPatientData.objects.filter(age__range=(45,61)).count())/float(total_patients))*100
	age_3 = format(age_3, '.2f')

	age_4 = (float(TempPatientData.objects.filter(age__range=(61,130)).count())/float(total_patients))*100
	age_4 = format(age_4, '.2f')

	#HOSPITAL CASES RESOLVED
	total_cases = PatientAppt.objects.filter().count()

	if (not total_cases == 0):

		resolved_cases = (float(PatientAppt.objects.filter(resolved=1).count())/float(total_cases))*100
		resolved_cases = format(resolved_cases, '.2f')

		unresolved_cases = (float(PatientAppt.objects.filter(resolved=0).count())/float(total_cases))*100
		unresolved_cases = format(unresolved_cases, '.2f')
	else:
		resolved_cases = 0
		unresolved_cases = 0


	#QUERY ALL THE MOST RECENT PATIENT WITHIN THE LAST 30 DAYS

	today = datetime.date.today()
	thirty_days_ago = today - datetime.timedelta(days=30)
	entries = Patient.objects.filter(date_created__gte=thirty_days_ago)
	accepted_count_last_30_days = 0
	all_accepted = 0
	all_denied = 0

	staff_roles = PermissionsRole.objects.exclude(role="patient").count()

	patient = Patient.objects.filter(approved=1).all()
	
	for patients in patient:
		all_accepted+=1


	for entry in entries:
		accepted_count_last_30_days+=1

	#print 'Accepted: %d and accepted_count_last_30_days: %d\n' %(all_accepted, accepted_count_last_30_days)

	context = {

		'roles' : roles,
		'num_males' : num_males,
		'num_females' : num_females,
		'num_other' : num_other,
		'num_PNTS' : num_PNTS,
		'total_patients' : total_patients,
		'num_white' : num_white,
		'num_indian' : num_indian,
		'num_hawaiian' : num_hawaiian,
		'num_black' : num_black,
		'num_asian' : num_asian,
		'num_other_race' : num_other_race,
		'num_1' : num_1,
		'num_2' : num_2,
		'num_3' : num_3,
		'num_4' : num_4,
		'num_5' : num_5,
		'num_6' : num_6,
		'num_7' : num_7,
		'age_1' : age_1,
		'age_2' : age_2,
		'age_3' : age_3,
		'age_4' : age_4,
		'unresolved_cases' : unresolved_cases,
		'resolved_cases' : resolved_cases,
		'accepted_count_last_30_days' : accepted_count_last_30_days,
		'all_accepted' : all_accepted,
		'staff_roles' : staff_roles
	}

	return render(request, 'stats.html', context)

def PatientDataView(request):

	#get permissions of current user
	roles = PermissionsRole.objects.filter(user=request.user)[:1].get()

	patients = ''

	if roles.role == 'doctor':
		current_doctor = Doctor.objects.filter(doctor_user=request.user)

		if PatientAppt.objects.filter(doctor=current_doctor).exists():

			patients = PatientAppt.objects.filter(doctor=current_doctor).all()
			if PatientAppt.objects.filter(doctor=current_doctor).count() == 0:
				patients = 0

			final_patient_list = []
			final_patient_users = []

			for patient in patients:
				if patient.user.user not in final_patient_users:
					final_patient_users.append(patient.user.user)
					final_patient_list.append(patient)

			patients = final_patient_list

		else:
			patients = 0



	context = {

		'roles' : roles,
		'patients' : patients

	}

	return render(request, 'view_patients.html', context)

def ScheduledDoctorAppointments(request):

	current_doctor = ''
	relevant_appts = ''
	roles 		   = ''

	if (Doctor.objects.filter(doctor_user = request.user).exists()):
		current_doctor = Doctor.objects.filter(doctor_user = request.user).get()
		relevant_appts = PatientAppt.objects.filter(doctor = current_doctor)
		roles = PermissionsRole.objects.filter(user__username=request.user.username)[:1].get()


	context = {

		'current_doctor' : current_doctor,
		'relevant_appts' : relevant_appts,
		'roles'          : roles
	}

	return render(request, 'doctor_scheduled_appointments.html', context)

def ResolvedPatientAjaxView(request):

	current_appt_num = ''
	current_appt = ''

	if request.is_ajax() or request.method == 'POST':

		primary_key_val = request.POST.get('appt_id')
		#print (primary_key_val)

		if PatientAppt.objects.filter(pk=primary_key_val).exists():
			current_appt = PatientAppt.objects.filter(pk=primary_key_val).get()

			if (current_appt.resolved == 0):
				current_appt.resolved = 1
				current_appt.save()
				current_appt_num = current_appt.resolved

			elif (current_appt.resolved == 1):
				current_appt.resolved = 0
				current_appt.save()
				current_appt_num = current_appt.resolved

	current_doctor = ''
	relevant_appts = ''
	roles 		   = ''

	if (Doctor.objects.filter(doctor_user = request.user).exists()):
		current_doctor = Doctor.objects.filter(doctor_user = request.user).get()
		relevant_appts = PatientAppt.objects.filter(doctor = current_doctor)
		roles = PermissionsRole.objects.filter(user__username=request.user.username)[:1].get()

	context = {

		'current_doctor' : current_doctor,
		'relevant_appts' : relevant_appts,
		'roles'          : roles,
		'current_appt'   : current_appt,
		'current_appt_num' : current_appt_num
	}

	return HttpResponseRedirect(reverse("ScheduledDoctorAppointments"))

def MedicalHistoryView(request):

	hsp_med_history = ""
	allergy_list 	= ""
	condition_list 	= ""

	if request.method == "POST" and 'pk_patient' in request.POST:

		patient_primary_key = request.POST.get('pk_patient', '')

		#print patient_primary_key

		patient_appts = PatientAppt.objects.filter(id=patient_primary_key).all()

		patient_obj = patient_appts[0].user

		patient_appts = PatientAppt.objects.filter(user=patient_obj).all()

		allergies = patient_obj.fill_from_application.allergies
		medications = patient_obj.fill_from_application.medications

		allergies = allergies.split(',')
		medications = medications.split(',')

		doc_meds = EMedication.objects.filter(patient=patient_obj).all()

		if (AddMedicalHistory.objects.filter(patient=patient_obj).exists()):

			hsp_med_history = AddMedicalHistory.objects.filter(patient=patient_obj).all()

			#print hsp_med_history

			condition_list = hsp_med_history.medical_conditions.split(',')

			allergy_list = hsp_med_history.allergies.split(',')



		context = {

			'appts' : patient_appts,
			'patient' : patient_obj,
			'temp_user_data' : patient_obj.fill_from_application,
			'allergies' : allergies,
			'medications' : medications,
			'doc_meds' : doc_meds,
			'hsp_med_history' : hsp_med_history,
			'allergy_list' : allergy_list,
			'condition_list' : condition_list
		}

	elif request.method == "POST" and 'pk_patient2' in request.POST:

		patient_primary_key = request.POST.get('pk_patient2', '')


		if (Patient.objects.filter(id=patient_primary_key).exists()):
			current_patient = Patient.objects.filter(id=patient_primary_key).get()
		elif (Patient.objects.filter(pk=patient_primary_key).exists()):
			current_patient = Patient.objects.filter(pk=patient_primary_key).get()

			#print ('EXISTS')
			current_patient = Patient.objects.filter(id=patient_primary_key).get()
			#print ('assigned based on user key')
		elif (Patient.objects.filter(pk=patient_primary_key).exists()):
			current_patient = Patient.objects.filter(pk=patient_primary_key).get()
			#print ('assigned based on primary key')


		if (AddMedicalHistory.objects.filter(patient=current_patient).exists()):

			hsp_med_history = AddMedicalHistory.objects.filter(patient=current_patient).all()

			#print hsp_med_history

		patient_appts = PatientAppt.objects.filter(user=current_patient).all()

		patient_obj = current_patient

		patient_appts = PatientAppt.objects.filter(user=patient_obj).all()

		allergies = patient_obj.fill_from_application.allergies
		medications = patient_obj.fill_from_application.medications

		allergies = allergies.split(',')
		medications = medications.split(',')

		doc_meds = EMedication.objects.filter(patient=current_patient).all()
		#print 'The doc meds are',
		#print doc_meds


		context = {

			'appts' : patient_appts,
			'patient' : patient_obj,
			'temp_user_data' : patient_obj.fill_from_application,
			'allergies' : allergies,
			'medications' : medications,
			'doc_meds' : doc_meds,
			'hsp_med_history' : hsp_med_history
		}


	return render(request, 'med_history.html', context)

def PrescribeMedicationView(request):

	title = "E-Medication Prescribe Form"
	form = EMedicationForm(request.POST or None)

	if form.is_valid():
		instance = form.save(commit=False)

		instance.save()
		return HttpResponseRedirect('formsuccess')


	context = {
		"form": form,
		"template_title": title,
	}
	return render(request, 'prescribe.html', context)

def ProcessPatientApproval(request):

	#Query the temp_patient_data from the primary key
	if request.method == "POST" and 'pk_pending' in request.POST:
		primary_key_val = request.POST.get('pk_pending', '')
		#print primary_key_val
		temp_object = TempPatientData.objects.filter(user_id=primary_key_val).get()

		#Create a new patient object 
		p = Patient.objects.create(fill_from_application=temp_object, user=temp_object.user, approved=1, alertSent=0)
		p.save()

		r = PermissionsRole.objects.create(role='patient', user=temp_object.user)
		r.save()


	return HttpResponseRedirect(reverse("PatientApprovalView"))

def PatientApprovalView(request):

	#Query all the people that have alert sent
	get_all_unapproved_patients = TempPatientData.objects.filter(data_sent=1).all()

	unapproved_patient_list = []
	temp_patient_data_list = []


	for each_patient in get_all_unapproved_patients:
		if (not Patient.objects.filter(fill_from_application = each_patient).exists()):
			unapproved_patient_list.append(each_patient)

	unapproved_count = len(unapproved_patient_list)

	context = {

		'unapproved_patient_list' : unapproved_patient_list,
		'size_of' : len(unapproved_patient_list)

	}

	return render(request, 'approval1.html', context)

def logout_user(request):
	logout(request)
	return HttpResponseRedirect(reverse_lazy('Home'))


class SuccessFormPageView(generic.TemplateView):
	template_name = 'accounts/formsuccess.html'

def appt_delete(request, pk):
	appt = get_object_or_404(PatientAppt,pk=pk)
	if request.method=='POST':
		appt.delete()
	current_appts_list = []
	#First you need to get the current patient to associate the patient with the appts
	current_patient = Patient.objects.filter(user=request.user)[:1].get()

	#Now you need to find all the appts that are associated with the current user who is logged in
	if (PatientAppt.objects.filter(user=current_patient)[:1].exists()):
		current_appts = PatientAppt.objects.filter(user=current_patient).all()
		for appts in current_appts:
			current_appts_list.append(appts)

	context = {

		'current_appts_list': current_appts_list,
		'current_patient': current_patient
	}
	return render(request,'view_appts.html',context)

def doctor_appt_delete(request, pk):
	doctor_appt = get_object_or_404(PatientAppt,pk=pk)
	if request.method=='POST':
		doctor_appt.delete()
	#First you need to get the current doctor to associate the doctor with the appts
	current_doctor = Doctor.objects.filter(doctor_user=request.user)

	if (Doctor.objects.filter(doctor_user = request.user).exists()):
		current_doctor = Doctor.objects.filter(doctor_user = request.user).get()
		relevant_appts = PatientAppt.objects.filter(doctor = current_doctor)
		roles = PermissionsRole.objects.filter(user__username=request.user.username)[:1].get()


	context = {

		'current_doctor' : current_doctor,
		'relevant_appts' : relevant_appts,
		'roles'          : roles

	}
	return render(request,'doctor_scheduled_appointments.html')


def clear_perscription_notification(request):

	#Find the prescription by the primary key and removing the notification
	if request.method == "POST" and 'pres' in request.POST:

		pres_pk = request.POST.get('pres')
		if (EMedication.objects.filter(pk=pres_pk).exists()):
			perscription_to_edit = EMedication.objects.filter(pk=pres_pk).get()
			perscription_to_edit.reminder = 1
			perscription_to_edit.save()
			return HttpResponseRedirect(reverse("Portal"))
	else:
		return HttpResponseRedirect(reverse("Portal"))


def get_lab_results(request):

	#This view is going to be responsible for getting all the lab results and description for each patient
	if request.method == "POST" and 'patient_labs' in request.POST:

		#We need to get all the lab results based on the patient PRIMARY KEY
		patient_labs = request.POST.get("patient_labs", "")
		patient_labs = int(patient_labs)

		patient_lab_results = LabReport.objects.filter(lab_patient__id=patient_labs).all()

		current_patient = Patient.objects.filter(id=patient_labs).get()

		context = {

			'patient_lab_results' : patient_lab_results,
			'current_patient' : current_patient
		}

		return render(request,'labresults.html', context)
	else:
		return HttpResponseRedirect(reverse("Portal"))

def display_all_lab_results(request):

	#Query all the lab reports in the system into an object to loop and display for

	all_lab_tests = LabReport.objects.all()


	if PermissionsRole.objects.filter(user__username=request.user.username)[:1].exists():
		roles = PermissionsRole.objects.filter(user__username=request.user.username)[:1].get()

	#print all_lab_tests

	context = {

		'all_lab_tests' : all_lab_tests,
		'roles' : roles
	}

	return render(request,'all_lab_results.html', context)

def delete_lab_results(request):

	if request.method == "POST" and "report_remove" in request.POST:

		lab_found = request.POST.get("report_remove", "")

		delete_this_lab = LabReport.objects.filter(pk=lab_found).get()
		delete_this_lab.delete()

		all_lab_tests = LabReport.objects.all()

		context = {

			'all_lab_tests' : all_lab_tests
		}

		return render(request,'all_lab_results.html', context)

def edit_lab_results(request):

	primary_key_val = ""

	if request.method == "POST" and "report_remove" in request.POST:

		lab_found = request.POST.get("report_remove", "")

		model_instance = LabReport.objects.get(pk=lab_found)

		#print 'The current lab model that has been found is: \n'
		#print model_instance

		primary_key_val = model_instance

		patient_object = model_instance.lab_patient

		form = LabReportForm(instance=model_instance)

		context = {
			'form' : form,
			'patient_object' : patient_object,
		}

		return render(request,'edit_lab_report.html', context)


	elif request.method == "POST" and "send_form" in request.POST:

		patient_id_key = request.POST.get('pk_patient2', '')
		# TempPatientData.objects.filter(id = 'pk_patient2').get()
		patient_id_key = int(patient_id_key)

		instance = get_object_or_404(LabReport, id=patient_id_key)

		form = LabReportForm(request.POST or None, instance=instance)
		if form.is_valid():
			form.save()

		return HttpResponseRedirect('formsuccess')


	elif request.method == "POST":


		form = LabReportForm(request.POST, instance=primary_key_val)

		context = {
			'form' : form
		}

		if form.is_valid():

			form.save()
			return HttpResponseRedirect('/accounts/portal/')

		return render(request,'all_lab_results.html', context)

def CreateLabReportView(request):

	title = "Lab Report Creation Form"
	form = LabReportForm(request.POST or None)

	if form.is_valid():
		instance = form.save(commit=False)

		instance.save()
		return HttpResponseRedirect('formsuccess')


	context = {
		"form": form,
		"template_title": title,
	}
	return render(request, 'create_report.html', context)


def FAQView(request):
	return render(request,'questions.html')


def ViewAllPatientData(request):

	temp_patient_data = Patient.objects.all()

	#print temp_patient_data

	context = {

		'temp_user_data' : temp_patient_data
	}

	return render(request, 'view_all_patient_data_hsp.html', context)

def RemoveEmergencyAlert(request):

	if request.method == "POST" and 'removal' in request.POST:

		post_key = request.POST.get('removal', '')

		removal_pk = Alert.objects.filter(alert_patient__pk=post_key).get()

		removal_pk.delete()

		return HttpResponseRedirect(reverse("ViewAlerts"))

	else:
		return HttpResponseRedirect(reverse("ViewAlerts"))

def ViewCurrentPrescriptions(request):

	if request.method == "POST" and "pk_patient2" in request.POST:
		prim_key = request.POST.get("pk_patient2", "")

		#Primary key for the patient is grabbed, now we need to get all the perscriptions that are associated with that patient
		current_patient = Patient.objects.filter(pk=prim_key).get()
		perscriptions = EMedication.objects.filter(patient=current_patient).all()

		perscription_list = []

		for scripts in perscriptions:
			perscription_list.append(scripts)

		context = {

			'scripts' : perscription_list,
			'current_patient' : current_patient
		}

	return render(request, 'view_pat_perscriptions.html', context)


def MedicalReportView(request):

	if request.method == "POST" and "pk_patient2" in request.POST:

		#Store the primary key into a variable to query the patient object
		primary_key_val = request.POST.get('pk_patient2', '')

		patient_obj = Patient.objects.filter(pk=primary_key_val).get()

		context = {

			'patient_obj' : patient_obj
		}
		return render(request,'upload_med_report.html', context)

	else: 
		return render(request,'upload_med_report.html')

def CreateMedicalReportView(request):

	if request.method == "POST":

		patient_prim_key = request.POST.get('pk_patient2', '')
		patient_allergies = request.POST.get('allergies', '')
		patient_conditions = request.POST.get('conditions', '')

		#parse out commas and grab the current patient
		current_patient = Patient.objects.filter(pk=patient_prim_key).get()

		allergy_list = patient_allergies.split(',')

		condition_list = patient_conditions.split(',')

		medical_history_object = AddMedicalHistory.objects.create(patient = current_patient, allergies = patient_allergies, medical_conditions = patient_conditions)

		medical_history_object.save()

		return render(request,'accounts/formsuccess.html')

def EditRelevantPatientMedicalHistory(request):


	if request.method == "POST" and not "send_form" in request.POST:

		patient_pk = request.POST.get("pk_patient2", "")

		instance = Patient.objects.filter(id=patient_pk).get()

		current_patient = instance

		instance = TempPatientData.objects.filter(patient=current_patient).get()

		form = TempPatientDataForm(instance = instance)

		context = {

			'form' : form,
			'current_patient' : current_patient
		}

		return render(request,'edit_patient_history.html', context)

	elif request.method == "POST" and "send_form" in request.POST:

		patient_id_key = request.POST.get('pk_patient2', '')
		# TempPatientData.objects.filter(id = 'pk_patient2').get()
		patient_id_key = int(patient_id_key)

		instance = get_object_or_404(TempPatientData, id=patient_id_key)

		form = TempPatientDataForm(request.POST or None, instance=instance)
		if form.is_valid():
			form.save()

		return HttpResponseRedirect('formsuccess')


def EditAppointmentPatientView(request, pk):

	appt = PatientAppt.objects.filter(pk=pk)[:1].get()
	form = PatientApptForm(instance=appt)
	health_cond = PatientHealthConditions.objects.filter(user=appt.user).get()
	if request.method =="POST":
		instance = form.save(commit=False)
		instance.user = appt.user
		instance.current_health_conditions = health_cond
		instance.save()

		form = PatientApptForm(instance=instance)
		if form.is_valid():
			form.save()
		else:
			print form.errors
			print 'invalid'
	
	context = {
		'form': form,
	}

	return render(request, 'schedule.html', context)

#Allow the patient to select their associated appointment and then push the data to the datbase
def PatientReviseAppointmentView(request):
	#Need to get the currently logged in patient
	#Need to get the primary key for the currently selected appointment in the system
	#Need to get all of the doctors to loop them through the combo box of the form

	if request.method == "POST" and 'current_patient_pk' in request.POST:

		#Query the patient from the database
		patient_search_key = request.POST.get('current_patient_pk', '')
		patient_appt_key = request.POST.get('current_appt_pk', '')

		if Patient.objects.filter(pk=patient_search_key).exists():

			#The object exists within the database, we need to store it
			current_patient = Patient.objects.filter(pk=patient_search_key).get()
			current_appt = PatientAppt.objects.filter(pk=patient_appt_key).get()

			#We need to query all of the doctors that lie within the system
			all_doctors = Doctor.objects.all()

			#Returning the current patient that is logged in
			#Returning the current appointment relevant to the patient that clicked on
			#Returning all the doctors that lie within the system to populate the combo fields

			#Get all of the appointment data and store into variables so you can reference it more easily in the template

			appt_date 				= current_appt.date
			appt_doctor 			= current_appt.doctor
			appt_pain_level 		= current_appt.pain_level
			appt_medical_conditions = current_appt.medical_conditions
			appt_allergies 			= current_appt.allergies
			appt_user 				= current_appt.user
			appt_current_health_con = current_appt.current_health_conditions
			appt_resolved 			= current_appt.resolved


			context = {

				'current_patient' : current_patient,
				'current_appt' : current_appt,
				'all_doctors' : all_doctors,
				'appt_date' : appt_date,
				'appt_doctor' : appt_doctor, 
				'appt_pain_level' : appt_pain_level, 
				'appt_medical_conditions' : appt_medical_conditions, 
				'appt_allergies' : appt_allergies, 
				'appt_user' : appt_user, 
				'appt_current_health_con' : appt_current_health_con, 
				'appt_resolved' : appt_resolved, 
				'patient_search_key' : patient_search_key,
				'patient_appt_key' : patient_appt_key,
			}

			#Return the context data to the template of the page to utilize in the template
			return render(request, 'appoint_revision_final.html', context)

		else:
			#If the request is not a POST method then return the template with no data inside of ti
			return render(request, 'appointment_revision_final.html')


#Add the ability to save the requested appointment changes from the portal of the appointment changer view
def SaveApptEditView(request):

	if request.method == "POST":

		#Query the patient from the database
		patient_search_key 		= request.POST.get('current_patient_pk', '')
		patient_appt_key 		= request.POST.get('current_appt_pk', '')
		patient_doctor_key 		= request.POST.get('chosen_doctor', '')

		new_appt_date 			= request.POST.get('appt_date', '')
		new_pain_level 			= request.POST.get('appt_pain_level', '')
		new_medical_conditions  = request.POST.get('appt_medical_conditions', '')
		new_allergies 			= request.POST.get('appt_allergies', '')

		#Convert into proper data type
		patient_search_key 		= int(patient_search_key)
		patient_appt_key 		= int(patient_appt_key)
		patient_doctor_key 		= int(patient_doctor_key)

		#push the post vars to the view to log the current patient data into teh system
		current_appt 			= PatientAppt.objects.filter(id=patient_appt_key).get()
		patient_doctor 			= Doctor.objects.filter(id=patient_doctor_key).get()

		#Begin updating the relevant fields for the appointment
		current_appt.date 				= new_appt_date
		current_appt.doctor 			= patient_doctor
		current_appt.pain_level 		= new_pain_level
		current_appt.medical_conditions = new_medical_conditions
		current_appt.allergies 			= new_allergies


		#Save the appointment updates to store into the database
		current_appt.save()

		#Return the patient to a success page
		return HttpResponseRedirect('formsuccess')