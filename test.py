from datasets import load_dataset
import pandas as pd
import json
ds = load_dataset("tasksource/folio")
print(ds["train"][0].keys())


# explore dataset
def printInstance(id):
    print('example premise')
    print('Premises')
    print('---------------')
    print(ds["train"][id]['premises'])
    print('---------------')
    print('FOL premises')
    print('---------------')
    print(ds["train"][id]['premises-FOL'])
    print('---------------')
    print('conclusion')
    print('---------------')
    print(ds["train"][id]['conclusion'])
    print('---------------')
    print('conclusion-FOL')
    print('---------------')
    print(ds["train"][id]['conclusion-FOL'])

# all entries (all conclusions separate)
df = pd.DataFrame(ds["train"])
print(df)
# all unique premise sets 
df["premises_key"] = df["premises"].apply(lambda x: json.dumps(x, ensure_ascii=False))
unique_premises = df.drop_duplicates("premises_key")[["premises_key","premises","premises-FOL"]]
print(len(unique_premises))


printInstance(20)