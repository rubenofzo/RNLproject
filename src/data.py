import re
from datasets import load_from_disk
from datasets import load_dataset
import os

from huggingface_hub import login


class dataHandler:
    def __init__(self):
        # pull dataset
        path = "data/raw"
        if not os.path.exists(path):
            # login("")
            dataset = load_dataset("yale-nlp/FOLIO")
            dataset.save_to_disk(path)
        else:
            dataset = load_from_disk(path)
        self.rawDataset = dataset

    def saveCsvData(self,name,dataset):
        dataset.to_csv(f"data/{name}.csv", index=False)

    def cleanData(self,df):
        oldNew = {
        #"Building(emmetBuilding) ∧ Five-Story(emmetBuilding) ∧ LocatedIn(emmetBuilding, portland) ∧ LocatedIn(portland, oregon))":
        #"Building(emmetBuilding) ∧ Five-Story(emmetBuilding) ∧ LocatedIn(emmetBuilding, portland) ∧ LocatedIn(portland, oregon)",

        "Customer(lily) ∧ In(lily, jameSFamily ∧ WatchIn(lily, tV, cinema)":
        "Customer(lily) ∧ In(lily, jameSFamily) ∧ WatchIn(lily, tV, cinema)",

        "pSOJ318.5-22" : "pSOJ3185_22",

        "¬Contain(tikTok, chatFeature) ∨ ¬ComputerProgram(tikTok))":"¬Contain(tikTok, chatFeature) ∨ ¬ComputerProgram(tikTok)",
        "Contain(tikTok, chatFeature) ⊕ ComputerProgram(tikTok))":"Contain(tikTok, chatFeature) ⊕ ComputerProgram(tikTok)",

        "Five-Story" : "FiveStory",
        "l-2021" : "l2021"
        }

        for old, new in oldNew.items():
            df["premises-FOL"] = df["premises-FOL"].str.replace(old, new, regex=False)
            df["conclusion-FOL"] = df["conclusion-FOL"].str.replace(old, new, regex=False)

        df["premises-FOL"] = df["premises-FOL"].replace(to_replace=r"(?<=\S)[-_](?=\S)", value='',regex=True)
        self.saveCsvData("clean",df)
        self.cleanDataset = df
        return df