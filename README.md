# Mutant

Currently, this project is based on Chroma.
This project will follow each commit in Chroma git history. 
After rewrite Chroma, this project will research on Milvus and VSearch,
or focus on Indexing optimize based on Faiss learning.


## Not expected things
Chroma use lots of third-party tools. Such as Sentry, PostHog and Clickhouse, which 
I'm not familiar. I think it's not a first priority in this time. I'll follow the code, 
but not verify things with those third-party things.

This repository is a project that first following the Chroma's git network history, then think to imporve it.
So may the first thousands commits will be the same as Chorma. The only diff is change the name.


Contents:

- `/doc` - Project documentation
- `/mutant-client` - Python client for mutant
- `/mutant-server` - FastAPI server used as the backend for Mutant client

### Get up and running on Linux
No requirements
```
/bin/bash -c "$(curl -fsSL https://gist.githubusercontent.com/ybai55/5254c2bd4cc916c1f2451b5394b17d8a/raw/32f7b412853894e171b12f518b9a8808150bfbc7/mutant_setup.sh)" 
python3 mutant/bin/test.py
```

### You should see something like

```
Getting heartbeat to verify the server is up
{'nanosecond heartbeat': 1667865642509760965000}
Logging embeddings into the database
Generating the index
True
Running a nearest neighbor search
{'ids': ['11540ca6-ebbc-4c81-8299-108d8c47c88c'], 'embeddings': [['sample_space', '11540ca6-ebbc-4c81-8299-108d8c47c88c', [1.0, 2.0, 3.0, 4.0, 5.0], '/images/1', 'training', None, 'spoon']], 'distances': [0.0]}
Success! Everything worked!
```


### Run in-memory Mutant

```
cd mutant-server
CHROMA_MODE="in-memory" uvicorn mutant_server.api:app --reload --log-level=debug
```