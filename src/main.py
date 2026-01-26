from pathlib import Path
from data import dataHandler
import json
from prover9 import Prover9
import pandas as pd
from datetime import datetime
from pipeline import Pipeline

def evaluate_df(df,_prover9):
    badFormatCounterLabel = badFormatCounterConc = 0
    amountWrongLabel = amountWrongConcl = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        amountWrongLabel,badFormatCounterLabel = _prover9.proveSingleProblem(i,df,amountWrongLabel,badFormatCounterLabel,againstLLM=True)
        amountWrongConcl,badFormatCounterConc = _prover9.compareConclusion(i,df,amountWrongConcl,badFormatCounterConc)

    if badFormatCounterLabel != badFormatCounterConc:
        print("Bad format counts not the same??")
        print(badFormatCounterLabel,badFormatCounterConc)
    badFormatCounter = max(badFormatCounterLabel,badFormatCounterConc)
    printScore(badFormatCounter,amountWrongLabel,amountWrongConcl,datacount)

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)
    printScore(badFormatCounter,wrongCounter,0,datacount)

def printScore(badFormatCounter,amountWrongLabel,amountWrongConcl,datacount):
    print("---")
    print("- Data information:")
    print("datasize:",datacount)
    amountBadFormat = (datacount-badFormatCounter)
    print("formattedIncorrectly:",badFormatCounter)
    if datacount != 0:
        print("ProcentageWellFormated:"," %",amountBadFormat/datacount)
        print("WellFormatedDatasize:  ",datacount-badFormatCounter)
    else:
        print("no data?")
        return
    
    print("---")
    print("- Does dfLabel == llmLabel?")
    if amountBadFormat != 0:
        print("provenCorrectly out of well formated:  %",(amountBadFormat-amountWrongLabel)/amountBadFormat)
    else:
        print("all bad formats :(")
    correctlyProvenLabel = datacount-amountWrongLabel-badFormatCounter
    print("correctly proven data out of all:  %",correctlyProvenLabel/datacount)
    print("correctly proven data count:  ",correctlyProvenLabel)

    print("---")
    print("- Does dfConcl <-> llmConcl?")
    if amountBadFormat != 0:
        print("provenCorrectly out of well formated:  %",(amountBadFormat-amountWrongConcl)/amountBadFormat)
    else:
        print("all bad formats :(")
    correctlyProvenConcl = datacount-amountWrongConcl-badFormatCounter
    print("correctly proven data out of all:  %",correctlyProvenConcl/datacount)
    print("correctly proven data count:  ",correctlyProvenConcl)
    #best output for gold data:
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
evaluateLLM = True
LLMtest = False


if __name__ == '__main__':
    runid = datetime.now().strftime("%Y%m%d_%H%M%S")
    _prover9 = Prover9(runid)
    #folder = Path("output/experiment1/alldata")
    #latest_file = max(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    
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
        print("Gemini")
        df = pd.read_json("output/experiment1/alldata/20260123_174547_gemini_all_cases.jsonl", lines=True)
        evaluate_df(df,_prover9)
        print()
        print("ChatGPT")
        df2 = pd.read_json("output/experiment1/alldata/20260121_175824_openai_all_cases.jsonl", lines=True)
        evaluate_df(df2,_prover9)
        # # Convert the latest experiment results to dataframe
        # folder = Path("output/experiment1/alldata")
        # latest_file = max(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        # df = pd.read_json(latest_file, lines=True)

        # # Uncomment if specific file is needed
        # # df = pd.read_json(Path("output/experiment1/alldata/20260121_175824_gemini.jsonl"), lines=True)

        # # make Prover9 test the LLM conclusion instead of the gold one
        # df["conclusion-FOL"] = df["llm_conclusion-FOL"]

        # datacount = len(df)  # if setMaxBaseline uses this global
        # setMaxBaseline(df, _prover9)
    #results
    """
    EXPERIMENT 1: guess FOL concl from FOL prem, NL prem and FOL concl
    Chatgpt
    ---
    - Data information:
    datasize: 683
    formattedIncorrectly: 15
    ProcentageWellFormated:  % 0.9780380673499268
    WellFormatedDatasize:   668
    ---
    - Does dfLabel == llmLabel?
    provenCorrectly out of well formated:  % 0.9236526946107785
    correctly proven data out of all:  % 0.9033674963396779
    correctly proven data count:   617
    ---
    - Does dfConcl <-> llmConcl?
    provenCorrectly out of well formated:  % 0.6826347305389222
    correctly proven data out of all:  % 0.6676427525622255
    correctly proven data count:   456
    
    Gemini
    ---
    - Data information:
    datasize: 683
    formattedIncorrectly: 66
    ProcentageWellFormated:  % 0.9033674963396779
    WellFormatedDatasize:   617
    ---
    - Does dfLabel == llmLabel?
    provenCorrectly out of well formated:  % 0.9724473257698542
    correctly proven data out of all:  % 0.8784773060029283
    correctly proven data count:   600
    ---
    - Does dfConcl <-> llmConcl?
    provenCorrectly out of well formated:  % 0.7811993517017828
    correctly proven data out of all:  % 0.705710102489019
    correctly proven data count:   482
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
