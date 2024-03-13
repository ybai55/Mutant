import hnswlib
import numpy as np
from mutant_server.index.abstract import Index
from mutant_server.utils import logger


class Hnswlib(Index):

    _index = None

    def __init__(self):
        pass

    def run(self, embedding_data):
        # more comments available at the source: https://github.com/nmslib/hnswlib

        # We split the data in two batches:
        data1 = embedding_data['embedding_data'].to_numpy().tolist()
        dim = len(data1[0])
        num_elements = len(data1)
        logger.debug("dimensionality is: ", dim)
        logger.debug("total number of elements: ", num_elements)
        logger.debug("max elements", num_elements//2)

        concatted_data = data1
        logger.debug("concatenated length: ", len(concatted_data))

        p = hnswlib.Index(space='l2', dim=dim)  # Declaring index, possible options are l2, cosine or ip
        p.init_index(max_elements=len(data1), ef_construction=100, M=16)  # Initing idnex
        p.set_ef(10)    # Controlling the recall by setting ef:
        p.set_num_threads(4)    # Set number of threads used during batch search/construction

        logger.debug("Adding first batch of %d elements..." % (len(data1)))
        p.add_items(data1)

        # Query the elements for themselves and measure recall:
        labels, distances = p.knn_query(data1, k=1)
        logger.debug(len(distances))
        logger.debug("Recall for the first batch:", np.mean(labels.reshape(-1) == np.arange(len(data1))), "\n")

        self._index = p

    def fetch(self, query):
        raise NotImplementedError

    def delete_batch(self, batch):
        raise NotImplementedError

    def persist(self):
        if self._index is None:
            return
        self._index.save_index(".mutant/index.bin")
        logger.debug('index saved to .mutant/index.bin')

    def load(self, elements, dimensionality):
        self._index = p
        self._index.load_index(".mutant/index.bin", max_elements=elements)