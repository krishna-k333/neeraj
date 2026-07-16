"""
Cloudinary upload helper for product catalog media.
"""
import cloudinary
import cloudinary.uploader
from config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

def upload_image(file_bytes: bytes, filename: str, folder: str = "neeraj/catalog") -> dict:
    result = cloudinary.uploader.upload(
        file_bytes,
        public_id=filename,
        folder=folder,
        resource_type="image",
        overwrite=False,
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}

def upload_video(file_bytes: bytes, filename: str, folder: str = "neeraj/videos") -> dict:
    result = cloudinary.uploader.upload(
        file_bytes,
        public_id=filename,
        folder=folder,
        resource_type="video",
        overwrite=False,
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}

def delete_media(public_id: str, resource_type: str = "image") -> dict:
    return cloudinary.uploader.destroy(public_id, resource_type=resource_type)
