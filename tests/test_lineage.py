from app.modules.lineage.cycles import find_cycles
from app.pipeline import compute


def test_multi_parent_mix_exact(dirty):  # TRAP-10
    row=dirty['lineage']['jobs']['BA-03']
    assert row['composition_g']=={'BR-08':'5058/25','CO-04':'96/5','ET-01':'1962/25'}
    assert row['input_g']=='300'


def test_actual_cycle(dirty):  # TRAP-20
    assert dirty['lineage']['cycles']==[{'members':['BA-09','BA-10'],'path':['BA-09','BA-10','BA-09']}]
    assert dirty['lineage']['jobs']['BA-09']['composition_g']=={}


def test_self_reference():
    assert find_cycles({'a':{'a'},'b':{'a'},'c':set()})==[{'members':['a'],'path':['a','a']}]


def test_two_step_lineage(dirty):
    row=next(x for x in dirty['lineage']['jobs']['BA-03']['lots'] if x['ticket']=='IN-06')
    assert row['from_coupon']==[{'coupon':'RT-B','work':'BA-02','line':7}]
    assert row['origin_g']=={'BR-08':'108/25','CO-04':'96/5','ET-01':'162/25'}


def test_upstream_failure_propagates(files):
    files['outputs']+='PK-A,BA-01,pack,621,20,g\n'
    result=compute(files,'lineage')['lineage']['jobs']
    assert result['BA-01']['codes']==['OUTPUT_DISPUTE']
    assert result['BA-02']['codes']==['UPSTREAM_PENDING'] and result['BA-02']['upstream_pending']==['BA-01']
    assert result['BA-03']['upstream_pending']==['BA-01','BA-02']
    assert result['BA-04']['codes']==[]


def test_mismatched_input_hold(dirty):
    result=dirty['lineage']['jobs']['BA-08']
    assert result['admitted_g']=='0' and result['input_g']=='70'
    assert 'INTAKE_MISMATCH' in result['codes'] and len(result['input_issues'])==5
