# Sanity check script to ensure that the Mutant client can connect
# and is capable of recieving data.

import mutantdb
from mutantdb.config import Settings

# run in in-memory mode
mutant_api = mutantdb.Client()

# uncomment to run in client-server mode
# mutant_api = mutant.Client(Settings(mutant_api_impl="rest",
#                               mutant_server_host="localhost",
#                               mutant_server_http_port="8000") )

mutant_api.set_collection_name("sample_space")
print("Getting heartbeat to verify the server is up")
print(mutant_api.heartbeat())

print("Logging embeddings into the database")
mutant_api.add(
    embedding=[[1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [10, 9, 8, 7, 6]],
    input_uri=["/images/1", "/images/2", "/images/3"],
    dataset="train",
    inference_class=["spoon", "knife", "fork"],
    collection_uuid="sample_space"
)

print("count")
print(mutant_api.count())

print("Generating the index")
print(mutant_api.create_index())

print("Running a nearest neighbor search")
print(mutant_api.get_nearest_neighbors([1, 2, 3, 4, 5], 1))

print("Success Everything worked!")
