from mutantdb.db import DB
from mutantdb.db.index.hnswlib import Hnswlib
from mutantdb.errors import NoDatapointsException
import uuid
import time
import os
import itertools

# from clickhouse_driver import connect, Client
import clickhouse_connect

COLLECTION_TABLE_SCHEMA = [
    {'uuid': 'UUID'},
    {'name': 'String'},
    {'metadata': 'Map(String, String)'}
]

EMBEDDING_TABLE_SCHEMA = [
    {'collection_uuid': 'UUID'},
    {'uuid': 'UUID'},
    {'embedding': 'Array(Float64)'},
    {'document': 'Nullable(String)'},
    {'id': 'Nullable(String)'},
    {'metadata': 'Map(String, String)'}
]


def db_array_schema_to_clickhouse_schema(table_schema):
    return_str = ""
    for element in table_schema:
        for k, v in element.items():
            return_str += f"{k} {v}, "
    return return_str


def db_schema_to_keys():
    return_str = ""
    for element in EMBEDDING_TABLE_SCHEMA:
        if element == EMBEDDING_TABLE_SCHEMA[-1]:
            return_str += f"{list(element.keys())[0]}"
        else:
            return_str += f"{list(element.keys())[0]}, "
    return return_str


class Clickhouse(DB):
    _conn = None

    def __init__(self, settings):
        self._conn = clickhouse_connect.get_client(host=settings.clickhouse_host, port=int(
            settings.clickhouse_port))  # Client(host=settings.clickhouse_host, port=settings.clickhouse_port)
        self._conn.command(f'''SET allow_experimental_lightweight_delete = true''')
        self._conn.command(
            f'''SET mutations_sync = 1''')  # https://clickhouse.com/docs/en/operations/settings/settings/#mutations_sync

        self._create_table_collections()
        self._create_table_embeddings()
        self._idx = Hnswlib(settings)
        self._settings = settings

    def _create_table_collections(self):
        self._conn.command(f'''CREATE TABLE IF NOT EXISTS collections (
            {db_array_schema_to_clickhouse_schema(COLLECTION_TABLE_SCHEMA)}
        ) ENGINE = MergeTree() ORDER BY uuid''')

    def _create_table_embeddings(self):
        self._conn.command(f'''CREATE TABLE IF NOT EXISTS embeddings (
            {db_array_schema_to_clickhouse_schema(EMBEDDING_TABLE_SCHEMA)}
        ) ENGINE = MergeTree() ORDER BY collection_uuid''')

    def create_collection(self, name, metadata=None):
        if metadata is None:
            metadata = {}

        # poor man's unique constraint
        checkname = self._conn.query(f'''
            SELECT * FROM collections WHERE name = '{name}'
        ''')

        if checkname.row_count > 0:
            raise Exception("Collection already exists with that name")

        collection_uuid = uuid.uuid4()
        data_to_insert = []
        data_to_insert.append([collection_uuid, name, metadata])

        self._conn.insert('collections', data_to_insert, column_names=['uuid', 'name', 'metadata'])
        return collection_uuid

    def get_collection(self, name):
        return self._conn.query_df(f'''
         SELECT * FROM collections WHERE name = '{name}'
         ''')

    def list_collections(self):
        return self._conn.query_df(f'''
         SELECT * FROM collections
         ''')

    def update_collection(self, name=None, metadata=None):
        # can not cast dict to map in clickhouse so we go through tuple
        metadata = [(key, value) for key, value in metadata.items()]

        self._conn.command(f'''
         ALTER TABLE 
            collections 
         UPDATE
            metadata = {metadata}
         WHERE 
            name = '{name}'
         ''')

    def delete_collection(self, name):
        self._conn.command(f'''
         DELETE FROM collections WHERE name = '{name}'
         ''')

    def add(self, collection_uuid, embedding, metadata=None, documents=None, ids=None):
        print("duckdb add, embeddings: ", embedding)

        data_to_insert = []
        for i in range(len(embedding)):
            data_to_insert.append([collection_uuid, uuid.uuid4(), embedding[i], metadata[i], documents[i], ids[i]])

        column_names = ["collection_uuid", "uuid", "embedding", "metadata", "document", "id"]
        self._conn.insert('embeddings', data_to_insert, column_names=column_names)

        return [x[1] for x in data_to_insert]  # return uuids

    def _fetch(self, where={}):
        return self._conn.query_df(f'''SELECT {db_schema_to_keys()} FROM embeddings {where}''')

    def _filter_metadata(self, key, value):
        return " " # TODO

    def fetch(self, ids=None, where={}, sort=None, limit=None, offset=None):
        print("clickhouse fetch, ids: ", ids)
        print("clickhouse fetch, where: ", where)

        if "collection_name" in where:
            collection_uuid = self.get_collection(where["collection_name"]).iloc[0].uuid
            del where["collection_name"]
            where['collection_uuid'] = collection_uuid

        s3 = time.time()
        # check to see if query is a dict and if it is a flat list of key value<string> pairs
        if where is not None:
            if not isinstance(where, dict):
                raise Exception("Invalid where: " + str(where))

            # ensure where only contains strings, as we only support string equality for now
            for key in where:
                if isinstance(where[key], str):
                    raise Exception("Invalid where: " + str(where))

        metadata_query = None
        # if where has a metadata key, we need to do a special query
        if "metadata" in where:
            metadata_query = where["metadata"]
            del where["metadata"]

        print('metadata_query', metadata_query)

        where = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
        if metadata_query is not None:
            for key, value in metadata_query.items():
                where += self._filter_metadata(key, value)

        if ids is not None:
            where += f" AND id IN {tuple(ids)}"

        if where:
            where = f"WHERE {where}"

        if sort is not None:
            where += f" ORDER BY {sort}"
        else:
            where += f" ORDER BY collection_uuid"  # stable ordering

        if limit is not None or isinstance(limit, int):
            where += f" LIMIT {limit}"

        if offset is not None or isinstance(offset, int):
            where += f" OFFSET {offset}"

        print("where: ", where)
        val = self._fetch(where=where)

        print(f"time to fetch {len(val)} embeddings: ", time.time() - s3)

        return val

    def _count(self, collection_uuid=None):
        where_string = ""
        if collection_uuid is not None:
            where_string = f"WHERE collection_uuid = '{collection_uuid}'"
        return self._conn.query(f"SELECT COUNT() FROM embeddings {where_string}").result_rows

    def count(self, collection_name=None):
        collection_uuid = self.get_collection(collection_name).iloc[0].uuid
        return self._count(collection_uuid=collection_uuid)[0][0]

    def _delete(self, where_str=None):
        uuids_deleted = self._conn.query_df(f'''SELECT uuid FROM embeddings {where_str}''')

        self._conn.execute(f'''
            DELETE FROM
                embeddings
        {where_str}
        ''')
        return uuids_deleted.uuid.tolist() if len(uuids_deleted) > 0 else []

    def delete(self, where={}):
        if where["collection_name"] is None:
            return {"error": "collection_name is required. Use reset to clear the entire db"}

        collection_uuid = self.get_collection(where["collection_name"]).iloc[0].uuid
        del where["collection_name"]
        where['collection_uuid'] = collection_uuid

        s3 = time.time()
        # check to see if query is a dict and if it is a flat list of key value pairs
        if where is not None:
            if not isinstance(where, dict):
                raise Exception("Invalid where: " + str(where))

            # ensure where is a flat dict
            for key in where:
                if isinstance(where[key], dict):
                    raise Exception("Invalid where: " + str(where))

        where_str = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])

        if where_str:
            where_str = f"WHERE {where_str}"
        deleted_uuids = self._delete(where_str)
        print(f"time to fetch {len(deleted_uuids)} embeddings for deletion: ", time.time() - s3)

        if len(where) == 1:
            self._idx.delete(where['collection_uuid'])
        else:
            self._idx.delete_from_index(where['collection_uuid'], deleted_uuids)

        return deleted_uuids

    def get_by_ids(self, ids=list):
        df = self._conn.query_df(f'''
        SELECT {db_schema_to_keys()} FROM embeddings WHERE uuid IN ({[id.hex for id in ids]})
        ''')
        return df

    def get_random(self, where={}, n=1):
        # check to see if query is a dict and if it is a flat list of key value pairs
        if where is not None:
            if not isinstance(where, dict):
                raise Exception("Invalid where: " + str(where))

            # ensure where is a flat dict
            for key in where:
                if isinstance(where[key], dict):
                    raise Exception("Invalid where: " + str(where))

        where = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
        if where:
            where = f"WHERE {where}"

        return self._conn.query_df(f'''
            SELECT {db_schema_to_keys()} FROM embeddings {where} ORDER BY rand() LIMIT {n}''')

    def get_nearest_neighbors(self, where, embedding, n_results):

        collection_uuid = self.get_collection(where["collection_name"]).iloc[0].uuid
        del where["collection_name"]
        where['collection_uuid'] = collection_uuid

        results = self.fetch(where)
        if len(results) > 0:
            ids = results.uuid.tolist()
        else:
            raise NoDatapointsException("No datapoints found for the supplied filter")

        uuids, distances = self._idx.get_nearest_neighbors(where['collection_uuid'], embedding, n_results, ids)

        return {
            "ids": uuids,
            "embeddings": self.get_by_ids(uuids[0]),
            "distances": distances.tolist()[0]
        }

    def create_index(self, collection_uuid) -> None:
        """Create an index for a collection_uuid and optionally scoped to a dataset. 
        Args:
            collection_uuid (str): The collection_uuid to create an index for
            dataset (str, optional): The dataset to scope the index to. Defaults to None.
        Returns:
            None
        """
        print(f"creating index for {collection_uuid}")
        query = {"collection_uuid": collection_uuid}
        fetch = self.fetch(query)
        self._idx.run(collection_uuid, fetch.uuid.tolist(), fetch.embedding.tolist())
        # mutant_telemetry.capture('created-index-run-process', {'n': len(fetch)})

    def add_incremental(self, collection_uuid, uuids, embeddings):
        self._idx.add_incremental(collection_uuid, uuids, embeddings)

    def has_index(self, collection_uuid):
        return self._idx.has_index(self, collection_uuid)

    def reset(self):
        self._conn.command('DROP TABLE collections')
        self._conn.command('DROP TABLE embeddings')
        self._create_table_collections()
        self._create_table_embeddings()

        self._idx.reset()
        self._idx = Hnswlib(self._settings)

    def raw_sql(self, sql):
        return self._conn.query_df(sql)

