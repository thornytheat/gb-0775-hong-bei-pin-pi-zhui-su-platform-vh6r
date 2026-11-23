from fractions import Fraction

from app.pipeline import compute
from app.source import receive


def test_duplicate_pack_once(dirty):
    assert dirty['packing']['jobs']['BA-01']['pack_g']=='600'
    assert dirty['packing']['packages']['PK-A']['line']==2


def test_negative_net_isolated(dirty):
    assert dirty['weighins']['reasons']['NEGATIVE_NET']==1
    assert 'PK-H' not in dirty['packing']['packages']


def test_negative_remainder_blocks_certification(dirty):
    row=dirty['packing']['jobs']['BA-07']
    assert row['budget']['remaining_g']=='-10' and row['budget']['code']=='NEGATIVE_REMAINDER'
    assert (row['hold_g'],row['pending_g'])==('0','100')


def test_spent_return_not_double_counted(dirty):
    returns=dirty['packing']['returns']
    assert [(k,returns[k]['drawn_g'],returns[k]['available_g']) for k in ('RT-A','RT-B','RT-D')]==[
        ('RT-A','300','0'),('RT-B','30','0'),('RT-D','0','100')]


def test_package_fraction(dirty):
    row=dirty['packing']['packages']['PK-C']
    assert row['g']=='275' and row['origin_g']['ET-01']=='3597/50'
    assert sum(Fraction(g) for g in row['origin_g'].values())==275


def test_clean_pack_has_no_pending():
    report=compute(receive({'sample':'clean'}))['packing']
    assert set(report['packages'])=={'PK-A','PK-B','PK-C','PK-D'}
    assert all(row['pending_g']=='0' for row in report['jobs'].values())
