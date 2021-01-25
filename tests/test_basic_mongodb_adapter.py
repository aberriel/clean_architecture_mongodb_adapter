from clean_architecture_mongodb_adapter.basic_mongodb_adapter import (
    BasicMongodbAdapter,
    NotExistsException)
from collections import namedtuple
from pytest import fixture, raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
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
def test_mogodb_adapter__logger_none(mock_logging,
                                     mock_get_table,
                                     mock_get_db):
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

    assert basic_adapter.table_name == mock_table_name
    assert basic_adapter.db_name == mock_db_name
    assert basic_adapter.db_url == mock_db_url
    assert basic_adapter.db_username == mock_db_username
    assert basic_adapter.db_password == mock_db_password
    assert basic_adapter._class == mock_adapted_class
    assert basic_adapter._db == mock_get_db()
    assert basic_adapter._table == mock_get_table()
    assert basic_adapter.logger == mock_logging.getLogger()


Factory = namedtuple('Factory', 'adapter, mock_table_name, mock_db_name,'
                                'mock_db_url, mock_db_username,'
                                'mock_db_password, mock_adapted_class,'
                                'mock_logger')


@fixture(scope='class')
def adapter_fixture(request):
    @patch(f'{prefix}.MongoClient')
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


def make_dict_key_item():
    return 'name'


def make_dict_value_item():
    return 'Anselmo'


def make_function_return_set():
    return (make_dict_key_item(), make_dict_value_item())


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
        self.adapter._class = str
        adapted_class_name = self.adapter.adapted_class_name
        assert adapted_class_name == 'str'

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
        mock_get_client().__getitem__.assert_called_with(self.mock_db_name)
        assert db == mock_get_client().__getitem__()

    def test__get_table(self):
        mock_db: dict = MagicMock()
        self.adapter._db = mock_db
        table = self.adapter._get_table()
        assert table == mock_db.__getitem__(self.mock_table_name)

    def test__instantiate_object(self):
        mock_class = MagicMock()
        self.adapter._class = mock_class
        mock_x = MagicMock()
        result = self.adapter._instantiate_object(mock_x)

        mock_class.from_json.assert_called_with(mock_x)
        mock_class.from_json().set_adapter.assert_called()
        assert result == mock_class.from_json()

    @patch.object(BasicMongodbAdapter, '_normalize_nodes')
    def test__clean_list_empty_elements(self, mock_normalize_nodes):
        mock_item_1 = MagicMock()
        mock_args = [mock_item_1]
        result = self.adapter._clean_list_empty_elements(mock_args)

        mock_normalize_nodes.assert_called_with(mock_item_1)
        assert mock_normalize_nodes.call_count == 1
        assert result == [mock_normalize_nodes()]

    @patch.object(BasicMongodbAdapter, '_normalize_nodes')
    def test__clean_dict_empty_elements(self, mock_normalize_nodes):
        mock_args = {'name': 'Anselmo'}
        result = self.adapter._clean_dict_empty_elements(mock_args)
        mock_normalize_nodes.assert_called_with('Anselmo')
        assert result == {'name': mock_normalize_nodes()}

    def test__clean_set_empty_elements(self):
        mock_arg = ['Anselmo', '', 22, 'Marcos']
        result = self.adapter._clean_set_empty_elements(mock_arg)
        assert result == {'Anselmo', 22, 'Marcos'}

    @patch.object(BasicMongodbAdapter, '_clean_set_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_list_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_dict_empty_elements')
    def test__normalize_nodes__set(self, mock_clean_dict,
                                   mock_clean_list,
                                   mock_clean_set):
        mock_arg: set = set()
        result = self.adapter._normalize_nodes(mock_arg)

        mock_clean_dict.assert_not_called()
        mock_clean_list.assert_not_called()
        mock_clean_set.assert_called_with(mock_arg)
        assert result == mock_clean_set()

    @patch.object(BasicMongodbAdapter, '_clean_set_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_list_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_dict_empty_elements')
    def test__normalize_nodes__dict(self, mock_clean_dict,
                                    mock_clean_list,
                                    mock_clean_set):
        mock_arg: dict = dict()
        result = self.adapter._normalize_nodes(mock_arg)

        mock_clean_dict.assert_called_with(mock_arg)
        mock_clean_list.assert_not_called()
        mock_clean_set.assert_not_called()
        assert result == mock_clean_dict()

    @patch.object(BasicMongodbAdapter, '_clean_set_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_list_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_dict_empty_elements')
    def test__normalize_nodes__list(self, mock_clean_dict,
                                    mock_clean_list,
                                    mock_clean_set):
        mock_arg: list = list()
        result = self.adapter._normalize_nodes(mock_arg)

        mock_clean_dict.assert_not_called()
        mock_clean_list.assert_called_with(mock_arg)
        mock_clean_set.assert_not_called()
        assert result == mock_clean_list()

    @patch.object(BasicMongodbAdapter, '_clean_set_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_list_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_dict_empty_elements')
    def test__normalize_nodes__not_on_cleaners(self, mock_clean_dict,
                                               mock_clean_list,
                                               mock_clean_set):
        mock_arg: str = 'Anselmo'
        result = self.adapter._normalize_nodes(mock_arg)

        mock_clean_set.assert_not_called()
        mock_clean_list.assert_not_called()
        mock_clean_dict.assert_not_called()
        assert result == mock_arg

    @patch.object(BasicMongodbAdapter, '_clean_set_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_list_empty_elements')
    @patch.object(BasicMongodbAdapter, '_clean_dict_empty_elements')
    def test__normalize_nodes__not_on_cleaners__none(self,
                                                     mock_clean_dict,
                                                     mock_clean_list,
                                                     mock_clean_set):
        mock_arg = None
        result = self.adapter._normalize_nodes(mock_arg)

        mock_clean_dict.assert_not_called()
        mock_clean_list.assert_not_called()
        mock_clean_set.assert_not_called()
        assert result is None

    def test__get_item_from_table(self):
        mock_item_id = MagicMock()
        mock_table = MagicMock()
        self.adapter._table = mock_table
        result = self.adapter._get_item_from_table(mock_item_id)

        mock_table.find_one.assert_called_with({'_id': mock_item_id})
        assert result == mock_table.find_one()

    @patch.object(BasicMongodbAdapter, '_instantiate_object')
    def test_list_all(self, mock_instantiate_object):
        mock_document = MagicMock()
        mock_table = MagicMock()
        mock_table.find = MagicMock(return_value=[mock_document])
        self.adapter._table = mock_table
        result = self.adapter.list_all()

        mock_table.find.assert_called_with({})
        mock_instantiate_object.assert_called_with(mock_document)
        assert result == [mock_instantiate_object()]

    @patch.object(BasicMongodbAdapter, '_get_item_from_table')
    @patch.object(BasicMongodbAdapter, '_instantiate_object')
    def test_get_by_id(self, mock_instantiate_object,
                       mock_get_item_from_table):
        mock_item_id = MagicMock()
        result = self.adapter.get_by_id(mock_item_id)

        mock_get_item_from_table.assert_called_with(mock_item_id)
        mock_instantiate_object.assert_called_with(mock_get_item_from_table())
        assert result == mock_instantiate_object()

    @patch.object(BasicMongodbAdapter,
                  '_get_item_from_table',
                  return_value=None)
    @patch.object(BasicMongodbAdapter, '_instantiate_object')
    def test_get_by_id__none(self, mock_instantiate_object,
                             mock_get_item_from_table):
        mock_item_id = MagicMock()
        result = self.adapter.get_by_id(mock_item_id)

        mock_get_item_from_table.assert_called_with(mock_item_id)
        mock_instantiate_object.assert_not_called()
        assert result is None

    @patch.object(BasicMongodbAdapter, 'get_by_id')
    def test__check_if_exists(self, mock_get_by_id):
        mock_item_id = MagicMock()
        result = self.adapter._check_if_exists(mock_item_id)

        mock_get_by_id.assert_called_with(mock_item_id)
        assert result is True

    @patch.object(BasicMongodbAdapter, 'get_by_id', return_value=None)
    def test__check_if_exists__not_item(self, mock_get_by_id):
        mock_item_id = '11'
        with raises(NotExistsException) as exc:
            self.adapter._check_if_exists(mock_item_id)

        mock_get_by_id.assert_called_with(mock_item_id)
        assert "Item 11 does not exist." in str(exc.value)

    @patch.object(BasicMongodbAdapter, '_normalize_nodes')
    def test_save(self, mock_normalize_nodes):
        mock_table = MagicMock()
        self.adapter._table = mock_table
        mock_json_data = MagicMock()
        result = self.adapter.save(mock_json_data)

        mock_normalize_nodes.assert_called_with(mock_json_data)
        mock_json_data.get.assert_called_with('_id')
        mock_table.update_one.assert_called_with(
            {'_id': mock_json_data.get()},
            {'$set': mock_normalize_nodes()},
            upsert=True)
        assert result == mock_table.update_one().upserted_id

    def test_delete(self):
        mock_item_id = MagicMock()
        mock_table = MagicMock()
        self.adapter._table = mock_table
        result = self.adapter.delete(mock_item_id)

        mock_table.delete_one.assert_called_with({'_id': mock_item_id})
        assert result == mock_table.delete_one().deleted_count

    @patch.object(BasicMongodbAdapter, '_process_filters')
    @patch.object(BasicMongodbAdapter, '_instantiate_object')
    def test_filter(self, mock_instantiate_object, mock_process_filters):
        mock_args = MagicMock()
        mock_result_item = MagicMock()
        mock_result = [mock_result_item]
        mock_table = MagicMock(find=MagicMock(return_value=mock_result))
        self.adapter._table = mock_table
        result = self.adapter.filter(args=mock_args)

        mock_process_filters.assert_called()
        mock_table.find.assert_called_with(mock_process_filters())
        mock_instantiate_object.assert_called()
        assert result == [mock_instantiate_object()]

    @patch.object(BasicMongodbAdapter, '_process_filter',
                  return_value=make_function_return_set())
    def test__process_filters(self, mock_process_filter):
        mock_args = {'age': 34}
        result = self.adapter._process_filters(mock_args)
        mock_process_filter.assert_called_with('age', 34)
        assert result == {'name': 'Anselmo'}

    @patch.object(BasicMongodbAdapter, '_process_filter_multiple')
    @patch.object(BasicMongodbAdapter, '_process_filter_single')
    def test__process_filter_single(self, mock_process_filter_single,
                                    mock_process_filter_multiple):
        mock_keys = 'anselmo__ana'
        mock_values = MagicMock()
        result_name, result_value = \
            self.adapter._process_filter(mock_keys, mock_values)

        mock_keys.split.assert_called_with('__')
        mock_process_filter_multiple.assert_not_called()
        mock_process_filter_single.assert_called_with(['ana'], mock_values)
        assert result_name == 'anselmo'
        assert result_value == mock_process_filter_single()

    @patch.object(BasicMongodbAdapter, '_process_filter_multiple')
    @patch.object(BasicMongodbAdapter, '_process_filter_single')
    def test__process_filter_multiple(self, mock_process_filter_single,
                                      mock_process_filter_multiple):
        mock_keys = 'anselmo__marcos__jose__maria__ana__camilla'
        mock_values = MagicMock()
        result_name, result_value = \
            self.adapter._process_filter(mock_keys, mock_values)

        mock_keys.split.assert_called_with('__')
        mock_process_filter_multiple.assert_called_with(
            ['marcos', 'jose', 'maria', 'ana', 'camilla'], mock_values)
        mock_process_filter_single.assert_not_called()
        assert result_name == 'anselmo'
        assert result_value == mock_process_filter_multiple()

    def test__process_filter_single(self):
        mock_filter_params = ['Anselmo', 'Marcos']
        mock_values = MagicMock()
        result = self.adapter._process_filter_single(
            mock_filter_params, mock_values)
        assert result == {'$Anselmo': mock_values}

    def test__process_filter_multiple(self):
        mock_filter_params = ['Anselmo', 'Marcos']
        mock_values = [34, 29]
        result = self.adapter._process_filter_multiple(
            mock_filter_params, mock_values)
        assert result == {
            'Anselmo': 34,
            'Marcos': 29}
