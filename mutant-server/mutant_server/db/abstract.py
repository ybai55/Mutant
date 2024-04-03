from abc import abstractmethod


# TODO: update this to match the clickhouse implementation
class Database:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add(
        self,
        model_space,
        embedding,
        input_uri,
        dataset=None,
        custom_quality_score=None,
        inference_class=None,
        label_class=None,
    ):
        pass

    @abstractmethod
    def count(self, model_space=None):
        pass

    @abstractmethod
    def fetch(self, where={}, sort=None, limit=None):
        pass

    @abstractmethod
    def get_by_ids(self, ids):
        pass

    @abstractmethod
    def reset(self):
        pass
