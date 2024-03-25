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
    # print("Data preview")
    # print(df.head())

    mutant = Mutant()
    mutant.reset()  # make sure we are using a fresh db
    allstart = time.time()
    start = time.time()

    dataset = "training"
    # Batch size
    BATCH_SIZE = 10_000
    # BATCH_SIZE = 100

    print("Loading in records with a batch size of: ", data_length)

    # iterate through df with a batch size of 100
    for i in range(0, data_length, BATCH_SIZE):
        if (i > 100):
            break

        end = time.time()
        page = i * BATCH_SIZE
        print(f"Time to process {BATCH_SIZE} rows: {end - start}, records loaded: {str(i)}")
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
            dataset=dataset,
            category_name=category_names
        )

    allend = time.time()
    print("time to log all", "{:.2f}".format(allend - allstart))

    fetched = mutant.count()
    print("Records loaded into the database: ", fetched)

    # time this function
    start = time.time()
    mutant.process()
    end = time.time()
    print("Time to process: " + str(end - start))

    knife_embedding = [0.2310010939836502, -0.3462161719799042, 0.29164767265319824, -0.09828940033912659,
                       1.814868450164795, -10.517369270324707, -13.531850814819336, -12.730537414550781,
                       -13.011675834655762, -10.257010459899902, -13.779699325561523, -11.963963508605957,
                       -13.948140144348145, -12.46799087524414, -14.569470405578613, -16.388280868530273,
                       -13.76762580871582, -12.192169189453125, -12.204055786132812, -12.259000778198242,
                       -13.696036338806152, -14.609177589416504, -16.951879501342773, -17.096384048461914,
                       -14.355693817138672, -16.643482208251953, -14.270745277404785, -14.375198364257812,
                       -14.381218910217285, -13.475995063781738, -12.694938659667969, -10.011992454528809,
                       -9.770626068115234, -13.155019760131836, -16.136341094970703, -6.552414417266846,
                       -11.243837356567383, -16.678457260131836, -14.629229545593262, -10.052337646484375,
                       -15.451828956604004, -12.561151504516602, -11.68396282196045, -11.975972175598145,
                       -11.09926986694336, -13.060500144958496, -12.075592994689941, -1.0808746814727783,
                       1.7046797275543213, -3.8080708980560303, -11.401922225952148, -12.184720039367676,
                       -13.262567520141602, -11.299583435058594, -13.654638290405273, -10.767330169677734,
                       -9.012763977050781, -10.202326774597168, -10.088111877441406, -13.247991561889648,
                       -9.651527404785156, -11.903244972229004, -13.922954559326172, -17.37179946899414,
                       -12.51513385772705, -7.8046746253967285, -14.406414985656738, -13.172696113586426,
                       -11.194984436035156, -12.029500961303711, -10.996524810791016, -10.828441619873047,
                       -8.673471450805664, -13.800869941711426, -9.680946350097656, -12.964024543762207,
                       -9.694372177124023, -13.132003784179688, -9.38864803314209, -14.305071830749512,
                       -14.4693603515625, -5.0566205978393555, -15.685358047485352, -12.493011474609375,
                       -8.424881935119629]
    # print("df['embedding_data'][0]: ", df['embedding_data'][0])
    # time this function
    start = time.time()
    get_nearest_neighbors = mutant.get_nearest_neighbors(knife_embedding, 4, "knife", "training")
    print("Nearest neighbors: ", len(get_nearest_neighbors['distances']), get_nearest_neighbors['ids'], get_nearest_neighbors)
    end = time.time()
    print("Time to get nearest neighbors: " + str(end - start))

    # highest_signal = mutant.rand()  # rand for now - by far the slowest operation
    # print("Record in a bisectional split: ", len(highest_signal))

    fetched = mutant.count()
    print("Records loaded into the database: ", fetched)
    del mutant

