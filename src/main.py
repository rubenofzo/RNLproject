from pathlib import Path
from data import dataHandler
import json
from prover9 import Prover9
import pandas as pd
from datetime import datetime
from pipeline import Pipeline

datacount = 1204

# def filterCorrectProblems(df, _prover9, limit=20):
#     correct_problems = []

#     for i in range(len(df)):
#         try:
#             # Try to prove the problem
#             is_wrong = _prover9.idToProve(i, df)

#             # If is_wrong == 0, then the label matches the prover9 result (proven correct)
#             if is_wrong == 0:
#                 correct_problems.append(i)
#                 if len(correct_problems) >= limit:
#                     break
#         except Exception as e:
#             # Skip problems that are not well-formatted
#             continue

#     # Return a dataframe with the filtered problems
#     filtered_df = df.iloc[correct_problems].reset_index(drop=True)
#     return filtered_df

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:

    for i in range(datacount):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)

    maxBaselineScore(badFormatCounter,wrongCounter)

def maxBaselineScore(badFormatCounter,wrongCounter):
    #datacount = 1204
    amountBadFormat = (datacount-badFormatCounter)
    print("formattedIncorrectly:",badFormatCounter)
    print("ProcentageWellFormated:"," %",amountBadFormat/datacount)
    print("Maximum baseline")
    print("provenCorrectly out of well formated:  %",(amountBadFormat-wrongCounter)/amountBadFormat)
    print("correctDatasize:  ",datacount-badFormatCounter)
    print("provenCorrectly out of all:  %",(datacount-wrongCounter-badFormatCounter)/datacount)
    print("new golden dataset:  ",datacount-wrongCounter-badFormatCounter)
    #best output:
    """
        formattedIncorrectly: 185
        ProcentageWellFormated:  % 0.8463455149501661
        Maximum baseline
        provenCorrectly out of well formated:  % 0.6712463199214916
        correctDatasize:   1019
        provenCorrectly out of all:  % 0.5681063122923588
        new golden dataset:   684
    """

if __name__ == '__main__':
    runid = datetime.now().strftime("%Y%m%d_%H%M%S")
    _prover9 = Prover9(runid)

    setGoldCSV = False
    if setGoldCSV:
        # load data
        data = dataHandler()
        trainingData = data.rawDataset["train"]
        validationData = data.rawDataset["validation"]
        train_df = pd.DataFrame(trainingData)
        val_df = pd.DataFrame(validationData)
        full_df = pd.concat([train_df, val_df], ignore_index=True)
        print(full_df.shape)
        full_df = data.cleanData(full_df)
        setMaxBaseline(full_df,_prover9)

    runExperimentGPT = False
    if runExperimentGPT:
        pipeline = Pipeline(runid)
        pipeline.runPipeline(llm="openai")

    runExperimentGemini = True
    if runExperimentGemini:
        pipeline = Pipeline(runid)
        pipeline.runPipeline(llm="gemini", experimentsize=50)

    evaluateLLM = False
    if evaluateLLM:
        # Convert the latest experiment results to dataframe
        folder = Path("output/experiment1/alldata")
        latest_file = max(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        df = pd.read_json(latest_file, lines=True)

        # Uncomment if specific file is needed
        # df = pd.read_json(Path("output/experiment1/alldata/20260121_175824_gemini.jsonl"), lines=True)

        # make Prover9 test the LLM conclusion instead of the gold one
        df["conclusion-FOL"] = df["llm_conclusion-FOL"]

        datacount = len(df)  # if setMaxBaseline uses this global
        setMaxBaseline(df, _prover9)
    # ChatGPT results:
    """
        formattedIncorrectly: 14
        ProcentageWellFormated:  % 0.9795021961932651
        Maximum baseline
        provenCorrectly out of well formated:  % 0.9237668161434978
        correctDatasize:   669
        provenCorrectly out of all:  % 0.9048316251830161
        new golden dataset:   618
    """
    # Gemini results:
    """
        formattedIncorrectly: 1
        ProcentageWellFormated:  % 0.98
        Maximum baseline
        provenCorrectly out of well formated:  % 0.9183673469387755
        correctDatasize:   49
        provenCorrectly out of all:  % 0.9
        new golden dataset:   45
    """



    # Tests the LLM generated FOL directly from a JSON file, used for testing during development
    LLMtest = False
    if LLMtest:
        with open("../llm_fol.json", "r", encoding="utf-8") as f:
            llm_data = json.load(f)

        for i in llm_data:
            premises = i["premises_FOL"] if "premises_FOL" in i else i["premises"]
            concl = i["conclusion_FOL"] if "conclusion_FOL" in i else i["conclusion"]

            # premises is a big newline string in your JSON -> split into lines
            if isinstance(premises, str):
                premises = [ln.strip() for ln in premises.splitlines() if ln.strip()]

            pred = _prover9.theoremProve(premises, concl)
            print(i.get("example_id"), i.get("story_id"), pred, "gold:", i.get("label"))
