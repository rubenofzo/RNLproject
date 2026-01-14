from data import dataHandler
from prover9 import Prover9
import pandas as pd

datacount = 1204

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

