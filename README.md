# DataJockey Brand Kit

The canonical DataJockey system for dashboards and data-led publishing:
written guidance, design tokens, fonts, brand assets, and a YAML-to-PDF
carousel generator.

This repository is the product. There is no installer and no generated copy of
the kit. Git provides provenance and updates; consuming projects reference the
checked-in repository directly.

## Use the kit in a project

### Git subtree (default)

Subtree keeps the kit at `dj-brand-kit/` inside a consuming repository without
requiring contributors to initialise anything after cloning:

```bash
git subtree add \
  --prefix=dj-brand-kit \
  https://github.com/dav1b/dj-brand-kit.git \
  main --squash
```

Pull a later kit release:

```bash
git subtree pull \
  --prefix=dj-brand-kit \
  https://github.com/dav1b/dj-brand-kit.git \
  main --squash
```

Push a committed kit improvement back to the canonical repository:

```bash
git subtree push \
  --prefix=dj-brand-kit \
  https://github.com/dav1b/dj-brand-kit.git \
  main
```

Use a Git submodule instead when independent history and pinned revisions are
more important than a self-contained checkout. Clone this repository directly
when working on the brand kit itself.

Do not copy the folder with a setup script. Do not maintain a second “installed”
copy: that creates drift and loses useful Git history.

## Connect a web app

Import the canonical tokens from the consuming app’s root CSS:

```css
@import "../../dj-brand-kit/tokens/dj-design.css";
```

The token file expects the bundled TTF files at `/fonts/<filename>`. Publish or
copy the contents of `dj-brand-kit/fonts/` to the app’s public `/fonts/`
directory as part of that app’s own build process. Keeping this step in the
consumer makes deployment assumptions explicit.

The token file includes a small global reset and base `html`/`body` styles.
Review that behavior before importing it into an established application.

## Give an AI coding agent the guidance

Agent configuration belongs to the consuming repository, not this kit. Point
the agent at the relevant checked-in files:

- Always: `guidance/00-index.md`
- Copywriting: `guidance/01-voice-and-principles.md`
- UI work: `guidance/02-color-system.md` through
  `guidance/07-export-application.md`
- Carousels: `guidance/08-carousel-application.md`
- Pre-ship review: `guidance/09-implementation-checklist.md`

No workflow depends on Claude Code or another specific agent.

## Generate a carousel

Create and activate a Python environment, then install the declared runtime
dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r dj-brand-kit/requirements.txt
```

Keep project briefs outside the kit:

```bash
mkdir -p carousel-briefs
cp dj-brand-kit/carousel/briefs/example-brief.yaml carousel-briefs/my-brief.yaml

python3 dj-brand-kit/carousel/generate.py \
  carousel-briefs/my-brief.yaml \
  --validate-only

python3 dj-brand-kit/carousel/generate.py carousel-briefs/my-brief.yaml
```

Rendering requires Chrome or Chromium. Output lands in
`carousel-briefs/out/`. Add that path to the consuming repository’s
`.gitignore` (a subtree’s own ignore file cannot govern its parent directory).
See [carousel/README.md](carousel/README.md) for the brief format, chart types,
and render options.

Only `carousel/briefs/example-brief.yaml` belongs in this repository.
Project-specific briefs belong to their project repository.

## Repository map

```text
dj-brand-kit/
├── assets/                  logos, monograms, and the six-mark icon system
├── carousel/
│   ├── briefs/              one synthetic, validated example
│   ├── renderer/            static HTML/CSS/JS slide renderer
│   └── generate.py          brief validator and Chrome PDF driver
├── fonts/                   bundled font binaries; read LICENSES.md
├── guidance/                brand and application rules
├── tests/                   validation and Chrome render smoke tests
├── tokens/dj-design.css     canonical CSS properties and base styles
├── IMPROVEMENT-PLAN.md      repository review and acceptance criteria
├── LICENSES.md              current rights and redistribution status
└── requirements*.txt        runtime and development dependencies
```

## Develop and verify

```bash
python3 -m pip install -r requirements-dev.txt
python3 carousel/generate.py carousel/briefs/example-brief.yaml --validate-only
python3 -m unittest discover -s tests -v
python3 tests/render_smoke.py
```

The first two checks do not require Chrome. The render smoke test does; it
generates the example PDF and verifies page count, orientation, and aspect
ratio. CI runs all checks on pushes and pull requests.

`tokens/dj-design.css` is the implementation source of truth. When palette or
typography guidance changes, update the tokens in the same commit. When the
carousel schema changes, update the example and tests in the same commit.

## Licensing

Read [LICENSES.md](LICENSES.md) before redistributing this repository or its
fonts. In particular, the repository does not currently declare a
repository-wide licence, and the bundled commercial typeface requires verified
usage and redistribution rights.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: yaml` | Install `requirements.txt` in the active Python environment. |
| Fonts fall back in a web app | Publish `fonts/*.ttf` at the app’s public `/fonts/` path, or adapt the font declarations in the consumer. |
| `No Chrome/Chromium found` | Install Chrome/Chromium or pass `--chrome "/path/to/browser"`. |
| `Brief invalid: ...` | Fix the named field; the schema and deck rules live in `guidance/08-carousel-application.md`. |
| Existing app styles change after token import | The token file includes a global reset and base page styles; isolate or split those rules in the consumer. |
