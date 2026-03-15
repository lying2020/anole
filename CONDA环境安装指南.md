# Anole Conda 环境安装指南

## 📋 概述

本指南将帮助您创建一个独立的 conda 环境来运行 Anole 项目，避免破坏现有 Python 环境。

## 🚀 快速开始

### 方法一：使用自动安装脚本（推荐）

```bash
cd /home/liying/Desktop/ECCV_2026/anole
bash setup_conda_env.sh
```

脚本会自动：
1. 检查 conda 是否安装
2. 创建名为 `anole` 的 conda 环境
3. 安装所有依赖包
4. 安装本地 transformers（editable mode）

### 方法二：手动安装

#### 1. 创建环境

```bash
conda env create -f environment.yml
```

#### 2. 激活环境

```bash
conda activate anole
```

#### 3. 安装依赖

```bash
# 安装 requirements.txt 中的包
pip install -r requirements.txt

# 安装本地 transformers（支持 Chameleon）
cd transformers
pip install -e .
cd ..
```

## 📦 环境配置说明

### environment.yml 包含：

- **Python 3.10** - 项目使用的 Python 版本
- **PyTorch 2.1.1** - 带 CUDA 12.1 支持
- **所有 requirements.txt 中的依赖**
  - accelerate, deepspeed, xformers 等
  - Pillow, numpy, pandas 等基础库

### 环境特点：

- ✅ 独立环境，不影响系统 Python
- ✅ 包含 CUDA 支持的 PyTorch
- ✅ 所有依赖版本固定，确保兼容性

## 🔧 使用方法

### 激活环境

```bash
conda activate anole
```

### 运行脚本

激活环境后，直接运行：

```bash
# 文本生成图像
python text2image.py -i "a beautiful sunset" -b 1 -s ./outputs/test/

# 交错生成
python interleaved_generation.py -i "Describe a cat with an image" -s ./outputs/test/

# 多模态推理
python inference.py -i input.json -s ./outputs/test/
```

### 不激活环境直接运行

也可以使用 `conda run` 直接运行（无需激活）：

```bash
conda run -n anole python text2image.py -i "a beautiful sunset" -b 1
```

## 🗑️ 管理环境

### 查看环境列表

```bash
conda env list
```

### 删除环境（如果需要重新安装）

```bash
conda env remove -n anole
```

### 更新环境

如果修改了 `environment.yml`：

```bash
conda env update -n anole -f environment.yml --prune
```

## ⚠️ 注意事项

1. **CUDA 版本**：确保系统 CUDA 版本与 PyTorch 的 CUDA 版本兼容（当前配置为 CUDA 12.1）

2. **GPU 内存**：7B 模型需要较大 GPU 内存，建议至少 16GB

3. **首次运行**：模型加载需要时间，请耐心等待

4. **环境隔离**：每次使用项目时，记得激活 conda 环境

## 🔍 故障排查

### 问题 1：conda 命令未找到

```bash
# 初始化 conda（如果使用 miniconda）
source ~/miniconda3/etc/profile.d/conda.sh

# 或添加到 ~/.bashrc
echo 'source ~/miniconda3/etc/profile.d/conda.sh' >> ~/.bashrc
source ~/.bashrc
```

### 问题 2：CUDA 不可用

检查 PyTorch CUDA 支持：

```bash
conda activate anole
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 问题 3：依赖冲突

如果遇到依赖冲突，可以尝试：

```bash
conda activate anole
pip install --upgrade --force-reinstall -r requirements.txt
```

### 问题 4：transformers 安装失败

确保在项目根目录下运行：

```bash
conda activate anole
cd /home/liying/Desktop/ECCV_2026/anole/transformers
pip install -e .
```

## 📝 验证安装

运行以下命令验证环境是否正确配置：

```bash
conda activate anole
python -c "
import torch
import chameleon
from constants import MODEL_7B_PATH
print(f'✓ PyTorch: {torch.__version__}')
print(f'✓ CUDA available: {torch.cuda.is_available()}')
print(f'✓ Chameleon imported')
print(f'✓ Model path: {MODEL_7B_PATH}')
"
```

如果所有检查都通过，说明环境配置成功！

## 🎉 完成

现在您可以安全地在独立的 conda 环境中运行 Anole 项目，不会影响系统的其他 Python 环境。
