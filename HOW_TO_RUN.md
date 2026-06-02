# ▶️ How to Run MHTMS

## ⚠️ Why CSS wasn't showing
Django's `runserver` does NOT serve static files when `DEBUG = False`.
This project has two settings files for this reason:

| File | Use case |
|---|---|
| `settings.py` | Production (DEBUG=False, WhiteNoise, gunicorn) |
| `settings_dev.py` | Local development (DEBUG=True, runserver) |

---

## 🖥️ Local Development (Recommended for testing)

```bash
# 1. Install dependencies
pip install django djangorestframework django-crispy-forms crispy-bootstrap5 whitenoise Pillow

# 2. Apply migrations
python manage.py migrate

# 3. Run with DEV settings (CSS will work!)
python manage.py runserver --settings=mhtms.settings_dev

# 4. Open browser
# → http://127.0.0.1:8000/login/
```

## 🚀 Production Deployment (gunicorn + whitenoise)

```bash
pip install gunicorn
python manage.py collectstatic --noinput
gunicorn mhtms.wsgi:application --bind 0.0.0.0:8000
```

---

## 👤 Demo Login Accounts

| Role   | Username          | Password     |
|--------|-------------------|--------------|
| Admin  | `admin`           | `Admin@1234` |
| Doctor | `dr_santos`       | `Doctor@1234`|
| Doctor | `dr_reyes`        | `Doctor@1234`|
| Nurse  | `nurse_dela_cruz` | `Nurse@1234` |
| Nurse  | `nurse_garcia`    | `Nurse@1234` |

---

## 🔗 URLs

| Page | URL |
|---|---|
| Login | `/login/` |
| Dashboard | `/dashboard/` |
| Patient Queue | `/triage/queue/` |
| Patient List | `/patients/` |
| Reports | `/triage/reports/` |
| API Stats (public) | `/api/v1/stats/` |
| API Patients (HIPAA masked) | `/api/v1/patients/` |
| Django Admin | `/admin/` |
