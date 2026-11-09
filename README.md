# Uma Race Art

Native-resolution, transparent Uma character assets for live race results, club builds and bracket lineups. Every playable outfit is indexed by **card ID** and **costume ID**. Original images are downloaded unchanged; this repository contains no screenshots from draft websites, enlarged thumbnails or fabricated outfit variants.

## Use in DDT2 or another race display

Load `catalog.json` and `resolve.js`. Pin the library URL to a Git commit when publishing a production site, or copy the required assets into that site's build.

```js
const art = UmaRaceArt.resolve(catalog, {card_id: 111602}, libraryBaseUrl);
// Or use the exact IDs supplied by a race export:
const sameArt = UmaRaceArt.resolve(catalog, {
  character_id: 1116,
  costume_id: 111626
}, libraryBaseUrl);
if (art) {
  image.src = art.url;
  image.alt = art.alt;
} else {
  // Show a neutral placeholder and the submitted Uma/outfit name.
  // Never silently substitute the character's original outfit.
}
```

**Gentildonna Wedding has card ID `111602`, but costume ID `111626`.** These identifiers are not interchangeable. A character ID alone cannot identify an outfit, so the resolver returns `null`. Conflicting IDs, unknown IDs, ambiguous mappings and unavailable files also return `null`.

All indexed race renders are 768 × 1024 transparent PNGs. At 2× device resolution, keep the image box at or below 384 × 512 CSS pixels and use `object-fit: contain`. Do not crop them into fake full-body images or upscale them for a hero. The separate `poses` collection includes larger official Gentildonna illustrations for hero/navigation presentation; it is never used as an implicit live-results fallback.

## Contents

- `catalog.json`: exact outfit metadata, original source URL, byte count, dimensions, SHA-256 and local path for each variant.
- `assets/racewear/<card_id>.png`: native full-body model render for that exact playable outfit.
- `assets/gentildonna/`: separately identified official illustrations and the original-outfit idle animation.
- `resolve.js`: small browser/CommonJS resolver with no dependencies.
- `index.html`: searchable asset review page. Serve this directory with `python -m http.server 8080`, then open localhost:8080.
- `scripts/sync.py`: refresh the playable-card catalog and download native images with bounded concurrency.
- `scripts/validate.py`: check every file's hash, dimensions, alpha channel and mapping uniqueness.

## Reproduce or update

Python 3.10+ and Node.js are sufficient. No image-processing library is needed; none of these commands edit image pixels.

```sh
# Recreate missing files from this exact catalog and reject changed source bytes.
python scripts/sync.py restore

# Deliberately update the source catalog and obtain new exact variants.
python scripts/sync.py sync

python scripts/validate.py
node tests/resolve.cjs
```

`sync` reads GameTora's public data manifest, then the current character-card dataset referenced by that manifest. It does not guess card IDs. Newly unavailable or undersized images are marked unavailable and the process fails, so a publication job cannot silently replace an exact outfit with another. Existing files are reused unchanged; remove one deliberately before `sync` if you intend to adopt revised source bytes. Review catalog changes before publishing.

## Sources and scope

The complete playable-outfit index and native 3D model renders are from [GameTora's character database](https://gametora.com/umamusume/characters). These are original asset files linked by its own image gallery, **not screenshots of that gallery**. Static model renders serve the same full-body lineup purpose as a race introduction; they are not claimed to be extracted frames of the game's race-opening animation. Some costumes outside the playable-card catalog may not have an exact mapping; those remain unavailable until separately verified.

Gentildonna's high-resolution illustrations come directly from the [official Cygames character page](https://umamusume.jp/character/gentildonna/). Its original racewear art and concept illustration are distinct poses of the same race outfit. The STARTING FUTURE illustration is recorded as a separate outfit, not racewear. The animated AVIF is an original-outfit idle render from GameTora; clients should use the static PNG when animated AVIF is unsupported.

The `source_page` and `source_url` on every entry preserve provenance. **All character/game artwork remains © Cygames, Inc.** GameTora supplies the model renders. No image ownership or redistribution license is asserted by this repository; retain these credits and observe the original publishers' terms. The MIT license applies only to the repository's original code.
