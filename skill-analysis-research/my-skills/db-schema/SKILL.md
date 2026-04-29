---
name: db-schema
description: 数据库设计助手 - 生成符合规范的表结构和Flyway/Alembic迁移脚本。当用户说"设计表"、"建表"、"数据库设计"、"写迁移脚本"时自动激活。
argument-hint: "[实体名称 或 功能描述]"
allowed-tools: Read, Write, Glob, Grep, Bash
---

# 数据库设计助手

遵循 `D:/gi021/project-standards/database/database-standards.md` 规范，生成 PostgreSQL 建表语句和版本化迁移脚本。

## 参数说明
- `$ARGUMENTS`：要设计的实体或功能（如 "用户表"、"订单系统"）

## 工作流程

### 第一步：读取现有迁移文件

扫描项目中的迁移目录，确定下一个版本号：
- Java 项目：`src/main/resources/db/migration/V*.sql`
- Python 项目：`alembic/versions/*.py`

### 第二步：设计数据模型

根据 `$ARGUMENTS` 分析需要哪些表，遵循规范：
- 命名：`snake_case` 复数表名，单数列名
- 主键：`BIGSERIAL` 或 `UUID`
- 时间戳：`TIMESTAMPTZ`，统一 UTC
- 必含：`created_at`、`updated_at`、`deleted_at`（软删除）

如果表关系不清晰，先输出 ER 图：
```
users ||--o{ orders : "places"
orders ||--|{ order_items : "contains"
order_items }|--|| products : "refers to"
```

### 第三步：生成迁移脚本

**Java（Flyway）** → 创建 `src/main/resources/db/migration/V{N}__{描述}.sql`：

```sql
-- V{N}__{描述}.sql
-- 严格遵循规范：
-- 1. snake_case 命名
-- 2. TIMESTAMPTZ 存时间
-- 3. 外键必须建索引
-- 4. 含软删除 deleted_at
-- 5. 含乐观锁 version

CREATE TABLE {table_name} (
    id          BIGSERIAL PRIMARY KEY,
    -- 业务字段...
    deleted_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version     INTEGER NOT NULL DEFAULT 0
);

-- 索引
CREATE INDEX idx_{table}_{col} ON {table}({col});

-- updated_at 自动更新触发器
CREATE TRIGGER trg_{table}_updated_at
    BEFORE UPDATE ON {table}
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

**Python（Alembic）** → 创建 `alembic/versions/{revision}_{描述}.py`：

```python
"""{描述}

Revision ID: {revision}
Revises: {down_revision}
Create Date: {今天}
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.create_table(
        '{table_name}',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        # 业务字段...
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('version', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('idx_{table}_{col}', '{table}', ['{col}'])

def downgrade() -> None:
    op.drop_table('{table_name}')
```

### 第四步：生成 ORM 模型骨架

**Java（JPA Entity）：**
```java
@Entity
@Table(name = "{table_name}")
@Getter @Setter @NoArgsConstructor
public class {Entity} {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    // 字段...
    @Column(name = "deleted_at") private Instant deletedAt;
    @Column(name = "created_at", updatable = false) private Instant createdAt;
    @Column(name = "updated_at") private Instant updatedAt;
    @Version private Integer version;
}
```

**Python（SQLAlchemy）：**
```python
class {Model}(Base):
    __tablename__ = "{table_name}"
    id: Mapped[int] = mapped_column(primary_key=True)
    # 字段...
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), ...)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), ...)
    version: Mapped[int] = mapped_column(default=0)
```

### 第五步：输出使用说明

说明如何执行迁移：
```bash
# Java
./gradlew flywayMigrate

# Python
alembic upgrade head
```
