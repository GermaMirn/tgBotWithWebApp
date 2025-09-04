from sqlalchemy import Column, Integer, String, BigInteger, Text, ForeignKey, JSON, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

# Таблица связи многие-ко-многим
group_students = Table(
  "group_students",
  Base.metadata,
  Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
  Column("student_id", UUID(as_uuid=True), ForeignKey("students.id"), primary_key=True),
)

class Student(Base):
  __tablename__ = "students"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
  telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
  level = Column(String(20), default="beginner")
  preferred_languages = Column(JSON, default=list)
  study_goals = Column(Text, nullable=True)

  languages = relationship("StudentLanguage", back_populates="student")
  groups = relationship("Group", secondary=group_students, back_populates="students")

class StudentLanguage(Base):
  __tablename__ = "student_languages"
  id = Column(Integer, primary_key=True, index=True)
  student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
  language = Column(String(50), nullable=False)
  current_level = Column(String(20), nullable=False)
  target_level = Column(String(20), nullable=True)

  student = relationship("Student", back_populates="languages")

class Group(Base):
  __tablename__ = "groups"
  id = Column(Integer, primary_key=True, index=True)
  students = relationship("Student", secondary=group_students, back_populates="groups")
