import re
from decimal import Decimal
from fractions import Fraction

SCALE = {'mg':Fraction(1,1000),'g':Fraction(1),'kg':Fraction(1000)}


def grams(raw, unit):
    if not re.fullmatch(r'[0-9]{1,9}(?:\.[0-9]{1,6})?',raw) or unit not in SCALE:
        raise ValueError('质量格式或单位无效')
    return Fraction(Decimal(raw))*SCALE[unit]
