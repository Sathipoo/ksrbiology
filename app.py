import os
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

from models import db, Material, Announcement, AdminConfig
from gcs_helper import (
    upload_file_to_gcs, generate_signed_url, delete_file_from_gcs,
    GCS_BUCKET_NAME, GCS_FOLDER_PREFIX
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ksr-biology-secret-super-key-2026")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///ksr_biology.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # Max 100MB upload limit

db.init_app(app)

# Helper: Admin login decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please sign in to access the teacher dashboard.", "warning")
            return redirect(url_for("admin_login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Prepopulate database with initial config and demo content if empty
def seed_initial_data():
    # 1. Admin Password Config
    default_pass = os.getenv("ADMIN_PASSWORD", "ksradmin2026")
    admin_pw_entry = AdminConfig.query.filter_by(key="admin_password_hash").first()
    if not admin_pw_entry:
        hashed = generate_password_hash(default_pass)
        db.session.add(AdminConfig(key="admin_password_hash", value=hashed))
        db.session.commit()
        
    # 2. Sample Announcements
    if Announcement.query.count() == 0:
        db.session.add(Announcement(
            title="NEET 2027 Rapid Revision Series Launched!",
            content="Check out the newly added High-Yield Genetics & Ecology Mind Maps under the Class 12 & NEET tabs.",
            badge="Exam Alert",
            link_url="#materials"
        ))
        db.session.add(Announcement(
            title="Class 10 CBSE Board Term-2 Sample Papers Available",
            content="Complete solution sheet with marking schemes has been uploaded.",
            badge="New Notes",
            link_url="#materials"
        ))
        db.session.commit()

# --- PUBLIC ROUTES ---

@app.route("/")
def index():
    # Fetch active announcements
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()
    
    # Fetch materials (pinned first, then newest)
    materials = Material.query.order_by(Material.is_pinned.desc(), Material.created_at.desc()).all()
    
    # Extract unique categories and chapters for filter pills
    grades = ["All", "Class 9", "Class 10", "Class 11", "Class 12", "NEET / Foundation"]
    categories = ["All", "Revision Notes", "Question Bank & PYQs", "Diagrams & Mind Maps", "Worksheets & Practice"]
    
    # Calculate stats
    total_materials = len(materials)
    total_downloads = sum(m.download_count for m in materials)
    total_chapters = len(set(m.chapter for m in materials if m.chapter))
    
    return render_template(
        "index.html",
        announcements=announcements,
        materials=materials,
        grades=grades,
        categories=categories,
        total_materials=total_materials,
        total_downloads=total_downloads,
        total_chapters=total_chapters,
        bucket_name=GCS_BUCKET_NAME,
        folder_prefix=GCS_FOLDER_PREFIX
    )

@app.route("/api/materials")
def api_materials():
    query = request.args.get("q", "").strip().lower()
    grade = request.args.get("grade", "All")
    category = request.args.get("category", "All")
    
    materials_query = Material.query
    
    if grade and grade != "All":
        materials_query = materials_query.filter(Material.grade == grade)
    if category and category != "All":
        materials_query = materials_query.filter(Material.category == category)
        
    materials = materials_query.order_by(Material.is_pinned.desc(), Material.created_at.desc()).all()
    
    if query:
        materials = [
            m for m in materials
            if query in m.title.lower() or query in (m.chapter or "").lower() or query in (m.description or "").lower()
        ]
        
    return jsonify([m.to_dict() for m in materials])

@app.route("/download/<int:material_id>")
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    # Increment download count
    material.download_count += 1
    db.session.commit()
    
    # Generate GCS signed download URL (forces download as original filename)
    signed_url = generate_signed_url(
        material.gcs_blob_name,
        disposition="attachment",
        download_name=material.filename,
        minutes=30
    )
    
    if signed_url:
        return redirect(signed_url)
    
    flash("Error generating download link. Please try again or contact teacher.", "danger")
    return redirect(url_for("index"))

@app.route("/preview/<int:material_id>")
def preview_material(material_id):
    material = Material.query.get_or_404(material_id)
    
    # Generate GCS signed inline preview URL (opens in browser PDF viewer)
    signed_url = generate_signed_url(
        material.gcs_blob_name,
        disposition="inline",
        download_name=material.filename,
        minutes=60
    )
    
    if signed_url:
        return redirect(signed_url)
    
    flash("Unable to load preview for this file.", "warning")
    return redirect(url_for("index"))

# --- ADMIN ROUTES ---

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
        
    if request.method == "POST":
        password = request.form.get("password", "")
        admin_entry = AdminConfig.query.filter_by(key="admin_password_hash").first()
        
        default_pw = os.getenv("ADMIN_PASSWORD", "ksradmin2026")
        is_valid = False
        
        if admin_entry and admin_entry.value:
            is_valid = check_password_hash(admin_entry.value, password)
        elif password == default_pw:
            is_valid = True
            
        if is_valid:
            session["admin_logged_in"] = True
            session.permanent = True
            flash("Welcome back, Teacher! Successfully logged in.", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        else:
            flash("Invalid teacher access password. Please try again.", "danger")
            
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("You have been signed out safely.", "info")
    return redirect(url_for("index"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    materials = Material.query.order_by(Material.is_pinned.desc(), Material.created_at.desc()).all()
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    total_materials = len(materials)
    total_downloads = sum(m.download_count for m in materials)
    
    return render_template(
        "admin/dashboard.html",
        materials=materials,
        announcements=announcements,
        total_materials=total_materials,
        total_downloads=total_downloads,
        bucket_name=GCS_BUCKET_NAME,
        folder_prefix=GCS_FOLDER_PREFIX
    )

@app.route("/admin/upload", methods=["POST"])
@admin_required
def admin_upload():
    title = request.form.get("title", "").strip()
    grade = request.form.get("grade", "Class 12").strip()
    chapter = request.form.get("chapter", "").strip()
    category = request.form.get("category", "Revision Notes").strip()
    description = request.form.get("description", "").strip()
    is_pinned = bool(request.form.get("is_pinned"))
    
    file = request.files.get("file")
    
    if not title or not chapter or not file or not file.filename:
        flash("Please fill all required fields and choose a file to upload.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    try:
        # Upload to Google Cloud Storage
        gcs_info = upload_file_to_gcs(file, folder="materials")
        
        # Save to Database
        new_material = Material(
            title=title,
            grade=grade,
            chapter=chapter,
            category=category,
            description=description,
            filename=gcs_info["original_filename"],
            gcs_blob_name=gcs_info["blob_name"],
            file_size=gcs_info["file_size"],
            file_type=gcs_info["file_type"],
            is_pinned=is_pinned,
            download_count=0
        )
        db.session.add(new_material)
        db.session.commit()
        
        flash(f"Successfully uploaded '{title}' ({gcs_info['file_size']}) to GCS bucket!", "success")
    except Exception as e:
        flash(f"Upload failed: {str(e)}", "danger")
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/material/<int:material_id>/toggle-pin", methods=["POST"])
@admin_required
def admin_toggle_pin(material_id):
    material = Material.query.get_or_404(material_id)
    material.is_pinned = not material.is_pinned
    db.session.commit()
    status = "pinned to top" if material.is_pinned else "unpinned"
    flash(f"'{material.title}' is now {status}.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/material/<int:material_id>/edit", methods=["POST"])
@admin_required
def admin_edit_material(material_id):
    material = Material.query.get_or_404(material_id)
    material.title = request.form.get("title", material.title).strip()
    material.grade = request.form.get("grade", material.grade).strip()
    material.chapter = request.form.get("chapter", material.chapter).strip()
    material.category = request.form.get("category", material.category).strip()
    material.description = request.form.get("description", "").strip()
    material.is_pinned = bool(request.form.get("is_pinned"))
    
    # Optional replace file
    new_file = request.files.get("file")
    if new_file and new_file.filename:
        # Delete old blob
        delete_file_from_gcs(material.gcs_blob_name)
        # Upload new blob
        gcs_info = upload_file_to_gcs(new_file, folder="materials")
        material.filename = gcs_info["original_filename"]
        material.gcs_blob_name = gcs_info["blob_name"]
        material.file_size = gcs_info["file_size"]
        material.file_type = gcs_info["file_type"]
        
    db.session.commit()
    flash(f"Updated '{material.title}' successfully.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/material/<int:material_id>/delete", methods=["POST"])
@admin_required
def admin_delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    blob_name = material.gcs_blob_name
    
    # Delete from GCS
    delete_file_from_gcs(blob_name)
    
    # Delete from DB
    db.session.delete(material)
    db.session.commit()
    flash(f"Material '{material.title}' deleted from GCS and database.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/announcement/add", methods=["POST"])
@admin_required
def admin_add_announcement():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    badge = request.form.get("badge", "Important").strip()
    link_url = request.form.get("link_url", "").strip()
    
    if title and content:
        ann = Announcement(
            title=title,
            content=content,
            badge=badge,
            link_url=link_url or None,
            is_active=True
        )
        db.session.add(ann)
        db.session.commit()
        flash("New announcement published live on the portal!", "success")
    else:
        flash("Announcement title and content cannot be empty.", "danger")
        
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/announcement/<int:ann_id>/delete", methods=["POST"])
@admin_required
def admin_delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash("Announcement removed.", "info")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/settings/password", methods=["POST"])
@admin_required
def admin_change_password():
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    
    if not new_password or len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    if new_password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    admin_entry = AdminConfig.query.filter_by(key="admin_password_hash").first()
    hashed = generate_password_hash(new_password)
    if admin_entry:
        admin_entry.value = hashed
    else:
        db.session.add(AdminConfig(key="admin_password_hash", value=hashed))
        
    db.session.commit()
    flash("Admin password updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# --- CLI COMMAND FOR CREATING TABLES & SAMPLE DATA ---
with app.app_context():
    db.create_all()
    seed_initial_data()

if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
