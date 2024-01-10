from enum import Enum
from typing import List, Optional

from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy_imageattach.entity import Image, image_attachment


# TODO Add classroom to Test

class Base(AsyncAttrs, DeclarativeBase):
    pass


classroom_user_table = Table(
    "classroom_user_table",
    Base.metadata,
    Column("user_tg_id", ForeignKey("users.tg_id"), primary_key=True),
    Column("classroom_id", ForeignKey("classrooms.id"), primary_key=True),
)


# class ClassroomParticipation(Base):
#     __tablename__ = 'class_participations'
#
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), unique=False)
#     classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), unique=False)


class RoleTitles(Enum):
    STUDENT = 0
    AUTHOR = 1


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=False, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    second_name: Mapped[str] = mapped_column(nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(nullable=False)
    grade_first_number: Mapped[int] = mapped_column(nullable=False, default=1)
    grade_second_number: Mapped[int] = mapped_column(nullable=False, default=1)

    roles: Mapped[List["Role"]] = relationship(back_populates="user", cascade="all,delete")  # Parent
    answers: Mapped[List["Answer"]] = relationship(back_populates="user", cascade="all,delete")  # Parent

    participations: Mapped[List["TestParticipation"]] = relationship(
        back_populates="user",
        cascade="all,delete")  # Parent

    classrooms: Mapped[List['Classroom']] = relationship(
        secondary=classroom_user_table, uselist=True, back_populates='participants')

    created_classrooms: Mapped[List["Classroom"]] = relationship(
        back_populates="author",
        cascade="all,delete")  # Parent

    created_tests: Mapped[List["Test"]] = relationship(
        back_populates="author",
        cascade="all,delete")  # Parent


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_title: Mapped[RoleTitles] = mapped_column(nullable=False, default=RoleTitles.STUDENT)

    user: Mapped[User] = relationship(back_populates="roles")  # Child
    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))


class TestParticipation(Base):
    __tablename__ = 'participations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    score: Mapped[int] = mapped_column(nullable=False, default=-1)

    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    user: Mapped[User] = relationship(back_populates="participations")  # Child

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    test: Mapped["Test"] = relationship(back_populates="participants")  # Child


class Classroom(Base):
    __tablename__ = 'classrooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    password: Mapped[str] = mapped_column(nullable=True, default=None)

    tests: Mapped[List["Test"]] = relationship(back_populates="classroom", cascade="all,delete")  # Parent

    author_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    author: Mapped[User] = relationship(back_populates="created_classrooms")  # Child

    participants: Mapped[List[User]] = relationship(
        secondary=classroom_user_table, uselist=True, back_populates='classrooms')


class Test(Base):
    __tablename__ = 'tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    time: Mapped[int] = mapped_column(nullable=False, default=-1)
    password: Mapped[str] = mapped_column(nullable=True, default=None)
    attempts_number: Mapped[int] = mapped_column(nullable=False, default=1)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    author: Mapped[User] = relationship(back_populates="created_tests")  # Child

    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), nullable=False)
    classroom: Mapped[Classroom] = relationship(back_populates="tests")  # Child

    participants: Mapped[List[TestParticipation]] = relationship(back_populates="test", cascade="all,delete")  # Parent
    tasks: Mapped[List["Task"]] = relationship(back_populates="test", cascade="all,delete")  # Parent


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(nullable=False, default=1)
    title: Mapped[str] = mapped_column(nullable=True, default=None)
    text: Mapped[str] = mapped_column(nullable=False)
    right_answer: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)

    images: Mapped[List["TaskImage"]] = image_attachment("TaskImage", cascade="all,delete")  # Parent
    answers: Mapped[List["Answer"]] = relationship(back_populates="task", cascade="all,delete")  # Parent

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    test: Mapped[Test] = relationship(back_populates="tasks")  # Child


class TaskImage(Base, Image):
    __tablename__ = 'task_images'

    task_id: Mapped[int] = mapped_column(ForeignKey(Task.id), primary_key=True, nullable=False)
    task: Mapped[Task] = relationship(Task, back_populates="images")  # Child
    order_index: Mapped[int] = mapped_column(primary_key=True)


class Answer(Base):
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(nullable=True, default=None)
    is_right: Mapped[bool] = mapped_column(nullable=False, default=False)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))  # Child
    task: Mapped[Task] = relationship(back_populates="answers")

    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))  # Child
    user: Mapped[User] = relationship(back_populates="answers")
