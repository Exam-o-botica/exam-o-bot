import asyncio

from sqlalchemy import select, insert, join

import typing as tp
from src.examobot.db.tables import Test, Task, Role, User, Classroom, TestStatus
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
import uuid

from src.examobot.db.tables import Base

DATABASE_URI = 'sqlite+aiosqlite:///mydatabase.db'


class EngineManager:
    def __init__(self, path: str) -> None:
        self.path = path

    async def __aenter__(self) -> AsyncEngine:
        self.engine = create_async_engine(self.path, echo=True)
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.engine.dispose()


class DBManager:
    def __init__(self):
        self.session_maker = None
        asyncio.run(self.init_())

    async def init_(self):
        async with EngineManager(DATABASE_URI) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    # adding user
    async def add_user(self, user_id: int, username: str, name: str, classroom_id: tp.Optional[str] = None,
                       test_id: tp.Optional[str] = None):

        if classroom_id and test_id:
            raise AssertionError("EXPECTED EITHER CLASSROOM_ID OR TEST_ID, NOT BOTH")

        if classroom_id:
            role = Role.STUDENT
            classroom = self.get_classroom_by_id(classroom_id)
            if classroom:  # correctly found classroom
                tests = self.get_available_tests_for_specific_classroom(classroom_id)
                classrooms = [classroom]
            else:
                classrooms = []
                tests = []

        elif test_id:
            role = Role.STUDENT
            test = self.get_test_by_id(test_id)
            tests = [test] if test else []
            classrooms = []

        else:
            role = Role.AUTHOR
            tests = []
            classrooms = []

        new_user = User(id=user_id, username=username, name=name, role=role, answers=[], tests=tests,
                        classrooms=classrooms, created_classrooms=[], created_tests=[])

        async with self.session_maker() as session:
            session.add(new_user)
            await session.commit()

    async def check_if_user_exists(self, user_id: int) -> bool:
        print('here1')
        query = select(User).where(User.id == user_id)
        print('here2')
        async with self.session_maker() as session:
            user = await session.execute(query)
            user = user.first()
            print("user", user)
        return bool(user)

    async def get_user_by_id(self, user_id: int) -> User:
        async with self.session_maker() as session:
            user = session.query(User).filter(User.id == user_id).first()
        return user

    async def get_classroom_by_id(self, classroom_id: str) -> Classroom:
        async with self.session_maker() as session:
            classroom = session.query(Classroom).filter(Classroom.id == classroom_id).first()
        return classroom

    async def get_test_by_id(self, test_id: str) -> Test:
        async with self.session_maker() as session:
            test = session.query(Test).filter(Test.id == test_id).first()
        return test

    async def add_user_to_classroom(self, classroom_id: str, user_id: int) -> None:
        async with self.session_maker() as session:
            classroom = session.query(Classroom).filter(Classroom.id == classroom_id).first()
            classroom.participants.append(user_id)
            await session.commit()

    async def get_available_tests_for_specific_classroom(self, classroom_id: str) -> list[Test]:
        query = select(Test).where(Test.classroom_id == classroom_id,
                                   Test.status_set_by_author == TestStatus.AVAILABLE)
        async with self.session_maker() as session:
            tests = await session.execute(query)

        return tests.scalars().all()

    # main menu authors queries

    async def get_classrooms_by_author_id(self, author_id: int) -> list[Classroom]:
        query = select(Classroom).where(Classroom.author_id == author_id)
        async with self.session_maker() as session:
            classrooms = await session.execute(query)

        return classrooms.scalars().all()

    async def get_tests_by_author_id(self, author_id: int) -> list[Test]:
        query = select(Test).where(Test.author_id == author_id)
        async with self.session_maker() as session:
            tests = await session.execute(query)

        return tests.scalars().all()

    async def add_classroom(self, author_id: int, title: str):
        new_classroom = Classroom(id=str(uuid.uuid4()),
                                  title=title,
                                  tests=[],
                                  author_id=author_id,
                                  participants=[])

        async with self.session_maker() as session:
            session.add(new_classroom)
            await session.commit()

    # -------------------------

    async def get_test_and_author_by_test_title(self, title: str):
        query = select(Test, User).join(User).where(Test.title == title)
        async with self.session_maker() as session:
            test = await session.execute(query)

        result = test.first()
        return result[0], result[1]

    async def get_tasks_by_test_id(self, test_id: int):
        query = select(Task).where(Task.test_id == test_id).order_by(Task.order_id)
        async with self.session_maker() as session:
            tasks = await session.execute(query)

        return tasks.scalars().all()

    #
    # async def get_test_titles(self):
    #     query = select(Test.title)
    #     async with self.session_maker() as session:
    #         tests = await session.execute(query)
    #
    #     return tests.all()
    #
    # async def get_test_and_author_by_test_title(self, title: str):
    #     query = select(Test, User).join(User).where(Test.title == title)
    #     async with self.session_maker() as session:
    #         test = await session.execute(query)
    #
    #     result = test.first()
    #     return result[0], result[1]
    #
    # async def get_tasks_by_test_id(self, test_id: int):
    #     query = select(Task).where(Task.test_id == test_id).order_by(Task.order_id)
    #     async with self.session_maker() as session:
    #         tasks = await session.execute(query)
    #
    #     return tasks.scalars().all()
    #
    # return tests.all()

# async def get_participations_by_test_id_and_tg_id(self, test_id, tg_id):
#     query = select(TestParticipation).where(TestParticipation.test_id == test_id,
#                                             TestParticipation.user_tg_id == tg_id)
#     async with self.session_maker() as session:
#         participations = await session.execute(query)
#
#     return participations.scalars().all()
#

# async def add_participation(self, test_id, tg_id, score=-1):
#     stmt = insert(TestParticipation).values(user_tg_id=tg_id, test_id=test_id, score=score)
#     async with self.session_maker() as session:
#         await session.execute(stmt)
#         await session.commit()
#
# async def initial_add(self):
#     async with self.session_maker() as session:
#         student_role = Role(
#             id=1,
#             role_title=RoleTitles.STUDENT
#         )
#         user1 = User(
#             tg_id=1,
#             first_name="F",
#             second_name="A",
#             last_name="V",
#             grade_first_number=1,
#             grade_second_number=2,
#         )
#         user1.roles.append(student_role)
#         student_role.user = user1
#
#         author_role = Role(
#             id=2,
#             role_title=RoleTitles.STUDENT
#         )
#         user2 = User(
#             tg_id=2,
#             first_name="A",
#             second_name="K",
#             last_name="P",
#             grade_first_number=1,
#             grade_second_number=3,
#         )
#         user2.roles.append(author_role)
#         author_role.user = user2
#
#         classroom = Classroom(
#             id=1,
#             password="1234",
#             author_id=2
#         )
#         classroom.participants.append(user1)
#         classroom.participants.append(user2)
#
#         test1 = Test(
#             id=1,
#             title="A test",
#             time=120,
#             attempts_number=3,
#             author=user2,
#             classroom=classroom
#         )
#         task1 = Task(
#             id=1,
#             order_id=1,
#             title="a",
#             text="Do it!",
#             right_answer="Done",
#             test=test1
#         )
#         task2 = Task(
#             id=2,
#             order_id=2,
#             title="b",
#             text="Do it!",
#             right_answer="Done!",
#             test=test1
#         )
#         test1.tasks.append(task1)
#         test1.tasks.append(task2)
#
#         test2 = Test(
#             id=2,
#             title="B test",
#             time=60,
#             attempts_number=1,
#             author=user2,
#             classroom=classroom
#         )
#         task3 = Task(
#             id=3,
#             order_id=1,
#             title="c",
#             text="Do it!",
#             right_answer="Done!",
#             test=test2
#         )
#         test2.tasks.append(task3)
#
#         session.add(student_role)
#         session.add(author_role)
#         session.add(user1)
#         session.add(user2)
#
#         session.add(classroom)
#
#         session.add(test1)
#         session.add(test2)
#         session.add(task1)
#         session.add(task2)
#         session.add(task3)
#
#         await session.flush()
#         await session.commit()
#
#         # stmt = insert(TestParticipation).values(user_tg_id=tg_id, test_id=test_id, score=score)
#         # await session.execute(stmt)

# async def initial_add(self):
#     async with self.session_maker() as session:
#         user1 = User(
#             role=Role.STUDENT,
#             tg_id=1,
#             first_name="F",
#             second_name="A",
#             last_name="V",
#             grade_first_number=1,
#             grade_second_number=2,
#         )
#
#         user2 = User(
#             role=Role.STUDENT,
#             tg_id=2,
#             first_name="A",
#             second_name="K",
#             last_name="P",
#             grade_first_number=1,
#             grade_second_number=3,
#         )
#
#         classroom = Classroom(
#             id=1,
#             password="1234",
#             author_id=2
#         )
#         classroom.participants.append(user1)
#         classroom.participants.append(user2)
#
#         test1 = Test(
#             id=1,
#             title="A test",
#             time=120,
#             attempts_number=3,
#             author=user2,
#             classroom=classroom
#         )
#         task1 = Task(
#             id=1,
#             order_id=1,
#             title="a",
#             text="Do it!",
#             right_answer="Done",
#             test=test1
#         )
#         task2 = Task(
#             id=2,
#             order_id=2,
#             title="b",
#             text="Do it!",
#             right_answer="Done!",
#             test=test1
#         )
#         test1.tasks.append(task1)
#         test1.tasks.append(task2)
#
#         test2 = Test(
#             id=2,
#             title="B test",
#             time=60,
#             attempts_number=1,
#             author=user2,
#             classroom=classroom
#         )
#         task3 = Task(
#             id=3,
#             order_id=1,
#             title="c",
#             text="Do it!",
#             right_answer="Done!",
#             test=test2
#         )
#         test2.tasks.append(task3)
#
#         session.add(user1)
#         session.add(user2)
#
#         session.add(classroom)
#
#         session.add(test1)
#         session.add(test2)
#         session.add(task1)
#         session.add(task2)
#         session.add(task3)
#
#         await session.flush()
#         await session.commit()

# stmt = insert(TestParticipation).values(user_tg_id=tg_id, test_id=test_id, score=score)
# await session.execute(stmt)
