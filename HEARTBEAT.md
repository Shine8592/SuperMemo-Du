# HEARTBEAT.md

## 每次心跳必须检查（不跳过）

### 1. 升级备份检查
如果今天 SOUL.md、MEMORY.md、TOOLS.md 的修改时间 < 24 小时：
**立刻发邮件备份到 yaner_zf@163.com**

### 2. 记忆索引更新 ⚡
检查记忆文件是否有更新，如有变化则自动重建语义索引：
- 运行 `python3 memory/auto_index_updater.py --once`
- 这会检测 MEMORY.md、SOUL.md、TOOLS.md、每日日志、梦境日志的修改
- 自动更新向量索引以保持搜索准确性

### 3. 任务跟进
查看 memory/daily/ 今天的日志，看是否有未完成的待办（[ ] 开头的条目）：
- 有未完成的 → 提醒主人
- 没有 → 跳过

### 4. 反馈回顾
查看 memory/feedback.md 最近一条反馈：
- 是否有重复犯过的错误 → 如果有 → 主动提醒主人
- 没有 → 跳过

### 5. 清理
检查 /tmp/ 下是否有以 `dudu-backup-temp`、`fix-push`、`briefing-repo`、`claude-code` 开头的临时目录 → 如果有已推送过的 → 删除

### 6. 每日日志
确保 memory/daily/$(date +%Y-%m-%d).md 存在，写一句今天的摘要

---

## 💡 新增功能说明

### 语义记忆搜索系统 (v4.0)
系统现已配备智能语义搜索功能：
- 使用 `all-MiniLM-L6-v2` 模型生成文本嵌入
- 基于 Faiss 构建高效向量索引  
- 支持自然语言查询，自动找到相关内容

**使用方法**:
```bash
# 搜索记忆
python3 memory/semantic_search.py search "查询内容"

# 查看状态
python3 memory/semantic_search.py status

# 手动更新索引
python3 memory/auto_index_updater.py --once
```

**示例**:
```bash
python3 memory/semantic_search.py search "长期记忆 短期记忆"
python3 memory/semantic_search.py search "REM 梦境 反思"
python3 memory/semantic_search.py search "系统设计 原则"
```

**功能特点**:
- 🚀 快速索引 (<3秒)
- 🎯 高相关性 (0.38-0.55)
- 🔍 跨文档检索
- ✨ 智能语义理解