"""Download native full-body assets; never create, enlarge or crop an image."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, re, struct, sys, time, urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_URL = 'https://gametora.com/data/manifests/umamusume.json'
MEDIA = 'https://media.gametora.com/umamusume/characters/render/trainee/idle/'

def download(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'UmaRaceArt/1.0 (native-asset catalog)'})
            with urllib.request.urlopen(request, timeout=40) as response:
                return response.read()
        except Exception:
            if attempt == 2: raise
            time.sleep(attempt + 1)

def png_info(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError('Expected an original PNG, received another format')
    width, height = struct.unpack('>II', data[16:24])
    if width < 768 or height < 1024:
        raise ValueError(f'Image is below the 768x1024 full-body quality floor: {width}x{height}')
    if data[25] not in (4, 6):
        raise ValueError('Full-body asset must contain an alpha channel')
    return {'width': width, 'height': height, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'alpha': True,
            'recommended_max_css_width_2x': width // 2,
            'recommended_max_css_height_2x': height // 2}

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def source_cards():
    manifest = json.loads(download(MANIFEST_URL))
    url = f"https://gametora.com/data/umamusume/character-cards.{manifest['character-cards']}.json"
    cards = json.loads(download(url))
    if not isinstance(cards, list) or not cards: raise ValueError('Empty source catalog')
    return cards, url

def descriptor(card):
    card_id = str(card['card_id'])
    if not re.fullmatch(r'\d{6}', card_id): raise ValueError('Invalid card ID')
    return {'id': f'{card_id}-racewear', 'card_id': card_id,
            'character_id': str(card['char_id']), 'character_name': card['name_en'],
            'character_name_ja': card.get('name_jp', ''),
            'costume_id': str(card['costume']), 'outfit_id': card.get('version', 'original'),
            'outfit_name': card.get('title', card.get('version', 'Original')),
            'kind': 'game-render', 'pose': 'idle', 'path': f'assets/racewear/{card_id}.png',
            'source_url': f'{MEDIA}{card_id}.png',
            'source_page': f"https://gametora.com/umamusume/characters/{card['url_name']}",
            'credit': 'Character © Cygames, Inc. · Model render: GameTora',
            'release_jp': card.get('release'), 'release_global': card.get('release_en')}

def materialize(asset):
    path = ROOT / asset['path']
    data = path.read_bytes() if path.exists() else download(asset['source_url'])
    info = png_info(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists(): path.write_bytes(data)
    return {**asset, **info, 'status': 'available'}

def sync(args):
    cards, source_url = source_cards()
    assets = [descriptor(card) for card in cards]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(materialize, asset): asset for asset in assets}
        for job in concurrent.futures.as_completed(jobs):
            asset = jobs[job]
            try: results.append(job.result())
            except Exception as error:
                print(f"Unavailable {asset['card_id']}: {error}", file=sys.stderr)
                results.append({**asset, 'status': 'unavailable', 'path': None})
    results.sort(key=lambda item: item['card_id'])
    poses_path = ROOT / 'poses.json'
    poses = json.loads(poses_path.read_text(encoding='utf-8')) if poses_path.exists() else []
    catalog = {'schema_version': 1, 'updated': args.date or str(date.today()),
               'source_catalog': source_url, 'source_manifest': MANIFEST_URL,
               'lookup_policy': 'Exact card_id, or exact character_id + costume_id. No base-outfit fallback.',
               'rights': 'Game artwork remains © Cygames, Inc.; no image license is granted by this repository.',
               'assets': results, 'poses': poses}
    write_json(ROOT / 'catalog.json', catalog)
    available = [asset for asset in results if asset['status'] == 'available']
    print(f"{len(available)}/{len(results)} exact variants; {sum(a['bytes'] for a in available):,} bytes")
    if len(available) != len(results): sys.exit(1)

def restore(args):
    """Reproduce the checked-in catalog exactly; useful for CI publication."""
    catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    assets = [item for item in catalog['assets'] + catalog.get('poses', []) if item.get('path')]
    def fetch_one(asset):
        path = ROOT / asset['path']
        if not path.resolve().is_relative_to(ROOT): raise ValueError('Unsafe asset path')
        data = path.read_bytes() if path.exists() else download(asset['source_url'])
        if hashlib.sha256(data).hexdigest() != asset['sha256']:
            raise ValueError(f"Source changed: {asset['path']}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists(): path.write_bytes(data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(fetch_one, assets))
    print(f'Restored {len(assets)} checksum-verified native assets')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['sync', 'restore'])
    parser.add_argument('--workers', type=int, choices=range(1, 7), default=4)
    parser.add_argument('--date', help='Explicit catalog date, YYYY-MM-DD')
    args = parser.parse_args()
    (sync if args.command == 'sync' else restore)(args)
