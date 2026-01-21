import os
os.environ["PROVER9"] = "/home/rubyorsmth/Documents/programmingFiles/RNLproject/prover9/bin/prover9"
import subprocess
import nltk
import re
str2exp = nltk.sem.Expression.fromstring
verbose = False
verbose2 = False
import csv
import os
from pathlib import Path
class Prover9:
    def __init__(self,runid):
        subprocess.run("wget -nv -O prover9.zip https://naturallogic.pro/_files_/download/RNL/prover9_64/prover9_2009_11A_64bit.zip", shell=True)
        subprocess.run("unzip -oq prover9.zip", shell=True)
        self.prover9 = nltk.Prover9()
        # self.prover9.config_prover9(r"C:\Program Files (x86)\Prover9-Mace4\bin-win32")
        self.prover9.config_prover9("/content/prover9/bin")
        self.runid = runid


    def init_csv(self,path):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf8") as f:
                f.write("id,premise,conclusion,premises-FOL,conclusion-FOL,label\n")

    # call to prove case i from df, so df[i]
    def proveSingleProblem(self,i,df,wrongCounter,badFormatCounter):
        try:
            _premise,_conclusion,_label,_NLpremise,_NLconclusion = datasetTriple(i,df)
            prover9Answer = self.theoremProve(_premise, _conclusion)
            if _label != prover9Answer:
                if verbose2:
                    print(id)
                    print("old premise & conc")
                    print(_premise[0])
                    print(_conclusion)
                    self.theoremProve(_premise, _conclusion)
                    print(":(",_label," is not ", prover9Answer)
                    print()
                wrongCounter += 1
            else:
                path = f"data/gold/{self.runid}.csv"
                self.init_csv(path)
                with open(path, "a", encoding="utf8", newline="") as f:
                    csv.writer(f).writerow([i, _NLpremise,_NLconclusion,_premise, _conclusion, _label])
        except Exception as e: 
            if verbose:
                _premise,_conclusion,_label,_,_ = datasetTriple(i,df)
                print("wrong format: ",i)
                print(repr(e))
                print(_premise)
                print(_conclusion)
                print()
            badFormatCounter += 1
        return wrongCounter,badFormatCounter
    
    # return 1 if lable was correct
    # def idToProve(self,id,_df):
    #     _premise,_conclusion,_label = datasetTriple(id,_df)
    #     prover9Answer = self.theoremProve(_premise, _conclusion)
    #     if _label != prover9Answer:
    #         if verbose:
    #             print(id)
    #             print("old premise & conc")
    #             print(_premise[0])
    #             print(_conclusion)
    #             self.theoremProve(_premise, _conclusion,help=True)
    #             print(":(",_label," is not ", prover9Answer)
    #             print()
    #         return 1
    #     return 0
    
    def theoremProve(self,premises, conclusion):
        if type(premises) == str: 
            premises = premises.split('\n')
        _premises = [ folioToProver9(s) for s in premises ]
        _conclusion = folioToProver9(conclusion)
        if verbose2:
            print("premise",_premises[0])
            print("conclusion: ",_conclusion)
        prover9true = str(self.prover9.prove(str2exp(_conclusion), [ str2exp(p) for p in _premises ]))
        if prover9true == "True":
            return "True"
        prover9false = str(self.prover9.prove(str2exp(negate(_conclusion)), [ str2exp(p) for p in _premises ]))
        if prover9false == "True":
            return "False"
        return "Uncertain"

    # def predict_label(self, premises_fol, conclusion_fol) -> str:
        # # premises_fol can be list[str] or newline-separated str
        # if isinstance(premises_fol, str):
        #     premises_fol = premises_fol.split("\n")

        # P = [folioToProver9(p) for p in premises_fol if str(p).strip()]
        # H = folioToProver9(conclusion_fol)

        # entailed = self.prover9.prove(str2exp(H), [str2exp(p) for p in P])
        # if entailed:
        #     return "True"

        # contradicted = self.prover9.prove(str2exp(negate(H)), [str2exp(p) for p in P])
        # if contradicted:
        #     return "False"

        # return "Uncertain"

## Functions to convert FOLIO logical syntax to Prover9 syntax.
def folioToProver9(s):
    #ensure bracket count
    def addMissingBrackets(s: str) -> str:
        balance = s.count('(') - s.count(')')
        if balance < 0:
            # if the balance is below 0, there are more ) than ( so a ( should be added (in the front)
            return ('('*balance) + s
        if balance > 0:
            return s + (')'*balance)
        return s
    s = addMissingBrackets(s)

    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()

    ## logic symbol swaps
    replacements = {
        "⊕": "|",
        "¬": "-",
        "∧": "&", 
        "∨": "|",
        "→": "->",
        "—>":"->",
        "←": "<-",
        "↔": "<->",
    }

    s = expand_xor(s)
    s = re.sub(r"∀\s*([a-zA-Z]\w*)", r"all \1", s)
    s = re.sub(r"∃\s*([a-zA-Z]\w*)", r"exists \1", s)
    for k, v in replacements.items():
        s = s.replace(k, v)

    # double brackets
    s = re.sub(r"\(\s*\(", "((", s)
    s = re.sub(r"\)\s*\)", "))", s)

    return s

# function to turn XOR into logical equivalent
def expand_xor(expr):
    """
    Expand XOR (⊕) to its equivalent form using AND and OR.
    XOR: p ⊕ q = (p & -q) | (-p & q)
    """
    def negate(term):
        """negate expression"""
        term = term.strip()
        # If already negated with -, remove it
        if term.startswith('-'):
            # Remove the negation
            inner = term[1:].strip()
            # If it was -(expr), return expr without outer parens if safe
            if inner.startswith('(') and inner.endswith(')'):
                return inner[1:-1]
            return inner
        # If starts with ¬, remove it
        if term.startswith('¬'):
            inner = term[1:].strip()
            if inner.startswith('(') and inner.endswith(')'):
                return inner[1:-1]
            return inner
        # Otherwise add negation
        # Wrap in parens if it contains operators (but not function calls)
        if any(op in term for op in ['&', '|', '->', '∧', '∨', '→', '⊕']):
            return f'-({term})'
        return f'-{term}'
    def replace_xor(match):
        left = match.group(1).strip()
        right = match.group(2).strip()
        
        # Build: (left & -right) | (-left & right)
        not_left = negate(left)
        not_right = negate(right)
        
        return f'(({left} & {not_right}) | ({not_left} & {right}))'
    
    # This pattern matches an operand which can be:
    # [-¬]? (negation) followed by either:
    # - \w+\([^)]*(?:\([^)]*\)[^)]*)*\) (function with args, allowing nested parens)
    # - \([^()]*(?:\([^()]*\)[^()]*)*\) (parenthesized expression)
    # - \w+ (simple variable)
    operand_pattern = r'(?:[-¬]?\s*(?:\w+\([^)]*(?:\([^)]*\)[^)]*)*\)|\([^()]*(?:\([^()]*\)[^()]*)*\)|\w+))'
    xor_pattern = rf'({operand_pattern})\s*⊕\s*({operand_pattern})'
    
    # Keep replacing until no more XORs found
    prev = None
    max_iterations = 10
    iterations = 0
    while prev != expr and iterations < max_iterations:
        prev = expr
        expr = re.sub(xor_pattern, replace_xor, expr)
        iterations += 1
    
    return expr

# helper functions

def negate(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("-"):
        return expr[1:].strip()
    return f"-({expr})"

def datasetTriple(id,_df):
        return _df['premises-FOL'][id],_df['conclusion-FOL'][id],_df['label'][id],_df['premises'][id],_df['conclusion'][id]

# def labelToBool(label):
#     if label == "Uncertain" or label == "False":
#         return False
#     elif label == "True":
#         return True
#     else:
#         print("help :(")
#         print(label)

