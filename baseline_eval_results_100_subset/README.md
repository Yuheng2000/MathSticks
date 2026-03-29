# Baseline Eval Results on the 100-item Public Subset

This directory contains the released baseline outputs for `MathSticks_bench_100.jsonl`, a fixed 100-example subset of the full 400-item benchmark with 25 examples from each level. These results are for the <b>pure-visual / image-only</b> setting: the model is shown the puzzle image and is <b>not</b> directly given the equation string.

The `Human` row shown in the leaderboard is a paper-based reference value for context only. It is not associated with a released prediction JSON file in this directory. For consistency with the `100`-item public subset, the displayed values are the nearest integer-count approximation on this split.

Files:
- `<model>.json`: detailed per-example outputs. Each record copies the benchmark fields and adds the model response in `response_raw`.
- `<model>.score.json`: aggregated accuracy summary for the same model, including per-level accuracy.
- `leaderboard.json` and `leaderboard.md`: the aggregated ranking across all released models.

If you contribute a new model result, please evaluate on the same subset, add both files for the model, and refresh the leaderboard files.
