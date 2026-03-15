import os
import json
import torch
import argparse
from PIL import Image
from pathlib import Path
from chameleon.inference.chameleon import ChameleonInferenceModel, Options
from constants import (
    MODEL_7B_PATH,
    TOKENIZER_TEXT_PATH,
    TOKENIZER_IMAGE_CFG_PATH,
    TOKENIZER_IMAGE_PATH,
)
from typing import List, Dict, Tuple

def split_token_sequence(
    tokens: torch.LongTensor,
    boi: int,
    eoi: int
) -> List[Tuple[str, torch.LongTensor]]:
    """
    Split a sequence of tokens into text and image segments.

    Args:
        tokens (torch.LongTensor): The token sequence.
        boi (int): Begin of image token.
        eoi (int): End of image token.

    Returns:
        List[Tuple[str, torch.LongTensor]]: List of tuples indicating segment type and tokens.
    """
    batch_size, _ = tokens.shape
    assert batch_size == 1, "Batch size must be 1"

    device = tokens.device
    tokens = tokens[0]  # remove batch dimension
    tokens = tokens.to(device)
    segments = []
    current_segment = []
    in_image_seg = False

    for token in tokens:
        if token == boi:
            # if entering an image segment, save the current text segment (if any)
            if current_segment:
                segments.append(("text_seg", torch.tensor(current_segment, dtype=tokens.dtype, device=device).reshape(1, -1)))
                current_segment = []
            in_image_seg = True
        elif token == eoi and in_image_seg:
            # if exiting an image segment, save the current image segment
            segments.append(("image_seg", torch.tensor(current_segment, dtype=tokens.dtype, device=device).reshape(1, -1)))
            current_segment = []
            in_image_seg = False
        else:
            current_segment.append(token)
    # save any remaining tokens
    if current_segment:
        if in_image_seg:
            segments.append(("image_seg", torch.tensor(current_segment, dtype=tokens.dtype, device=device).reshape(1, -1)))
        else:
            segments.append(("text_seg", torch.tensor(current_segment, dtype=tokens.dtype, device=device).reshape(1, -1)))
    return segments

def main(args: argparse.Namespace):
    """Main function to generate and process model output."""
    # Load Chameleon model
    model = ChameleonInferenceModel(
        MODEL_7B_PATH.as_posix(),
        TOKENIZER_TEXT_PATH.as_posix(),
        TOKENIZER_IMAGE_CFG_PATH.as_posix(),
        TOKENIZER_IMAGE_PATH.as_posix(),
    )
    # Print model configuration
    print(f"Model path: {MODEL_7B_PATH}")
    print(f"Text tokenizer path: {TOKENIZER_TEXT_PATH}")
    print(f"Image tokenizer config path: {TOKENIZER_IMAGE_CFG_PATH}")
    print(f"Image tokenizer path: {TOKENIZER_IMAGE_PATH}")
    # Generate options
    options = Options()
    # 确保生成足够的长度
    options.max_gen_len = 4096  # 最大生成长度
    options.max_seq_len = 4096  # 最大序列长度
    print(f"生成参数: max_gen_len={options.max_gen_len}, max_seq_len={options.max_seq_len}")
    # Prepare prompt
    input_path: Path = Path(args.input)
    with open(input_path, "r") as f:
        input_segs: List[Dict[str, str]] = json.load(f)
        assert not input_segs is None
    batch_prompt_ui = [[]]
    for input_seg in input_segs:
        if input_seg["type"] == "text":
            batch_prompt_ui[0] += [
                {"type": "text", "value": input_seg["content"]}
            ]
        else:
            assert input_seg["type"] == "image"
            abs_path: Path = os.path.abspath(input_seg["content"])
            batch_prompt_ui[0] += [
                {"type": "image", "value": f"file:{abs_path}"},
            ]
    # generate
    print("=" * 50)
    print("开始生成内容...")
    print(f"Options: txt={options.txt}, img={options.img}")
    print(f"Prompt UI 长度: {len(batch_prompt_ui[0])}")
    print("正在调用 model.generate()...")
    import sys
    sys.stdout.flush()  # 确保输出立即显示

    try:
        # 使用 stream 方法以便可以看到进度
        token_count = 0
        tokens_list = []
        print("开始流式生成...")
        eos_id = model.vocab.eos_id
        boi_id = model.vocab.begin_image
        eoi_id = model.vocab.end_image
        print(f"EOS token ID: {eos_id}, BOI token ID: {boi_id}, EOI token ID: {eoi_id}")

        for token in model.stream(batch_prompt_ui=batch_prompt_ui, options=options):
            token_id = token.id.item() if token.id.numel() == 1 else token.id[0].item()
            token_count += 1

            # 检查是否是特殊 token
            if token_id == eos_id:
                print(f"  检测到 EOS token，停止生成")
            elif token_id == boi_id:
                print(f"  检测到 BOI (Begin of Image) token")
            elif token_id == eoi_id:
                print(f"  检测到 EOI (End of Image) token")

            tokens_list.append(token.id)

        if not tokens_list:
            print("警告: 没有生成任何 tokens")
            tokens = torch.LongTensor()
        else:
            tokens = torch.stack(tokens_list).T
            print(f"生成完成，总共获得 {tokens.shape[1]} 个 tokens")
            # print(f"生成的 token IDs: {tokens[0].tolist() if tokens.numel() > 0 else 'empty'}")
    except KeyboardInterrupt:
        print("\n用户中断了生成过程")
        return
    except Exception as e:
        print(f"生成过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return
    # split
    if tokens.numel() == 0:
        print("错误: 没有生成任何 tokens，无法继续处理")
        return

    boi, eoi = model.vocab.begin_image, model.vocab.end_image   # 8197(boi), 8196(eoi)
    print(f"开始分割 token 序列，BOI={boi}, EOI={eoi}")
    segments = split_token_sequence(tokens, boi, eoi)
    print(f"分割得到 {len(segments)} 个段")

    # decode
    os.makedirs(args.save_dir, exist_ok=True)
    for seg_id, (seg_type, seg_tokens) in enumerate(segments):
        if seg_type == "image_seg":
            assert seg_tokens.shape[1] == 1024
            img: Image = model.decode_image(seg_tokens)[0]
            image_path = os.path.join(args.save_dir, f"{seg_id}.png")
            img.save(image_path)
            print(f"<img: {image_path}>")
        else:
            assert seg_type == "text_seg"
            decoded_text = model.decode_text(seg_tokens)[0]
            print(decoded_text)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate interleaved image-text content based on text instructions.")
    parser.add_argument("-i", "--input", type=str, default="./inputs/input1.json", help="The multimodal input file.")
    parser.add_argument("-s", "--save_dir", type=str, default="./outputs/inference/", help="The directory to save the generated images.")
    args: argparse.Namespace = parser.parse_args()
    return args

if __name__ == "__main__":
    args: argparse.Namespace = parse_arguments()
    main(args)
