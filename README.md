# Suave Deletes 

**Suave Deletes** is a Python library that provides a soft delete functionality for SQLAlchemy models.  

Soft deletes allow you to mark records as deleted without actually removing them from the database, making it easy to recover or audit data as needed.  

## Features

- Soft delete: Mark records as deleted without permanently removing them from the database.
- Automatic Query Filtering: Automatically filter out soft-deleted records from your queries.
- Customizable: Configure which models and fields use soft delete functionality.
- Simple Integration: Easily integrate with your existing SQLAlchemy models.

## Installation
You can install Suave Deletes using pip:  
``
pip install suave-deletes
``

## Usage
To use Suave Deletes, simply import and apply it to your SQLAlchemy models.  
Here is a basic example:

#### Configuration

```angular2html
from sqlalchemy import create_engine
from suave_deletes.session import create_suave_delete_session

def create_session():
    engine = create_engine(
        "Your database URI"
    )

    current_session = create_suave_delete_session(engine)

    with current_session() as session:
        yield session

```
#### Implementation
```angular2html
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from suave_deletes.mixins import SuaveDeleteMixin
from suave_deletes.sessions import create_suave_delete_session

DeclarativeBase = declarative_base()
session = create_suave_delete_session()

class Base(DeclarativeBase, SuaveDeleteMixin):
    deleted_at = mapped_column(DateTime, default=None)


class MyModel(Base):
    __tablename__ = 'my_model'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Creates instance 
obj = MyModel(name="example")
session.add(obj)
session.commit()

# Soft delete the instance
session.delete(obj)
session.commit()

# Query only non-deleted records
non_deleted_records = session.query(MyModel).all()

# Query all records, including soft deleted ones 
all_records = session.query(MyModel).with_deleted_at().all()
```

## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue on [GitHub](https://github.com/stefanFramework/suave_deletes). If you would like to contribute code, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Acknowledgments
Thanks to the SQLAlchemy community for their excellent library and documentation.


