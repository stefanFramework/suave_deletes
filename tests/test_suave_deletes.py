import pytest

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import ForeignKey

from suave_deletes.mixins import SuaveDeleteMixin
from suave_deletes.sessions import create_suave_delete_session

Base = declarative_base()


class User(SuaveDeleteMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    deleted_at = Column(DateTime)


class Workspace(SuaveDeleteMixin, Base):
    __tablename__ = 'workspaces'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    participants = relationship(
        "Participant",
        back_populates="workspace",
        cascade="all, delete, delete-orphan"
    )
    deleted_at = Column(DateTime)


class Participant(SuaveDeleteMixin, Base):
    __tablename__ = 'participants'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))
    workspace = relationship("Workspace", back_populates="participants")
    deleted_at = Column(DateTime, nullable=True)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))


@pytest.fixture(scope='module')
def engine():
    return create_engine('sqlite:///:memory:')


@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    Session = create_suave_delete_session(engine)
    session = Session()
    yield session
    session.close()

def test_soft_delete(session):
    user = User(name="Test User")
    session.add(user)
    session.commit()

    assert session.query(User).count() == 1

    session.delete(user)
    session.commit()

    assert session.query(User).count() == 0

    assert session.query(User).with_deleted_at().count() == 1


def test_query_with_soft_delete(session):
    user_john = User(name="John")
    user_karen = User(name="Karen")

    session.add(user_john)
    session.add(user_karen)
    session.commit()

    assert session.query(User).count() == 2

    session.delete(user_karen)
    session.commit()

    users = session.query(User).all()

    assert len(users) == 1
    assert users[0].name == "John"


def test_soft_delete_on_participants(session):
    workspace = Workspace(name="Test Workspace")
    participant1 = Participant(name="Participant 1", workspace=workspace)
    participant2 = Participant(name="Participant 2", workspace=workspace)

    workspace.participants.append(participant1)
    workspace.participants.append(participant2)

    session.add(workspace)
    session.commit()

    assert len(workspace.participants) == 2

    session.delete(participant1)
    session.commit()

    assert len(workspace.participants) == 1
    assert workspace.participants[0].name == "Participant 2"

def test_soft_delete_does_not_activate_if_deleted_at_column_does_not_exist(session):
    task = Task(name="Test Task")

    session.add(task)

    task = session.query(Task).first()
    assert task.name == "Test Task"

    session.delete(task)
    none_existing_task = session.query(Task).first()
    assert none_existing_task is None
