---
name: mongo-manager
description: MongoDB 管理助手，帮助用户连接和操作 MongoDB。执行查询、管理集合、聚合分析、索引管理。当用户想要查询 MongoDB、操作集合、Mongo 聚合数据时自动激活。
allowed-tools: Bash
---

# MongoDB 管理助手

## 概述
帮助用户通过 Claude Code 操作 MongoDB 文档数据库。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`
MongoDB 通过 Docker 运行在 WSL 中。

## 核心功能

### 1. 查询文档
**触发词**: "查询 MongoDB"、"Mongo find"、"查看集合"

```bash
# 列出数据库
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import list_databases
print(list_databases(env='local-wsl'))
"

# 列出集合
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import list_collections
print(list_collections('testdb', env='local-wsl'))
"

# 查询文档
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import find
import json
result = find('users', {}, database='testdb', env='local-wsl')
print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
"

# 条件查询
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import find
import json
result = find('users', {'name': 'Alice'}, database='testdb', env='local-wsl')
print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
"
```

### 2. 插入文档
**触发词**: "Mongo 插入"、"添加文档"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import insert
result = insert('users', {'name': 'Dave', 'email': 'dave@test.com'}, database='testdb', env='local-wsl')
print(result)
"
```

### 3. 通过 mongosh 操作
```bash
# 需要先安装 mongosh: winget install MongoDB.Shell
mongosh "mongodb://dev:devmongo123@127.0.0.1:27017/admin"

# 或通过 Docker
wsl sudo docker exec -it devtools-mongo mongosh -u dev -p devmongo123 --authenticationDatabase admin
```

### 4. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.mongo_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 使用示例
```
"查询 MongoDB testdb 中 users 集合的所有文档"
"在 MongoDB 中插入一条新用户记录"
"列出所有 MongoDB 数据库"
"Mongo 聚合: 按 category 统计 products 数量"
```
