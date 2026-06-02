# 🏥 Municipal Health & Triage Management System (MHTMS)

A full-featured Django web application for local health clinics in Leyte, Eastern Visayas, Philippines.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install django djangorestframework django-crispy-forms crispy-bootstrap5 Pillow
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Create superuser (or use seeder)
```bash
python manage.py createsuperuser
```

### 4. Run development server
```bash
python manage.py runserver
```

---

## 👤 Demo Accounts

| Role   | Username         | Password    |
|--------|-----------------|-------------|
| Admin  | admin           | Admin@1234  |
| Doctor | dr_santos       | Doctor@1234 |
| Doctor | dr_reyes        | Doctor@1234 |
| Nurse  | nurse_dela_cruz | Nurse@1234  |
| Nurse  | nurse_garcia    | Nurse@1234  |

---

## 📁 Project Structure

```
mhtms/
├── accounts/          # Custom User model, roles, login, user management
│   ├── models.py      # User with role field (admin/doctor/nurse)
│   ├── views.py       # Login, dashboard, user CRUD
│   ├── decorators.py  # @doctor_required, @nurse_required, @admin_required
│   └── forms.py       # Login, UserCreation, UserEdit forms
│
├── patients/          # Patient registration and records
│   ├── models.py      # Patient, AuditLog models
│   ├── views.py       # Patient CRUD with Anti-IDOR protection
│   └── forms.py       # PatientForm
│
├── triage/            # Triage, queue, consultations, reports
│   ├── models.py      # TriageRecord, Consultation (with priority ordering)
│   ├── views.py       # Triage form, patient queue, bulk actions, reports
│   ├── forms.py       # TriageForm, ConsultationStatusForm
│   └── templatetags/
│       └── triage_tags.py   # Custom template filters and tags
│
├── api/               # Django REST Framework API
│   ├── views.py       # Public stats + HIPAA-masked patient endpoints
│   └── serializers.py # HIPAAMaskedPatientSerializer, PublicStatsSerializer
│
├── templates/         # All HTML templates
│   ├── base.html      # Sidebar layout
│   ├── accounts/      # Login, dashboard, user management
│   ├── patients/      # Patient list, detail, registration form
│   └── triage/        # Queue, triage form, consultation, reports
│       └── tags/      # Inclusion tag partials
│
└── static/css/
    └── mhtms.css      # Full custom design system
```

---

## 🔐 Security Features

### Anti-IDOR Protection
- All patient views filter by user role and ownership
- Nurses can only view patients they registered or triaged
- Doctors see all queue patients
- Admin sees everything
- 403 custom error page shown on unauthorized access

### DEBUG = False
- No traceback in production
- Custom 403, 404, 500 error pages
- No sensitive data leaked in error responses

### Role-Based Access Control
- `@doctor_required` — only doctors + admin
- `@nurse_required` — nurses, doctors, admin
- `@admin_required` — admin only
- All routes enforce authentication

### Audit Logging
- Every create, edit, view, discharge, login, logout is logged
- AuditLog model stores: user, action, patient, description, timestamp, IP

---

## 🔌 API Endpoints

### Public (No Auth Required)
```
GET /api/v1/stats/
{
  "region": "Leyte",
  "total_patients": 250,
  "critical_cases": 20,
  "treated_cases": 180
}

GET /api/v1/queue/
{
  "queue_length": 8,
  "by_priority": [...]
}
```

### HIPAA-Masked (Unauthenticated)
```
GET /api/v1/patients/
{
  "patient_name": "HIPAA Restricted",
  "diagnosis": "HIPAA Restricted",
  "address": "HIPAA Restricted",
  "age_group": "Adult (18-59)",
  "gender": "M"
}
```

### Authenticated (Full Access)
- Session auth required
- Returns full patient data

---

## 🎨 Priority Highlighting

| Priority | Color  | Django Tag            |
|----------|--------|----------------------|
| Critical | Red    | `{% show_priority_badge c.priority %}` |
| High     | Orange | Dynamic CSS class    |
| Medium   | Yellow | `priority-medium`    |
| Low      | Green  | `priority-low`       |

Critical patients also have a CSS pulse animation on the queue dashboard.

---

## ⚡ Bulk Actions

Doctors can select multiple patients and apply:
- 🚪 Discharge All
- ✅ Mark as Treated
- 🛏️ Admit All
- 🩺 Move to Consultation

---

## 🏗️ Django Models

- `User` — Custom AbstractUser with role field
- `Patient` — Full patient record with auto-generated ID (PT-00001)
- `TriageRecord` — Vitals + symptoms + priority
- `Consultation` — Status tracking + doctor assignment + diagnosis
- `AuditLog` — Full activity trail
