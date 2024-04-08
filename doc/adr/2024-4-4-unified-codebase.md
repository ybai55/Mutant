# Unified Codebase

## Context

We would like users to have a "10 second" getting started experience,
for example via a Google Collab notebook. However, Google notebooks do
not support running Docker or other long-running subprocesses, making
a mandatory client+server model non-viable.

## Decision

We will combine the `mutant-server` and `mutant-client` projects into
a single codebase.

The codebase can be consumed as a library, or the server entry-point
can be invoked to run a server to which other clients can connect.

The customer-facing Python API is 100% identical, whether running in
client+server or client-only mode.

We will split the project's dependencies so packages that are only
required for the server components will use a separate
`mutant[server]` or `mutant[all]` PIP dependency.

## Python API Refactoring

We will create abstract interfaces (using Python's `abc` module as
described in [PEP 3119](https://peps.python.org/pep-3119/))
representing key parts of mutant's internal structure.

Concrete singleton implementations of each functionality will be
obtained by invoking argument-free factory functions that return a
concrete type which depends on context and system wide configuration
(e.g. environment variables.) This serves as a rudimentary but
functional form of dependency injection.

Most code should be written only against the abstract interfaces and
strongly avoid requiring or importing any concrete implementations;
this will result in more lighweight runtime and allow users to
entirely omit dependencies they don't plan on using.

#### `mutant.API`

Defines mutant's primary customer-facing API.

Implementations:

- `mutant.api.Local` - Client implemented via direct calls to
  algorithm or DB classes.
- `mutant.api.Celery` - Extension of `mutant.api.Local`, which
  delegates some potentially long-running operations to a Celery
  worker pool.
- `mutant.api.FastAPI` - Client implementation backed by requests to
   a remote `mutant.server.FastAPI` instance (see below.)
- `mutant.api.ArrowFlight` - Client implementation backed by requests to
   a remote `mutant.server.ArrowFlight` instance (see below.)

#### `mutant.DB`

Define's mutant's data strorage and persistence layer.

Implementations:

- `mutant.db.Clickhouse` - Clickhouse database implementation.
- `mutant.db.DuckDB` - In-memory DuckDB implementation
- `mutant.db.PersistentDuckDB` - Extension of `mutant.db.DuckDB` that
  persists data in a local directory.

#### `mutant.Server`

A class which takes an instance of `mutant.API` and exposes it for
remote access.

Implementations:

- `mutant.server.FastAPI` - Run a FastAPI/ASGI webserver.
- `mutant.server.ArrowFlight` - Run an ArrowFlight gRPC server.

## Consequences

- mutant can run in a Collab notebook or dev machine, with no
  configuration required beyond `pip install`.
- The mutant PIP package will be slightly more heavyweight.
- The mutant project structure (considered as a whole) will be less
  complex.
- A well-factored class structure will allow us degrees of freedom in
  the future for exploring and comparing alternative protocols,
  storage mechanisms, and locations of computation. It also creates a
  path to multi-teir architectures where some computation or storage
  is delegated to a remote SaaS product.


背景 Context

我们希望用户拥有“10 秒钟”的快速入门体验，例如通过 Google Colab 实现。但是，Google Colab 笔记本不支持运行 Docker 或其他长时间运行的子进程，这使得强制性的客户端-服务器模型变得不可行。

决定 Decision


我们将把 mutant-server 和 mutant-client 项目合并成一个single codebase。
Codebase 既可以作为 library 使用，也可以调用 server 的 entry-point 运行 server，供其他客户端连接。
面向客户的 Python API 在 client+server 模式和仅 client-only 模式下完全相同。
我们将拆分项目的依赖项，需要的 PIP 依赖项将使用单独的 mutant[server] 或 mutant[all]。
Python API 重构 (Refactoring)

我们将使用 Python 的 abc 模块 (遵循 PEP 3119 标准) 创建抽象接口(abstract interface)，来representing Mutant 内部结构的关键部分。
具体功能的单例实现将通过调用无参工厂函数来获得。该函数会返回一个具体的类型，该类型取决于上下文和系统配置（例如环境变量）。这是一种简单但实用的依赖注入形式。
大部分代码应该只针对抽象接口进行编写，并严格避免引用或导入任何具体的实现。这样做将带来以下好处：
- 更加轻量级的运行时：由于只依赖于接口，程序在运行时只需要加载最少的代码，从而提高运行效率。
- 用户可以完全省略不必要的依赖项：通过抽象接口，用户可以选择只集成他们需要的功能，从而减少程序的体积和复杂性。

mutant.API

此部分定义了 Mutant 面向用户的主要 API。具体实现方式如下：
- mutant.api.Local: 客户端, 直接调用算法或数据库类来实现功能。
- mutant.api.Celery: 它扩展了mutant.api.Local 的功能，可以将一些耗时的操作委托给 Celery worker 进程池来执行。
- mutant.api.FastAPI: 这种客户端通过向远程的 mutant.server.FastAPI 实例发送请求来实现功能。（见下文描述 ）适用于需要将后端服务独立部署的场景。
- mutant.api.ArrowFlight: 这种客户端通过向远程的 mutant.server.ArrowFlight 实例发送请求来实现功能。（见下文描述 mutant.server.ArrowFlight）提供另一种高效的远程通信方式。


mutant.DB

此部分定义了Mutant的 data storage 和 persistence layer.

具体实现:
- mutant.db.Clickhouse - 实现 Clickhouse database .
- mutant.db.DuckDB - 实现 In-memory DuckDB 
- mutant.db.PersistentDuckDB - 扩展了 mutant.db.DuckDB , 实现了local文件的持久化数据(persists data).

mutant.Server

定义了用于将 mutant.API 实例暴露为远程访问的类

具体实现:
- mutant.server.FastAPI - 基于 FastAPI/ASGI 框架运行的 web 服务器，可通过 HTTP 请求进行交互。适用于一般的 RESTful API 使用场景
- mutant.server.ArrowFlight - 基于 ArrowFlight gRPC 框架运行的服务器，可通过高效的 gRPC 协议进行通信。适用于注重性能和低延迟的场景

采用这种架构的优劣 Consequences

优点：
- 易于上手： Mutant 可以直接在 Google Colab 或开发机器上运行，无需额外配置，只需使用 pip install 安装即可。
- 降低项目复杂度： 整个项目结构更加简洁易懂，维护起来更加方便。
- 扩展性强： 通过良好的类结构设计，未来可以方便地探索和对比不同的通信协议、存储机制以及计算位置。同时为构建多层架构铺平了道路，例如将部分计算或存储任务转移到远程的 SaaS 产品上。
缺点：
- 服务器端体积稍大： 虽然客户端轻量，但包含服务器端的 Mutant 安装包会稍微大一些。