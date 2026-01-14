from data import dataHandler
from prover9 import Prover9
import pandas as pd

def setMaxBaseline(df,_prover9):
    badFormatCounter = 0
    wrongCounter = 0
    # test if all theorems get proves:

    for i in range(1000):
        wrongCounter,badFormatCounter = _prover9.proveSingleProblem(i,df,wrongCounter,badFormatCounter)

    maxBaselineScore(badFormatCounter,wrongCounter)

def maxBaselineScore(badFormatCounter,wrongCounter):
    datacount = 1000
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
    formattedIncorrectly: 169
    ProcentageWellFormated:  % 0.8311688311688312
    Maximum baseline
    usefulDatasize:   832
    provenCorrectly:   663
    provenCorrectly out of all:  % 0.6623376623376623
    provenCorrectly out of well formated:  % 0.796875
    """

if __name__ == '__main__':
    _prover9 = Prover9()
    # load data
    data = dataHandler()
    trainingData = data.rawDataset["train"]
    train_df = pd.DataFrame(trainingData)
    train_df = data.cleanData(train_df)
    setMaxBaseline(train_df,_prover9)

