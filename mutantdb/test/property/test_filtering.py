from typing import Any, Dict, List, cast
from hypothesis import given, settings, HealthCheck
import pytest
from mutantdb.api import API
from mutantdb.test.property import invariants
from mutantdb.api.types import (
    Document,
    Embedding,
    Embeddings,
    IDs,
    Metadata,
    Metadatas,
    Where,
    WhereDocument,
)
import mutantdb.test.property.strategies as strategies
import hypothesis.strategies as st
import logging
import random


def _filter_where_clause(clause: Where, metadata: Metadata) -> bool:
    """Return true if the where clause is true for the given metadata map"""

    key, expr = list(clause.items())[0]

    # Handle the shorthand for equal: {key: val} where val is a simple value
    if (
        isinstance(expr, str)
        or isinstance(expr, bool)
        or isinstance(expr, int)
        or isinstance(expr, float)
    ):
        return _filter_where_clause({key: {"$eq": expr}}, metadata)

    # expr is a list of clauses
    if key == "$and":
        assert isinstance(expr, list)
        return all(_filter_where_clause(clause, metadata) for clause in expr)

    if key == "$or":
        assert isinstance(expr, list)
        return any(_filter_where_clause(clause, metadata) for clause in expr)

    # expr is an operator expression
    assert isinstance(expr, dict)
    op, val = list(expr.items())[0]

    assert isinstance(metadata, dict)
    if key not in metadata:
        return False
    metadata_key = metadata[key]
    if op == "$eq":
        return key in metadata and metadata_key == val
    elif op == "$ne":
        return key in metadata and metadata_key != val

    # The following conditions only make sense for numeric values
    assert isinstance(metadata_key, int) or isinstance(metadata_key, float)
    assert isinstance(val, int) or isinstance(val, float)
    if op == "$gt":
        return (key in metadata) and (metadata_key > val)
    elif op == "$gte":
        return key in metadata and metadata_key >= val
    elif op == "$lt":
        return key in metadata and metadata_key < val
    elif op == "$lte":
        return key in metadata and metadata_key <= val
    else:
        raise ValueError("Unknown operator: {}".format(key))


def _filter_where_doc_clause(clause: WhereDocument, doc: Document) -> bool:
    key, expr = list(clause.items())[0]

    if key == "$and":
        assert isinstance(expr, list)
        return all(_filter_where_doc_clause(clause, doc) for clause in expr)
    if key == "$or":
        assert isinstance(expr, list)
        return any(_filter_where_doc_clause(clause, doc) for clause in expr)

    # Simple $contains clause
    assert isinstance(expr, str)
    if key == "$contains":
        return expr in doc
    else:
        raise ValueError("Unknown operator: {}".format(key))


EMPTY_DICT: Dict[Any, Any] = {}
EMPTY_STRING: str = ""


def _filter_embedding_set(
    record_set: strategies.RecordSet, filter: strategies.Filter
) -> IDs:
    """Return IDs from the embedding set that match the given filter object"""

    normalized_record_set = invariants.wrap_all(record_set)

    ids = set(normalized_record_set["ids"])

    filter_ids = filter["ids"]
    if filter_ids is not None:
        filter_ids = invariants.wrap(filter_ids)
        assert filter_ids is not None
        # If the filter ids is an empty list then we treat that as get all
        if len(filter_ids) != 0:
            ids = ids.intersection(filter_ids)

    for i in range(len(normalized_record_set["ids"])):
        if filter["where"]:
            metadatas: Metadatas
            if isinstance(normalized_record_set["metadatas"], list):
                metadatas = normalized_record_set["metadatas"]
            else:
                metadatas = [EMPTY_DICT] * len(normalized_record_set["ids"])
            filter_where: Where = filter["where"]
            if not _filter_where_clause(filter_where, metadatas[i]):
                ids.discard(normalized_record_set["ids"][i])

        if filter["where_document"]:
            documents = normalized_record_set["documents"] or [EMPTY_STRING] * len(
                normalized_record_set["ids"]
            )
            if not _filter_where_doc_clause(filter["where_document"], documents[i]):
                ids.discard(normalized_record_set["ids"][i])

    return list(ids)


collection_st = st.shared(
    strategies.collections(add_filterable_data=True, with_hnsw_params=True),
    key="coll",
)
recordset_st = st.shared(
    strategies.recordsets(collection_st, max_size=1000), key="recordset"
)


@settings(
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.large_base_example,
    ]
)  # type: ignore
@given(
    collection=collection_st,
    record_set=recordset_st,
    filters=st.lists(strategies.filters(collection_st, recordset_st), min_size=1),
)
def test_filterable_metadata_get(
    caplog, api: API, collection: strategies.Collection, record_set, filters
) -> None:
    caplog.set_level(logging.ERROR)

    api.reset()
    coll = api.create_collection(
        name=collection.name,
        metadata=collection.metadata,  # type: ignore
        embedding_function=collection.embedding_function,
    )

    if not invariants.is_metadata_valid(invariants.wrap_all(record_set)):
        with pytest.raises(Exception):
            coll.add(**record_set)
        return

    coll.add(**record_set)

    for filter in filters:
        result_ids = coll.get(**filter)["ids"]
        expected_ids = _filter_embedding_set(record_set, filter)
        assert sorted(result_ids) == sorted(expected_ids)


@settings(
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.large_base_example,
    ]
)
@given(
    collection=collection_st,
    record_set=recordset_st,
    filters=st.lists(
        strategies.filters(collection_st, recordset_st, include_all_ids=True),
        min_size=1,
    ),
)
def test_filterable_metadata_query(
    caplog: pytest.LogCaptureFixture,
    api: API,
    collection: strategies.Collection,
    record_set: strategies.RecordSet,
    filters: List[strategies.Filter],
) -> None:
    caplog.set_level(logging.ERROR)

    api.reset()
    coll = api.create_collection(
        name=collection.name,
        metadata=collection.metadata,  # type: ignore
        embedding_function=collection.embedding_function,
    )
    normalized_record_set = invariants.wrap_all(record_set)

    if not invariants.is_metadata_valid(normalized_record_set):
        with pytest.raises(Exception):
            coll.add(**record_set)
        return

    coll.add(**record_set)
    total_count = len(normalized_record_set["ids"])
    # Pick a random vector
    random_query: Embedding
    if collection.has_embeddings:
        assert normalized_record_set["embeddings"] is not None
        assert all(isinstance(e, list) for e in normalized_record_set["embeddings"])
        random_query = normalized_record_set["embeddings"][
            random.randint(0, total_count - 1)
        ]
    else:
        assert isinstance(normalized_record_set["documents"], list)
        assert collection.embedding_function is not None
        random_query = collection.embedding_function(
            [normalized_record_set["documents"][random.randint(0, total_count - 1)]]
        )[0]
    for filter in filters:
        result_ids = set(
            coll.query(
                query_embeddings=random_query,
                n_results=total_count,
                where=filter["where"],
                where_document=filter["where_document"],
            )["ids"][0]
        )
        expected_ids = set(
            _filter_embedding_set(
                cast(strategies.RecordSet, normalized_record_set), filter
            )
        )
        assert len(result_ids.intersection(expected_ids)) == len(result_ids)


def test_empty_filter(api: API) -> None:
    """Test that a filter where no document matches returns an empty result"""
    api.reset()
    coll = api.create_collection(name="test")

    test_ids: IDs = ["1", "2", "3"]
    test_embeddings: Embeddings = [[1, 1], [2, 2], [3, 3]]
    test_query_embedding: Embedding = [1, 2]
    test_query_embeddings: Embeddings = [test_query_embedding, test_query_embedding]

    coll.add(ids=test_ids, embeddings=test_embeddings)

    res = coll.query(
        query_embeddings=test_query_embedding,
        where={"q": {"$eq": 4}},
        n_results=3,
        include=["embeddings", "distances", "metadatas"],
    )
    assert res["ids"] == [[]]
    assert res["embeddings"] == [[]]
    assert res["distances"] == [[]]
    assert res["metadatas"] == [[]]

    res = coll.query(
        query_embeddings=test_query_embeddings,
        where={"test": "yes"},
        n_results=3,
    )
    assert res["ids"] == [[], []]
    assert res["embeddings"] is None
    assert res["distances"] == [[], []]
    assert res["metadatas"] == [[], []]


def test_boolean_metadata(api: API) -> None:
    """Test that metadata with boolean values is correctly filtered"""
    api.reset()
    coll = api.create_collection(name="test")

    test_ids: IDs = ["1", "2", "3"]
    test_embeddings: Embeddings = [[1, 1], [2, 2], [3, 3]]
    test_metadatas: Metadatas = [{"test": True}, {"test": False}, {"test": True}]

    coll.add(ids=test_ids, embeddings=test_embeddings, metadatas=test_metadatas)

    res = coll.get(where={"test": True})

    assert res["ids"] == ["1", "3"]
