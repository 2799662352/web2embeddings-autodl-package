#!/bin/bash

# ChromaDB MCP Server 启动脚本
# 自动检测环境并使用合适的配置启动 MCP 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 默认配置
DEFAULT_CHROMADB_PATH="/root/autodl-tmp/artifacts/vector_stores/chroma_db"
DEFAULT_COLLECTION_NAME="danbooru_training_data_jina-embeddings-v3"
DEFAULT_MODEL_NAME="jinaai/jina-embeddings-v3"
DEFAULT_DEVICE="auto"
DEFAULT_MEMORY_COLLECTION="user_memories"

# 解析命令行参数
CHROMADB_PATH="$DEFAULT_CHROMADB_PATH"
COLLECTION_NAME="$DEFAULT_COLLECTION_NAME"
MODEL_NAME="$DEFAULT_MODEL_NAME"
DEVICE="$DEFAULT_DEVICE"
MEMORY_COLLECTION="$DEFAULT_MEMORY_COLLECTION"
CONFIG_FILE=""
VERBOSE=false

print_usage() {
    cat << EOF
使用方法: $0 [选项]

选项:
    -d, --chromadb-path PATH     ChromaDB 数据库路径 (默认: $DEFAULT_CHROMADB_PATH)
    -c, --collection-name NAME   集合名称 (默认: $DEFAULT_COLLECTION_NAME)
    -m, --model-name NAME        模型名称 (默认: $DEFAULT_MODEL_NAME)
    --device DEVICE              设备 (默认: $DEFAULT_DEVICE)
    --memory-collection NAME     内存集合名称 (默认: $DEFAULT_MEMORY_COLLECTION)
    --config FILE                配置文件路径
    -v, --verbose                详细输出
    -h, --help                   显示此帮助信息

示例:
    # 使用默认配置启动
    $0
    
    # 指定自定义路径
    $0 -d /custom/path/chroma_db -c my_collection
    
    # 使用配置文件
    $0 --config config/mcp_server_config.json
    
    # CPU 模式
    $0 --device cpu
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--chromadb-path)
            CHROMADB_PATH="$2"
            shift 2
            ;;
        -c|--collection-name)
            COLLECTION_NAME="$2"
            shift 2
            ;;
        -m|--model-name)
            MODEL_NAME="$2"
            shift 2
            ;;
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --memory-collection)
            MEMORY_COLLECTION="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            print_usage
            exit 1
            ;;
    esac
done

# 显示启动信息
log_info "启动 ChromaDB MCP Server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 环境检测
log_step "检测运行环境..."

# 检测是否在 AutoDL 环境
if [[ -d "/root/autodl-tmp" ]]; then
    log_info "检测到 AutoDL 环境"
    DETECTED_ENV="autodl"
elif [[ -f "/.dockerenv" ]]; then
    log_info "检测到 Docker 环境"
    DETECTED_ENV="docker"
else
    log_info "检测到本地开发环境"
    DETECTED_ENV="local"
fi

# 如果指定了配置文件，加载配置
if [[ -n "$CONFIG_FILE" ]]; then
    if [[ -f "$CONFIG_FILE" ]]; then
        log_info "加载配置文件: $CONFIG_FILE"
        # 这里可以添加配置文件解析逻辑
    else
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
fi

# 验证 Python 环境
log_step "验证 Python 环境..."

if ! command -v python &> /dev/null; then
    log_error "未找到 Python 解释器"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
log_info "Python 版本: $PYTHON_VERSION"

# 检查必需的包
log_step "检查必需的依赖包..."

REQUIRED_PACKAGES=("fastmcp-server" "chromadb" "sentence-transformers" "torch")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import ${package//-/_}" &> /dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    log_error "缺少以下依赖包: ${MISSING_PACKAGES[*]}"
    log_info "请运行: pip install ${MISSING_PACKAGES[*]}"
    exit 1
fi

log_info "所有依赖包已安装"

# 验证数据库路径
log_step "验证数据库配置..."

if [[ ! -d "$CHROMADB_PATH" ]]; then
    log_error "ChromaDB 路径不存在: $CHROMADB_PATH"
    log_info "请先运行主向量化程序生成数据库"
    exit 1
fi

log_info "数据库路径: $CHROMADB_PATH"

# 检查 GPU 可用性
log_step "检查硬件配置..."

if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
    if [[ -n "$GPU_INFO" ]]; then
        log_info "检测到 GPU: $GPU_INFO"
        if [[ "$DEVICE" == "auto" ]]; then
            DEVICE="cuda"
            log_info "自动选择 CUDA 设备"
        fi
    else
        log_warn "未检测到可用 GPU，使用 CPU"
        if [[ "$DEVICE" == "auto" ]]; then
            DEVICE="cpu"
        fi
    fi
else
    log_warn "未安装 nvidia-smi，假设使用 CPU"
    if [[ "$DEVICE" == "auto" ]]; then
        DEVICE="cpu"
    fi
fi

# 显示最终配置
log_step "启动配置："
echo "  数据库路径: $CHROMADB_PATH"
echo "  集合名称: $COLLECTION_NAME"
echo "  内存集合: $MEMORY_COLLECTION"
echo "  模型名称: $MODEL_NAME"
echo "  运行设备: $DEVICE"
echo "  详细模式: $VERBOSE"

# 构建启动命令
MCP_SERVER_SCRIPT="$SCRIPT_DIR/chroma_mcp_server_minimal.py"

if [[ ! -f "$MCP_SERVER_SCRIPT" ]]; then
    log_error "MCP 服务器脚本不存在: $MCP_SERVER_SCRIPT"
    exit 1
fi

LAUNCH_CMD=(
    python "$MCP_SERVER_SCRIPT"
    --chromadb-path "$CHROMADB_PATH"
    --collection-name "$COLLECTION_NAME"
    --memory-collection-name "$MEMORY_COLLECTION"
    --model-name "$MODEL_NAME"
    --device "$DEVICE"
)

# 显示启动命令
if [[ "$VERBOSE" == "true" ]]; then
    log_info "启动命令: ${LAUNCH_CMD[*]}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "启动 MCP 服务器..."
log_info "按 Ctrl+C 停止服务器"
echo ""

# 设置信号处理
cleanup() {
    log_info "正在停止 MCP 服务器..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# 启动服务器
exec "${LAUNCH_CMD[@]}"