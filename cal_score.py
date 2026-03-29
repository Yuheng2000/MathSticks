import json
import re

def process_jsonl_file(input_file, output_file):
    correct_count = 0
    total_count = 0
    level_correct = {1: 0, 2: 0, 3: 0, 4: 0}  # Correct counts by level
    level_total = {1: 0, 2: 0, 3: 0, 4: 0}    # Total counts by level

    print(f"================== Processing file ==================")
    print(f"{input_file}")
    print(f"=====================================================")
    
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            item = json.loads(line.strip())
            total_count += 1
            
            # Track per-level totals
            level = item.get("level", 1)
            if level in level_total:
                level_total[level] += 1
            
            # Merge both one-move and two-move answers
            option_answer_all = item["option_answer"]["mode_1"] + item["option_answer"]["mode_2"]

            for option in option_answer_all:
                option["pick"] = [option["pick"]] if isinstance(option["pick"], str) else option["pick"]
                option["place"] = [option["place"]] if isinstance(option["place"], str) else option["place"]
            
            # Initialize the parsed prediction
            prediction = {"pick": [], "place": []}
            
            # Extract the boxed answer
            if item["response_raw"]:
                matches = re.findall(r'boxed\{([^}]*)\}', item["response_raw"])
            else:
                # total_count -= 1
                matches = None
                print(f"Warning: 'response_raw' can not be extracted in item with id {item['id']}")

            if matches:
                last_match = matches[-1]
                # Extract Move commands
                moves = re.findall(r'Move\(([^)]*)\)', last_match)
                for move in moves:
                    parts = [p.strip() for p in move.split(',')]
                    if len(parts) == 2:
                        prediction["pick"].append(parts[0])
                        prediction["place"].append(parts[1])
            
            # Check whether the prediction matches any valid answer
            score = 0.0
            for option in option_answer_all:
                # Compare sets without considering order
                if (set(prediction["pick"]) == set(option["pick"]) and 
                    set(prediction["place"]) == set(option["place"])):
                    score = 1.0
                    correct_count += 1
                    # Track per-level correct counts
                    if level in level_correct:
                        level_correct[level] += 1
                    break
            
            # Prepare the output item
            output_item = {
                "id": item["id"],
                "level": item["level"],
                "score": score,
                "problem": item["problem"],
                "solution_num": item["solution_num"],
                "prediction": prediction,
                "option_answer": option_answer_all
            }
            
            # Write the output record
            outfile.write(json.dumps(output_item, ensure_ascii=False) + '\n')
    
    # Compute accuracy
    accuracy = correct_count / total_count if total_count > 0 else 0.0
    print(f"Total items processed: {total_count}")
    print(f"Correct items: {correct_count}")
    print(f"Accuracy: {accuracy:.2%}")
    
    # Print per-level statistics
    print("Level statistics:")
    for level in [1, 2, 3, 4]:
        if level_total[level] > 0:
            level_acc = level_correct[level] / level_total[level]
            print(f"  Level {level}: {level_correct[level]}/{level_total[level]} = {level_acc:.2%}")
        else:
            print(f"  Level {level}: 0/0 = N/A")
    print()
    return accuracy, level_correct, level_total

# Example usage
if __name__ == "__main__":
    # Input and output file paths
    input_jsonls = [
        "Qwen_Qwen2.5-VL-32B-Instruct_with_solutions.jsonl",
        "Qwen_Qwen2.5-VL-72B-Instruct_with_solutions.jsonl",
        "InternVL3-38B_with_solutions.jsonl",
        "InternVL3-78B_with_solutions.jsonl",
        "gemini-2.5-pro-preview-05-06_with_solutions.jsonl",
        "gemini-2.5-flash-preview-05-20_with_solutions.jsonl",
        "claude-sonnet-4-20250514_with_solutions.jsonl",
        "doubao-seed-1-6-250615_with_solutions.jsonl",
        "doubao-seed-1-6-thinking-250615_with_solutions.jsonl",
        "gpt-4o-2024-11-20_with_solutions.jsonl",
        "o3-2025-04-16_with_solutions.jsonl",
        "o4-mini-2025-04-16_with_solutions.jsonl",
        # "robobrain_with_solutions.jsonl",
    ]

    accuracies = []  # Accuracy for each file
    model_level_accuracies = []  # Per-model level accuracies [model1_levels, model2_levels, ...]

    for input_jsonl in input_jsonls:
        #acc, level_correct, level_total = process_jsonl_file(f"./score_by_solution_type/one_move/{input_jsonl}",f"./score_by_solution_type/one_move/score_{input_jsonl}")
        acc, level_correct, level_total = process_jsonl_file(f"./{input_jsonl}",f"./score_{input_jsonl}")
        # acc = process_jsonl_file(f"./score/{input_jsonl}",f"./score/score_{input_jsonl}")

        accuracies.append(acc*100)
        
        # Collect per-level accuracy for the current model
        current_model_levels = []
        for level in [1, 2, 3, 4]:
            if level_total[level] > 0:
                level_acc = level_correct[level] / level_total[level] * 100
                current_model_levels.append(round(level_acc, 2))
            else:
                current_model_levels.append(0.0)
        model_level_accuracies.append(current_model_levels)
        #process_jsonl_file(f"./score_by_solution_type/two_move/{input_jsonl}", f"./score_by_solution_type/two_move/score_{input_jsonl}")

    print(f"Accuracy list: {[round(a, 2) for a in accuracies]}")
    
    # Print per-level accuracy for each model
    for i, model_levels in enumerate(model_level_accuracies):
        model_name = input_jsonls[i].replace("_with_solutions.jsonl", "")
        print(f"{model_name} level accuracies: {model_levels}")
