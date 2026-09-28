# 🌿 KSR Biology Digital Learning & Resource Portal

A minimalistic, modern, and high-performance Flask web portal for biology educators and students. Built with **Google Cloud Storage (GCS)** for secure, high-speed study material hosting and downloads.

---

## ✨ Features

### 🎓 Student Portal (Public)
* **Zero Friction Access:** Instant browsing with no student login or signup barriers.
* **Smart Filter Pills:** Filter materials by Grade (`Class 9`, `Class 10`, `Class 11`, `Class 12`, `NEET / Foundation`) and Resource Type (`Revision Notes`, `Question Bank & PYQs`, `Diagrams & Mind Maps`, `Worksheets & Practice`).
* **Real-time Instant Search:** Filter materials on-the-fly by topic, chapter, or keywords.
* **1-Click High-Speed Downloads:** Direct GCS v4 Signed URLs ensuring instant, reliable downloads.
* **Live In-Browser Preview:** Instant PDF preview in one click.
* **Live Announcement Ticker:** Real-time exam notifications, schedule alerts, and test updates.
* **WhatsApp Doubt Support:** 1-click button for students to connect directly with the teacher.

### 👩‍🏫 Teacher Admin Dashboard (`/admin`)
* **Secure Single-Teacher Authentication:** Simple PIN/Password login (`ksradmin2026` by default).
* **GCS Cloud Upload:** Drag-and-drop or select files (PDF, Word, Images, etc.) which upload directly to Google Cloud Storage (`pika-wil/ksr-biology/materials/...`).
* **Resource Management:** Edit metadata, toggle "Pinned / Featured" badges, replace files, or delete from both GCS and database.
* **Download Analytics:** Track download counts per material.
* **Live Notice Board Publisher:** Add or remove instant announcements visible on the home page.
* **Password Management:** Change teacher credentials anytime from the dashboard.

---

## 🚀 Quick Start

### 1. Requirements & Setup
Make sure you have Python 3.10+ installed.

```bash
# Clone or navigate to the project directory
cd /Users/sathishkumardm/Pikachooz2.0/ksrbiology

# Activate the existing virtual environment or create one
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)
The `.env` file is already configured with your Google Cloud credentials:
```env
GOOGLE_APPLICATION_CREDENTIALS=gcp_creds.json
GCS_BUCKET_NAME=pika-wil
GCS_FOLDER_PREFIX=ksr-biology
ADMIN_PASSWORD=ksradmin2026
SECRET_KEY=ksr-biology-super-secure-key-2026
```

### 3. Run the App
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
├── .env                  # GCP credentials and app secrets
├── gcp_creds.json        # Google Cloud Service Account credentials
├── app.py                # Flask routes, authentication, APIs
├── models.py             # SQLite / SQLAlchemy data models
├── gcs_helper.py         # Google Cloud Storage upload & signed URL helper
├── requirements.txt      # Python dependencies
├── run.sh                # Quick start script
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
