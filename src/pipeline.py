from openai import OpenAI
from pathlib import Path
import os
import json
import pandas as pd


class Pipeline:
    def __init__(self,runid):
        # Set your OpenAI API key here
        api_key = ("sk-proj-EkdySd_E0Oz6J_MrZFZ-d6-j3Wo0rxBq5UA" 
                   "O-ha9A0__zqKWSPO8yVkN9HPLPrLOimdODEGB7yc"
                            "BSNfwhQDGiK9dU5Oqbq1EA")

        self.client = OpenAI(api_key=api_key)
        self.runid = runid

    def promptLLM(self,prompt, model="gpt-5.1-2025-11-13"):
        try:
            response = self.client.responses.create(
                model=model,
                input=prompt
            )
            answer = response.output_text
            return answer

        except Exception as e:
            print(f"Error: {e}")
            return None

    def runPipeline(self, experimentsize=0, outputDir="experiment1"):
        df = self.importPromptdata()

        output_path_all_data = Path(f"output/{outputDir}/alldata/{self.runid}.jsonl")
        output_path_clean = Path(f"output/{outputDir}/results/{self.runid}.jsonl")
        output_path_all_data.parent.mkdir(parents=True, exist_ok=True)
        output_path_clean.parent.mkdir(parents=True, exist_ok=True)

        # run the first N rows (cap at df length), or loop over full df if experimentsize=0
        n = min(experimentsize, len(df)) or len(df)

        for i in range(n):
            row = df.iloc[i]

            premises = str(row["premise"]).strip()
            premises_fol = str(row["premises-FOL"]).strip()
            conclusion = str(row["conclusion"]).strip()
            conclusion_fol = str(row["conclusion-FOL"]).strip()

            prompt = f"""
                Convert the following conclusion into first-order logic (FOL) for Prover9.
    
                Rules:
                - Use only: all, exists, ->, &, |, -, =
                - Keep predicate and constant names consistent across ALL statements.
                - Output ONLY one valid string.
                - Only convert the conclusion, do return or modify the premises.
                - Do not introduce new named entities/constants in the conclusion.
                - Be very careful with negation. If the natural language contains ‘not’ or ‘unaware’, that must appear as -Predicate(...)
                - Double-check the final formula by restating it in English.
                - When translating to Prover9, represent exclusive "either/or" statements using the negated equivalence syntax -(A <-> B). instead of the inclusive disjunction |.
                
                premises: "{premises}"
                premises_FOL: "{premises_fol}"
                conclusion: "{conclusion}"
            """

            response = self.promptLLM(prompt)
            print("gold:  " + conclusion_fol)
            print("ai:    " + response)
            print("-----")

            record = {
                "story_id": int(row["id"]),
                "label": str(row["label"]),
                "premises": premises,
                "premises-FOL": premises_fol,
                "conclusion": conclusion,
                "conclusion-FOL": conclusion_fol,
                "llm_conclusion-FOL": response,
            }

            record_clean = {
                "story_id": int(row["id"]),
                "label": str(row["label"]),
                "conclusion-FOL": conclusion_fol,
                "llm_conclusion-FOL": response,
            }

            with open(output_path_all_data, "a", encoding="utf8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            with open(output_path_clean, "a", encoding="utf8") as f:
                f.write(json.dumps(record_clean, ensure_ascii=False) + "\n")

        print(f"Wrote {n} records to: {output_path_all_data.resolve()}")



    @staticmethod
    def importPromptdata():
        # read clean.csv from data/gold/ and return as dataframe
        path = Path(f"data/gold/gold.csv")
        if path.exists():
            df = pd.read_csv(path)
            return df
        else:
            print(f"File {path} does not exist.")
            return None
