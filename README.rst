=================================================
       Clean Architecture MongoDB Adapter
=================================================


Concrete implementation of adapter to MongoDB, using clean architecture adapter layer.


Introduction
------------

If you don't know the clean architecture pattern, you can learn about on this `book
<https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164/ref=sr_1_1?dchild=1&keywords=clean+architecture&qid=1612138443&sr=8-1>`_.

Clean architecture pattern, in resume, can develop complex systems with a hight flexible architecture that can maintain easily.
This model provides a set of layers can be isolates all logic levels. Simply, it has these layers:

- Domain-entity layer: all entity classes that provide system objects or "actors". In a common "entity layer", we can instantialize business elements as objects.
- Data-access layer (adapters): all data access classes.
- Interactors: where exists all business logic. Here, we implement business use-cases as a flow peocess.
- API and other edge interfaces: all edge interfaces, as APIs, events (to a desktop app), and others.


How to Use
----------

In an example, I have a User model with some common user fields (username, name, password). This model needs to import marshmallow tom implement a model check.
First, I present the basic entity structure:

.. code-block:: python

    from marshmallow import Schema, fields
    from uuid import uuid4

    class BasicEntity(BasicValue):
        def __init__(self, _id=None):
            self._id = _id or str(uuid4())
            self.adapter = None

        def set_adapter(self, adapter):
            self.adapter = adapter

        def save(self):
            my_id = self.adapter.save(self.to_json())
            return my_id

        def update(self):
            my_id = self.adapter.save(self.to_json())
            return my_id

        def delete(self):
            self.adapter.delete(self._id)

        @classmethod
        def from_json(cls, dict_data):
            return cls.Schema().load(dict_data)

        def to_json(self):
            return self.Schema().dump(self)

        def __eq__(self, other):
            return all([getattr(self, attr) == getattr(other, attr)
                        for attr in self.Schema().fields.keys()])

        class Schema(Schema):
            _id = fields.String(required=True, allow_none=True)


Second, you can see the User model:

.. code-block:: python

    from .basic_entity import BasicEntity

    class User(BasicEntity):
        def __init__(self,
                     username: str,
                     password: str = None,
                     name: str = None,
                     _id: str = None):
            super(User, self).__init__(_id=_id)
            self.name = name
            self.username = username
            self.password = password

        class Schema(BasicEntity.Schema):
            name = fields.Str(required=False, allow_none=True)
            username = fields.String(required=True, allow_none=False)
            password = fields.String(required=True, allow_none=False)

            @post_load
            def post_load(self, data, many, partial):
                return User(**data)


On a example, if you want to create a new user (on a interactor, for example), first you need to define a User adapter.
Because all persist logic exists on basic adapter, you only need to inherit from basic adapter.
For example:

.. code-block:: python

    from .basic_mongodb_adapter import BasicMongodbAdapter
    from app_example.app_domain import User


    class UserAdapter(BasicMongodbAdapter):
        def __init__(self, table_name: str,
                     db_name: str,
                     db_url: str,
                     db_username: str,
                     db_password: str):
            super(UserAdapter, self).__init__(
                  table_name=table_name,
                  db_name=db_name,
                  db_url=db_url,
                  db_username=db_username,
                  db_password=db_password,
                  adapted_class=User)

With it, you can create your interactor or other code layer to create users.
In this case, I assume that you use a config.py file with this format:

.. code-block:: python

    from decouple import config

    class Config:
	    MONGODB_URL = config('MONGODB_URL', 'mongo_url')
	    MONGODB_DATABASE = config('MONGODB_DATABASE', 'database_name')
	    MONGODB_USERNAME = config('MONGODB_USERNAME', 'username')
	    MONGODB_PASSWORD = config('MONGODB_PASSWORD', 'password')
	    USER_TABLE_NAME = config('USER_TABLE_NAME', 'user')

With it, I instantiate an user adapter and can create easily the user:

.. code-block:: python

    from app_example.app_adapters import UserAdapter
    from app_examploe.app_domain import User

    def get_user_adapter(self):
        config_obj = Config()
        adapter = UserAdapter(
            table_name=config_obj.USER_TABLE_NAME,
            db_name=config_obj.MONGODB_DATABASE,
            db_url=config_obj.MONGODB_URL,
            db_username=config_obj.MONGODB_USERNAME,
            db_password=config_obj.MONGODB_PASSWORD)
        return adapter

    def create_user(username: str,
                    password: str,
                    name: str):
        user_adapter = get_user_adapter()
        user_obj = User(username=username,
                        password=password,
                        name=name)
        user.set_adapter(user_adapter)
        user.save()

Installation
------------

Install via `pip:
<https://github.com/pypa/pip>`_

::

    $ pip install clean-architecture-mongodb-adapter

Install from source:

::

    $ git clone https://github.com/aberriel/clean_architecture_mongodb_adapter.git
    $ cd boto
    $ python setup.py install

