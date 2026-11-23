from datetime import UTC,datetime
from time import perf_counter_ns

from app.config import RULE_VERSION
from app.errors import RoastError
from app.pipeline import compute

from .fingerprint import address, checksum, encode


def seal_run(cabinet, files, previous=None):
    start=perf_counter_ns()
    reports=compute(files)
    key,hashes=address(files)
    digest=checksum(encode(reports))
    if previous is not None and (previous['id'],previous['result_sha256'])!=(key,digest):
        raise RoastError('REPLAY_CHANGED','复算摘要与原卷联不同',409)
    manifest=dict(id=key,rules=RULE_VERSION,files=hashes,result_sha256=digest,
                  created_at=datetime.now(UTC).isoformat(timespec='seconds'),elapsed_ms=(perf_counter_ns()-start)//1_000_000)
    inserted=cabinet.write(dict(manifest=manifest,files=files,reports=reports))
    stored=cabinet.read(key)
    if stored['manifest']['result_sha256']!=digest or checksum(encode(stored['reports']))!=digest or stored['files']!=files:
        raise RoastError('REPLAY_CHANGED','存量归档未通过一致性核验',409)
    return dict(id=key,manifest=stored['manifest'],reused=not inserted,balance=reports['balance'])
