import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.tables import Student

router = APIRouter()


class StudentCreate(BaseModel):
    display_name: str
    grade_level: int
    school: str | None = None
    roast_preference: float = 0.0


class StudentResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    grade_level: int
    school: str | None
    roast_preference: float

    model_config = {"from_attributes": True}


DB = Annotated[AsyncSession, Depends(get_db)]


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(data: StudentCreate, db: DB):
    student = Student(**data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/", response_model=list[StudentResponse])
async def list_students(db: DB):
    result = await db.execute(select(Student).order_by(Student.display_name))
    return result.scalars().all()


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: uuid.UUID, db: DB):
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student
