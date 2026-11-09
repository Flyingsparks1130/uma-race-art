"""Validate native image quality and variant mappings without editing images."""
import hashlib, json
from pathlib import Path
from sync import ROOT, png_info

catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
ids = set()
for asset in catalog['assets'] + catalog.get('poses', []):
    if asset['id'] in ids: raise ValueError(f"Duplicate asset: {asset['id']}")
    ids.add(asset['id'])
    if asset.get('status') == 'unavailable': continue
    path = (ROOT / asset['path']).resolve()
    if not path.is_relative_to(ROOT): raise ValueError('Unsafe path')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != asset['sha256']:
        raise ValueError(f'Checksum mismatch: {path.name}')
    if path.suffix == '.png':
        info = png_info(data)
        for key in ('width', 'height', 'bytes', 'alpha'):
            if info[key] != asset[key]: raise ValueError(f'Incorrect {key}: {path.name}')
    if 'thumb/' in asset['source_url'] or '/256/' in asset['source_url']:
        raise ValueError('Thumbnail source is prohibited')
cards = [a['card_id'] for a in catalog['assets']]
if len(cards) != len(set(cards)): raise ValueError('Duplicate card mapping')
print(f"Validated {len(catalog['assets'])} outfit variants and {len(catalog.get('poses', []))} pose assets")
