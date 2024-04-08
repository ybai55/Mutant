from mutant.db.index.hnswlib import Hnswlib
from mutant.db.clickhouse import (
    Clickhouse,
    db_array_schema_to_clickhouse_schema,
    EMBEDDING_TABLE_SCHEMA,
    db_schema_to_keys,
)
import pandas as pd
import duckdb
import uuid
import itertools
import json


def clickhouse_to_duckdb_schema(table_schema):
    for item in table_schema:
        if 'embedding' in item:
            item['embedding'] = 'REAL[]'
        # capitalize the key
        item[list(item.keys())[0]] = item[list(item.keys())[0]].upper()
        if 'NULLABLE' in item[list(item.keys())[0]]:
            item[list(item.keys())[0]] = item[list(item.keys())[0]].replace('NULLABLE(', '').replace(')', '')
        if 'UUID' in item[list(item.keys())[0]]:
            item[list(item.keys())[0]] = 'STRING'
        if 'FLOAT64' in item[list(item.keys())[0]]:
            item[list(item.keys())[0]] = 'REAL'
        if 'MAP(STRING, STRING)' in item[list(item.keys())[0]]:
            item[list(item.keys())[0]] = 'JSON'

    return table_schema


# TODO: inherits ClickHouse for convenience of copying behavior, not
# because it's logically a subtype. Factoring out the common behavior
# to a third superclass they both extend would be preferable.
class DuckDB(Clickhouse):

    # duckdb has different types, so we want to convert the clickhouse schema to duckdb schema
    def _create_table_embeddings(self):
        self._conn.execute(f'''CREATE TABLE embeddings (
                    {db_array_schema_to_clickhouse_schema(clickhouse_to_duckdb_schema(EMBEDDING_TABLE_SCHEMA))}
                ) ''')


    # duckdb has a different way of connecting to the database
    def __init__(self, settings):
        self._conn = duckdb.connect()
        self._create_table_embeddings()
        self._idx = Hnswlib(settings)
        self._settings = settings

        # https://duckdb.org/docs/extensions/overview
        self._conn.execute("INSTALL 'json';")
        self._conn.execute("LOAD 'json';")

    # the execute many syntax is different than clickhouse, the (?,?) syntax is different than clickhouse
    def add(
        self,
        model_space,
        embedding,
        input_uri,
        dataset=None,
        metadata=None,
    ):
        metadata = [json.dumps(x) if not isinstance(x, str) else x for x in metadata]

        data_to_insert = []
        for i in range(len(embedding)):
            data_to_insert.append(
                [
                    model_space[i],
                    str(uuid.uuid4()),
                    embedding[i],
                    input_uri[i],
                    dataset[i],
                    metadata[i]
                ]
            )

        insert_string = (
            "model_space, uuid, embedding, input_uri, dataset, metadata"
        )
        self._conn.executemany(
            f"""
         INSERT INTO embeddings ({insert_string}) VALUES (?,?,?,?,?,?)""",
            data_to_insert,
        )

    def count(self, model_space=None):
        return self._count(model_space=model_space).fetchall()[0][0]

    def _filter_metadata(self, key, value):
        return f" ADD json_extract_string(metadata, '$.{key}' = '{value}')"

    def _fetch(self, where=""):
        val = self._conn.execute(f"""SELECT {db_schema_to_keys()} FROM embeddings {where}""").df()
        # Convert UUID strings to UUID objects
        val["uuid"] = val["uuid"].apply(lambda x: uuid.UUID(x))
        return val

    def _delete(self, where_str):
        uuids_deleted = self._conn.execute(f"""SELECT uuid FROM embeddings {where_str}""").fetchall()
        self._conn.execute(
            f"""
            DELETE FROM
                embeddings
        {where_str}
        """
        ).fetchall()[0]
        return [uuid.UUID(x[0]) for x in uuids_deleted]

    def get_by_ids(self, ids=list):
        # select from duckdb table where ids are in the list
        if not isinstance(ids, list):
            raise Exception("ids must be a list")

        if not ids:
            # create an empty pandas dataframe
            return pd.DataFrame()

        return self._conn.execute(
            f"""
            SELECT
                {db_schema_to_keys()}
            FROM
                embeddings
            WHERE
                uuid IN ({','.join([("'" + str(x) + "'") for x in ids])})
        """
        ).df()

    def raw_sql(self, sql):
        return self._conn.execute(sql).df()

    def get_random(self, where={}, n=1):
        # check to see if query is a dict and if it is a flat list of key value pairs
        if where is not None:
            if not isinstance(where, dict):
                raise Exception("Invalid where: " + str(where))

            # ensure where is a flat dict
            for key in where.keys():
                if isinstance(where[key], dict):
                    raise Exception("Invalid where: " + str(where[key]))

        where = " AND ".join([f"{key} = '{value}'" for key, value in where.items()])
        if where:
            where = f"WHERE {where}"

        return self._conn.execute(f'''
            SELECT {db_schema_to_keys()} FROM embeddings {where} LIMIT {n}''').df()  # ORDER BY rand()




class PersistentDuckDB(DuckDB):

    _save_folder = None

    def __init__(self, settings):
        super().__init__(settings=settings)
        self._save_folder = settings.mutant_cache_dir

        self.load()

    def set_save_folder(self, path):
        self._save_folder = path

    def get_save_folder(self):
        return self._save_folder

    def persist(self):
        """
        Persist the database to disk
        """
        print("Persisting DB to disk, putting it in the save folder", self._save_folder)
        if self._conn is None:
            return

        # if the db is empty, dont save
        if self.count() == 0:
            return

        self._conn.execute(
            f"""
                COPY
                    (SELECT * FROM embeddings)
                TO '{self._save_folder}/mutant.parquet'
                    (FORMAT PARQUET);
            """
        )

    def load(self):
        """
        Load the database from disk
        """
        import os

        # load in the embeddings
        if not os.path.exists(f"{self._save_folder}/mutant.parquet"):
            print(f"No existing DB found in {self._save_folder}, skipping load")
        else:
            path = self._save_folder + "/mutant.parquet"
            self._conn.execute(f"INSERT INTO embeddings SELECT * FROM read_parquet('{path}');")

    def __del__(self):
        print("PersistantDuckDB del, about to run persist")
        self.persist()
