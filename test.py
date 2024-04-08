import mutantdb
from mutantdb.config import Settings

mutant = mutantdb.Client(Settings(mutant_api_impl="rest",
                              mutant_server_host="localhost",
                              mutant_server_http_port="8000"))
# mutant = mutantdb.Client()

mutant.reset()

print("heartbeat", mutant.heartbeat())

print("create", mutant.create_collection("test", {"test": "test"}))

# print("list", mutant.list_collections())

# print("get", mutant.update_collection("test", {"test": "another"}))

# print("get", mutant.get_collection("test"))

# print("delete", mutant.delete_collection("test"))

# print("list", mutant.list_collections())

print("count", mutant.count("test"))

print("add", mutant.add(
    collection_name="test",
    embedding=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4]], 
))
print("add", mutant.add(
    collection_name="test",
    embedding=[[5.1, 4.3, 3.2], [6.5, 5.9, 4.4]], 
    metadata=[{"uri": "img11.png", "style": "style1"}, {"uri": "img10.png", "style": "style1"}]
))
print("add", mutant.add(
    collection_name="test",
    embedding=[[11.0, 12.0, 13.0]], 
    metadata=[{"uri": "img12.png", "style": "style1"}]
))
# print("add", mutant.add(
#     collection_name="test",
#     embedding=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4]], 
#     metadata=[{"apples": "bananas"}, {"apples": "oranges"}]
# ))




# print("create_index", mutant.create_index("test"))

# print("fetch", mutant.fetch("test", limit=2))

print("ann", mutant.search("test", [11.1, 12.1, 13.1], n_results=1))

# print("delete", mutant.delete("test"))

# print("count", mutant.count("test"))

# update the embedding for where metadata.uri == "img12.png"
# we search for the first embedding that matches the metadata
# and update it with the new embedding
print("add", mutant.update(
    collection_name="test",
    embedding=[[5.1, 4.3, 3.2], [6.5, 5.9, 4.4]], 
    metadata=[{"uri": "img12.png"}, {"uri": "img10.png"}]
))