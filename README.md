# Mutant

本项目做为Vector_DB的起步项目. 
初步是整个复写Chroma的源码. 之所以选择Chroma是因为Python更容易一些. 并且Chroma感觉曝光率相对也高一些. 
在复写Chroma之后, 会继续参考Milvus, VSearch等项目. 或主要方向放在Faiss上来深入研究index方向的优化.

当然, 在复写Chroma上, 肯定存在各种问题. 目前是打算跟着Github的commit network来做. 正好也能感受一下Chroma
在17个月的开发过程中的思考过程.

This repository is a project that first following the Chroma's git network history, then think to imporve it.
So may the first thousands commits will be the same as Chorma. The only diff is change the name.


Contents:

- `/doc` - Project documentation
- `/mutant-client` - Python client for mutant
- `/mutant-server` - FastAPI server used as the backend for Mutant client