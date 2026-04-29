---
name: ftp-manager
description: FTP/SFTP 文件传输管理助手，帮助用户上传下载文件、浏览远程目录、同步文件。当用户想要 FTP 上传、SFTP 下载、浏览远程服务器文件时自动激活。
allowed-tools: Bash
---

# FTP/SFTP 文件传输管理助手

## 概述
帮助用户通过 Claude Code 进行 FTP/SFTP 文件传输操作。

## 连接配置
配置文件: `D:/devtools-hub/connections.json`

## 核心功能

### 1. 浏览远程目录
**触发词**: "浏览远程目录"、"FTP 列表"、"远程文件"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.ftp_client import list_dir
for item in list_dir('/', env='local-wsl'):
    print(item)
"

# 或通过 curl
curl ftp://ftpdev:devftp123@127.0.0.1/
```

### 2. 下载文件
**触发词**: "FTP 下载"、"下载文件"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.ftp_client import download
print(download('files/welcome.txt', '/tmp/welcome.txt', env='local-wsl'))
"

# 读取远程文件内容
cd D:/devtools-hub && python -c "
from python.devtools.ftp_client import read_text
print(read_text('files/welcome.txt', env='local-wsl'))
"
```

### 3. 上传文件
**触发词**: "FTP 上传"、"上传文件"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.ftp_client import upload
print(upload('/tmp/myfile.txt', 'files/myfile.txt', env='local-wsl'))
"
```

### 4. SFTP 操作（通过 SSH）
**触发词**: "SFTP 传输"、"SFTP 下载"

```bash
cd D:/devtools-hub && python -c "
from python.devtools.ssh_client import sftp_client
sftp, client = sftp_client(env='local-wsl')
print(sftp.listdir('/home'))
client.close()
"
```

### 5. 测试连接
```bash
cd D:/devtools-hub && python -c "
from python.devtools.ftp_client import test_connection
print(test_connection(env='local-wsl'))
"
```

## 使用示例
```
"浏览 FTP 服务器的根目录"
"从 FTP 下载 welcome.txt 文件"
"上传本地文件到 FTP 服务器"
"通过 SFTP 传输文件到服务器"
"查看远程 FTP 文件的内容"
```
