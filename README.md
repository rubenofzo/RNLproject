

# RNLproject — NL → FOL Translation + Prover9 Evaluation

This repository contains the full experimental pipeline used in our **Reasoning with Natural Language** project. The goal is to evaluate how well Large Language Models (LLMs) translate natural-language (NL) premises and conclusions into **Prover9-style first-order logic (FOL)** and verify semantic correctness using **Prover9** (via NLTK).

## What this code does

* **Run NL → FOL translation experiments**: generate Prover9-style first-order logic (premises + conclusion) from natural-language problems using **OpenAI's GPT-5.1** and **Gemini 2.5 flash**.
* **Create a “clean gold” subset**: filter the dataset to only instances where the **gold FOL parses** and **Prover9’s inferred label matches** the dataset label.
* **Automatically verify logic with a theorem prover**: use **Prover9** to classify each problem as **entailed / contradicted / unknown**.
* **Evaluate LLM outputs quantitatively**:

  * check **label agreement** (Prover9 result vs gold label)
  * check **conclusion equivalence under premises** (mutual entailment)
  * run extra combined checks for the full “premises + conclusion” condition
* **Log and inspect failure cases**: export rows that are **wrong format** or **label mismatches** into separate CSVs for debugging.
* **Reproduce and compare multiple runs/models**: save outputs as timestamped **JSONL** files and re-evaluate them later (single run or multiple runs).

At a high level, the main pipeline:

1. **Loads the FOLIO dataset**.
2. **Applies normalization** and cleaning fixes to the gold FOL.
3. **Builds a “clean gold” subset** where Prover9 can parse the gold formulas and the inferred label matches the dataset label.
4. **Prompts an LLM** to generate FOL (premises + conclusion) in a strict machine-parseable format.
5. **Evaluates generated FOL** with Prover9 using:
  * **Label consistency:** Does Prover9’s output match the dataset label?
  * **Conclusion equivalence:** Checks mutual entailment under the story premises.
  * **Premise derivability:** Are generated premises entailed by the gold premises?



All major actions are controlled from `src/main.py` using boolean flags.

---

## Repository Structure

* **`src/main.py`**: Entry point; toggle flags here to run specific steps.
* **`src/data.py`**: Handles FOLIO downloading, caching, and cleaning.
* **`src/pipeline.py`**: Manages LLM prompting and JSONL output generation.
* **`src/fol_clean.py`**: Parses and cleans model responses into FOL strings.
* **`src/prover9.py`**: Prover9 wrapper, evaluation metrics, and symbol normalization.
* **`data/`**: Contains raw, gold, and error-log CSV files.
* **`data/gold/gold.csv`**: Contains the preprocessed gold FOLIO subset.
* **`output/`**: Stores full (`alldata`) and minimal (`results`) JSONL run files.
* **`Results.md`**: Contains our experiment results of running the LLMs over the FOLIO subset and scored by our Prover9 based metrics
* **`output/experiment1/alldata/20260121_175824_openai_all_cases.jsonl and output/experiment1/alldata/20260123_174547_gemini_all_cases.jsonl`**: Contain the LLM answers for the first experiment
* **`output/experiment1/alldata/20260128_203053_gemini_all_cases.jsonl and output/experiment1/alldata/20260128_202827_openai_all_cases.jsonl`**: Contain the LLM answers for the second experiment


---

## Requirements

### Python

* **Recommended:** Python 3.10+
* **Install dependencies:**
```bash
pip install -r requirements.txt

```


## API Keys (OpenAI + Gemini)

The project supports OpenAI and Google Gemini. Own API keys are required for running the experiment. The keys can be set in the Pipeline.py file.

---

## How to Run

Run all commands from the repository root to ensure relative paths resolve correctly:

```bash
python src/main.py

```

### Configuration Flags (`src/main.py`)

Flip the following booleans to `True` to execute specific workflows:

| Flag | Purpose |
| --- | --- |
| `setGoldCSV` | Downloads FOLIO, cleans it, and builds `data/gold/gold.csv`. |
| `runExperimentGPT` | Runs the translation experiment using OpenAI. |
| `runExperimentGemini` | Runs the translation experiment using Google Gemini. |
| `evaluateLLM` | Automatically evaluates the most recent run in the output folder. |
| `evaluateAllLLms` | Evaluates specific hardcoded JSONL paths. |
| `LLMtest` | Performs a quick local test using `llm_fol.json`. |

---

## Evaluation Metrics

The system categorizes results into several buckets:

* **Label Check:** Does Prover9's result (True/False/Uncertain) match the dataset?
* **Conclusion Check:** Are the gold and LLM conclusions mutually entailed?
* **Format Logs:** * **Parsing failures:** Logged to `data/wrong_format/`
* **Label mismatches:** Logged to `data/incorrect_label/`
* **Successes:** Logged to `data/gold/`



---

## Troubleshooting

* **Prover9 not found:** Ensure `config_prover9` points to the folder containing the actual `prover9` executable (not just the parent folder).
* **Invalid JSON:** If the LLM returns malformed JSON, the parser will attempt a line-based fallback. If this fails, the case is marked as `wrong_format`.
* **Rate Limits:** If you hit API limits, reduce the `max_workers` value in `src/pipeline.py`.
---
Made by: Ruben de Boer, Sewal Korkmaz and Selcuk Canak
