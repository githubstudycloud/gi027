---
name: pg-manager
description: PostgreSQL 数据库管理助手，帮助用户连接和操作 PostgreSQL。执行 SQL 查询、管理表和视图、分析查询计划。当用户想要操作 PostgreSQL、psql 查询、PG 数据库时自动激活。
allowed-tools: Bash
---

# PostgreSQL 数据库管理助手

## 概述
帮助用户通过 Claude Code 直接操作 PostgreSQL 数据库。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`

## 核心功能

### 1. 执行 SQL 查询
**触发词**: "查询 PostgreSQL"、"PG 查询"、"psql 执行"

```bash
# 通过 Python 封装
cd D:/devtools-hub && python -c "
from python.devtools.pg_client import execute
import json
result = execute('SELECT * FROM products', env='local-wsl')
print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
"

# 通过 psql CLI
PGPASSWORD=devpg123 psql -h 127.0.0.1 -U dev -d testdb -c "SELECT * FROM products"
```

### 2. 查看表结构
**触发词**: "PG 表结构"、"PostgreSQL 表"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.pg_client import list_tables, describe_table
import json
print('Tables:', json.dumps(list_tables(env='local-wsl'), indent=2, default=str))
print('Structure:', json.dumps(describe_table('products', env='local-wsl'), indent=2, default=str))
"
```

### 3. 查询计划分析
**触发词**: "PG 查询计划"、"EXPLAIN ANALYZE"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.pg_client import execute
import json
result = execute('EXPLAIN ANALYZE SELECT * FROM products WHERE category = %s', ('electronics',), env='local-wsl')
print(json.dumps(result, indent=2, default=str))
"
```

### 4. 数据备份
**触发词**: "PostgreSQL 备份"、"pg_dump"

```bash
PGPASSWORD=devpg123 pg_dump -h 127.0.0.1 -U dev testdb > /tmp/testdb_pg_backup.sql
```

### 5. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.pg_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 使用示例
```
"查询 PostgreSQL 中 products 表的所有电子产品"
"分析这个 PG 查询的执行计划"
"查看 testdb 的所有表结构"
"备份 PostgreSQL 数据库"
```
