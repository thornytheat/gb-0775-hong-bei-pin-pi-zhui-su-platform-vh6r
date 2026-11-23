from app.errors import RoastError
from app.modules.runs.fingerprint import checksum,encode

from .recall import recall


def verify_and_export(document):
    files, manifest, reports=(document[key] for key in ('files','manifest','reports'))
    if {name:checksum(text) for name,text in files.items()}!=manifest['files'] or checksum(encode(reports))!=manifest['result_sha256']:
        raise RoastError('BAD_SEAL','称签原件或结果校验失败',409)
    if not reports['balance']['balanced']:
        raise RoastError('UNBALANCED','重量差额尚未对平',409)
    evidence={**document,'packages':recall(reports)}
    return {**evidence,'verified':True,'seal':checksum(encode(evidence))}
