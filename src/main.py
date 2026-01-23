from pathlib import Path
from data import dataHandler
import json
from prover9 import Prover9
import pandas as pd
from datetime import datetime
from pipeline import Pipeline

def evaluate_df(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)
        wrongCounter,badFormatCounter = _prover9.compareConclusion(i,df,wrongCounter,badFormatCounter)

    maxBaselineScore(badFormatCounter,wrongCounter,datacount)

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)

    maxBaselineScore(badFormatCounter,wrongCounter,datacount)

def maxBaselineScore(badFormatCounter,wrongCounter,datacount):
    amountBadFormat = (datacount-badFormatCounter)
    print("formattedIncorrectly:",badFormatCounter)
    if datacount != 0:
        print("ProcentageWellFormated:"," %",amountBadFormat/datacount)
    else:
        print("no data?")
        return
    print("Maximum baseline")
    if amountBadFormat != 0:
        print("provenCorrectly out of well formated:  %",(amountBadFormat-wrongCounter)/amountBadFormat)
    else:
        print("all bad formats :(")
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

#config

setGoldCSV = False
runExperimentGPT = False
runExperimentGemini = False
evaluateLLM = False
LLMtest = False


if __name__ == '__main__':
    runid = datetime.now().strftime("%Y%m%d_%H%M%S")
    _prover9 = Prover9(runid)
    #folder = Path("output/experiment1/alldata")
    #latest_file = max(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    df = pd.read_json("output/experiment1/alldata/20260121_175824_all_cases.jsonl", lines=True)
    evaluate_df(df,_prover9)

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

    if runExperimentGPT:
        pipeline = Pipeline(runid)
        pipeline.runPipeline(llm="openai")

    if runExperimentGemini:
        pipeline = Pipeline(runid)
        pipeline.runPipeline(llm="gemini", experimentsize=50)

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
