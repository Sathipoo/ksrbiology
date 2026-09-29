# 🌿 KSR Biology Digital Learning & Resource Portal

A minimalistic, modern, and high-performance Flask web portal for biology educators and students. Built with **Google Cloud Storage (GCS)** for secure, high-speed study material hosting and downloads.

---

## ✨ Features

### 🎓 Student Portal (Public)
* **Zero Friction Access:** Instant browsing with no student login or signup barriers.
* **Smart Filter Pills:** Filter materials by Grade (`Class 9`, `Class 10`, `Class 11`, `Class 12`, `NEET / Foundation`) and Resource Type (`Revision Notes`, `Question Bank & PYQs`, `Diagrams & Mind Maps`, `Worksheets & Practice`).
* **Real-time Instant Search:** Filter materials on-the-fly by topic, chapter, or keywords.
* **1-Click High-Speed Downloads:** Direct GCS v4 Signed URLs or Cloud Run GCS streaming fallback.
* **Live In-Browser Preview:** Instant PDF preview in one click.
* **Live Announcement Ticker:** Real-time exam notifications, schedule alerts, and test updates.

### 👩‍🏫 Teacher Admin Dashboard (`/admin`)
* **Secure Single-Teacher Authentication:** Simple PIN/Password login (`ksradmin2026` by default).
* **GCS Cloud Upload:** Drag-and-drop or select files (PDF, Word, Images, etc.) which upload directly to Google Cloud Storage (`pika-wil/ksr-biology/materials/...`).
* **Resource Management:** Edit metadata, toggle "Pinned / Featured" badges, replace files, or delete from both GCS and database.
* **Download Analytics:** Track download counts per material.
* **Live Notice Board Publisher:** Add or remove instant announcements visible on the home page.
* **Password Management:** Change teacher credentials anytime from the dashboard.

---

## ☁️ Deploying to Google Cloud Run

The application is fully configured for **Google Cloud Run** using native **Application Default Credentials (ADC)** — no service account JSON key file is needed on Cloud Run!

### Option A: One-Command Deployment via `deploy.sh`
```bash
./deploy.sh
```

### Option B: Deploy directly using `gcloud`
```bash
gcloud run deploy ksrbiology \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=pika-wil,GCS_FOLDER_PREFIX=ksr-biology,ADMIN_PASSWORD=ksradmin2026,SECRET_KEY=ksr-biology-cloud-run-key-2026"
```

> **Note:** Ensure your Cloud Run runtime service account (e.g. `PROJECT_NUMBER-compute@developer.gserviceaccount.com` or custom service account) has the **Storage Object Admin** role on the bucket `pika-wil`.

---

## 💻 Local Development

### 1. Requirements & Setup
```bash
cd /Users/sathishkumardm/Pikachooz2.0/ksrbiology

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
For local development, copy `.env.example` to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=gcp_creds.json
GCS_BUCKET_NAME=pika-wil
GCS_FOLDER_PREFIX=ksr-biology
ADMIN_PASSWORD=ksradmin2026
SECRET_KEY=ksr-biology-super-secure-key-2026
```

### 3. Run Locally
```bash
./run.sh
```
or
```bash
python3 app.py
```

* **Student Portal:** `http://127.0.0.1:5001`
* **Teacher Login:** `http://127.0.0.1:5001/admin/login` (Default password: `ksradmin2026`)

---

## 📁 Directory Structure
```
ksrbiology/
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore (excludes credentials & DB)
├── .dockerignore         # Docker ignore for lean containers
├── Dockerfile            # Production multi-threaded Gunicorn image
├── deploy.sh             # 1-Click Cloud Run deploy script
├── README.md             # Documentation
├── app.py                # Flask application, routes, APIs
├── models.py             # SQLAlchemy models & schema
├── gcs_helper.py         # GCS upload, signed URLs, and Cloud Run ADC fallback
├── requirements.txt      # Python dependencies
├── run.sh                # Local startup script
├── static/
│   ├── css/
│   │   └── style.css     # Modern responsive design & theme
│   └── js/
│       └── main.js       # Real-time search, filters, modals
└── templates/
    ├── base.html         # Base template with nav, footer, alerts
    ├── index.html        # Public student portal
    └── admin/
        ├── login.html    # Teacher login
        └── dashboard.html# Full resource management dashboard
```
