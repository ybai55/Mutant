from mutant_client import Mutant
import pyarrow.parquet as pq
import numpy as np
from pandas.io.json import json_normalize
import json
import time
import os


if __name__ == "__main__":

    file = '../data__nogit/yolov3_objects_large.parquet'

    print("Loading parquet file:", file)
    py = pq.read_table(file)
    df = py.to_pandas()
    # print the length of the df
    print("Number of records:", len(df))

    data_length = len(df)
    print("Data preview")
    print(df.head())

    mutant = Mutant(app="yolov3", model_version="1.0.0", layer="pool5")
    mutant.reset()  # make sure we are using a fresh db
    allstart = time.time()
    start = time.time()

    app = "yolov3"
    model_version = '1.0.0'
    layer = "pool5"
    dataset = "training"
    # Batch size
    BATCH_SIZE = 100

    print("Loading in records with a batch size of: ", data_length)

    # iterate through df with a batch size of 100
    for i in range(0, data_length, BATCH_SIZE):
        if (i > 100):
            break

        end = time.time()
        page = i * BATCH_SIZE
        print("Time to process BATCH_SIZE rows: " + str(end - start), ", records loaded: " + str(i))
        start = time.time()

        # get the batch
        batch = df[i:i + BATCH_SIZE]

        # iterate through the batch
        for index, row in batch.iterrows():
            for idx, annotation in enumerate(row['infer']['annotations']):
                annotation['bbox'] = annotation['bbox'].tolist()
                row['infer']['annotations'] = row['infer']['annotations'].tolist()

            row['embedding_data'] = row['embedding_data'].tolist()

        # get the data
        embedding_data = batch['embedding_data'].tolist()
        metadata = batch['metadata_list'].tolist()
        input_uri = batch['resource_uri'].tolist()
        inference_data = batch['infer'].tolist()

        # get category name from batch["infer"]
        category_names = []
        for index, row in batch.iterrows():
            for idx, annotation in enumerate(row['infer']['annotations']):
                category_names.append(annotation['category_name'])

        # log the batch
        mutant.log_batch(
            embedding_data=embedding_data,
            metadata=metadata,
            input_uri=input_uri,
            inference_data=inference_data,
            app=app,
            model_version=model_version,
            layer=layer,
            dataset=dataset,
            category_name=category_names
        )

    mutant.process()

    print("df['embedding_data'][0]: ", df['embedding_data'][0])
    get_nearest_neighbors = mutant.get_nearest_neighbors(df['embedding_data'][0], 10)
    print("Nearest neighbors: ", get_nearest_neighbors)

    highest_signal = mutant.rand()  # rand for now - by far the slowest operation
    print("Record in a bisectional split: ", len(highest_signal))

    # del mutant
    fetched = mutant.count()
    print("Records loaded into the database: ", fetched)

