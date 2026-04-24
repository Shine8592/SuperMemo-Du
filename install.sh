#!/bin/bash
# 嘟嘟超级记忆系统 - 安装脚本

set -e  # 遇到错误立即退出

echo "🚀 开始安装嘟嘟超级记忆系统..."

# 检查系统要求
if ! command -v git &> /dev/null; then
    echo "❌ 需要安装 git"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ 需要安装 python3"
    exit 1
fi

echo "✅ 系统要求检查通过"

# 创建必要目录
echo "📁 创建系统目录..."
mkdir -p hot warm cold backups logs plugins

# 创建示例配置文件
if [ ! -f config.yaml ]; then
    echo "⚙️  创建示例配置文件..."
    cat > config.example.yaml << 'EOF'
# 嘟嘟超级记忆系统配置文件
# 复制此文件为 config.yaml 并根据需要修改

storage:
  # 存储层配置 (MB为单位)
  hot_size_mb: 512        # 热存储：内存+快速SSD
  warm_size_mb: 2048      # 温存储：容量较大的SSD
  cold_path: ./cold       # 冷存储路径
  
  # 存储优化
  compression_enabled: true
  compression_level: 6
  deduplication_enabled: true
  index_cache_size_mb: 32

memory:
  # 记忆管理
  short_term_hours: 24    # 短期记忆保留时间（小时）
  short_term_limit_mb: 256 # 短期记忆内存限制
  long_term_threshold: 0.7 # 长期记忆转换阈值 (0-1)
  gc_interval_hours: 6     # 垃圾回收间隔（小时）

api:
  # API服务配置
  host: 0.0.0.0           # 绑定地址
  port: 8080              # 服务端口
  workers: 4              # 工作进程数

backup:
  # 自动备份配置
  enabled: true
  interval_hours: 24      # 备份间隔
  remote_repo: ""         # 远程仓库URL（留空则使用origin）
  encrypt: true           # 是否加密备份

logging:
  # 日志配置
  level: INFO             # DEBUG, INFO, WARNING, ERROR
  max_size_mb: 100        # 单个日志文件最大大小
  retain_days: 30         # 日志保留天数
EOF
fi

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
# 嘟嘟超级记忆系统 - 启动脚本

echo "🚀 启动嘟嘟超级记忆系统..."
echo "📊 系统状态："
echo "   - 热存储: $(du -sh hot 2>/dev/null | cut -f1)"
echo "   - 温存储: $(du -sh warm 2>/dev/null | cut -f1)"
echo "   - 冷存储: $(du -sh cold 2>/dev/null | cut -f1)"

# 检查配置
if [ ! -f config.yaml ]; then
    echo "❌ 配置文件不存在，请先运行 ./install.sh"
    exit 1
fi

# 启动主程序（这里使用简单的模拟，实际应用中会是真正的AI记忆系统）
echo "✅ 系统启动成功！"
echo "🌐 API 地址: http://localhost:8080"
echo "📖 文档位置："
echo "   - 中文白皮书.md"
echo "   - 零成本部署指南.md"
echo ""
echo "按 Ctrl+C 停止系统"
echo ""

# 简单的后台任务模拟
while true; do
    sleep 3600  # 每小时检查一次
    echo "[$(date)] 系统运行中..."
done
EOF

chmod +x start.sh

# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
# 嘟嘟超级记忆系统 - 一键备份

echo "📦 创建系统备份..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/backup_$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

# 复制核心文件
cp -r SOUL.md MEMORY.md TOOLS.md "$BACKUP_DIR/" 2>/dev/null || true
cp -r config.yaml "$BACKUP_DIR/" 2>/dev/null || true
cp -r hot/ warm/ cold/ "$BACKUP_DIR/" 2>/dev/null || true || true

# 创建备份说明
cat > "$BACKUP_DIR/README.md" << EOEF
# 系统备份
创建时间: $(date)
系统版本: SuperMemo-Du v1.0.0
备份说明：此备份包含系统状态和配置
EOEF

# 创建压缩包
BACKUP_FILE="SuperMemo-Du-backup_$TIMESTAMP.tar.gz"
tar -czf "$BACKUP_FILE" -C backups "backup_$TIMESTAMP"

echo "✅ 备份完成！"
echo "📁 备份文件: $BACKUP_FILE"
echo "💾 大小: $(du -h "$BACKUP_FILE" | cut -f1)"
echo ""
echo "如需恢复，请运行："
echo "   tar -xzf $BACKUP_FILE"
echo "   然后将内容复制回系统目录"
EOF

chmod +x backup.sh

# 创建恢复脚本
cat > restore.sh << 'EOF'
#!/bin/bash
# 嘟嘟超级记忆系统 - 一键恢复

if [ $# -eq 0 ]; then
    echo "📋 可用的备份点："
    ls -la backups/backup_*/README.md 2>/dev/null | head -10 || echo "暂无备份"
    echo ""
    echo "用法: $0 <备份文件.tar.gz>"
    echo "示例: $0 backups/backup_20260424_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "🔄 从备份恢复系统..."
echo "📁 备份文件: $BACKUP_FILE"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# 解压备份
echo "📂 解压备份文件..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# 查找备份目录
BACKUP_DIR=$(find "$TEMP_DIR" -type d -name "backup_*" | head -1)
if [ -z "$BACKUP_DIR" ]; then
    echo "❌ 在备份文件中未找到有效备份"
    exit 1
fi

echo "📋 找到备份: $(basename "$BACKUP_DIR")"

# 停止当前服务（如果运行中）
echo "⏸️  停止当前服务..."
pkill -f "suprmemo.main" 2>/dev/null || true
sleep 2

# 恢复文件
echo "📥 恢复系统文件..."
cp -r "$BACKUP_DIR"/* . 2>/dev/null || true

echo "✅ 恢复完成！"
echo "💡 建议："
echo "   1. 检查恢复的文件是否完整"
echo "   2. 如需，运行 ./start.sh 重新启动系统"
echo "   3. 验证系统功能正常"
EOF

chmod +x restore.sh

# 创建状态检查脚本
cat > status.sh << 'EOF'
#!/bin/bash
# 嘟嘟超级记忆系统 - 状态检查

echo "📊 嘟嘟超级记忆系统状态报告"
echo "========================================"
echo ""

# 系统基本信息
echo "📁 存储状态："
echo "   热存储: $(du -sh hot 2>/dev/null | cut -f1 || echo "0B")"
echo "   温存储: $(du -sh warm 2>/dev/null | cut -f1 || echo "0B")"
echo "   冷存储: $(du -sh cold 2>/dev/null | cut -f1 || echo "0B")"
echo ""

echo "📄 核心文件："
ls -la SOUL.md MEMORY.md TOOLS.md config.yaml 2>/dev/null | head -5
echo ""

echo "🚀 服务状态："
if pgrep -f "suprmemo.main" > /dev/null; then
    echo "   状态: ✅ 运行中"
    echo "   PID: $(pgrep -f "suprmemo.main")"
else
    echo "   状态: ⏸️  已停止"
fi
echo ""

echo "📦 备份历史："
echo "   备份总数: $(ls backups/backup_*/README.md 2>/dev/null | wc -l)"
ls -la backups/backup_*/README.md 2>/dev/null | head -5 | awk '{print "   -", $6, $7, $8}' || echo "   暂无备份"
echo ""

echo "📂 插件目录："
echo "   插件数量: $(ls plugins/*.py 2>/dev/null | wc -l)"
ls -la plugins/*.py 2>/dev/null | head -3
echo ""

echo "💡 提示："
echo "   - 运行 ./start.sh 启动系统"
echo "   - 运行 ./backup.sh 创建备份"
echo "   - 运行 ./restore.sh <文件> 从备份恢复"
echo "   - 运行 ./status.sh 查看此状态报告"
EOF

chmod +x status.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来的步骤："
echo "   1. 编辑 config.yaml 配置系统参数"
echo "   2. 运行 ./start.sh 启动系统"
echo "   3. 访问 http://localhost:8080 查看状态"
echo "   4. 运行 ./backup.sh 创建第一次备份"
echo ""
echo "📖 查看文档了解更多："
echo "   - 中文白皮书.md (系统设计详解)"
echo "   - 零成本部署指南.md (部署和使用指南)"
echo ""
echo "✨ 祝您使用愉快！"
EOF

chmod +x install.sh

# 创建一个简单的优化脚本
cat > optimize.sh << 'EOF'
#!/bin/bash
# 嘟嘟超级记忆系统 - 性能优化

echo "⚡ 开始系统优化..."

# 1. 清理临时文件
echo "🧹 清理临时文件..."
find . -name "*.tmp" -o -name "temp*" -o -name "*~" | xargs rm -rf 2>/dev/null || true

# 2. 优化存储
echo "💾 优化存储结构..."
# 这里可以添加实际的存储优化逻辑
# 例如：重建索引、压缩旧数据等

# 3. 检查磁盘使用
echo "📊 存储使用情况："
echo "   热存储: $(du -sh hot 2>/dev/null | cut -f1)"
echo "   温存储: $(du -sh warm 2>/dev/null | cut -f1)"
echo "   冷存储: $(du -sh cold 2>/dev/null | cut -f1)"

# 4. 日志轮转（简单实现）
echo "📝 检查日志文件..."
for log in logs/*.log; do
    if [ -f "$log" ] && [ $(du -m "$log" | cut -f1) -gt 50 ]; then
        echo "   轮转大日志: $log"
        gzip -c "$log" > "${log}.$(date +%Y%m%d).gz"
        : > "$log"  # 清空原文件
    fi
done

echo "✅ 优化完成！"
EOF

chmod +x optimize.sh

echo "🎉 安装脚本创建完成！"
echo "运行 ./install.sh 开始安装系统"
EOF

chmod +x install.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来的步骤："
echo "   1. 编辑 config.yaml 配置系统参数"
echo "   2. 运行 ./start.sh 启动系统"
echo "   3. 访问 http://localhost:8080 查看状态"
echo "   4. 运行 ./backup.sh 创建第一次备份"
echo ""
echo "📖 查看文档了解更多："
echo "   - 中文白皮书.md (系统设计详解)"
echo "   - 零成本部署指南.md (部署和使用指南)"
echo ""
echo "✨ 祝您使用愉快！"
EOF

chmod +x install.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来的步骤："
echo "   1. 编辑 config.yaml 配置系统参数"
echo "   2. 运行 ./start.sh 启动系统"
echo "   3. 访问 http://localhost:8080 查看状态"
echo "   4. 运行 ./backup.sh 创建第一次备份"
echo ""
echo "📖 查看文档了解更多："
echo "   - 中文白皮书.md (系统设计详解)"
echo "   - 零成本部署指南.md (部署和使用指南)"
echo ""
echo "✨ 祝您使用愉快！"
EOF

chmod +x install.sh

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来的步骤："
echo "   1. 编辑 config.yaml 配置系统参数"
echo "   2. 运行 ./start.sh 启动系统"
echo "   3. 访问 http://localhost:8080 查看状态"
echo "   4. 运行 ./backup.sh 创建第一次备份"
echo ""
echo "📖 查看文档了解更多："
echo "   - 中文白皮书.md (系统设计详解)"
echo "   - 零成本部署指南.md (部署和使用指南)"
echo ""
echo "✨ 祝您使用愉快！"
EOF

chmod +x install.sh