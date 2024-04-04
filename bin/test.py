# Sanity check script to ensure that the Mutant client can connect
# and is capable of recieving data.

from mutant_client import Mutant

mutant =Mutant()
mutant.set_model_space('sample_space')
print("Getting heartbeat to verify the server is up")
print(mutant.heartbeat())

print("Logging embeddings into the database")
mutant.add(
    [[1,2,3,4,5], [5,4,3,2,1], [10,9,8,7,6]],
    ["/images/1", "/images/2", "/images/3"],
    ["training", "training", "training"],
    ['spoon', 'knife', 'fork']
)

print("count")
print(mutant.count())

print("Generating the index")
print(mutant.create_index())

print("Running a nearest neighbor search")
print(mutant.get_nearest_neighbors([1, 2, 3, 4, 5], 1))

print("Success Everything worked!")
