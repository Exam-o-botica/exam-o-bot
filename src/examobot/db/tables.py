from enum import Enum
from typing import List, Optional

from sqlalchemy import ForeignKey, Column, LargeBinary, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Role(Enum):
    STUDENT = 0
    AUTHOR = 1


class TestStatus(Enum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class AnswerStatus(Enum):
    UNCHECKED = 0
    CORRECT = 1
    INCORRECT = 2


class UserTestParticipationStatus(Enum):
    PASSED_HAS_ATTEMPTS = 0
    PASSED_NO_ATTEMPTS = 1
    NOT_PASSED = 2


class AwaitStatusPrefix(Enum):
    CLASSROOM_NAME = "CMN:"
    TEST_NAME = "TTN:"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Column = Column(BigInteger,
                        primary_key=True, autoincrement=False, nullable=False, index=True)

    username: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(nullable=False, default=Role.AUTHOR)
    await_status: Mapped[str] = mapped_column(nullable=True, default=None)

    answers: Mapped[List["Answer"]] = relationship(back_populates="user", cascade="all,delete")  # Parent

    created_classrooms: Mapped[List["Classroom"]] = relationship(
        back_populates="author",  # todo maybe we need uselist=True here, maybe not, who knows
        cascade="all,delete")  # Parent

    created_tests: Mapped[List["Test"]] = relationship(
        back_populates="author",
        cascade="all,delete")  # Parent


class Classroom(Base):
    __tablename__ = 'classrooms'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(index=True, autoincrement=False)

    title: Mapped[str] = mapped_column(primary_key=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped[User] = relationship(back_populates="created_classrooms")  # Child

    classroom_test_connections: Mapped[List["ClassroomTestConnection"]] = (
        relationship(back_populates="classroom", cascade="all,delete", uselist=True))  # Parent


class Test(Base):
    __tablename__ = 'tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(index=True, autoincrement=False)

    title: Mapped[str] = mapped_column(nullable=False, unique=False, index=True)
    time: Mapped[int] = mapped_column(nullable=False, default=-1)
    deadline: Mapped[int] = mapped_column(nullable=False, default=-1)
    attempts_number: Mapped[int] = mapped_column(nullable=False, default=1)
    status_set_by_author: Mapped[TestStatus] = mapped_column(nullable=False, default=TestStatus.AVAILABLE)
    link: Mapped[str] = mapped_column(nullable=False)
    meta_data: Mapped[Optional[str]] = mapped_column(nullable=False, default=None)

    author_id: Mapped[BigInteger] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped[User] = relationship(back_populates="created_tests")  # Child

    tasks: Mapped[List["Task"]] = relationship(back_populates="test", cascade="all,delete")  # Parent
    classroom_test_connections: Mapped[List["ClassroomTestConnection"]] = (
        relationship(back_populates="test", cascade="all,delete", uselist=True))  # Parent


class UserClassroomParticipation(Base):
    __tablename__ = 'user_classroom_participation'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Column = Column(ForeignKey("users.id"), nullable=False)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), nullable=False)


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(index=True, autoincrement=False)

    order_id: Mapped[int] = mapped_column(nullable=False, default=1)
    title: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    text: Mapped[str] = mapped_column(nullable=False)
    correct_answer: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    images = Column(LargeBinary, nullable=True, default=None)
    score: Mapped[int] = mapped_column(nullable=False, default=0)
    task_type: Mapped[str] = mapped_column(nullable=False)
    meta_data: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)

    answers: Mapped[List["Answer"]] = relationship(back_populates="task", cascade="all,delete")  # Parent

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    test: Mapped[Test] = relationship(back_populates="tasks")  # Child


class Answer(Base):
    __tablename__ = 'answers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(index=True, autoincrement=False)

    text: Mapped[Optional[str]] = mapped_column(nullable=True, default=None)
    status: Mapped[AnswerStatus] = mapped_column(nullable=False, default=AnswerStatus.UNCHECKED)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))  # Child
    task: Mapped[Task] = relationship(back_populates="answers")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # Child
    user: Mapped[User] = relationship(back_populates="answers")


class UserTestParticipation(Base):
    __tablename__ = 'user_test_participation'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Column = Column(ForeignKey("users.id"), nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    status: Mapped[UserTestParticipationStatus] = mapped_column(
        nullable=False, default=UserTestParticipationStatus.NOT_PASSED)


class ClassroomTestConnection(Base):
    __tablename__ = 'classroom_test_connection'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))  # Child
    test: Mapped[Test] = relationship(back_populates="classroom_test_connections", uselist=False)

    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"))  # Child
    classroom: Mapped[Classroom] = relationship(back_populates="classroom_test_connections", uselist=False)
