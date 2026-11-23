import hashlib
import json

from app.config import RULE_VERSION


def encode(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def checksum(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def address(files):
    hashes={name:checksum(text) for name,text in files.items()}
    return checksum(encode([RULE_VERSION,hashes])),hashes
