from fractions import Fraction

from .stock import stock


def verify_mass(intake, trace, packing):
    jobs={}
    for work, recipe in trace['jobs'].items():
        dispatch=packing['jobs'][work]
        incoming=Fraction(recipe['input_g'])
        remaining=Fraction(dispatch['hold_g'])+Fraction(dispatch['return_g'])
        delta=incoming-remaining-sum(Fraction(dispatch[key]) for key in ('pack_g','loss_g','pending_g'))
        origin_delta=incoming-Fraction(dispatch['pending_g'])-sum(Fraction(g) for g in recipe['composition_g'].values())
        jobs[work]=dict(input_g=str(incoming),pack_g=dispatch['pack_g'],loss_g=dispatch['loss_g'],
                        remainder_g=str(remaining),pending_g=dispatch['pending_g'],delta_g=str(delta),
                        origin_delta_g=str(origin_delta),codes=recipe['codes'],job_line=recipe['job_line'])
    line_delta={key:row['records']-row['accepted']-row['isolated'] for key,row in intake['files'].items()}
    warehouse=stock(trace,packing)
    packages={key:Fraction(row['g'])-sum(Fraction(g) for g in row['origin_g'].values()) for key,row in packing['packages'].items()}
    balanced=warehouse['balanced'] and not any(line_delta.values()) and not any(packages.values())
    balanced=balanced and all(row['delta_g']==row['origin_delta_g']=='0' for row in jobs.values())
    return dict(jobs=jobs,warehouse=warehouse,line_delta=line_delta,balanced=balanced,
                package_delta_g={key:str(value) for key,value in packages.items()})
