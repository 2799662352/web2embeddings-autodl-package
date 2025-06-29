#!/bin/bash
# Web2Embeddings AutoDL 快速开始脚本
# 这个脚本将引导您完成整个设置和运行过程

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查CUDA
check_cuda() {
    print_info "检查 CUDA 环境..."
    if command -v nvidia-smi &> /dev/null; then
        print_success "CUDA 环境检测成功"
        nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits | head -1
    else
        print_warning "未检测到 CUDA，将使用 CPU 模式"
        return 1
    fi
}

# 检查Python环境
check_python() {
    print_info "检查 Python 环境..."
    python_version=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python 版本: $python_version"
    
    if python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Python 版本满足要求 (>=3.8)"
    else
        print_error "Python 版本过低，需要 3.8 或更高版本"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装 Python 依赖包..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    print_success "依赖安装完成"
}

# 检查数据文件
check_data() {
    local data_file="data/danbooru_training_data.jsonl"
    
    if [[ -f "$data_file" ]]; then
        local line_count=$(wc -l < "$data_file")
        print_success "发现训练数据: $line_count 行"
        
        # 显示前几行作为示例
        print_info "数据示例:"
        head -3 "$data_file" | cat -n
        return 0
    else
        print_warning "未找到训练数据文件: $data_file"
        print_info "是否要生成示例数据? (y/n)"
        read -r response
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            generate_sample_data
        else
            print_error "请将您的 JSONL 格式数据放置到 $data_file"
            exit 1
        fi
    fi
}

# 生成示例数据
generate_sample_data() {
    print_info "生成示例训练数据..."
    
    print_info "请选择生成的文档数量:"
    echo "1) 小规模测试 (100 文档)"
    echo "2) 中等规模 (1000 文档) - 推荐"
    echo "3) 大规模测试 (5000 文档)"
    echo "4) 自定义数量"
    read -p "请输入选项 (1-4): " choice
    
    case $choice in
        1) num_docs=100 ;;
        2) num_docs=1000 ;;
        3) num_docs=5000 ;;
        4) 
            read -p "请输入文档数量: " num_docs
            if ! [[ "$num_docs" =~ ^[0-9]+$ ]]; then
                print_error "无效输入，使用默认值 1000"
                num_docs=1000
            fi
            ;;
        *) 
            print_warning "无效选择，使用默认值 1000"
            num_docs=1000
            ;;
    esac
    
    python examples/sample_data_generator.py --num-docs $num_docs --validate
    print_success "示例数据生成完成"
}

# 配置优化建议
optimize_config() {
    print_info "根据您的硬件配置优化设置..."
    
    # 检测GPU内存
    if command -v nvidia-smi &> /dev/null; then
        gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        print_info "检测到 GPU 内存: ${gpu_memory}MB"
        
        # 根据GPU内存推荐配置
        if (( gpu_memory >= 20000 )); then
            config_template="examples/config_templates/large_dataset_config.json"
            print_success "推荐使用大数据集配置 (batch_size=64)"
        elif (( gpu_memory >= 8000 )); then
            config_template="config/training_config.json"
            print_success "使用默认配置 (batch_size=32)"
        else
            config_template="examples/config_templates/small_dataset_config.json"
            print_success "推荐使用小数据集配置 (batch_size=16)"
        fi
    else
        config_template="examples/config_templates/cpu_config.json"
        print_success "使用 CPU 配置"
    fi
    
    # 询问是否要使用推荐配置
    print_info "是否使用推荐的配置? (y/n)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        if [[ "$config_template" != "config/training_config.json" ]]; then
            cp "$config_template" config/training_config.json
            print_success "配置文件已更新"
        fi
    fi
}

# 运行向量化
run_vectorization() {
    print_info "开始运行向量化进程..."
    print_info "这可能需要几分钟到几小时，具体取决于数据量和硬件配置"
    
    # 显示当前配置
    print_info "当前配置:"
    cat config/training_config.json | jq .
    
    print_info "按 Enter 继续，或 Ctrl+C 取消..."
    read -r
    
    # 运行向量化
    python main.py
    
    if [[ $? -eq 0 ]]; then
        print_success "向量化完成！"
        
        # 显示输出统计
        if [[ -f "artifacts/vector_stores/collections.txt" ]]; then
            print_info "生成的集合:"
            cat artifacts/vector_stores/collections.txt
        fi
        
        # 询问是否要生成可视化
        print_info "是否要生成 3D 可视化? (y/n)"
        read -r response
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            run_visualization
        fi
    else
        print_error "向量化过程中出现错误"
        exit 1
    fi
}

# 运行可视化
run_visualization() {
    print_info "生成 3D/2D 可视化..."
    python src/visualizer.py
    
    if [[ $? -eq 0 ]]; then
        print_success "可视化生成完成！"
        print_info "可视化文件位置: artifacts/visualizations/"
        ls -la artifacts/visualizations/
    else
        print_error "可视化生成失败"
    fi
}

# 主函数
main() {
    echo "================================================"
    echo "🚀 Web2Embeddings AutoDL 快速开始脚本"
    echo "================================================"
    echo
    
    # 检查基本环境
    check_python
    check_cuda
    echo
    
    # 安装依赖
    print_info "是否要安装/更新依赖包? (y/n)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        install_dependencies
    fi
    echo
    
    # 检查数据
    check_data
    echo
    
    # 优化配置
    optimize_config
    echo
    
    # 运行向量化
    run_vectorization
    
    echo
    echo "================================================"
    echo "🎉 所有任务完成！"
    echo "================================================"
    echo
    print_success "向量数据库位置: $(pwd)/artifacts/vector_stores/chroma_db/"
    if [[ -d "artifacts/visualizations" ]]; then
        print_success "可视化文件位置: $(pwd)/artifacts/visualizations/"
    fi
    echo
    print_info "您现在可以使用生成的向量数据库进行语义搜索和 RAG 应用了！"
}

# 错误处理
trap 'print_error "脚本执行中断"; exit 1' INT

# 运行主函数
main "$@"