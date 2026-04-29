---
name: redis-manager
description: Redis 缓存管理助手，帮助用户连接 Redis 执行操作。查看键值、设置缓存、监控内存、管理数据结构。当用户想要操作 Redis、查看缓存、设置键值、Redis 监控时自动激活。
allowed-tools: Bash
---

# Redis 缓存管理助手

## 概述
帮助用户通过 Claude Code 操作 Redis 缓存服务。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`

## 核心功能

### 1. 键值操作
**触发词**: "查看缓存"、"设置键值"、"Redis GET/SET"

```bash
# GET
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import get
print(get('greeting', env='local-wsl'))
"

# SET
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import set
set('mykey', 'myvalue', ttl=3600, env='local-wsl')
print('OK')
"

# 通过 redis-cli（WSL）
wsl redis-cli -h 127.0.0.1 -a devredis123 GET greeting
```

### 2. 搜索键
**触发词**: "Redis 搜索"、"查找键"、"KEYS 模式"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import keys
print(keys('user:*', env='local-wsl'))
"
```

### 3. 服务器信息与监控
**触发词**: "Redis 状态"、"Redis 监控"、"Redis INFO"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import info
result = info('memory', env='local-wsl')
print(result)
"

# 或通过 CLI
wsl redis-cli -h 127.0.0.1 -a devredis123 INFO memory
wsl redis-cli -h 127.0.0.1 -a devredis123 INFO stats
```

### 4. 删除键
**触发词**: "Redis 删除"、"清除缓存"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import delete
print(delete('mykey', env='local-wsl'))
"
```

### 5. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.redis_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 数据结构操作

### Hash
```bash
wsl redis-cli -h 127.0.0.1 -a devredis123 HGETALL user:1
```

### List
```bash
wsl redis-cli -h 127.0.0.1 -a devredis123 LRANGE recent:logs 0 -1
```

### Set / Sorted Set
```bash
wsl redis-cli -h 127.0.0.1 -a devredis123 SMEMBERS myset
wsl redis-cli -h 127.0.0.1 -a devredis123 ZRANGE myzset 0 -1 WITHSCORES
```

## 使用示例
```
"查看 Redis 中 user:1 的数据"
"设置缓存 session:abc 值为 {...} TTL 1小时"
"搜索所有匹配 user:* 的键"
"查看 Redis 内存使用情况"
"清除所有 session:* 缓存"
```
