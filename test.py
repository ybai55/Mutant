import mutantdb
from mutantdb.config import Settings

mutant = mutantdb.Client(Settings(mutant_api_impl="rest",
                                  mutant_server_host="localhost",
                                  mutant_server_http_port="8000"))

mutant.reset()

print("heartbeat", mutant.heartbeat())

print("create", mutant.create_collection("test", {"test", "test"}))


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

# mutant.set_collection_name("test")
