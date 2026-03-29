import argparse
import base64
import json
import os
import random
import re
import time
from pathlib import Path

from openai import OpenAI


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


DEFAULT_MODELS = [
    "gpt-5.2",
    "gemini-3.1-pro-preview",
    "grok-4-1-fast-non-reasoning",
    "grok-4-1-fast-reasoning",
    "qwen3.5-plus",
    "qwen3.5-397b-a17b",
    "deepseek-v3.2",
    "glm-5",
    "doubao-seed-2-0-pro",
    "llama-4-maverick",
    "kimi-k2.5",
]


def safe_name(name):
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)


def read_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_stratified_subset(input_jsonl, subset_jsonl, per_level, seed):
    all_items = read_jsonl(input_jsonl)
    by_level = {}
    for item in all_items:
        level = item.get("level")
        by_level.setdefault(level, []).append(item)

    rng = random.Random(seed)
    chosen = []
    for level in [1, 2, 3, 4]:
        if level not in by_level:
            raise ValueError(f"Missing level {level} in {input_jsonl}")
        candidates = by_level[level]
        if len(candidates) < per_level:
            raise ValueError(
                f"Level {level} has only {len(candidates)} items, less than per_level={per_level}"
            )
        chosen.extend(rng.sample(candidates, per_level))

    chosen.sort(key=lambda x: (x.get("level", 0), str(x.get("id", ""))))
    write_jsonl(subset_jsonl, chosen)
    return chosen


def encode_image_to_data_url(image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def call_model(client, model, image_data_url, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": NO_TEXT_PROMPT},
                ],
            }
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content


def is_non_retryable_error(err_msg):
    msg = (err_msg or "").lower()
    keywords = [
        "model not found",
        "invalid model",
        "does not exist",
        "unsupported model",
        "incorrect api key",
        "unauthorized",
        "permission",
    ]
    return any(k in msg for k in keywords)


def normalize_option(option):
    pick = option.get("pick", [])
    place = option.get("place", [])
    if isinstance(pick, str):
        pick = [pick]
    if isinstance(place, str):
        place = [place]
    return {"pick": set(pick), "place": set(place)}


def parse_prediction(response_raw):
    prediction = {"pick": [], "place": []}
    if not response_raw:
        return prediction
    matches = re.findall(r"boxed\{([^}]*)\}", response_raw, flags=re.IGNORECASE)
    if not matches:
        return prediction
    moves = re.findall(r"Move\(([^)]*)\)", matches[-1])
    for move in moves:
        parts = [p.strip() for p in move.split(",")]
        if len(parts) == 2:
            prediction["pick"].append(parts[0])
            prediction["place"].append(parts[1])
    return prediction


def score_records(records):
    total = len(records)
    correct = 0
    level_total = {1: 0, 2: 0, 3: 0, 4: 0}
    level_correct = {1: 0, 2: 0, 3: 0, 4: 0}

    for item in records:
        level = item.get("level", 1)
        if level in level_total:
            level_total[level] += 1
        pred = parse_prediction(item.get("response_raw"))
        pred_pick = set(pred["pick"])
        pred_place = set(pred["place"])

        options = item.get("option_answer", {})
        option_answer_all = options.get("mode_1", []) + options.get("mode_2", [])
        matched = False
        for opt in option_answer_all:
            norm = normalize_option(opt)
            if pred_pick == norm["pick"] and pred_place == norm["place"]:
                matched = True
                break

        if matched:
            correct += 1
            if level in level_correct:
                level_correct[level] += 1

    accuracy = (correct / total) if total else 0.0
    level_accuracy = {}
    for level in [1, 2, 3, 4]:
        denom = level_total[level]
        level_accuracy[level] = (level_correct[level] / denom) if denom else 0.0

    return {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "level_total": level_total,
        "level_correct": level_correct,
        "level_accuracy": level_accuracy,
    }


def load_existing_results(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(path, records):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def evaluate_one_model(
    client,
    model,
    subset_items,
    image_dir,
    output_dir,
    temperature,
    max_retries,
    sleep_seconds,
    resume,
):
    model_safe = safe_name(model)
    result_json = output_dir / f"{model_safe}.json"
    score_json = output_dir / f"{model_safe}.score.json"

    records = load_existing_results(result_json) if resume else []
    done_ids = {str(r.get("id")) for r in records}

    total = len(subset_items)
    for idx, item in enumerate(subset_items, start=1):
        item_id = str(item.get("id"))
        if item_id in done_ids:
            continue

        image_rel = item.get("image")
        image_path = Path(image_dir) / image_rel
        image_data_url = encode_image_to_data_url(image_path)

        response_raw = None
        last_error = None
        for _ in range(max_retries):
            try:
                response_raw = call_model(client, model, image_data_url, temperature)
                last_error = None
                break
            except Exception as e:
                last_error = str(e)
                if is_non_retryable_error(last_error):
                    break
                time.sleep(sleep_seconds)

        record = dict(item)
        record["model"] = model
        record["temperature"] = temperature
        record["response_raw"] = response_raw
        if last_error is not None:
            record["error"] = last_error
        records.append(record)
        done_ids.add(item_id)

        save_results(result_json, records)
        print(f"[{model}] {idx}/{total} done (id={item_id})")

    stats = score_records(records)
    with open(score_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    return stats, result_json, score_json


def write_leaderboard(output_dir, model_stats):
    leaderboard = []
    for model, stats in model_stats.items():
        leaderboard.append(
            {
                "model": model,
                "accuracy": stats["accuracy"],
                "correct": stats["correct"],
                "total": stats["total"],
                "level_accuracy": stats["level_accuracy"],
            }
        )
    leaderboard.sort(key=lambda x: x["accuracy"], reverse=True)

    leaderboard_json = output_dir / "leaderboard.json"
    with open(leaderboard_json, "w", encoding="utf-8") as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

    leaderboard_md = output_dir / "leaderboard.md"
    with open(leaderboard_md, "w", encoding="utf-8") as f:
        f.write("| Rank | Model | Accuracy | Correct/Total | L1 | L2 | L3 | L4 |\n")
        f.write("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for i, row in enumerate(leaderboard, start=1):
            l1 = row["level_accuracy"][1] * 100
            l2 = row["level_accuracy"][2] * 100
            l3 = row["level_accuracy"][3] * 100
            l4 = row["level_accuracy"][4] * 100
            f.write(
                f"| {i} | {row['model']} | {row['accuracy'] * 100:.2f}% | "
                f"{row['correct']}/{row['total']} | {l1:.2f}% | {l2:.2f}% | {l3:.2f}% | {l4:.2f}% |\n"
            )


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-model MathSticks evaluation via API-compatible endpoint")
    parser.add_argument("--input", default="MathSticks_bench_400.jsonl")
    parser.add_argument("--subset", default="MathSticks_bench_100.jsonl")
    parser.add_argument("--image-dir", default="./image")
    parser.add_argument("--output-dir", default="./baseline_eval_results_100_subset")
    parser.add_argument("--per-level", type=int, default=25)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--sleep-seconds", type=int, default=3)
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--base-url", default=os.environ.get("BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument(
        "--api-key",
        default=os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY"),
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--rebuild-subset", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.api_key:
        raise ValueError("Missing API key. Use --api-key or set API_KEY/OPENAI_API_KEY.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    subset_path = Path(args.subset)
    if args.rebuild_subset or not subset_path.exists():
        subset_items = build_stratified_subset(
            input_jsonl=args.input,
            subset_jsonl=args.subset,
            per_level=args.per_level,
            seed=args.seed,
        )
        print(f"Subset written to {args.subset}, total={len(subset_items)}")
    else:
        subset_items = read_jsonl(args.subset)
        print(f"Using existing subset {args.subset}, total={len(subset_items)}")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    client = OpenAI(api_key=args.api_key, base_url=args.base_url)

    model_stats = {}
    for model in models:
        print(f"\n=== Evaluating model: {model} ===")
        stats, result_json, score_json = evaluate_one_model(
            client=client,
            model=model,
            subset_items=subset_items,
            image_dir=args.image_dir,
            output_dir=output_dir,
            temperature=args.temperature,
            max_retries=args.max_retries,
            sleep_seconds=args.sleep_seconds,
            resume=args.resume,
        )
        print(
            f"[{model}] accuracy={stats['accuracy'] * 100:.2f}% "
            f"({stats['correct']}/{stats['total']})"
        )
        print(f"[{model}] results: {result_json}")
        print(f"[{model}] score:   {score_json}")
        model_stats[model] = stats

    write_leaderboard(output_dir, model_stats)
    print(f"\nLeaderboard files saved under: {output_dir}")


if __name__ == "__main__":
    main()
