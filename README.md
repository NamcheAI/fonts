# Namche Fonts

**Namche-Shadow** — custom type for Namche, based on Geist Sans with an **inner-corner round** (fillet) pipeline.

## Layout

| Path | Role |
|------|------|
| [`geist-font-original/`](geist-font-original/) | Immutable pristine Geist upright sources — **do not edit** |
| [`geist-font-main/`](geist-font-main/) | Working tree, scripts, proofs, built fonts |
| [`geist-font-main/scripts/`](geist-font-main/scripts/) | Inner-round engine + local preview UI |
| [`VERSION`](VERSION) | Current release version |
| [`VERSIONING.md`](VERSIONING.md) | How we version, tag, and ship releases |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| [`AUTHORS.txt`](AUTHORS.txt) / [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt) | Attribution |

## Quick start (preview UI)

```bash
cd geist-font-main
python3 scripts/inner_round_app.py
# → http://127.0.0.1:8765
```

Details: [`geist-font-main/scripts/INNER_ROUND_README.md`](geist-font-main/scripts/INNER_ROUND_README.md)

## Versioning

See **[VERSIONING.md](VERSIONING.md)**. Short version: SemVer in `VERSION`, tags as `vMAJOR.MINOR.PATCH`, changelog required for every release, binaries attached to GitHub Releases.

## Credits

- **Michael Marte** — Namche-Shadow design direction and contribution
- **Cursor (Grok)** — co-author, tooling and repository setup
- Upstream **Geist** by Vercel / Basement Studio / Andrés Briganti (OFL) — see `AUTHORS.txt`

## License

Upstream Geist is licensed under the SIL Open Font License (`OFL.txt` in the Geist trees). Keep attribution with any redistributed font files.
