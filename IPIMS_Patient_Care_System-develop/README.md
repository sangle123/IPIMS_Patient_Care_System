<html>
<head>
# Django & Python Interactive Health System
</head>

<body>
<img src="https://travis-ci.org/Schachte/IPIMS_Patient_Care_System.svg?branch=develop"><br>

This is a collaborative project for CSE360. Our basic goal is to create a "health management system" that fulfills<br />
the needs of a basic private clinic. The various features can be found below

#How To Run This System In Your Machine<br>
<ol>
<li>Download PIP: http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows</li>
<li>Download Python: https://www.python.org/</li>
<li>Download the repo onto your local computer so you're in possession of all the files.</li>
<li>Ensure that you have python installed on your machine</li>
<li>Open your terminal or command line and navigate to the folder IPIMS_Django_Source_Files/ipcms</li>
<li>Run the command ./SYSTEM_SETUP from terminal and everything will automate in a bash script




In order to login to the admin panel, you need to navigate to http://localhost:8000/admin. The login can be create by opening your terminal to the project directory and typing in python createsuperuser.

<br>
<br><br>
<h1>Pre-load Fixture Data</h1><br>
<ol>
<li>Navigate to directory that the fixtures directory lives inside of</li>
<li>Type: 'python manage.py loaddata fixtures/initial_data.json4'</li>
</ol>


<h3>The usernames and passwords are the same</h3>
<ul>
    <li>patient1@patient.com - patient4@patient4.com</li>
    <li>nurse1@nurse1.com</li>
    <li>doctor1@doctor1.com</li>
    <li>hsp1@hsp1.com - hsp2@hsp2.com</li>
    <li>admin, admin</li>
</ul>

#Group Website For Management
<a href="http://group.ryan-schachte.com">http://group.ryan-schachte.com</a>
<br>

=======
# Project Contributors:<br />
<b>Admin</b> Wade Kariniemi- wkariniemi@gmail.com<br />
<b>Admin</b> Katelyn Duffy- katelyn.duffy@cox.net<br />
<b>Lead Dev</b> Ryan Schachte - code@asu.edu - (480) - 452 - 8825<br />
<b>Dev</b> Reman Koshaba- rkoshab1@asu.edu<br />
<b>Dev</b> Kevin Duong- ktduong@asu.edu<br />
<b>Dev</b> Minghao Wei(ming) mw19910824@gmail.com<br />
<b>Dev</b> Po-Kai(Jerry) Huang- jaffny@yahoo.com.tw<br />
<b>Dev</b> Javier Peralta - perajavier626@gmail.com<br />
<b>Dev</b> Jezreel Garcia - jgarci72@asu.edu<br />
<b>Dev</b> Sang Le - (602) 802 3450 - sble1@asu.edu<br />
<br>
=======


#<center>Useful Tutorials & Learning Resources</center></br>
<a href="https://docs.djangoproject.com/en/1.8/intro/tutorial01/">The Polls Tutorial (Written)</a>
This is a very useful tutorial written by English professors. The documentation is great and walks you through the basics of getting started.

<a href="https://www.youtube.com/watch?v=KZHXjGP71kQ">Getting Started with Django with Kenneth Love (Video)</a>
Also a very good beginner tutorial that will actually walk you through building a functional app with a database implementation and useful functionality.

<a href="https://www.youtube.com/playlist?list=PLEsfXFp6DpzRcd-q4vR5qAgOZUuz8041S">Creating MVP Landing Page in Django with Justin Mitchell (Video Series LONG)</a>
Don’t go through every single video in-depth. It’s time consuming, but very useful. 

#Relevant Resources<br>
We will be using HipChat for seamless group communication of the web. <a href="https://hipchat.com">Click Here</a></br>
We will be using Trello for clean and simple project management. <a href="https://trello.com/b/YylyWZ6n">Click Here</a></br>
We will be using Django framework, you can find a tutorial <a href="https://docs.djangoproject.com/en/1.8/intro/tutorial01/">Here</a></br>
<a href="https://docs.djangoproject.com/en/1.8/howto/windows/">For Windows</a></br>

#Various Features<br />
Managing patients’ information. <br />
Facilitating interactions between patients and health providers.<br />
Analysis of relevant statistical data for patient populations.<br /><br />

<b>1. Registration Information:</b><br />
I. Personal data, name, current address, SSN, contact details
and health care insurance information.<br />
II. Patient medical history (before the first visit)<br />
  a) Health service provider (HSP) staff upload the
medical reports (any known allergies, or past medical
history) which can be accessed by health service
providers.<br />
b) HSP staff can update the medical history records.<br />
c) The patient health records and history are stored.<br />

<b>2. Schedule Appointments</b><br />
a) Patients can request for appointments to health
providers.<br />
b) Patients selects the doctor (or the category of
doctors) for requested appointments (based on
the patient’s requirement, such as the types of
healthcare problems).<br />

<b>3. Update Healthcare Conditions</b><br />
a) Patient can update health conditions/concerns based on welldefined
systems like chest pain, nausea etc. <br />
b) Patient can send alert of health conditions/concerns to the IPIMS. <br />
c) IPIMS can determine the health condition severity of each
patients. The implemented system should provide accurate
outputs for quality evaluation. <br />
d) Arrival of an input with severe condition will trigger appropriate
actions to the healthcare provider for appropriate actions. <br />
e) In case of emergency, alert will be triggered to the available
doctors of emergency ward depending on the type of health
concerns. <br />

<b>4. Service to Doctors</b> <br />
a) Doctors can access each patient cases from IPIMS. <br />
b) Doctors and nurses update health conditions/concerns of
patients. <br />
c) Doctors can e-prescribe (with print functionalities)
medicines and lab tests. <br />
d) Doctors can also access lab records of patients. <br />

<b>5. Service to Staff </b> <br />
a) Healthcare service provider staff can retrieve information of
each patients like pharmacist can access the prescription of
the patients recommended by the doctor etc. <br />

<b>6. Lab Records </b><br />
a) Lab staff can enter or upload lab reports of
patients.<br />
b) Lab staff can edit lab records of the patients.<br />
7. Generation of Healthcare Statistical Reports<br />
a) Analysis of health outcomes.<br />
b) Tracking of the admission rates.<br />
c) Analysis of type of patients etc.<br />
d) Analysis of patient populations.<br />

<b>7. Generation of Healthcare Statistical Reports </b><br />
a) Analysis of health outcomes.<br />
b) Tracking of the admission rates.<br />
c) Analysis of type of patients etc.<br />
d) Analysis of patient populations.<br />

#Optional Features<br/>
... <br/>

</body>
</html>
