from openai import OpenAI
from google import genai
from pathlib import Path
import os
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading




class Pipeline:
    def __init__(self,runid):
        # Set your OpenAI API key here

        self.openai_client = OpenAI(api_key=openai_api_key)
        self.gemini_client = genai.Client(api_key=gemini_api_key)

        self.runid = runid
        self.write_lock = threading.Lock()


    def promptLLM(self,prompt, llm, openai_model="gpt-5.1-2025-11-13", gemini_model="gemini-2.5-flash"):
        try:
            if llm == "openai":
                response = self.openai_client.responses.create(
                    model=openai_model,
                    input=prompt
                )
                return response.output_text

            elif llm == "gemini":
                response = self.gemini_client.models.generate_content(
                    model=gemini_model,
                    contents=prompt
                )
                return response.text

        except Exception as e:
            print(f"Error: {e}")
            return None

    def runPipeline(self, llm, experimentsize=10, outputDir="experiment1"):
        df = self.importPromptdata()

        self.output_path_all_data = Path(f"output/{outputDir}/alldata/{self.runid}_{llm}.jsonl")
        self.output_path_clean = Path(f"output/{outputDir}/results/{self.runid}_{llm}.jsonl")
        self.output_path_all_data.parent.mkdir(parents=True, exist_ok=True)
        self.output_path_clean.parent.mkdir(parents=True, exist_ok=True)

        # run the first N rows (cap at df length), or loop over full df if experimentsize=0
        n = min(experimentsize, len(df))# or len(df)

        with ThreadPoolExecutor(max_workers=16) as executor: #run in seperate threads to make parralel, max_workers is for rate limit
             futures = [
                 executor.submit(self.processRow, df.iloc[i], llm)
                 for i in range(n)
             ]

             for fut in as_completed(futures):
                 fut.result()

        print(f"Wrote {n} records to: {self.output_path_all_data.resolve()}")

    def processRow(self,row,llm):
        try:
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
                
                premises: "{premises}"
                premises_FOL: "{premises_fol}"
                conclusion: "{conclusion}"
            """

            response = self.promptLLM(prompt, llm=llm)
            #print("gold:  " + conclusion_fol)
            #print("ai:    " + response)
            #print("-----")

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

            with self.write_lock:
                with open(self.output_path_all_data, "a", encoding="utf8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

                with open(self.output_path_clean, "a", encoding="utf8") as f:
                    f.write(json.dumps(record_clean, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error on row {row['id']}: {e}")

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
