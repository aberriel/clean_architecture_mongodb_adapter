from pymongo import MongoClient
import logging
import ssl


class NotExistsException(BaseException):
    pass


class BasicMongodbAdapter:
    def __init__(self, table_name: str,
                 db_name: str,
                 db_url: str,
                 db_username: str,
                 db_password: str,
                 adapted_class,
                 logger=None):
        self.table_name = table_name
        self.db_name = db_name
        self.db_url = db_url
        self.db_username = db_username
        self.db_password = db_password
        self._class = adapted_class

        self._db = self._get_db()
        self._table = self._get_table()
        self._logger = logger if logger else logging.getLogger()

    @property
    def logger(self):
        return self._logger

    @property
    def adapted_class(self):
        return self._class

    @property
    def adapted_class_name(self):
        return self._class.__name__

    def _get_client(self):
        connection_string = self.db_url.format(username=self.db_username, password=self.db_password)
        self.logger.debug(f'connection_string: {connection_string}')
        return MongoClient(connection_string, ssl_cert_reqs=ssl.CERT_NONE)

    def _get_db(self):
        client = self._get_client()
        self.logger.debug(f'db_name: {self.db_name}')
        return client[self.db_name]

    def _get_table(self):
        self.logger.debug(f'table_name: {self.table_name}')
        return self._db[self.table_name]

    def _instantiate_object(self, x):
        self.logger.debug(f'BasicMongodbAdapter._instantiate_object -> x: {str(x)}')
        obj = self._class.from_json(x)
        obj.set_adapter(self)
        return obj

    @staticmethod
    def _clean_list_empty_elements(arg):
        result = []
        for value in arg:
            clean_value = BasicMongodbAdapter._normalize_nodes(value)
            if clean_value:
                result.append(clean_value)
        return result

    @staticmethod
    def _clean_dict_empty_elements(arg):
        result = {}
        for key, value in arg.items():
            clean_value = BasicMongodbAdapter._normalize_nodes(value)
            if clean_value:
                result.update({key: clean_value})
        return result

    @staticmethod
    def _clean_set_empty_elements(arg):
        arg = set(x for x in arg if not hasattr(x, '__len__') or
                  len(x) > 0)
        return arg

    @staticmethod
    def _normalize_nodes(arg):
        cleaners = {set: BasicMongodbAdapter._clean_set_empty_elements,
                    list: BasicMongodbAdapter._clean_list_empty_elements,
                    dict: BasicMongodbAdapter._clean_dict_empty_elements}

        arg_type = type(arg)
        if arg_type in cleaners:
            return cleaners[arg_type](arg)

        if not hasattr(arg, '__len__') or len(arg) != 0:
            return arg
        else:
            return None

    def _get_item_from_table(self, item_id):
        query = {'_id': item_id}
        return self._table.find_one(query)

    def list_all(self):
        documents = self._table.find({})
        objects = [self._instantiate_object(d) for d in documents]
        return objects

    def get_by_id(self, item_id):
        raw_item = self._get_item_from_table(item_id)
        if raw_item:
            return self._instantiate_object(raw_item)
        return None

    def _check_if_exists(self, item_id):
        item = self.get_by_id(item_id)
        if not item:
            raise NotExistsException(f"Item {item_id} does not exist.")

    def save(self, json_data):
        cleaned_data = BasicMongodbAdapter._normalize_nodes(json_data)
        update_filter = {'_id': json_data.get('_id')}
        update_query = {'$set': cleaned_data}
        update_result = self._table.update_one(update_filter, update_query, upsert=True)
        return update_result.upserted_id

    def delete(self, item_id):
        query_delete = {'_id': item_id}
        delete_result = self._table.delete_one(query_delete)
        return delete_result.deleted_count

    def filter(self, **kwargs):
        filters = self._process_filters(kwargs)
        self.logger.debug(f'filters: {filters}')
        query_result = self._table.find(filters)
        self.logger.info(f'query_result: {query_result}')

        #objects = [self._instantiate_object(x) for x in query_result]
        objects = list()
        for item in query_result:
            object = self._instantiate_object(item)
            self.logger.info(f'Object mounted: {object}')
            objects.append(object)
        self.logger.debug(f'I got {str(len(objects))} objects')
        return objects

    def _process_filters(self, kwargs):
        filters = dict()
        for k, v in kwargs.items():
            key, value = self._process_filter(k, v)
            filters[key] = value
        return filters

    def _process_filter(self, keys, values):
        key_array = keys.split('__')
        key_name = key_array[0]
        filter_params = key_array[1:]
        if len(filter_params) > 1:
            return key_name, self._process_filter_multiple(filter_params, values)
        return key_name, self._process_filter_single(filter_params, values)

    @staticmethod
    def _process_filter_single(filter_params, values):
        return { f'${filter_params[0]}': values }

    @staticmethod
    def _process_filter_multiple(filter_params, values):
        filters = dict()
        for i in range(len(filter_params)):
            filters[f'{filter_params[i]}'] = values[i]
        return filters
