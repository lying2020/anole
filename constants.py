import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

default_ckpt_path = "/home1/cjl/models/anole-7b"

ckpt_path = Path(os.getenv("CKPT_PATH", default_ckpt_path))

MODEL_7B_PATH = ckpt_path / "models" / "7b"

MODEL_30B_PATH = ckpt_path / "models" / "30b"

TOKENIZER_TEXT_PATH = ckpt_path / "tokenizer" / "text_tokenizer.json"

TOKENIZER_IMAGE_PATH = ckpt_path / "tokenizer" / "vqgan.ckpt"

TOKENIZER_IMAGE_CFG_PATH = ckpt_path / "tokenizer" / "vqgan.yaml"
