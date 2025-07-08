#!/bin/bash

# Proxy Subscription Converter - 一键运行脚本
# 自动创建虚拟环境、安装依赖、运行转换

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python是否安装
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python 未安装，请先安装 Python 3.6 或更高版本"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "检测到 Python 版本: $PYTHON_VERSION"
    
    # 获取主版本号和次版本号
    MAJOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    MINOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    
    # 检查是否支持的版本 (>= 3.6)
    if [[ $MAJOR_VERSION -gt 3 ]] || [[ $MAJOR_VERSION -eq 3 && $MINOR_VERSION -ge 6 ]]; then
        log_success "Python 版本满足要求"
    else
        log_error "Python 版本过低，需要 3.6 或更高版本"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        $PYTHON_CMD -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在，跳过创建"
    fi
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # macOS/Linux
        source venv/bin/activate
    fi
    log_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    log_info "检查并安装依赖包..."
    
    # 升级pip
    pip install --upgrade pip --quiet
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --quiet
        log_success "依赖包安装完成"
    else
        log_warning "requirements.txt 文件不存在，手动安装依赖..."
        pip install requests PyYAML --quiet
        log_success "依赖包安装完成"
    fi
}

# 显示帮助信息
show_help() {
    echo ""
    echo "代理订阅转换工具 - 一键运行脚本"
    echo ""
    echo "用法:"
    echo "  $0 <订阅链接> [选项]"
    echo ""
    echo "参数:"
    echo "  订阅链接        必需，代理订阅链接地址"
    echo ""
    echo "选项:"
    echo "  -o, --output    输出文件前缀 (默认: config)"
    echo "  -f, --format    输出格式 surge/clash/both (默认: both)"
    echo "  -h, --help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 https://example.com/subscription"
    echo "  $0 https://example.com/subscription -o my_config"
    echo "  $0 https://example.com/subscription -f surge"
    echo ""
}

# 验证订阅链接
validate_url() {
    local url="$1"
    if [[ ! "$url" =~ ^https?:// ]]; then
        log_error "订阅链接格式不正确，必须以 http:// 或 https:// 开头"
        return 1
    fi
    return 0
}

# 运行转换
run_conversion() {
    local subscription_url="$1"
    local output_prefix="$2"
    local format="$3"
    
    log_info "开始转换订阅链接..."
    log_info "订阅地址: $subscription_url"
    log_info "输出前缀: $output_prefix"
    log_info "输出格式: $format"
    echo ""
    
    # 运行转换脚本
    python convert_subscription.py "$subscription_url" -o "$output_prefix" -f "$format"
    
    if [ $? -eq 0 ]; then
        echo ""
        log_success "转换完成！"
        echo ""
        log_info "生成的文件:"
        
        if [[ "$format" == "surge" || "$format" == "both" ]]; then
            if [ -f "${output_prefix}.surge.conf" ]; then
                echo "  📱 Surge 配置: ${output_prefix}.surge.conf"
            fi
        fi
        
        if [[ "$format" == "clash" || "$format" == "both" ]]; then
            if [ -f "${output_prefix}.clash.yaml" ]; then
                echo "  ⚡ Clash 配置: ${output_prefix}.clash.yaml"
            fi
        fi
        
        echo ""
        log_info "配置特性:"
        echo "  ✅ 支持 VMess、Shadowsocks、Trojan 协议"
        echo "  ✅ 智能分组 (AI、流媒体、游戏等)"
        echo "  ✅ 广告拦截和应用净化"
        echo "  ✅ 自动规则更新"
        echo "  ✅ 每个分组可选择所有节点"
        echo ""
        log_success "请将生成的配置文件导入到对应的客户端中使用"
        
    else
        log_error "转换失败，请检查订阅链接是否正确"
        exit 1
    fi
}

# 清理环境
cleanup() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        deactivate 2>/dev/null || true
    fi
}

# 主函数
main() {
    # 设置清理函数
    trap cleanup EXIT
    
    # 解析命令行参数
    SUBSCRIPTION_URL=""
    OUTPUT_PREFIX="config"
    FORMAT="both"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -o|--output)
                OUTPUT_PREFIX="$2"
                shift 2
                ;;
            -f|--format)
                FORMAT="$2"
                if [[ ! "$FORMAT" =~ ^(surge|clash|both)$ ]]; then
                    log_error "格式参数只能是 surge、clash 或 both"
                    exit 1
                fi
                shift 2
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                if [ -z "$SUBSCRIPTION_URL" ]; then
                    SUBSCRIPTION_URL="$1"
                else
                    log_error "多余的参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$SUBSCRIPTION_URL" ]; then
        log_error "缺少订阅链接参数"
        show_help
        exit 1
    fi
    
    # 验证订阅链接
    if ! validate_url "$SUBSCRIPTION_URL"; then
        exit 1
    fi
    
    # 显示欢迎信息
    echo ""
    echo "=========================================="
    echo "🚀 代理订阅转换工具 v1.0"
    echo "=========================================="
    echo ""
    
    # 检查转换脚本是否存在
    if [ ! -f "convert_subscription.py" ]; then
        log_error "转换脚本 convert_subscription.py 不存在"
        log_info "请确保在正确的目录中运行此脚本"
        exit 1
    fi
    
    # 执行步骤
    check_python
    create_venv
    activate_venv
    install_dependencies
    run_conversion "$SUBSCRIPTION_URL" "$OUTPUT_PREFIX" "$FORMAT"
    
    echo ""
    log_success "🎉 所有操作完成！"
}

# 运行主函数
main "$@"