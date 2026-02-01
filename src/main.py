from pathlib import Path
from data import dataHandler
import json
from prover9 import Prover9
import pandas as pd
from datetime import datetime
from pipeline import Pipeline

def evaluate_df(df,_prover9,PC=False):
    badFormatCounterLabel = badFormatCounterConc = badFormatCounterPrem = 0
    amountWrongLabel = amountWrongConcl = amountWrongPC =0
    metric3bad = metric4bad = metric5bad = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        amountWrongLabel,badFormatCounterLabel = _prover9.proveSingleProblem(i,df,amountWrongLabel,badFormatCounterLabel,LLMConclusion=True)
        amountWrongConcl,badFormatCounterConc = _prover9.evaluateConclusion(i,df,amountWrongConcl,badFormatCounterConc)
        if PC:
            metric3bad,metric4bad,metric5bad,badFormatCounterPrem = _prover9.evaluatePremises(i,df,metric3bad,metric4bad,metric5bad,badFormatCounterPrem)

    if badFormatCounterLabel != badFormatCounterConc != badFormatCounterPrem:
        print("Bad format counts not the same??")
        print(badFormatCounterLabel,badFormatCounterConc,badFormatCounterPrem)
    badFormatCounter = max(badFormatCounterLabel,badFormatCounterConc,badFormatCounterPrem)

    printScore(badFormatCounter, amountWrongLabel, amountWrongConcl,metric3bad,metric4bad,metric5bad, datacount, PC=PC)

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:
    datacount = len(df.index)
    for i in range(datacount):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)
    printScore(badFormatCounter,wrongCounter,0,datacount)

def printScore(badFormatCounter,amountWrongLabel,amountWrongConcl,metric3bad,metric4bad,metric5bad,datacount,PC=False):
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
    printProvenStats(amountWrongLabel,badFormatCounter,datacount)

    print("---")
    print("- Does dfConcl <-> llmConcl?")
    printProvenStats(amountWrongConcl,badFormatCounter,datacount)

    if not PC:
        return
    print("---")
    print("- Does P => LLMP?")
    printProvenStats(metric3bad,badFormatCounter,datacount)

    print("---")
    print("- Does dfPrem+Concl <-> llmPrem+Concl?")
    printProvenStats(metric4bad,badFormatCounter,datacount)
    
    print("---")
    print("- Does dfPrem+dfConcl <-> llmPrem+llmConcl?")
    printProvenStats(metric5bad,badFormatCounter,datacount)

def printProvenStats(_amountWrong,_badFormatCounter,_datacount):
    _amountBadFormat = (_datacount-_badFormatCounter)
    if _amountBadFormat != 0:
        print("provenCorrectly out of well formated:  %",(_amountBadFormat-_amountWrong)/_amountBadFormat)
    else:
        print("all bad formats :(")
    _correctlyProven = _datacount-_amountWrong-_badFormatCounter
    print("correctly proven data out of all:  %",_correctlyProven/_datacount)
    print("correctly proven data count:  ",_correctlyProven)
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
evaluateLLM = False
evaluateAllLLms = True
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
        pipeline.runPipeline(llm="gemini")

    if evaluateLLM:
        # Convert the latest experiment results to dataframe
        folder = Path("output/experiment1/alldata")
        latest_file = max(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        df = pd.read_json(latest_file, lines=True)

        # Uncomment if specific file is needed
        # df = pd.read_json(Path("output/experiment1/alldata/20260121_175824_gemini.jsonl"), lines=True)
        # make Prover9 test the LLM conclusion instead of the gold one
        evaluate_df(df,_prover9)

    if evaluateAllLLms:
        # print("Experiment 1: FOL conclusion generation")
        # print("Gemini")
        # df = pd.read_json("output/experiment1/alldata/20260123_174547_gemini_all_cases.jsonl", lines=True)
        # evaluate_df(df,_prover9)
        # print()
        # print("ChatGPT")
        # df2 = pd.read_json("output/experiment1/alldata/20260121_175824_openai_all_cases.jsonl", lines=True)
        # evaluate_df(df2,_prover9)
        
        print("Experiment 2: FOL premises + conclusion generation")
        print("Gemini")
        df3 = pd.read_json("output/experiment1/alldata/20260128_203053_gemini_all_cases.jsonl", lines=True) 
        evaluate_df(df3,_prover9,PC=True)
        print()
        print("ChatGPT")
        df4 = pd.read_json("output/experiment1/alldata/20260128_202827_openai_all_cases.jsonl", lines=True)
        evaluate_df(df4,_prover9,PC=True)

    #results

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
