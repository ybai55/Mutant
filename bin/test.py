# Sanity check script to ensure that the Mutant client can connect
# and is capable of receiving data.
import mutantdb

# run in in-memory mode
mutant_api = mutantdb.Client()
print(mutant_api.heartbeat())