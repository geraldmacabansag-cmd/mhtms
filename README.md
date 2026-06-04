# 🏥 Municipal Health \& Triage Management System (MHTMS)

A full-featured Django web application for local health clinics in Leyte, Eastern Visayas, Philippines.

\---

## 🚀 Quick Start

### 1\. Install dependencies

```bash
pip install django djangorestframework django-crispy-forms crispy-bootstrap5 Pillow
```

### 2\. Apply migrations

```bash
python manage.py migrate
```

### 3\. Create superuser (or use seeder)

```bash
python manage.py createsuperuser
```

### 4\. Run development server

```bash
python manage.py runserver
```

\---

## 👤 Demo Accounts

|Role|Username|Password|
|-|-|-|
|Admin|admin|admin1|
|Doctor|benjo\_dr|benjo\_dr123|
|Doctor|gerald\_dr|gerald\_dr123|
|Nurse|ash\_nr|ash\_nr123|
|Nurse|anne\_nr|anne\_nr123|

\---

\---

## 🔐 Security Features

### Anti-IDOR Protection

* All patient views filter by user role and ownership
* Nurses can only view patients they registered or triaged
* Doctors see all queue patients
* Admin sees everything
* 403 custom error page shown on unauthorized access

### DEBUG = False

* No traceback in production
* Custom 403, 404, 500 error pages
* No sensitive data leaked in error responses

### Role-Based Access Control

* `@doctor\_required` — only doctors + admin
* `@nurse\_required` — nurses, doctors, admin
* `@admin\_required` — admin only
* All routes enforce authentication

### Audit Logging

* Every create, edit, view, discharge, login, logout is logged
* AuditLog model stores: user, action, patient, description, timestamp, IP

\---

## 🔌 API Endpoints

### Public (No Auth Required)

```
GET /api/v1/stats/
{
  "region": "Leyte",
  "total\_patients": 250,
  "critical\_cases": 20,
  "treated\_cases": 180
}

GET /api/v1/queue/
{
  "queue\_length": 8,
  "by\_priority": \[...]
}
```

### HIPAA-Masked (Unauthenticated)

```
GET /api/v1/patients/
{
  "patient\_name": "HIPAA Restricted",
  "diagnosis": "HIPAA Restricted",
  "address": "HIPAA Restricted",
  "age\_group": "Adult (18-59)",
  "gender": "M"
}
```

### Authenticated (Full Access)

* Session auth required
* Returns full patient data

\---

## 🎨 Priority Highlighting

|Priority|Color|Django Tag|
|-|-|-|
|Critical|Red|`{% show\_priority\_badge c.priority %}`|
|High|Orange|Dynamic CSS class|
|Medium|Yellow|`priority-medium`|
|Low|Green|`priority-low`|

Critical patients also have a CSS pulse animation on the queue dashboard.

\---

## ⚡ Bulk Actions

Doctors can select multiple patients and apply:

* 🚪 Discharge All
* ✅ Mark as Treated
* 🛏️ Admit All
* 🩺 Move to Consultation

\---

## 🏗️ Django Models

* `User` — Custom AbstractUser with role field
* `Patient` — Full patient record with auto-generated ID (PT-00001)
* `TriageRecord` — Vitals + symptoms + priority
* `Consultation` — Status tracking + doctor assignment + diagnosis
* `AuditLog` — Full activity trail

