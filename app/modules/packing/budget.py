from collections import defaultdict
from fractions import Fraction


def budgets(supply):
    outputs=defaultdict(list)
    for row in supply['outputs'].values():
        outputs[row['work']].append(row)
    result={}
    for work,job in supply['jobs'].items():
        issued=sum((Fraction(row['g']) for row in outputs[work]),Fraction())
        remaining=Fraction(job['g'])-issued
        code=None
        if work in supply['by_output_issue']:
            code='OUTPUT_DISPUTE'
        elif remaining<0:
            code='NEGATIVE_REMAINDER'
        result[work]=dict(outputs=outputs[work],issued_g=str(issued),remaining_g=str(remaining),code=code,
                          rejected=supply['by_output_issue'].get(work,[]))
    return result
