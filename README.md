# Mutant

本项目做为Vector_DB的起步项目. 
初步是整个复写Chroma的源码. 之所以选择Chroma是因为Python更容易一些. 并且Chroma感觉曝光率相对也高一些. 
在复写Chroma之后, 会继续参考Milvus, VSearch等项目. 或主要方向放在Faiss上来深入研究index方向的优化.

当然, 在复写Chroma上, 肯定存在各种问题. 目前是打算跟着Github的commit network来做. 正好也能感受一下Chroma
在17个月的开发过程中的思考过程.


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
/bin/bash -c "$(curl -fsSL https://gist..../chroma_setup.sh)" 
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