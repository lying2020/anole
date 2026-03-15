import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# 优先使用环境变量，其次尝试从project.py导入，最后使用默认路径
try:
    from project import anole_7b_v0_1_path
    default_ckpt_path = anole_7b_v0_1_path
except ImportError:
    default_ckpt_path = "./data"

ckpt_path = Path(os.getenv("CKPT_PATH", default_ckpt_path))

MODEL_7B_PATH = ckpt_path / "models" / "7b"

MODEL_30B_PATH = ckpt_path / "models" / "30b"

TOKENIZER_TEXT_PATH = ckpt_path / "tokenizer" / "text_tokenizer.json"

TOKENIZER_IMAGE_PATH = ckpt_path / "tokenizer" / "vqgan.ckpt"

TOKENIZER_IMAGE_CFG_PATH = ckpt_path / "tokenizer" / "vqgan.yaml"
