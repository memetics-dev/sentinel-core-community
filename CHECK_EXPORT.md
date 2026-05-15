# Export Check

## Included
- root `README.md`
- `COMMUNITY_PREVIEW.md`
- community preview docs
- supported hardware and installation overview docs
- pilot scenario suite doc
- installer MVP scripts
- public-facing ops-console routes and shared public components
- static public scenario data
- limited safe Edge Core preview with scripts and sanitized config

## Excluded
- `.git/`
- `.next/`
- `node_modules/`
- `.sentinel-core/`
- `.env*`
- `*.db`
- private household config
- founder-specific private notes
- commercial/private roadmap and strategy docs
- git history and deployment keys

## Validation Steps
- search for obvious secrets in `community-export/`
- confirm excluded runtime/build directories are absent
- build the public preview frontend from the export package if possible
