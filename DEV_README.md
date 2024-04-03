### Using core code/modules outside Docker

Adding `127.0.0.1 clickhouse` to /etc/hosts is only necessary if you want to use the app's core code outside of Docker, while still using Clickhouse inside Docker. 
This is because inside Docker Clickhouse is mapped to `clickhouse` as the network name. 
Outside, Docker containers are simply mapped to ports on 127.0.0.1. 
There are two ways to use the core code outside of Docker then: 

(1) update the url from `clickhouse` to `127.0.01` inside clickhouse.py (FYI mutant-server inside Docker *will* break), 

or map requests locally on your host machine to `clickhouse` over to Docker's `127.0.0.1`. Adding the line to /etc/hosts fulfills 
#2. This is outside the usage pattern of normal use, but it's useful to know how and why it can work. 