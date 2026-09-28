from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Material(db.Model):
    __tablename__ = "materials"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(50), nullable=False, default="Class 12")  # e.g., Class 9, Class 10, Class 11, Class 12, NEET / Medical
    chapter = db.Column(db.String(150), nullable=False)  # e.g., Genetics, Cell Biology, Ecology
    category = db.Column(db.String(100), nullable=False, default="Revision Notes") # Revision Notes, Question Bank & PYQs, Diagrams & Mind Maps, Worksheets
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    gcs_blob_name = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.String(50), default="1.0 MB")
    file_type = db.Column(db.String(20), default="PDF")
    is_pinned = db.Column(db.Boolean, default=False)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "grade": self.grade,
            "chapter": self.chapter,
            "category": self.category,
            "description": self.description,
            "filename": self.filename,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "is_pinned": self.is_pinned,
            "download_count": self.download_count,
            "created_at": self.created_at.strftime("%b %d, %Y")
        }

class Announcement(db.Model):
    __tablename__ = "announcements"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    badge = db.Column(db.String(50), default="Important") # e.g. "Important", "Exam Alert", "New Notes", "Live Class"
    link_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminConfig(db.Model):
    __tablename__ = "admin_config"
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
