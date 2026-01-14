from data import dataHandler
import json
from prover9 import Prover9
import pandas as pd

datacount = 1204

def filterCorrectProblems(df, _prover9, limit=20):
    correct_problems = []

    for i in range(len(df)):
        try:
            # Try to prove the problem
            is_wrong = _prover9.idToProve(i, df)

            # If is_wrong == 0, then the label matches the prover9 result (proven correct)
            if is_wrong == 0:
                correct_problems.append(i)
                if len(correct_problems) >= limit:
                    break
        except Exception as e:
            # Skip problems that are not well-formatted
            continue

    # Return a dataframe with the filtered problems
    filtered_df = df.iloc[correct_problems].reset_index(drop=True)
    return filtered_df

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:

    for i in range(datacount-1):
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
        provenCorrectly out of well formated:  % 0.7978410206084396
        correctDatasize:   1019
        provenCorrectly out of all:  % 0.675249169435216
        new golden dataset:   813
    """

if __name__ == '__main__':
    _prover9 = Prover9()
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



    with open("../llm_fol.json", "r", encoding="utf-8") as f:
        llm_data = json.load(f)

    for i in llm_data:
        premises = i["premises_FOL"] if "premises_FOL" in i else i["premises"]
        concl = i["conclusion_FOL"] if "conclusion_FOL" in i else i["conclusion"]

        # premises is a big newline string in your JSON -> split into lines
        if isinstance(premises, str):
            premises = [ln.strip() for ln in premises.splitlines() if ln.strip()]

        pred = _prover9.predict_label(premises, concl)
        print(i.get("example_id"), i.get("story_id"), pred, "gold:", i.get("label"))