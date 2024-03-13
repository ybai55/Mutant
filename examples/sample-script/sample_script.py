from hashlib import new
import mutant_client

new_labels = mutant_client.fetch_new_labels()
print(new_labels)