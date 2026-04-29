---
name: kafka-manager
description: Kafka 消息队列管理助手，帮助用户管理 Topic、生产消费消息、监控消费组和偏移量。当用户想要操作 Kafka、发送消息、查看 Topic、管理消费组时自动激活。
allowed-tools: Bash
---

# Kafka 消息队列管理助手

## 概述
帮助用户通过 Claude Code 管理 Kafka 消息队列。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`
Kafka 通过 Docker 运行在 WSL 中。

## 核心功能

### 1. Topic 管理
**触发词**: "查看 Topic"、"创建 Topic"、"Kafka Topic"

```bash
# 列出所有 topic
cd D:/devtools-hub && python -c "
from python.devtools.kafka_client import list_topics
print(list_topics(env='local-wsl'))
"

# 通过 Docker CLI
wsl sudo docker exec devtools-kafka kafka-topics --list --bootstrap-server localhost:9092

# 创建 topic
cd D:/devtools-hub && python -c "
from python.devtools.kafka_client import create_topic
print(create_topic('my-events', partitions=3, env='local-wsl'))
"

# Topic 详情
wsl sudo docker exec devtools-kafka kafka-topics --describe --topic test-events --bootstrap-server localhost:9092
```

### 2. 发送消息
**触发词**: "发送消息到 Topic"、"Kafka 生产"、"produce"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.kafka_client import send_message
import json
result = send_message('test-events', {'action': 'test', 'data': 'hello'}, key='test-1', env='local-wsl')
print(json.dumps(result, default=str))
"
```

### 3. 消费消息
**触发词**: "消费消息"、"Kafka 消费"、"consume"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.kafka_client import consume_messages
import json
msgs = consume_messages('test-events', max_messages=5, env='local-wsl', from_beginning=True)
print(json.dumps(msgs, indent=2, default=str))
"

# 通过 Docker CLI 消费
wsl sudo docker exec devtools-kafka kafka-console-consumer --topic test-events --bootstrap-server localhost:9092 --from-beginning --max-messages 5
```

### 4. 消费组管理
**触发词**: "消费组状态"、"Kafka lag"、"消费组"

```bash
# 查看消费组
wsl sudo docker exec devtools-kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# 消费组详情（含 lag）
wsl sudo docker exec devtools-kafka kafka-consumer-groups --describe --group devtools-group --bootstrap-server localhost:9092
```

### 5. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.kafka_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 使用示例
```
"列出所有 Kafka Topic"
"创建一个名为 user-events 的 Topic，3 个分区"
"发送一条测试消息到 test-events"
"消费 test-events 的最新 10 条消息"
"查看消费组 devtools-group 的 lag"
```
