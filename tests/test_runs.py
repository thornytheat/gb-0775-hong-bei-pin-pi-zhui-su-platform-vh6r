from concurrent.futures import ThreadPoolExecutor

import pytest

from app.errors import RoastError
from app.main import create_app
from app.modules.runs.cabinet import Cabinet
from app.modules.runs.service import seal_run


def test_archived_manifest(client):
    response=client.post('/api/runs',json={'sample':'dirty'})
    assert response.status_code==201 and response.json['manifest']['rules']=='roast-ledger-1.0'
    assert len(response.json['manifest']['files'])==4


def test_repeat_is_same(client):
    first=client.post('/api/runs',json={'sample':'dirty'}).json
    result=client.post(f"/api/runs/{first['id']}/rerun").json
    assert result=={**first,'reused':True} and len(client.get('/api/runs').json['runs'])==1


def test_reopen(tmp_path):
    path=tmp_path/'restock'
    first=create_app(path).test_client().post('/api/runs',json={'sample':'dirty'}).json
    stored=create_app(path).test_client().get(f"/api/runs/{first['id']}").json
    assert stored=={k:first[k] for k in ('id','manifest','balance')}


def test_atomic_link_failure(monkeypatch,tmp_path,files):
    cabinet=Cabinet(tmp_path/'transaction')
    def rejected_link(*args):
        raise PermissionError('cannot publish')
    monkeypatch.setattr('app.modules.runs.cabinet.os.link',rejected_link)
    with pytest.raises(PermissionError):
        seal_run(cabinet,files)
    assert list(cabinet.path.iterdir())==[]


def test_parallel_publish(tmp_path,files):
    cabinet=Cabinet(tmp_path/'racing')
    with ThreadPoolExecutor(max_workers=4) as pool:
        all_runs=list(pool.map(lambda _:seal_run(cabinet,files),range(4)))
    assert len(list(cabinet.path.iterdir()))==1 and sum(row['reused'] for row in all_runs)==3


def test_damaged_archive(tmp_path,files):
    cabinet=Cabinet(tmp_path/'corrupt')
    key=seal_run(cabinet,files)['id']
    (cabinet.path/f'{key}.json').write_text('partial')
    with pytest.raises(RoastError) as error:
        cabinet.read(key)
    assert error.value.code=='DAMAGED_RUN'
