from fractions import Fraction


def recall(report):
    labels=report['supply']['origins']
    packages={}
    for key,row in report['packing']['packages'].items():
        net=Fraction(row['g'])
        shares={origin:dict(grams=mass,share=str(Fraction(mass)/net),label=labels[origin]['label'],
                            line=labels[origin]['line']) for origin,mass in row['origin_g'].items()} if net else {}
        packages[key]=dict(work=row['work'],net_g=row['g'],packing_line=row['line'],origins=shares,
                           inputs=report['lineage']['jobs'][row['work']]['lots'])
    return packages
