#!/bin/bash

# Anole 项目 Conda 环境安装脚本
# 使用方法: bash setup_conda_env.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Anole 项目 Conda 环境安装脚本"
echo "=========================================="

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda，请先安装 conda 或 miniconda"
    exit 1
fi

echo "✓ Conda 已安装"

# 环境名称
ENV_NAME="anole"
ENV_FILE="environment.yml"

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 未找到 $ENV_FILE 文件"
    exit 1
fi

echo "✓ 找到环境配置文件: $ENV_FILE"

# 检查环境是否已存在
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "⚠️  环境 '$ENV_NAME' 已存在"
    read -p "是否删除并重新创建? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有环境..."
        conda env remove -n "$ENV_NAME" -y
    else
        echo "跳过环境创建，直接安装依赖..."
        ENV_EXISTS=true
    fi
else
    ENV_EXISTS=false
fi

# 创建环境（如果不存在）
if [ "$ENV_EXISTS" = false ]; then
    echo "创建 Conda 环境: $ENV_NAME"
    conda env create -f "$ENV_FILE"
    echo "✓ 环境创建完成"
else
    echo "使用现有环境: $ENV_NAME"
fi

# 激活环境并安装依赖
echo ""
echo "激活环境并安装依赖..."
echo "=========================================="

# 使用 conda run 在环境中执行命令
conda run -n "$ENV_NAME" pip install -r requirements.txt

echo ""
echo "安装本地 transformers (editable mode)..."
cd transformers
conda run -n "$ENV_NAME" pip install -e .
cd ..

echo ""
echo "=========================================="
echo "✓ 安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  1. 激活环境: conda activate $ENV_NAME"
echo "  2. 运行脚本: python text2image.py -i 'your prompt'"
echo ""
echo "或者使用 conda run 直接运行:"
echo "  conda run -n $ENV_NAME python text2image.py -i 'your prompt'"
echo ""
