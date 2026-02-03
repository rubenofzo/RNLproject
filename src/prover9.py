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
import traceback
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
                f.write("id,NLpremise,NLconclusion,premise-FOL,conclusion-FOL,LLM-conclusion-FOL,label,prover9_answer\n")

    # call to prove case i from df, so df[i]
    def proveSingleProblem(self, i, df, wrongCounter, badFormatCounter,LLMConclusion=False,LLMPremise=False):
        try:
            _premise, _conclusion, _label, _NLpremise, _NLconclusion = fetchFolioRow(i, df)
            orginal_conclusion = _conclusion
            if LLMConclusion:
                _conclusion = df['llm_conclusion-FOL'][i]
            if LLMPremise:
                _premise = df['llm_premises-FOL'][i] 
            prover9Answer = self.theoremProve(_premise, _conclusion)

            if _label != prover9Answer:
                if verbose2:
                    print(id)
                    print("old premise & conc")
                    print(_premise[0])
                    print(_conclusion)
                    self.theoremProve(_premise, _conclusion)
                    print(":(", _label, " is not ", prover9Answer)
                    print()

                wrong_path = f"data/incorrect_label/{self.runid}.csv"
                self.init_csv(wrong_path)
                with open(wrong_path, "a", encoding="utf8", newline="") as f:
                    csv.writer(f).writerow([i, _NLpremise, _NLconclusion, _premise,orginal_conclusion, _conclusion, _label, prover9Answer])

                wrongCounter += 1

            else:
                path = f"data/gold/{self.runid}.csv"
                self.init_csv(path)
                with open(path, "a", encoding="utf8", newline="") as f:
                    csv.writer(f).writerow([i, _NLpremise, _NLconclusion, _premise,orginal_conclusion, _conclusion, _label, prover9Answer])

        except Exception as e:
            _premise, _conclusion, _label, _, _ = fetchFolioRow(i, df)
            if verbose:
                print("wrong format: ", i)
                print(repr(e))
                print(_premise)
                print(_conclusion)
                print()
            badFormatCounter += 1
            wrong_path = f"data/wrong_format/{self.runid}.csv"
            self.init_csv(wrong_path)
            with open(wrong_path, "a", encoding="utf8", newline="") as f:
                csv.writer(f).writerow([i, _premise, _conclusion, _label])

        return wrongCounter, badFormatCounter

    def theoremProve(self, premises, conclusion):

        if isinstance(premises, str):
            premises = premises.split("\n")

        premises = [clean_line(p) for p in premises if clean_line(p)]
        conclusion = clean_line(conclusion)

        _premises = [folioToProver9(s) for s in premises]
        _conclusion = folioToProver9(conclusion)

        prover9true = str(self.prover9.prove(str2exp(_conclusion), [str2exp(p) for p in _premises]))
        if prover9true == "True":
            return "True"

        prover9false = str(self.prover9.prove(str2exp(negate(_conclusion)), [str2exp(p) for p in _premises]))
        if prover9false == "True":
            return "False"

        return "Uncertain"

    def proveBothWaysUnderPremises(self, premises, gold_concl, llm_concl):
        # Old proveBothWays(gold, llm) checked equivalence in empty context (no premises),
        # which is too strict and often false even if they mean the same thing in the story.
        # New: check equivalence GIVEN the premises:
        #   (premises + gold => llm) AND (premises + llm => gold)

        if isinstance(premises, str):
            premises = premises.split("\n")
        premises = [clean_line(p) for p in premises if clean_line(p)]
        gold_concl = clean_line(gold_concl)
        llm_concl = clean_line(llm_concl)

        P = [folioToProver9(p) for p in premises]
        G = folioToProver9(gold_concl)
        L = folioToProver9(llm_concl)

        def entails(assumptions, goal):
            return str(self.prover9.prove(str2exp(goal), [str2exp(a) for a in assumptions])) == "True"

        # test if Premises + gold entail the same as 
        return entails(P + [G], L) and entails(P + [L], G)
    
    def comparePremises(self, llm_premises, gold_premises):
        # Can the premises be derived from the original set of premises? Is no new (false) info deduced? 
        if isinstance(llm_premises, str):
            llm_premises = llm_premises.split("\n")
        if isinstance(gold_premises, str):
            gold_premises = gold_premises.split("\n")
        llm_premises = [clean_line(p) for p in llm_premises if clean_line(p)]
        gold_premises = [clean_line(p) for p in gold_premises if clean_line(p)]

        #print(gold_premises)

        G_P = [folioToProver9(p) for p in gold_premises]
        L_P = [folioToProver9(p) for p in llm_premises]


        def entails(assumptions, goal):
            return str(self.prover9.prove(str2exp(goal), [str2exp(a) for a in assumptions])) == "True"

        result = True
        for l_p in L_P:
            result = result and entails(G_P, l_p)

        # test if Premises + gold entail the same as 
        return result

    def evaluateConclusion(self,i,df,wrongCounter,badFormatCounter):
        try:
            _premise,_conclusion,_label,_NLpremise,_NLconclusion = fetchFolioRow(i,df)
            _llmconclusion= df['llm_conclusion-FOL'][i]
            prover9Answer = self.proveBothWaysUnderPremises(_premise, _conclusion, _llmconclusion)
            if not prover9Answer:
                wrongCounter += 1
        except Exception as e: 
            badFormatCounter += 1
        return wrongCounter,badFormatCounter
    
    def evaluatePremises(self,i,df,metric3bad,metric4bad,metric5bad,badFormatCounter):
        try:
            _premises,_conclusion,_label,_NLpremise,_NLconclusion = fetchFolioRow(i,df)
            _llmconclusion= df['llm_conclusion-FOL'][i]
            _llmpremises= df['llm_premises-FOL'][i]
            # metric 3
            metric3Answer = self.comparePremises(_llmpremises, _premises) #verify if premises can logically be derived
            if not metric3Answer:
                metric3bad += 1
            # metric 4
            # check if label from LLMP + C is same as gold label
            metric4bad,_ = self.proveSingleProblem(i, df, metric4bad, badFormatCounter,LLMPremise=True)
            #metric 5 
            #check if label from LLMP + LLMC is same as gold label
            metric5bad,_ = self.proveSingleProblem(i, df, metric5bad, badFormatCounter,LLMConclusion=True,LLMPremise=True)
        except Exception as e: 
            badFormatCounter += 1
            # print(repr(e))
            # traceback.print_exc()
            # print()
        return metric3bad,metric4bad,metric5bad,badFormatCounter
        
        

## Functions to convert FOLIO logical syntax to Prover9 syntax.
def folioToProver9(s):
    #ensure bracket count
    def addMissingBrackets(s: str) -> str:
        balance = s.count('(') - s.count(')')
        if balance < 0:
            # if the balance is below 0, there are more ) than ( so a ( should be added (in the front)
            return ('(' * (-balance)) + s
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
def clean_line(s: str) -> str:
    s = str(s).strip()
    s = re.sub(r"\.\s*$", "", s)  # drop trailing period
    return s

def negate(expr: str) -> str:
    expr = expr.strip()
    if expr.startswith("-"):
        return expr[1:].strip()
    return f"-({expr})"

def fetchFolioRow(id,_df):
        return _df['premises-FOL'][id],_df['conclusion-FOL'][id],_df['label'][id],_df['premises'][id],_df['conclusion'][id]

def fetchLLManswers(id,_df):
    return _df['llm_premise-FOL'][id],_df['llm_conclusion-FOL'][id]


