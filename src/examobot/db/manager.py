from typing import Any

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from examobot.db.tables import Test, Task, Role, User, Classroom


class DBManager:
    def __init__(self, session_maker: async_sessionmaker[Any]):
        self.session_maker = session_maker

    async def get_test_titles(self):
        query = select(Test.title)
        async with self.session_maker() as session:
            tests = await session.execute(query)

        return tests.all()

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

    # async def get_participations_by_test_id_and_tg_id(self, test_id, tg_id):
    #     query = select(TestParticipation).where(TestParticipation.test_id == test_id,
    #                                             TestParticipation.user_tg_id == tg_id)
    #     async with self.session_maker() as session:
    #         participations = await session.execute(query)
    #
    #     return participations.scalars().all()

    # async def add_participation(self, test_id, tg_id, score=-1):
    #     stmt = insert(TestParticipation).values(user_tg_id=tg_id, test_id=test_id, score=score)
    #     async with self.session_maker() as session:
    #         await session.execute(stmt)
    #         await session.commit()

    async def initial_add(self):
        async with self.session_maker() as session:
            user1 = User(
                role=Role.STUDENT,
                tg_id=1,
                first_name="F",
                second_name="A",
                last_name="V",
                grade_first_number=1,
                grade_second_number=2,
            )


            user2 = User(
                role=Role.STUDENT,
                tg_id=2,
                first_name="A",
                second_name="K",
                last_name="P",
                grade_first_number=1,
                grade_second_number=3,
            )

            classroom = Classroom(
                id=1,
                password="1234",
                author_id=2
            )
            classroom.participants.append(user1)
            classroom.participants.append(user2)

            test1 = Test(
                id=1,
                title="A test",
                time=120,
                attempts_number=3,
                author=user2,
                classroom=classroom
            )
            task1 = Task(
                id=1,
                order_id=1,
                title="a",
                text="Do it!",
                right_answer="Done",
                test=test1
            )
            task2 = Task(
                id=2,
                order_id=2,
                title="b",
                text="Do it!",
                right_answer="Done!",
                test=test1
            )
            test1.tasks.append(task1)
            test1.tasks.append(task2)

            test2 = Test(
                id=2,
                title="B test",
                time=60,
                attempts_number=1,
                author=user2,
                classroom=classroom
            )
            task3 = Task(
                id=3,
                order_id=1,
                title="c",
                text="Do it!",
                right_answer="Done!",
                test=test2
            )
            test2.tasks.append(task3)

            session.add(user1)
            session.add(user2)

            session.add(classroom)

            session.add(test1)
            session.add(test2)
            session.add(task1)
            session.add(task2)
            session.add(task3)

            await session.flush()
            await session.commit()

            # stmt = insert(TestParticipation).values(user_tg_id=tg_id, test_id=test_id, score=score)
            # await session.execute(stmt)
