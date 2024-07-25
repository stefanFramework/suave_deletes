import pytest

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base

from suave_deletes.mixins import SuaveDeleteMixin
from suave_deletes.sessions import create_suave_delete_session

Base = declarative_base()


class User(SuaveDeleteMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    deleted_at = Column(DateTime)


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
