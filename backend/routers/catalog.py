from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Product
from services.cloudinary_client import upload_image, upload_video, delete_media
import uuid

router = APIRouter()


@router.get("/")
async def list_products(
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    q = select(Product).order_by(Product.created_at.desc())
    if category:
        q = q.where(Product.category == category)
    result = await db.execute(q)
    products = result.scalars().all()
    return [p.__dict__ for p in products]


@router.post("/")
async def add_product(
    name: str = Form(...),
    category: str = Form("saree"),
    color: str = Form(""),
    price: float = Form(0.0),
    description: str = Form(""),
    tags: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    filename = f"{uuid.uuid4().hex}"
    is_video = file.content_type.startswith("video")

    if is_video:
        result = upload_video(content, filename)
        media_type = "video"
    else:
        result = upload_image(content, filename)
        media_type = "image"

    product = Product(
        name=name,
        category=category,
        color=color,
        price=price,
        description=description,
        tags=tags,
        cloudinary_url=result["url"],
        cloudinary_public_id=result["public_id"],
        media_type=media_type,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product.__dict__


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    delete_media(product.cloudinary_public_id, product.media_type)
    await db.delete(product)
    await db.commit()
    return {"deleted": product_id}


@router.get("/search")
async def search_catalog(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Product).where(
            Product.name.ilike(f"%{q}%") |
            Product.tags.ilike(f"%{q}%") |
            Product.color.ilike(f"%{q}%") |
            Product.category.ilike(f"%{q}%")
        ).limit(20)
    )
    return [p.__dict__ for p in result.scalars().all()]
