---
name: mysql-manager
description: MySQL 数据库管理助手，帮助用户连接和操作 MySQL。执行 SQL 查询、管理表结构、导入导出数据、查看慢查询。当用户想要查询 MySQL、执行 SQL、管理 MySQL 数据库时自动激活。
allowed-tools: Bash
---

# MySQL 数据库管理助手

## 概述
帮助用户通过 Claude Code 直接操作 MySQL 数据库，支持多环境连接管理。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`
支持多环境: local-wsl, dev, prod 等

## 核心功能

### 1. 执行 SQL 查询
**触发词**: "查询 MySQL"、"执行 SQL"、"SELECT"、"在XX数据库查询"

**使用方式**:
```bash
# 通过 Python 封装执行（推荐）
cd D:/devtools-hub && python -c "
from python.devtools.mysql_client import execute
import json
result = execute('SELECT * FROM users', env='local-wsl')
print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
"

# 通过 mysql CLI 执行
mysql -h 127.0.0.1 -u dev -pdevpass123 testdb -e "SELECT * FROM users"

# 指定环境
cd D:/devtools-hub && python -c "
from python.devtools.mysql_client import execute
result = execute('SHOW TABLES', env='dev')
print(result)
"
```

### 2. 查看表结构
**触发词**: "查看表结构"、"DESCRIBE"、"SHOW TABLES"

```bash
# 列出所有表
cd D:/devtools-hub && python -c "
from python.devtools.mysql_client import show_tables
print(show_tables(env='local-wsl'))
"

# 查看表结构
cd D:/devtools-hub && python -c "
from python.devtools.mysql_client import describe_table
import json
print(json.dumps(describe_table('users', env='local-wsl'), indent=2, default=str))
"
```

### 3. 数据导出
**触发词**: "MySQL 导出"、"mysqldump"、"备份数据库"

```bash
# 导出整个数据库
mysqldump -h 127.0.0.1 -u dev -pdevpass123 testdb > /tmp/testdb_backup.sql

# 导出指定表
mysqldump -h 127.0.0.1 -u dev -pdevpass123 testdb users > /tmp/users_backup.sql

# 导出为 CSV
mysql -h 127.0.0.1 -u dev -pdevpass123 testdb -e "SELECT * FROM users" -B > /tmp/users.tsv
```

### 4. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.mysql_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 环境切换
使用 `env` 参数指定环境:
- `local-wsl`: WSL 本地测试环境（默认）
- `dev`: 开发服务器
- 自定义: 在 connections.json 中添加

## 使用示例
```
"查询 local-wsl 的 MySQL testdb 中所有用户"
"在 dev 环境执行 SQL: SELECT COUNT(*) FROM orders WHERE status='completed'"
"查看 testdb 的所有表结构"
"导出 users 表数据"
"MySQL 慢查询分析"
```

## 安全提示
- 生产环境操作需要确认
- 不执行 DROP DATABASE 等危险操作前先确认
- 密码通过环境变量管理，不硬编码
