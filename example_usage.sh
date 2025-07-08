#!/bin/bash

# 示例用法脚本

echo "=== 代理订阅转换工具示例 ==="
echo ""

echo "🚀 推荐使用一键脚本："
echo ""

# 示例1：一键转换（推荐）
echo "示例1：一键生成 Surge 和 Clash 配置文件"
echo "命令：./convert.sh <你的订阅链接>"
echo ""

# 示例2：仅生成 Surge 配置
echo "示例2：仅生成 Surge 配置"
echo "命令：./convert.sh <你的订阅链接> -f surge -o my_surge"
echo ""

# 示例3：仅生成 Clash 配置
echo "示例3：仅生成 Clash 配置"
echo "命令：./convert.sh <你的订阅链接> -f clash -o my_clash"
echo ""

echo "📋 一键脚本特性："
echo "  ✅ 自动检查Python环境"
echo "  ✅ 自动创建虚拟环境"
echo "  ✅ 自动安装依赖包"
echo "  ✅ 自动运行转换"
echo "  ✅ 支持 macOS/Linux/Windows"
echo ""

echo "📁 生成的文件："
echo "- config.surge.conf  # Surge 配置文件"
echo "- config.clash.yaml  # Clash 配置文件"
echo ""

echo "💡 手动运行（高级用户）："
echo "1. 创建虚拟环境：python3 -m venv venv"
echo "2. 激活环境：source venv/bin/activate"
echo "3. 安装依赖：pip install -r requirements.txt"
echo "4. 运行转换：python convert_subscription.py <订阅链接>"
echo ""

echo "🎯 使用建议："
echo "- 初次使用：直接运行一键脚本"
echo "- 批量转换：可以编写循环脚本调用一键脚本"
echo "- 定制需求：修改 convert_subscription.py 后手动运行"