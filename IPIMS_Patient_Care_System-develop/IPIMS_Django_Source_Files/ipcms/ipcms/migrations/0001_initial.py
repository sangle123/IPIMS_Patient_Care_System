# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AddMedicalHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allergies', models.CharField(default=b'', max_length=255)),
                ('medical_conditions', models.CharField(default=b'', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alert_level', models.IntegerField(default=0)),
                ('alert_description', models.CharField(default=b'', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doctor_first_name', models.CharField(default=b'', max_length=256)),
                ('doctor_last_name', models.CharField(default=b'', max_length=256)),
                ('doctor_type', models.CharField(default=b'Select Doctor Type', max_length=256, choices=[(b'Gynecologist', b'Gynecologist'), (b'Neurologist', b'Neurologist'), (b'Therapist', b'Therapist'), (b'Allergist', b'Allergist'), (b'Cardiologist', b'Cardiologist'), (b'Dermatologist', b'Dermatologist'), (b'Oncologist', b'Oncologist'), (b'ENT', b'ENT'), (b'Plastic Surgeon', b'Plastic Surgeon'), (b'Psychiatrist', b'Psychiatrist'), (b'Urologist', b'Urologist'), (b'Podiatrist', b'Podiatrist')])),
                ('doctor_user', models.OneToOneField(default=b'', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EMedication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medication_name', models.CharField(default=b'', max_length=255)),
                ('medication_quantity', models.IntegerField(default=0, null=True, blank=True)),
                ('reminder', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LabReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lab_results', models.CharField(max_length=255, choices=[(b'positive', b'Positive'), (b'negative', b'Negative')])),
                ('lab_test', models.CharField(max_length=255, choices=[(b'Blood pressure screening', b'Blood pressure screening'), (b'C-reactive protein test', b'C-reactive protein test'), (b'Colonoscopy', b'Colonoscopy'), (b'Diabetes risk tests', b'Diabetes risk tests'), (b'Pap smear', b'Pap smear'), (b'Skin cancer exam', b'Skin cancer exam'), (b'Blood Tests', b'Blood Tests')])),
                ('lab_notes', models.TextField(default=b'Insert Notes For Lab Test')),
            ],
        ),
        migrations.CreateModel(
            name='LabTech',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lab_first_name', models.CharField(default=b'', max_length=256)),
                ('lab_last_name', models.CharField(default=b'', max_length=256)),
                ('lab_user', models.OneToOneField(default=b'', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('approved', models.IntegerField(default=0)),
                ('alertSent', models.IntegerField(default=0)),
                ('date_created', models.CharField(default=b'9-20-1995', max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PatientAppt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.CharField(unique=True, max_length=1000)),
                ('pain_level', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('medical_conditions', models.CharField(default=b'None', max_length=1000)),
                ('allergies', models.CharField(default=b'None', max_length=1000)),
                ('resolved', models.IntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PatientHealthConditions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nausea_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('hunger_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('anxiety_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('stomach_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('body_ache_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('chest_pain_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('user', models.OneToOneField(default=b'', blank=True, to='ipcms.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='PermissionsRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=256, choices=[(b'admin', b'admin'), (b'nurse', b'nurse'), (b'staff', b'staff'), (b'doctor', b'doctor'), (b'patient', b'patient'), (b'lab', b'lab')])),
                ('user', models.OneToOneField(default=b'', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TempPatientData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_address', models.CharField(max_length=256)),
                ('first_name', models.CharField(default=b'', max_length=256)),
                ('last_name', models.CharField(default=b'', max_length=256)),
                ('age', models.IntegerField(default=18)),
                ('gender', models.CharField(default=b'Select a gender', max_length=256, choices=[(b'male', b'Male'), (b'female', b'Female'), (b'other', b'Other'), (b'prefer not to say', b'Prefer Not To Say')])),
                ('race', models.CharField(default=b'Other', max_length=256, choices=[(b'white', b'White'), (b'american_indian_alaskan_native', b'American Indian or Alaskan Native'), (b'hawaiian', b'Native Hawaiian or Other Pacific Islander'), (b'black', b'Black or African American'), (b'asian', b'Asian'), (b'other', b'Other')])),
                ('income', models.CharField(default=b'Prefer Not To Say', max_length=256, choices=[(b'$0-$10,000', b'$0-$10,000'), (b'$10,001-$30,000', b'$10,001-$30,000'), (b'$30,001-$60,000', b'$30,001-$60,000'), (b'$60,001-$85,000', b'$60,001-$85,000'), (b'$85,001-$110,000', b'$85,001-$110,000'), (b'$110,001+', b'$110,001+'), (b'Prefer Not To Say', b'Prefer Not To Say')])),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(default=b'', max_length=128, blank=True)),
                ('DOB', models.CharField(max_length=255, null=True, blank=True)),
                ('ssn', models.IntegerField(blank=True)),
                ('allergies', models.CharField(default=b'', max_length=256)),
                ('address', models.CharField(default=b'', max_length=256)),
                ('medications', models.CharField(default=b'', max_length=256)),
                ('insurance_provider', models.CharField(max_length=256)),
                ('insurance_policy_number', models.IntegerField(blank=True)),
                ('data_sent', models.IntegerField(default=0)),
                ('user', models.OneToOneField(null=True, default=b'', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='patientappt',
            name='current_health_conditions',
            field=models.ForeignKey(default=b'', blank=True, to='ipcms.PatientHealthConditions', null=True),
        ),
        migrations.AddField(
            model_name='patientappt',
            name='doctor',
            field=models.ForeignKey(default=-1, to='ipcms.Doctor'),
        ),
        migrations.AddField(
            model_name='patientappt',
            name='user',
            field=models.ForeignKey(default=b'', blank=True, to='ipcms.Patient'),
        ),
        migrations.AddField(
            model_name='patient',
            name='fill_from_application',
            field=models.OneToOneField(null=True, default=b'', to='ipcms.TempPatientData'),
        ),
        migrations.AddField(
            model_name='patient',
            name='user',
            field=models.OneToOneField(null=True, default=b'', blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='labreport',
            name='lab_patient',
            field=models.ForeignKey(default=b'0', to='ipcms.Patient'),
        ),
        migrations.AddField(
            model_name='labreport',
            name='lab_tech',
            field=models.ForeignKey(default=b'', to='ipcms.LabTech'),
        ),
        migrations.AddField(
            model_name='emedication',
            name='patient',
            field=models.ForeignKey(default=b'', to='ipcms.Patient'),
        ),
        migrations.AddField(
            model_name='emedication',
            name='prescribed_by_doctor',
            field=models.ForeignKey(default=b'0', to='ipcms.Doctor'),
        ),
        migrations.AddField(
            model_name='alert',
            name='alert_patient',
            field=models.OneToOneField(null=True, to='ipcms.Patient'),
        ),
        migrations.AddField(
            model_name='addmedicalhistory',
            name='patient',
            field=models.ForeignKey(default=b'', to='ipcms.Patient'),
        ),
    ]
