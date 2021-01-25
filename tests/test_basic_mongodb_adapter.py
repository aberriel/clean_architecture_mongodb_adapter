from clean_architecture_mongodb_adapter.basic_mongodb_adapter import (
    BasicMongodbAdapter,
    NotExistsException)
from collections import namedtuple
from pytest import fixture
from unittest import TestCase
from unittest.mock import MagicMock, patch

import ssl


prefix = 'clean_architecture_mongodb_adapter.basic_mongodb_adapter'


@patch.object(BasicMongodbAdapter, '_get_db')
@patch.object(BasicMongodbAdapter, '_get_table')
@patch(f'{prefix}.logging')
def test_mongodb_adapter(mock_logging, mock_get_table, mock_get_db):
    mock_table_name = MagicMock()
    mock_db_name = MagicMock()
    mock_db_url = MagicMock()
    mock_db_username = MagicMock()
    mock_db_password = MagicMock()
    mock_adapted_class = MagicMock()
    mock_logger = MagicMock()
    basic_adapter = BasicMongodbAdapter(
        table_name=mock_table_name,
        db_name=mock_db_name,
        db_url=mock_db_url,
        db_username=mock_db_username,
        db_password=mock_db_password,
        adapted_class=mock_adapted_class,
        logger=mock_logger)

    assert basic_adapter.table_name == mock_table_name
    assert basic_adapter.db_name == mock_db_name
    assert basic_adapter.db_url == mock_db_url
    assert basic_adapter.db_username == mock_db_username
    assert basic_adapter.db_password == mock_db_password
    assert basic_adapter._class == mock_adapted_class
    mock_get_db.assert_called()
    assert basic_adapter._db == mock_get_db()
    mock_get_table.assert_called()
    assert basic_adapter._table == mock_get_table()
    assert basic_adapter._logger == mock_logger
    mock_logging.getLogger.assert_not_called()


@patch.object(BasicMongodbAdapter, '_get_db')
@patch.object(BasicMongodbAdapter, '_get_table')
@patch(f'{prefix}.logging')
def test_mogodb_adapter__logger_none(mock_logging, mock_get_table, mock_get_db):
    mock_table_name = MagicMock()
    mock_db_name = MagicMock()
    mock_db_url = MagicMock()
    mock_db_username = MagicMock()
    mock_db_password = MagicMock()
    mock_adapted_class = MagicMock()
    basic_adapter = BasicMongodbAdapter(
        table_name=mock_table_name,
        db_name=mock_db_name,
        db_url=mock_db_url,
        db_username=mock_db_username,
        db_password=mock_db_password,
        adapted_class=mock_adapted_class)


Factory = namedtuple('Factory', 'adapter, mock_table_name, mock_db_name,'
                                'mock_db_url, mock_db_username,'
                                'mock_db_password, mock_adapted_class,'
                                'mock_logger')


@fixture(scope='class')
def adapter_fixture(request):
    def factory(table_name: str = MagicMock(),
                db_name: str = MagicMock(),
                db_url: str = MagicMock(),
                db_username: str = MagicMock(),
                db_password: str = MagicMock(),
                adapted_class=MagicMock(),
                logger=MagicMock()):
        adapter = BasicMongodbAdapter(
            table_name=table_name,
            db_name=db_name,
            db_url=db_url,
            db_username=db_username,
            db_password=db_password,
            adapted_class=adapted_class,
            logger=logger)
        return Factory(adapter, table_name, db_name, db_url,
                       db_username, db_password, adapted_class, logger)
    request.cls.factory = factory


    @pytest.mark.usefixtures('adapter_fixture')
    class TestBasicMongodbAdapter(TestCase):
        def setUp(self):
            fac = TestBasicMongodbAdapter.factory()
            self.adapter: BasicMongodbAdapter = fac.adapter
            self.mock_table_name = fac.mock_table_name
            self.mock_db_name = fac.mock_db_name
            self.mock_db_url = fac.mock_db_url
            self.mock_db_username = fac.mock_db_username
            self.mock_db_password = fac.mock_db_password
            self.mock_adapted_class = fac.mock_adapted_class
            self.mock_logger = fac.mock_logger

        def tearDown(self):
            pass

        def test_init(self):
            assert self.adapter.table_name == self.mock_table_name
            assert self.adapter.db_name == self.mock_db_name
            assert self.adapter.db_url == self.mock_db_url
            assert self.adapter.db_username == self.mock_db_username
            assert self.adapter.db_password == self.mock_db_password
            assert self.adapter._class == self.mock_adapted_class
            assert self.adapter._logger == self.mock_logger

        def test_logger(self):
            logger_data = self.adapter.logger
            assert logger_data == self.mock_logger

        def test_adapted_class(self):
            adapted_class_data = self.adapter.adapted_class
            assert adapted_class_data == self.mock_adapted_class

        def test_adapted_class_name(self):
            adapted_class_name = self.adapter.adapted_class_name
            assert adapted_class_name == self.mock_adapted_class.__name__

        @patch(f'{prefix}.MongoClient')
        def test__get_client(self, mock_mongo_client):
            client = self.adapter._get_client()
            self.mock_db_url.format.assert_called_with(
                username=self.mock_db_username,
                password=self.mock_db_password)
            mock_mongo_client.assert_called_with(
                self.mock_db_url.format(), ssl_cert_reqs=ssl.CERT_NONE)
            assert client == mock_mongo_client()

        @patch.object(BasicMongodbAdapter, '_get_client')
        def test__get_db(self, mock_get_client):
            db = self.adapter._get_db()
            mock_get_client.assert_called()
            assert db == getattr(mock_get_client(), self.mock_db_name)

        def test__get_table(self):
            table = self.adapter._get_table()
