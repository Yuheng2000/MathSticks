from openai import OpenAI
from tqdm import tqdm
import base64
import time
import random
import json
import os
import argparse
import sys

# Configuration via environment variables (no hardcoded secrets)
# Required: OPENAI_API_KEY, optional: OPENAI_BASE_URL, MODEL
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_api_base = os.environ.get("OPENAI_BASE_URL")
model = os.environ.get("MODEL")

PROMPT = """
**Task:**  
You are given an incorrectly displayed equation "{equation}" constructed from matchsticks in a seven-segment format. Each segment (with matchstick or without matchstick) is labeled with a unique identifier (e.g., A0, C4). Your goal is to modify the equation by moving **one or two matchsticks** to make it mathematically correct. 

**Constraints:**  
- Only reposition existing matchsticks (no addition/removal). 
- Only one or two matchsticks can be moved, and each matchstick can only be moved once. 
- The final equation must be mathematically valid.  
- Preserve digit legibility (no broken/unrecognizable characters).  

**Output Requirements:**  
1. **Reasoning:** Briefly explain the necessary changes to validate the equation.  
2. **Final Solution Format:** Provide the answer strictly in the format:  
   - For single move: `\\boxed{{Move(<original_label>, <target_label>)}}`, for example: `\\boxed{{Move(B2, D5)}}` 
   - For two moves: `\\boxed{{Move(<original_label1>, <target_label1>), Move(<original_label2>, <target_label2>)}}`, for example: `\\boxed{{Move(A0, C3), Move(E1, F4)}}`

**Note:**
Observe the image carefully to identify the matchstick positions and their labels.
Gray dashed segments indicate no matchstick, while solid segments indicate a matchstick is present.
Ensure the final answer adheres precisely to the `\\boxed{{}}` format for automated parsing.
"""


NO_TEXT_PROMPT = """
**Task:**  
You are given an incorrectly displayed equation constructed from matchsticks in a seven-segment format, as shown in the image. Each segment (with matchstick or without matchstick) is labeled with a unique identifier (e.g., A0, C4). Your goal is to modify the equation by moving **one or two matchsticks** to make it mathematically correct. 

**Constraints:**  
- Only reposition existing matchsticks (no addition/removal). 
- Only one or two matchsticks can be moved, and each matchstick can only be moved once. 
- The final equation must be mathematically valid.  
- Preserve digit legibility (no broken/unrecognizable characters).  

**Output Requirements:**  
1. **Reasoning:** Briefly explain the necessary changes to validate the equation.  
2. **Final Solution Format:** Provide the answer strictly in the format:  
   - For single move: `\\boxed{{Move(<original_label>, <target_label>)}}`, for example: `\\boxed{{Move(B2, D5)}}` 
   - For two moves: `\\boxed{{Move(<original_label1>, <target_label1>), Move(<original_label2>, <target_label2>)}}`, for example: `\\boxed{{Move(A0, C3), Move(E1, F4)}}`

**Note:**
Observe the image carefully to identify the matchstick positions and their labels.
Gray dashed segments indicate no matchstick, while solid segments indicate a matchstick is present.
Ensure the final answer adheres precisely to the `\\boxed{{}}` format for automated parsing.
"""


def process_image_with_retry(
    sample_id,
    image_path,
    problem,
    use_no_text_prompt=True,
    max_retries=3,
    sleep_min=10,
    sleep_max=30,
):
    """
    Process an image with retry logic.

    Args:
        sample_id: Identifier for the image
        image_path: Path to the image file
        problem: The problem/equation to process
        use_no_text_prompt: If True, use image-only task prompt; otherwise include equation text
        max_retries: Maximum number of retry attempts
        sleep_min: Minimum backoff seconds between retries
        sleep_max: Maximum backoff seconds between retries

    Returns:
        The API response string if successful, None otherwise.
    """
    client_kwargs = {"api_key": openai_api_key}
    if openai_api_base:
        client_kwargs["base_url"] = openai_api_base
    client = OpenAI(**client_kwargs)

    retry_count = 0
    while retry_count < max_retries:
        try:
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
            base64_img = f"data:image/png;base64,{encoded_image}"

            prompt_text = NO_TEXT_PROMPT if use_no_text_prompt else PROMPT.format(equation=problem)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_img},
                            },
                            {"type": "text", "text": prompt_text},
                        ],
                    }
                ],
            )
            return response.choices[0].message.content

        except Exception:
            retry_count += 1
            if retry_count < max_retries:
                sleep_time = random.uniform(sleep_min, sleep_max)
                time.sleep(sleep_time)
            else:
                # Do not leak paths or full problem text in logs
                safe_model = (model or "model").replace("/", "_")
                with open(f"error_{safe_model}.txt", "a", encoding="utf-8") as error_file:
                    error_file.write(f"{sample_id}\n")
                return None


def run(
    input_file,
    output_file,
    image_dir,
    use_no_text_prompt=True,
    max_retries=3,
    sleep_min=10,
    sleep_max=30,
):
    """
    Main function to run image processing.
    """
    processed_id_list = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as outfile:
            for line in outfile:
                line = line.strip()
                if not line:
                    continue
                try:
                    processed_id_list.append(json.loads(line)["id"])
                except Exception:
                    # Skip malformed output lines silently
                    continue

    # Count total lines for progress bar
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            total_lines = sum(1 for _ in f)
    except Exception:
        total_lines = None

    safe_model = (model or "model").replace("/", "_")
    with open(output_file, "a", encoding="utf-8") as outfile:
        with open(input_file, "r", encoding="utf-8") as infile:
            for line in tqdm(infile, total=total_lines, desc=safe_model):
                try:
                    item = json.loads(line.strip())
                except json.JSONDecodeError:
                    print("Warning: failed to parse a line; skipping.")
                    continue

                sample_id = item.get("id")
                if sample_id is None:
                    print("Warning: item without 'id'; skipping.")
                    continue

                if sample_id in processed_id_list:
                    print(f"Skipping already processed ID: {sample_id}")
                    continue

                problem = item.get("problem", "")
                image_rel = item.get("image")
                if not image_rel:
                    print(f"Warning: item {sample_id} missing 'image'; skipping.")
                    continue

                image_path = os.path.join(image_dir, image_rel)
                response = process_image_with_retry(
                    sample_id,
                    image_path,
                    problem,
                    use_no_text_prompt=use_no_text_prompt,
                    max_retries=max_retries,
                    sleep_min=sleep_min,
                    sleep_max=sleep_max,
                )

                item["response_raw"] = response
                if model:
                    item["model"] = model
                outfile.write(json.dumps(item, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process matchstick equation images.")
    parser.add_argument("--input", required=True, help="Path to input JSONL file")
    parser.add_argument(
        "--output",
        required=False,
        help="Path to output JSONL file (default: <model>_with_solutions.jsonl)",
    )
    parser.add_argument(
        "--image-dir",
        default="./image",
        help="Directory containing images (default: ./image)",
    )
    parser.add_argument(
        "--with-text",
        action="store_true",
        help="Include equation text prompt instead of image-only task",
    )
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries per item")
    parser.add_argument("--sleep-min", type=int, default=10, help="Min backoff seconds")
    parser.add_argument("--sleep-max", type=int, default=30, help="Max backoff seconds")

    args = parser.parse_args()

    if not openai_api_key:
        print("Error: OPENAI_API_KEY is not set in environment.")
        sys.exit(1)

    safe_model = (model or "model").replace("/", "_")
    output_filename = args.output or f"{safe_model}_with_solutions.jsonl"

    run(
        input_file=args.input,
        output_file=output_filename,
        image_dir=args.image_dir,
        use_no_text_prompt=not args.with_text,
        max_retries=args.max_retries,
        sleep_min=args.sleep_min,
        sleep_max=args.sleep_max,
    )
    print(f"Processing complete. Results saved to: {output_filename}")