

import mutantdb 

client = mutantdb.Client()
print(client.heartbeat()) # returns a nanosecond heartbeat /api/v1/heartbeat
client.reset() # resets the database  /api/v1/reset
print(client.list_collections()) # returns a list of collections /api/v1/list_collections

# # Create a collection
collection = client.create_collection(name="test")
# collection = client.get_collection(name="test") # does this to a roundtrip to the server, have things like dimensionality
# #create_index
# collection = client.update_collection(oldName="test", newName="test2") # this feels a little odd to me (Jeff)
# client.delete_collection(name="test")
# collection.peek() # returns a list of the first 10 items in the collection
# collection.count() # returns the number of items in the collection

print(client.list_collections()) 

# # Add some embeddings
# collection.add( # add fails if collisions on id
#     embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
#     metadatas=[{"uri": "img1.png", "style": "style1"}, {"uri": "img2.png", "style": "style1"}, {"uri": "img3.png", "style": "style1"}, {"uri": "img4.png", "style": "style1"}, {"uri": "img5.png", "style": "style1"}, {"uri": "img6.png", "style": "style1"}, {"uri": "img7.png", "style": "style1"}, {"uri": "img8.png", "style": "style1"}],
#     documents=["doc1", "doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8"],
#     ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8"], # are forced to be unique
#     # flag
#     add_to_index=False # probably not worth the complexity, ... benchmark? probably dont have
# )
# # exception if they try to insert too many items 
# collection.upsert( # always succeeds
#     embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
#     metadatas=[{"uri": "img1.png", "style": "style1"}, {"uri": "img2.png", "style": "style1"}, {"uri": "img3.png", "style": "style1"}, {"uri": "img4.png", "style": "style1"}, {"uri": "img5.png", "style": "style1"}, {"uri": "img6.png", "style": "style1"}, {"uri": "img7.png", "style": "style1"}, {"uri": "img8.png", "style": "style1"}],
#     documents=["doc1", "doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8"],
#     ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8"], 
# )

# collection.add(
#     embeddings=[6.5, 5.9, 4.4],
#     metadatas={"uri": "img9.png", "style": "style1"},
#     documents="doc9",
#     uris="uri9",
# )

# # supports multiple at once 
# collection.query( # or query_by_embeddings, query_by_texts, search 
#     query_embeddings=[11.1, 12.1, 13.1],
#     # OR // COULD BE an AND and return a tuple
#     query_texts="doc10",
#     n_results=10, # k, or top k, or top k results... can we remove this? and just do it for users
#     where={"style": "style1"}, # performance considerations, duckdb, clickhouse, support lt, gt, !=, etc 
#     # TODO: fixed/test the case where we load in 50 items, we filter out 49, does it return
# )

# collection.get( # you get it all back and you just fucking deal with it
#     ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8"],
# 		# where/filter?
# )

# collection.delete( # propagates to the index
#     ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8"],
# 	# where/filter?
# )

# collection.update( # fails if id doesnt exist 
#     ids=["id1", "id2", "id3", "id4", "id5", "id6", "id7", "id8"], 
#     # THE BELOW IS OPTIONAL
#     embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], [4.5, 6.9, 4.4]],
#     metadatas=[{"uri": "img1.png", "style": "style1"}, {"uri": "img2.png", "style": "style1"}, {"uri": "img3.png", "style": "style1"}, {"uri": "img4.png", "style": "style1"}, {"uri": "img5.png", "style": "style1"}, {"uri": "img6.png", "style": "style1"}, {"uri": "img7.png", "style": "style1"}, {"uri": "img8.png", "style": "style1"}],
#     documents=["doc1", "doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8"],
#     # flags -- probably cut this for now to avoid dirty state between the index and items 
#     # update_embeddings=True,
#     # update_index=False
# )
