import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from src.examobot.db.tables import Test, Task, User, Classroom, Base, UserClassroomParticipation, \
    UserTestParticipation

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

    # USERS

    async def add_user(self, user_id: int, username: str, name: str) -> User:
        new_user = User(id=user_id, username=username, name=name)
        async with self.session_maker() as session:
            session.add(new_user)
            await session.commit()
        return new_user

    async def check_if_user_exists(self, user_id: int) -> bool:
        query = select(User).where(User.id == user_id)  # that's correct
        async with self.session_maker() as session:
            user = await session.execute(query)
            user = user.first()
        return bool(user)

    async def get_user_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)
        async with self.session_maker() as session:
            user = await session.execute(query)
        return user.first()

    # CLASSROOMS AND TESTS

    async def get_tests_by_author_id(self, author_id: int) -> list[Test]:
        query = select(Test).where(Test.author_id == author_id)
        async with self.session_maker() as session:
            tests = await session.execute(query)

        return tests.scalars().all()

    async def add_test(self, author_id: int, title: str, time: int, deadline: int, attempts_number: int, link: str,
                       meta_data: str):
        new_test = Test(
            uuid=str(uuid.uuid4()),
            title=title,
            time=time,
            deadline=deadline,
            attempts_number=attempts_number,
            author_id=author_id,
            link=link,
            meta_data=meta_data
        )
        async with self.session_maker() as session:
            session.add(new_test)
            await session.commit()

        return new_test

    async def get_classroom_by_uuid(self, classroom_uuid: str) -> Classroom:
        query = select(Classroom).where(Classroom.uuid == classroom_uuid)
        async with self.session_maker() as session:
            result = await session.execute(query)
            classroom = result.scalars().first()
        return classroom

    async def get_test_by_uuid(self, test_uuid: str) -> Test:
        query = select(Test).where(Test.uuid == test_uuid)
        async with self.session_maker() as session:
            result = await session.execute(query)
            test = result.scalars().first()
        return test

    async def get_classrooms_by_author_id(self, author_id: int) -> list[Classroom]:
        query = select(Classroom).where(Classroom.author_id == author_id)
        async with self.session_maker() as session:
            classrooms = await session.execute(query)

        return classrooms.scalars().all()

    async def check_if_user_in_test(self, test_id: int, user_id: int) -> bool:
        query = select(UserTestParticipation).where(UserTestParticipation.test_id == test_id and
                                                    UserTestParticipation.user_id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
        return bool(result.first())

    async def check_if_user_in_classroom(self, classroom_id: int, user_id: int) -> bool:
        query = select(UserClassroomParticipation).where(UserClassroomParticipation.classroom_id == classroom_id and
                                                         UserClassroomParticipation.user_id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
        return bool(result.first())

    async def add_user_to_test_participants(self, test_id: int, user_id: int):
        async with self.session_maker() as session:
            new_user_test = UserTestParticipation(user_id=user_id, test_id=test_id)
            session.add(new_user_test)
            await session.commit()

    async def add_user_to_classroom(self, classroom_id: int, user_id: int):
        async with self.session_maker() as session:
            new_user_classroom = UserClassroomParticipation(user_id=user_id, classroom_id=classroom_id)
            session.add(new_user_classroom)
            await session.commit()

    async def add_classroom(self, author_id: int, title: str):
        new_classroom = Classroom(
            uuid=str(uuid.uuid4()),
            title=title,
            author_id=author_id,
        )

        async with self.session_maker() as session:
            session.add(new_classroom)
            await session.commit()

        return new_classroom

    async def get_tasks_by_test_id(self, test_id: int):
        query = select(Task).where(Task.test_id == test_id).order_by(Task.order_id)
        async with self.session_maker() as session:
            tasks = await session.execute(query)

        return tasks.scalars().all()

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
