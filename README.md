<h1 align="center">MathSticks: A Benchmark for Visual Symbolic Compositional Reasoning with Matchstick Puzzles</h1>

<h3 align="center">Bridging visual perception, symbolic manipulation, and arithmetic consistency.</h3>

<p align="center">
  <a href="https://arxiv.org/pdf/2510.00483"><img src="https://img.shields.io/badge/arXiv-2510.00483-b31b1b.svg?logo=arxiv" alt="arXiv"></a>
  &nbsp;
  <a href="https://huggingface.co/datasets/yuheng2000/MathSticks"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-MathSticks-yellow" alt="Dataset"></a>
  &nbsp;
  <a href="MathSticks_bench_400.jsonl"><img src="https://img.shields.io/badge/%F0%9F%A7%AA%20Benchmark-400%20Items-0f766e" alt="400-item benchmark"></a>
  &nbsp;
  <a href="MathSticks_bench_100.jsonl"><img src="https://img.shields.io/badge/%F0%9F%94%8D%20Public%20Subset-100%20Items-2563eb" alt="100-item public subset"></a>
  &nbsp;
  <a href="baseline_eval_results_100_subset/leaderboard.md"><img src="https://img.shields.io/badge/%F0%9F%96%BC%EF%B8%8F%20Setting-Pure--Visual%20Only-7c3aed" alt="Pure visual only"></a>
  &nbsp;
  <a href="baseline_eval_results_100_subset/leaderboard.md"><img src="https://img.shields.io/badge/%F0%9F%8F%86%20Leaderboard-100--Item%20Snapshot-orange" alt="Leaderboard"></a>
  &nbsp;
  <a href="baseline_eval_results_100_subset"><img src="https://img.shields.io/badge/%F0%9F%93%A6%20Results-Detailed%20JSONs-2ea44f" alt="Detailed JSONs"></a>
</p>

<table>
  <tr>
    <td width="62%" valign="top">
      <p>
        MathSticks is a benchmark for <b>Visual Symbolic Compositional Reasoning (VSCR)</b> that jointly tests visual perception,
        symbolic manipulation, and arithmetic consistency. Each task presents an incorrect matchstick equation in a seven-segment style,
        and the model must move exactly one or two sticks to repair it under strict conservation and digit-legibility constraints.
      </p>
      <ul>
        <li><b>Two evaluation regimes.</b> Text-guided and pure-visual settings diagnose whether failure comes from reading the puzzle or reasoning over it.</li>
        <li><b>Systematic coverage.</b> The benchmark spans Levels 1-4, one-stick vs. two-stick edits, solution multiplicity, and operator changes.</li>
        <li><b>Two release scales.</b> This repo keeps the full <code>400</code>-item benchmark and also provides a fixed <code>100</code>-item public subset with <code>25</code> samples per level for open leaderboard submissions.</li>
        <li><b>Important setting.</b> The current public <code>100</code>-item snapshot is <b>pure-visual only</b>: the model sees the rendered image but is <b>not</b> given the equation string directly.</li>
      </ul>
      <p>
        The released benchmark remains the curated <code>MathSticks_bench_400.jsonl</code>. The public leaderboard in this repo is a lighter-weight,
        fixed subset based on <code>MathSticks_bench_100.jsonl</code>, intended for faster iteration and lower-cost reruns rather than replacing the full benchmark.
      </p>
      <p>
        In other words, this public snapshot includes both <b>OCR-like perception</b> and <b>symbolic reasoning</b>: the model must first read the equation from the image and then decide which sticks to move.
      </p>
      <p>
        Perhaps the most striking part of MathSticks is the <b>human-model difficulty gap</b>: these puzzles often feel simple and intuitive to people, but even today's strongest frontier multimodal models still make surprisingly frequent mistakes. On the current public pure-visual snapshot, the best released model baselines reach <code>83/100</code>, while the human reference is about <code>92/100</code>.
      </p>
    </td>
    <td width="38%" align="center" valign="top">
      <img src="example.png" width="100%" alt="MathSticks example">
      <br/>
      <sub><b>Example.</b> Input puzzle, reasoning trace, and move-format prediction.</sub>
    </td>
  </tr>
</table>

## 🔥 News

- **`2026-03-29`**: We update the public leaderboard with the latest evaluation results on the current `100`-item pure-visual subset.
- **`2025-10-17`**: MathSticks is accepted by the <b>NeurIPS MATH-AI Workshop, 2025</b>.
- **`2025-09-30`**: We open-source the benchmark, the dataset construction pipeline, and the paper.

## Why MathSticks?

MathSticks is designed to be deceptively small but structurally demanding:

- **Easy for humans, still hard for frontier models.** Tasks that feel almost trivial to people can still expose major weaknesses in current multimodal reasoning systems.
- **Vision alone is not enough.** The model must correctly perceive lit vs. unlit segments and identify valid move locations.
- **Symbolic manipulation alone is not enough.** The moved sticks must still form legible digits and a valid arithmetic equation.
- **Strict output parsing matters.** The answer must be expressed in a boxed `Move(...)` format, so hand-wavy reasoning does not count.

Evaluations across 14 VLMs reveal substantial limitations: closed-source models only become reliable on simpler cases, open-source models struggle in the pure-visual regime, and humans still maintain a large advantage. This makes MathSticks a compact but diagnostic stress test for multimodal reasoning.

## What Is Released In This Repo?

- **Full benchmark:** [`MathSticks_bench_400.jsonl`](MathSticks_bench_400.jsonl) with the corresponding rendered images under [`image/`](image).
- **Public leaderboard subset:** [`MathSticks_bench_100.jsonl`](MathSticks_bench_100.jsonl), a fixed `100`-example subset with `25` samples from each level.
- **Detailed baseline outputs:** [`baseline_eval_results_100_subset/`](baseline_eval_results_100_subset), including per-example outputs, score summaries, and the <b>pure-visual</b> public leaderboard snapshot.
- **Evaluation scripts:** [`eval.py`](eval.py), [`cal_score.py`](cal_score.py), [`eval_api.py`](eval_api.py), and [`run_api_eval.sh`](run_api_eval.sh).

<table>
  <tr>
    <td width="58%" align="center">
      <img src="results.png" width="100%" alt="MathSticks results summary">
      <br/>
      <sub><b>Results.</b> Model performance across task regimes.</sub>
    </td>
    <td width="42%" align="center">
      <img src="stat.png" width="100%" alt="MathSticks statistics">
      <br/>
      <sub><b>Coverage.</b> Difficulty, move complexity, multiplicity, and operator-flip statistics.</sub>
    </td>
  </tr>
</table>

## 🏆 Leaderboard Snapshot

The table below reports the current public snapshot on [`MathSticks_bench_100.jsonl`](MathSticks_bench_100.jsonl). This release uses the <b>pure-visual / image-only</b> setting: the model is shown the puzzle image, but the equation string is <b>not</b> provided. So the task includes OCR-like reading of the sticks in addition to symbolic reasoning. Each row also has a corresponding detailed JSON file in [`baseline_eval_results_100_subset/`](baseline_eval_results_100_subset), so the released results are fully inspectable.

Three quick observations stand out:

1. **Human performance remains clearly ahead** at roughly `92/100` on the public subset projection, showing that the benchmark still leaves substantial room above the best current model results.
2. **Among released model baselines, Gemini 3.1 Pro Preview and GPT-5.4-high are tied at the top** with `83/100`, though their level-wise profiles differ.
3. **Harder pure-visual cases remain brittle for most models**, with many systems still collapsing to near-zero accuracy under strict move-format scoring.

<table>
  <tr>
    <th>Rank</th>
    <th>Provider</th>
    <th>Model</th>
    <th>Accuracy</th>
    <th>Correct</th>
    <th>L1</th>
    <th>L2</th>
    <th>L3</th>
    <th>L4</th>
  </tr>
  <tr>
    <td>👤 Ref.</td>
    <td><img src="https://img.shields.io/badge/Human-Reference-6b7280" alt="Human"></td>
    <td><code>Human</code></td>
    <td><b>92.00%</b></td>
    <td>92/100</td>
    <td>96.00%</td>
    <td>100.00%</td>
    <td>84.00%</td>
    <td>88.00%</td>
  </tr>
  <tr>
    <td>🥇 1</td>
    <td><img src="https://img.shields.io/badge/Google-Gemini-4285F4?logo=google&logoColor=white" alt="Google Gemini"></td>
    <td><code>gemini-3.1-pro-preview</code></td>
    <td>83.00%</td>
    <td>83/100</td>
    <td>96.00%</td>
    <td>76.00%</td>
    <td>72.00%</td>
    <td>88.00%</td>
  </tr>
  <tr>
    <td>🥈 2</td>
    <td><img src="https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white" alt="OpenAI GPT"></td>
    <td><code>gpt-5.4-high</code></td>
    <td>83.00%</td>
    <td>83/100</td>
    <td>88.00%</td>
    <td>84.00%</td>
    <td>76.00%</td>
    <td>84.00%</td>
  </tr>
  <tr>
    <td>🥉 3</td>
    <td><img src="https://img.shields.io/badge/Qwen-Alibaba%20Cloud-FF6A00?logo=alibabacloud&logoColor=white" alt="Qwen"></td>
    <td><code>qwen3.5-397b-a17b</code></td>
    <td>55.00%</td>
    <td>55/100</td>
    <td>76.00%</td>
    <td>36.00%</td>
    <td>56.00%</td>
    <td>52.00%</td>
  </tr>
  <tr>
    <td>4</td>
    <td><img src="https://img.shields.io/badge/Qwen-Alibaba%20Cloud-FF6A00?logo=alibabacloud&logoColor=white" alt="Qwen"></td>
    <td><code>qwen3.5-plus</code></td>
    <td>40.00%</td>
    <td>40/100</td>
    <td>76.00%</td>
    <td>24.00%</td>
    <td>24.00%</td>
    <td>36.00%</td>
  </tr>
  <tr>
    <td>5</td>
    <td><img src="https://img.shields.io/badge/Doubao-ByteDance-000000?logo=bytedance&logoColor=white" alt="Doubao"></td>
    <td><code>doubao-seed-2-0-pro</code></td>
    <td>17.00%</td>
    <td>17/100</td>
    <td>48.00%</td>
    <td>4.00%</td>
    <td>4.00%</td>
    <td>12.00%</td>
  </tr>
  <tr>
    <td>6</td>
    <td><img src="https://img.shields.io/badge/Kimi-Moonshot-14B8A6" alt="Kimi"></td>
    <td><code>kimi-k2.5</code></td>
    <td>2.00%</td>
    <td>2/100</td>
    <td>8.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>7</td>
    <td><img src="https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white" alt="OpenAI GPT"></td>
    <td><code>gpt-5.4</code></td>
    <td>1.00%</td>
    <td>1/100</td>
    <td>4.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>8</td>
    <td><img src="https://img.shields.io/badge/DeepSeek-DeepSeek-4D6BFE" alt="DeepSeek"></td>
    <td><code>deepseek-v3.2</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>9</td>
    <td><img src="https://img.shields.io/badge/GLM-Zhipu%20AI-2563EB" alt="GLM"></td>
    <td><code>glm-5</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>10</td>
    <td><img src="https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white" alt="OpenAI GPT"></td>
    <td><code>gpt-5.2</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>11</td>
    <td><img src="https://img.shields.io/badge/Grok-xAI-000000?logo=x&logoColor=white" alt="Grok"></td>
    <td><code>grok-4-1-fast-non-reasoning</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>12</td>
    <td><img src="https://img.shields.io/badge/Grok-xAI-000000?logo=x&logoColor=white" alt="Grok"></td>
    <td><code>grok-4-1-fast-reasoning</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
  <tr>
    <td>13</td>
    <td><img src="https://img.shields.io/badge/Llama-Meta-0866FF?logo=meta&logoColor=white" alt="Llama"></td>
    <td><code>llama-4-maverick</code></td>
    <td>0.00%</td>
    <td>0/100</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
    <td>0.00%</td>
  </tr>
</table>

## Evaluate Your Own Model

The repo includes both a generic evaluator and the public leaderboard runner.

1. **Run generic evaluation**

```bash
python eval.py \
  --input MathSticks_bench_400.jsonl \
  --image-dir ./image \
  --output predictions.jsonl
```

2. **Score predictions**

```bash
python cal_score.py \
  --pred predictions.jsonl \
  --label MathSticks_bench_400.jsonl \
  --output score.json
```

3. **Reproduce the public `100`-item leaderboard snapshot**

```bash
API_KEY=xxx BASE_URL=https://your-proxy.example/v1 ./run_api_eval.sh
```

This uses the committed [`MathSticks_bench_100.jsonl`](MathSticks_bench_100.jsonl) subset and writes detailed outputs under [`baseline_eval_results_100_subset/`](baseline_eval_results_100_subset). The default public snapshot is <b>pure-visual</b>, so the model only receives the rendered image.

## Collaboration and Open Evaluation

We welcome community submissions of new model results.

Please:

1. Evaluate on [`MathSticks_bench_100.jsonl`](MathSticks_bench_100.jsonl) so submissions stay comparable.
2. Add both the detailed per-example output file (`<model>.json`) and the summary score file (`<model>.score.json`) under [`baseline_eval_results_100_subset/`](baseline_eval_results_100_subset).
3. Refresh [`baseline_eval_results_100_subset/leaderboard.json`](baseline_eval_results_100_subset/leaderboard.json) and [`baseline_eval_results_100_subset/leaderboard.md`](baseline_eval_results_100_subset/leaderboard.md).
4. Mention the provider/API and any non-default evaluation settings in the PR description.

## <img src="https://img.shields.io/badge/📘-Benchmark%20Format-2563eb" alt="Benchmark format">

<details>
<summary><b>Benchmark JSONL format</b></summary>

Each line in the benchmark JSONL contains one puzzle with the following fields:

- `id`: unique sample identifier, e.g. `"00075585"`.
- `level`: difficulty level in `1-4`.
- `image`: image path relative to repo root, e.g. `level1/00075585_8-9=3.png`.
- `problem`: the displayed equation string.
- `solution_num`: `[one_move_count, two_move_count]`.
- `mode_1_solution`: canonical one-move solutions.
- `mode_2_solution`: canonical two-move solutions.
- `option_answer`: order-invariant move representation for robust parsing.

Example:

```json
{
  "id": "00075585",
  "level": 1,
  "problem": "8-9=3",
  "image": "level1/00075585_8-9=3.png",
  "solution_num": [0, 4],
  "mode_1_solution": [],
  "mode_2_solution": [
    {"solution": "8 - 6 = 2", "moves": ["Move(B2, B5)", "Move(C3, C5)"]},
    {"solution": "9 - 9 = 0", "moves": ["Move(A5, C5)", "Move(C0, C6)"]},
    {"solution": "6 + 3 = 9", "moves": ["Move(A2, G0)", "Move(B6, C6)"]},
    {"solution": "9 - 0 = 9", "moves": ["Move(A5, B5)", "Move(B0, C6)"]}
  ],
  "option_answer": {
    "mode_1": [],
    "mode_2": [
      {"pick": ["B2", "C3"], "place": ["B5", "C5"]},
      {"pick": ["A5", "C0"], "place": ["C5", "C6"]},
      {"pick": ["A2", "B6"], "place": ["G0", "C6"]},
      {"pick": ["A5", "B0"], "place": ["B5", "C6"]}
    ]
  }
}
```

</details>

<details>
<summary><b>Evaluation protocol</b></summary>

- Input can be pure-visual or text-guided.
- The model must output a boxed `Move(...)` or a pair of moves in the specified format.
- Scoring checks both semantic validity and exact move-format parsing.
- Results can be broken down by level, move budget, solution multiplicity, and operator variation.

</details>

## Citation

If MathSticks, the public leaderboard, or the evaluation pipeline helps your work, please cite:

```bibtex
@article{mathsticks2025,
  title   = {MathSticks: A Benchmark for Visual Symbolic Compositional Reasoning with Matchstick Puzzles},
  author  = {Ji, Yuheng and Tan, Huajie and Chi, Cheng and Xu, Yijie and Zhao, Yuting and Zhou, Enshen and Lyu, Huaihai and Wang, Pengwei and Wang, Zhongyuan and Zhang, Shanghang and Zheng, xiaolong},
  journal = {arXiv preprint arXiv:2510.00483},
  year    = {2025}
}
```
