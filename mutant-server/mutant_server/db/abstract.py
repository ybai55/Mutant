from abc import abstractmethod

# TODO: update this to match the clickhouse implementation
class Database:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_batch(
        self,
        model_space,
        embedding_data,
        input_uri,
        dataset=None,
        custom_quality_score=None,
        category_name=None,
    ):
        pass

    @abstractmethod
    def count(self, model_space=None):
        pass

    @abstractmethod
    def fetch(self, where_filter={}, sort=None, limit=None):
        pass

    @abstractmethod
    def get_by_ids(self, ids):
        pass

    @abstractmethod
    def reset(self):
        pass
