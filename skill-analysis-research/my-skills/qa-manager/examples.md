# Q&A Manager 使用示例

## 基础示例

### 示例 1: 保存一个简单的问答

**用户输入：**
```
保存这个问答：
问题：如何在 Python 中读取 JSON 文件？
答案：使用 json.load() 方法读取文件内容并解析为 Python 对象。

import json
with open('data.json', 'r') as f:
    data = json.load(f)
```

**系统操作：**
1. 创建问题实体 "Python-JSON文件读取"
2. 保存完整内容到观察记录
3. 自动提取标签：#Python #JSON #文件操作
4. 标记状态为 "verified"
5. 记录时间戳

**确认消息：**
```
✓ 问答已保存！
  标题: Python-JSON文件读取
  标签: #Python #JSON #文件操作
  状态: verified

  你可以稍后通过搜索 "JSON" 或 "Python 文件" 来找到这个问答。
```

---

### 示例 2: 搜索历史问答

**用户输入：**
```
搜索关于 React 性能优化的问答
```

**系统输出：**
```
找到 3 个相关问答：

1. 📌 React-列表渲染性能优化
   标签: #React #性能 #列表
   日期: 2025-12-15
   摘要: 使用 React.memo 和虚拟滚动优化大列表...

2. 📌 React-useMemo使用场景
   标签: #React #Hooks #性能
   日期: 2025-12-18
   摘要: useMemo 用于缓存计算结果，避免重复计算...

3. 📌 React-性能分析工具
   标签: #React #性能 #DevTools
   日期: 2025-12-20
   摘要: 使用 React DevTools Profiler 分析组件渲染...

需要查看完整答案吗？（输入序号如 "查看 1"）
```

---

### 示例 3: 查看完整问答

**用户输入：**
```
显示 React 列表渲染的完整问答
```

**系统输出：**
```
# React-列表渲染性能优化

## 问题
在 React 应用中，当渲染包含数千条数据的列表时，滚动性能很差。如何优化？

## 答案

### 方法 1: 使用 React.memo
对列表项组件进行记忆化，避免不必要的重新渲染。

```jsx
const ListItem = React.memo(({ item }) => {
  return <div>{item.name}</div>;
});
```

### 方法 2: 虚拟滚动
使用 react-window 或 react-virtualized 只渲染可见区域。

```jsx
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={35}
>
  {Row}
</FixedSizeList>
```

### 方法 3: 正确使用 key
确保使用稳定的唯一 key，避免使用数组索引。

```jsx
{items.map(item => (
  <ListItem key={item.id} item={item} />
))}
```

## 元数据
- **标签**: #React #性能 #列表渲染 #虚拟滚动
- **日期**: 2025-12-15
- **状态**: verified
- **相关问答**:
  - React-useMemo使用场景
  - React-性能分析工具

## 后续问题
- 何时应该使用 useCallback？
- 如何测量组件渲染性能？

---
想要更新这个答案？输入 "更新这个问答"
```

---

### 示例 4: 更新问答

**用户输入：**
```
更新 React 列表渲染的问答，添加关于 key 的最佳实践
```

**系统操作：**
1. 定位 "React-列表渲染性能优化" 实体
2. 添加新的观察记录：
   ```
   update_2025-12-21: 补充 key 属性最佳实践
   - 避免使用数组索引作为 key
   - 确保 key 在兄弟元素中唯一
   - key 应该稳定、可预测
   - 示例代码...
   ```
3. 更新时间戳

**确认消息：**
```
✓ 问答已更新！
  添加了关于 key 属性的最佳实践
  更新时间: 2025-12-21

  历史版本已保留，你可以查看完整的更新历史。
```

---

### 示例 5: 组织和分类

**用户输入：**
```
显示我的问答统计
```

**系统输出：**
```
📊 Q&A 知识库统计

总计: 48 个问答

按分类分布:
  🎨 前端开发: 20 (42%)
    - React: 12
    - Vue: 5
    - CSS: 3

  🔧 后端开发: 15 (31%)
    - Python: 8
    - Node.js: 4
    - 数据库: 3

  🚀 DevOps: 8 (17%)
    - Docker: 5
    - CI/CD: 3

  🐛 故障排查: 5 (10%)

最近添加 (7天内): 6 个问答

热门标签:
  #React (12) #Python (8) #性能优化 (7)
  #API (6) #Docker (5) #错误处理 (5)

状态分布:
  ✓ verified: 35
  📝 draft: 10
  ⚠️ outdated: 3
```

---

## 高级示例

### 示例 6: 批量操作

**用户输入：**
```
将所有标记为 "outdated" 的问答列出来，我要更新它们
```

**系统输出：**
```
找到 3 个过时的问答：

1. ⚠️ JavaScript-Promise使用方法
   日期: 2024-08-15
   原因: ES2022 已有更好的 async/await 模式

2. ⚠️ React-类组件生命周期
   日期: 2024-09-20
   原因: 现在主要使用函数组件和 Hooks

3. ⚠️ Webpack配置优化
   日期: 2024-10-10
   原因: Vite 已成为主流

建议操作：
- 更新现有答案（推荐）
- 删除并创建新问答
- 标记为 deprecated 保留历史
```

---

### 示例 7: 智能关联

**用户输入：**
```
我正在学习 React Hooks，有相关的问答吗？
```

**系统输出：**
```
根据你的学习需求，找到以下相关问答：

📚 基础知识:
1. React-Hooks基本概念 (#基础 #Hooks)
2. useState使用详解 (#Hooks #状态管理)
3. useEffect完整指南 (#Hooks #副作用)

⚡ 性能优化:
4. useMemo使用场景 (#性能 #Hooks)
5. useCallback避免重渲染 (#性能 #Hooks)

🔧 高级用法:
6. 自定义Hooks开发 (#高级 #Hooks)
7. useReducer复杂状态管理 (#状态管理 #Hooks)

💡 建议学习路径:
  基础(1-3) → 性能(4-5) → 高级(6-7)

需要查看具体哪个问答？
```

---

### 示例 8: 导出备份

**用户输入：**
```
将前端开发相关的问答导出为 markdown 文件
```

**系统操作：**
1. 搜索所有前端相关问答
2. 按分类组织
3. 生成 markdown 文件

**生成文件：** `qa-export-frontend-2025-12-21.md`

```markdown
# 前端开发 Q&A 集合
导出时间: 2025-12-21
总计: 20 个问答

## React (12 个)

### Q1: React-列表渲染性能优化
**标签:** #React #性能
**日期:** 2025-12-15

#### 问题
在 React 应用中，当渲染包含数千条数据的列表时，滚动性能很差。如何优化？

#### 答案
[完整答案内容...]

---

### Q2: React-useMemo使用场景
...

## Vue (5 个)
...

## CSS (3 个)
...
```

---

### 示例 9: 复杂搜索

**用户输入：**
```
找一下所有关于性能优化的问答，但排除 CSS 相关的
```

**系统输出：**
```
🔍 搜索: #性能优化 -#CSS

找到 12 个问答：

按技术栈分组:

📱 React (5):
1. React-列表渲染性能优化
2. React-代码分割与懒加载
3. React-状态更新优化
...

🐍 Python (4):
1. Python-大文件处理优化
2. Python-数据库查询性能
...

🐳 Docker (3):
1. Docker-镜像体积优化
2. Docker-构建缓存策略
...
```

---

### 示例 10: 交互式更新

**用户输入：**
```
帮我改进 "Python-JSON文件读取" 这个问答，添加错误处理和性能建议
```

**系统响应：**
```
找到问答: Python-JSON文件读取

当前答案:
使用 json.load() 方法读取文件内容并解析为 Python 对象。

我建议添加以下改进:

1. ✅ 错误处理
   - 文件不存在
   - JSON 格式错误
   - 编码问题

2. ✅ 性能优化
   - 大文件流式读取
   - 使用 orjson 加速解析

3. ✅ 最佳实践
   - 使用上下文管理器
   - 指定编码格式

是否应用这些改进？[是/否/让我选择]
```

**用户选择：** 是

**系统生成更新后的答案：**
```
更新后的答案:

### 基础用法
```python
import json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### 完整的错误处理
```python
import json
from pathlib import Path

def read_json_safe(filepath):
    try:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        print(f"JSON 格式错误: {e}")
        return None
    except UnicodeDecodeError:
        # 尝试其他编码
        with open(path, 'r', encoding='gbk') as f:
            return json.load(f)
```

### 大文件优化
```python
import ijson  # 流式解析

def read_large_json(filepath):
    with open(filepath, 'rb') as f:
        # 逐项解析，不占用大量内存
        for item in ijson.items(f, 'item'):
            yield item
```

### 性能对比
```python
import orjson  # 更快的 JSON 库

# 标准库: ~1.2s 处理 100MB
with open('large.json', 'r') as f:
    data = json.load(f)

# orjson: ~0.3s 处理 100MB
with open('large.json', 'rb') as f:
    data = orjson.loads(f.read())
```

✓ 答案已更新！
  新增: 错误处理、性能优化建议
  更新时间: 2025-12-21
```

---

## 实际工作流示例

### 场景: 调试一个 Bug

```
用户: "遇到一个 CORS 错误，怎么解决？"

Claude: [提供解决方案]

用户: "这个方案很有用，保存下来"

[qa-manager 自动激活]
系统:
  ✓ 问答已保存: CORS错误解决方案
  标签: #CORS #API #错误处理

  我注意到你之前也保存过相关问答:
  - API跨域问题排查 (2025-12-10)

  是否关联这两个问答？[是/否]

用户: "是"

系统:
  ✓ 已创建关联
  你现在有一个 "跨域问题" 主题群组，包含 2 个问答
```

---

### 场景: 准备技术面试

```
用户: "列出所有关于算法和数据结构的问答，按难度排序"

系统:
📚 算法与数据结构 Q&A (18 个)

🟢 基础 (7):
1. 数组与链表的区别
2. 二分查找实现
3. 栈和队列应用场景
...

🟡 中等 (8):
1. 动态规划入门
2. 二叉树遍历方法
3. 哈希表冲突解决
...

🔴 高级 (3):
1. 红黑树实现原理
2. 图算法-最短路径
3. 贪心算法证明

💡 复习建议:
  - 今天: 复习基础 1-3
  - 明天: 练习中等难度 1-4
  - 后天: 挑战高级题目

需要生成复习计划吗？
```

---

## 提示与技巧

### 💡 快速保存技巧
```
# 简短格式（推荐日常使用）
"保存：如何使用 Git rebase？答：用于重写提交历史..."

# 对话式（自然交流）
"刚才关于 Docker 的答案很有用，帮我记下来"

# 指定分类
"保存到 DevOps 分类：Kubernetes 部署策略..."
```

### 💡 搜索技巧
```
# 精确搜索
"查找标题包含 'React' 的问答"

# 模糊搜索
"找一下之前问过的关于优化的东西"

# 组合搜索
"搜索 React 或 Vue 相关的性能优化问答"

# 时间筛选
"显示最近一周添加的问答"
```

### 💡 组织技巧
```
# 创建主题集合
"将所有关于认证的问答归类到'安全'主题"

# 建立学习路径
"基于我保存的 Python 问答，创建一个学习路径"

# 标记重要程度
"将常用的问答标记为'高频使用'"
```

---

## 常见问题解决方案

**Q: 保存了重复的问答怎么办？**
```
用户: "合并这两个关于 Redux 的问答"

系统:
  找到重复问答:
  1. Redux基础概念 (2025-12-10)
  2. Redux入门教程 (2025-12-18)

  合并策略:
  ✓ 保留最新答案作为主要内容
  ✓ 将旧答案归入历史记录
  ✓ 合并所有标签和参考链接
  ✓ 保留两个创建时间

  合并完成！新标题建议: Redux完整指南
```

**Q: 如何批量导入现有笔记？**
```
用户: "将 notes/coding-tips.md 中的内容导入为问答"

系统:
  解析文件中发现 15 个 Q&A 段落

  预览前 3 个:
  1. Git 分支管理策略 (#Git #版本控制)
  2. SQL 优化技巧 (#数据库 #性能)
  3. CSS Flexbox 布局 (#CSS #布局)

  导入选项:
  [ ] 全部导入 (15 个)
  [ ] 选择性导入
  [✓] 预览并确认每个

  开始导入？
```

**Q: 如何导出给团队？**
```
用户: "导出所有项目相关的问答为 Wiki 格式"

系统:
  正在生成团队 Wiki...

  ✓ 创建索引页面
  ✓ 按模块分类 (前端/后端/DevOps)
  ✓ 生成侧边栏导航
  ✓ 添加搜索索引

  已生成:
  - wiki/index.md (索引)
  - wiki/frontend/...
  - wiki/backend/...
  - wiki/search-index.json

  可直接发布到 GitHub Wiki 或 GitBook
```
