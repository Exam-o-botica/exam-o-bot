import asyncio
import uuid

from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from src.examobot.db.tables import Test, Task, User, Classroom, Base, UserClassroomParticipation, \
    UserTestParticipation, UserTestParticipationStatus, TestStatus

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

    async def get_user_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)  # that's fine
        async with self.session_maker() as session:
            result = await session.execute(query)
            user = result.scalars().first()
        return user

    async def add_user(self, user_id: int, username: str, name: str) -> User:
        new_user = User(id=user_id, username=username, name=name)
        async with self.session_maker() as session:
            session.add(new_user)
            await session.commit()
        return new_user

    async def check_if_user_exists(self, user_id: int) -> bool:
        query = select(User).where(User.id == user_id)  # that's fine
        async with self.session_maker() as session:
            user = await session.execute(query)
            user = user.first()
        return bool(user)

    # CREATED CLASSROOMS AND TESTS

    async def get_test_by_id(self, test_id: int) -> Test:
        query = select(Test).where(Test.id == test_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
            test = result.scalars().first()
        return test

    async def get_classroom_by_id(self, classroom_id: int) -> Classroom:
        query = select(Classroom).where(Classroom.id == classroom_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
            classroom = result.scalars().first()
        return classroom

    async def get_tests_by_author_id(self, author_id: int) -> list[Test]:
        query = select(Test).where(Test.author_id == author_id)
        async with self.session_maker() as session:
            tests = await session.execute(query)

        return tests.scalars().all()

    # async def add_test(self, author_id: int, title: str, time: int, deadline: int, attempts_number: int, link: str, meta_data: str):
    async def add_test(self, **kwargs):
        uuid_ = str(uuid.uuid4())
        kwargs["uuid"] = uuid_
        new_test = Test(**kwargs)
        async with self.session_maker() as session:
            session.add(new_test)
            await session.commit()

        test = await self.get_test_by_uuid(uuid_)
        return test

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

    async def delete_classroom(self, classroom_id: int):
        classroom = await self.get_classroom_by_id(classroom_id)
        query2 = select(UserClassroomParticipation).where(UserClassroomParticipation.classroom_id == classroom_id)
        async with self.session_maker() as session:
            # res1 = await session.execute(query1)
            res2 = await session.execute(query2)
            items = res2.scalars().all()
            for i in items:
                await session.delete(i)
            # classrooms, user_classrooms = res1.scalars().all(), res2.scalars().all()
            # for i in cl
            # map(session.delete, classrooms)
            # map(session.delete, user_classrooms)
            await session.delete(classroom)
            await session.commit()

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
        query = select(UserTestParticipation).where(and_(UserTestParticipation.test_id == test_id,
                                                         UserTestParticipation.user_id == user_id))
        async with self.session_maker() as session:
            result = await session.execute(query)
            test = result.scalars().first()
        return bool(test)

    async def check_if_user_in_classroom(self, classroom_id: int, user_id: int) -> bool:
        query = select(UserClassroomParticipation).where(and_(UserClassroomParticipation.classroom_id == classroom_id,
                                                              UserClassroomParticipation.user_id == user_id))
        async with self.session_maker() as session:
            result = await session.execute(query)
            classroom = result.scalars().first()
        return bool(classroom)

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

    async def get_users_in_classroom(self, classroom_id: int):
        query = select(User).join(UserClassroomParticipation).where(
            UserClassroomParticipation.classroom_id == classroom_id)
        async with self.session_maker() as session:
            users = await session.execute(query)
        return users.scalars().all()

    async def update_test_by_id(self, test_id: int, **kwargs):
        query = update(Test).values(**kwargs).where(Test.id == test_id)
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

    async def update_classroom_by_id(self, classroom_id: int, **kwargs):
        query = update(Classroom).values(**kwargs).where(Classroom.id == classroom_id)
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

    # CURRENT TESTS

    async def get_current_ended_or_with_no_attempts_tests_by_user_id(self, user_id: int):
        query = select(Test).join(UserTestParticipation).where(and_(UserTestParticipation.user_id == user_id,
                                                                    or_(Test.status_set_by_author == TestStatus.UNAVAILABLE,
                                                                        UserTestParticipation.status == UserTestParticipationStatus.PASSED_NO_ATTEMPTS)))
        async with self.session_maker() as session:
            tests = await session.execute(query)
        return tests.scalars().all()

    async def get_current_available_test_with_attempts_by_user_id(self, user_id: int):
        query = select(Test).join(UserTestParticipation).where(and_(UserTestParticipation.user_id == user_id,
                                                                    Test.status_set_by_author == TestStatus.AVAILABLE,
                                                                    UserTestParticipation.status != UserTestParticipationStatus.PASSED_NO_ATTEMPTS))
        async with self.session_maker() as session:
            tests = await session.execute(query)
        return tests.scalars().all()

    async def get_tasks_by_test_id(self, test_id: int):
        query = select(Task).where(Task.test_id == test_id).order_by(Task.order_id)
        async with self.session_maker() as session:
            tasks = await session.execute(query)

        return tasks.scalars().all()

    async def get_current_classrooms_by_user_id(self, user_id: int):
        query = (
            select(Classroom).join(UserClassroomParticipation).where(
                UserClassroomParticipation.user_id == user_id))  # that's fine
        async with self.session_maker() as session:
            classrooms = await session.execute(query)
        return classrooms.scalars().all()

    async def update_test_by_id(self, test_id: int, **kwargs):
        query = update(Test).values(**kwargs).where(Test.id == test_id)
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

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
