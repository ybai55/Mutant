import json
from mutant_client import Mutant

mutant = Mutant()
mutant.reset()

# log
for i in range(10):
    Mutant.log(
        embedding_data=[1,2,3,4,5,6,7,8,9,10],
        input_uri="https://www.google.com",
        dataset=None
    )


# fetch all
allres = mutant.get_all()
print(allres)


# count
print("count is", mutant.count()['count'])

# persist
mutant.persist()

# heartbeat
print(mutant.heartbeat())

# rand
print(mutant.rand())

# process
mutant.process()

# reset
mutant.reset()
print("count is", mutant.count()['count'])