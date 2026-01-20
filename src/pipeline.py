from openai import OpenAI
from pathlib import Path
import os
import json

class Pipeline:
    def __init__(self,runid):
        # Set your OpenAI API key here
        api_key = os.getenv("OPENAI_API_KEY")  # Or set it directly: api_key = "your-api-key-here"
        self.client = OpenAI(api_key=api_key)
        self.runid = runid

    def promptLLM(self,prompt, model="gpt-5.1-2025-11-13",outputDir="experiment1"):
        try:
            response = self.client.responses.create(
                model=model,
                input=prompt
            )
            answer = response.output_text

            record = {
                "run_id": self.runid,
                "model": model,
                "prompt": prompt,
                "output": answer
            }

            # Write the answer to the file
            path = Path(f"output/{outputDir}/{self.runid}.txt")
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf8") as f:
                f.write(json.dumps(record) + "\n")

            return record["output"]

        except Exception as e:
            print(f"Error: {e}")
            return None

    def runPipeline(self,experimentSize=1,outputDir="experiment1"):
        for i in range(experimentSize):
            prompt = "Explain machine learning simply."
            response = self.promptLLM(prompt,outputDir=outputDir)
            print("Response:", response)
        