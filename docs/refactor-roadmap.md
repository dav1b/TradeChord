# Refactor implementation record and roadmap

Last updated: 2026-07-28

This is the living record of the TradeChord refactor. It separates completed
implementation from operational work and optional future improvements. New
ideas and feedback should be added here before they are promoted into the
active work queue.

Status labels:

- **Done** — implemented and verified in the current working tree.
- **Next** — the next operational or engineering work to complete.
- **Later** — valuable work that is not needed for the current architecture.
- **Idea** — plausible improvement that still needs a decision or evidence.
- **Non-goal** — deliberately excluded unless the project changes materially.

## 1. Target state

TradeChord is one Git repository containing two independent toolchains joined
by a versioned data contract:

```text
WITS API
  → Python collection and validation
  → data/releases/<version>/trade_matrix.csv.gz
  → committed route-specific browser projections
  → SvelteKit + D3 dashboard
```

The governing principle is:

> A fresh clone can run and build the dashboard with Node alone. Python and
> WITS access are only required when deliberately generating a data release.

The canonical matrix is the archival analytical artifact. Browser projections
are a separate representation generated for the actual dashboard routes. The
pipeline owns data semantics; the web application owns presentation and
interaction.

## 2. Architectural decisions

These decisions are implemented and should be treated as defaults:

1. The frontend repository remains the Git-history base.
2. The Python pipeline lives under `pipeline/`; the SvelteKit application
   lives under `web/`.
3. Normal web development never invokes Python or contacts WITS.
4. Published canonical releases and browser projections are committed.
5. Export and import values are collected directly from WITS using
   `XPRT-TRD-VL` and `MPRT-TRD-VL`.
6. The canonical record contains a `flow` dimension.
7. Export and import partners are ranked independently, then collected using
   their union so a displayed bilateral balance has both explicit flows.
8. Mirror trade is a possible validation signal, not the source of imports.
9. ROW is synthetic and reconciled independently for each flow.
10. A successful but omitted WITS series can be materialized as an
    authoritative zero; an uncollected flow remains unavailable.
11. Canonical gzip output is deterministic, including `mtime=0`.
12. The dashboard does not fetch or aggregate the canonical matrix.
13. `/` receives per-country projections; `/all` receives a purpose-built
    `overview.json`.
14. Browser projections are committed directly under
    `web/static/data/<version>/`; there are no symlinks or copy hooks.
15. `web/static/data/current.json` selects the active immutable release.
16. The release manifest hashes the canonical matrix and every browser
    projection.
17. Staging, raw responses, caches, and generated shards are ephemeral and
    ignored by Git.
18. Data publication is manual. It is not a web-build dependency and does not
    run against WITS on every CI push.
19. Vercel is the production target, with `web/` as the project root.
20. The public explorer is static-first and CDN-served; runtime compute is not
    part of ordinary scene navigation.
21. Versioned data URLs are immutable and long-cacheable; `current.json`
    remains revalidating or short-lived.
22. Future projections are split and prefetched around interaction latency,
    not around legacy chart components.
23. Production performance is governed by measured payload, bundle, Core Web
    Vitals, responsiveness, and accessibility budgets.

## 3. Completed implementation

### 3.1 Repository and toolchains — Done

- Consolidated the project into the monorepo structure.
- Added root orchestration through the `Makefile`.
- Kept Node and Python installation, tests, and builds independent.
- Pinned Node through `.nvmrc` and `package.json` engines.
- Pinned the supported Python range in `pipeline/pyproject.toml`.
- Removed obsolete frontend dependencies and stale Vite configuration.
- Removed the legacy browser-side 14 MB CSV loading and aggregation path.
- Added strict ignore rules for the large WITS cache, staging data, raw data,
  shards, Python environments, browser test output, and build output.

### 3.2 Direct dual-flow collection — Done

- Unified export and import collection behind the same collector.
- Made the WITS indicator mapping authoritative in one code path.
- Added explicit request-result statuses instead of swallowing failures.
- Distinguished success, authoritative empty responses, not-found series,
  HTTP failures, retry exhaustion, and parse failures.
- Ranked export and import partners independently.
- Added a second collection phase that fetches the union of those partner
  rankings for both flows.
- Materialized authoritative zero observations for requested
  partner/product/year combinations omitted by successful WITS range
  responses.
- Recomputed ROW and coverage after completing the partner union.

### 3.3 Data correctness and validation — Done

- Added a canonical `flow` dimension with integer current-USD values.
- Added duplicate compound-key detection.
- Added negative and invalid-value checks.
- Added reporter × flow completeness checks.
- Added exact requested-year shape checks.
- Added WLD product/year shape checks.
- Added direct export/import partner-union equality checks.
- Added a required coordinated partner strategy for dual-flow runs.
- Added flow-specific WLD/ROW reconciliation.
- Made unresolved HTTP, retry, and parse failures release-blocking.
- Removed the option to bypass strict validation during publication.
- Added concise coverage summaries with minimum, percentile, average,
  threshold, and worst-case observations.

### 3.4 Artifact and projection contract — Done

- Added deterministic canonical CSV gzip output.
- Added JSON schemas for manifests, records, and projections.
- Advanced the active browser/release contract to schema version 2.
- Added immutable canonical release directories under `data/releases/`.
- Added route-specific projections under `web/static/data/<version>/`.
- Added `countries.json`, per-country projections, and `overview.json`.
- Added per-file SHA-256 hashes for every browser projection.
- Added canonical matrix and manifest checksum files.
- Added a release verification command that checks canonical and browser
  artifacts and the active manifest pointer.
- Made browser projections build in a temporary directory and promote only
  after successful generation.
- Made `current.json` update atomically and last.
- Added a `reproject` command for immutable projection-only compatibility
  releases.

### 3.5 Correct unavailable-value semantics — Done

- Added `exportAvailable` and `importAvailable` to bilateral projection rows.
- Made bilateral `balanceUsd` nullable when either flow was not explicitly
  collected.
- Prevented legacy one-sided observations from appearing as zero-valued trade
  or false balances.
- Updated chord, treemap, slope, tooltip, and trade-point handling to
  distinguish unavailable data from an authoritative zero.
- Preserved ROW behavior as a separately identified synthetic remainder.

### 3.6 Dashboard and user experience — Done

- Added country names alongside ISO3 codes.
- Updated the country picker and page headings to use names and codes.
- Added methodology disclosure in the dashboard.
- Added application-level navigation/loading feedback.
- Added a route error page.
- Kept component inputs route-specific rather than loading unnecessary
  country projections on `/all`.
- Added browser interaction coverage for initial loading, country selection,
  URL updates, cross-filtering, release display, and the overview route.
- Introduced the first centralized explorer controller for durable
  representation and partner/product selection state.
- Added stable semantic country, partner, flow, and product key helpers.
- Replaced the module-global cross-filter with page-scoped explorer context.
- Implemented the first continuous-scene prototype: the partner chord
  transforms into an exact ranked partner view and reverses without losing
  selection.
- Made representation and selection linkable through `view`, `partner`, and
  `product` URL state, including browser back/forward restoration.

### 3.7 Testing, CI, and documentation — Done

- Added offline SDMX, conversion, reconciliation, duplicate, completeness,
  projection, partner-union, and verification tests.
- Added Ruff and pytest to the Python CI job.
- Added `svelte-check`, production build, and Playwright to the web CI job.
- Added a large-file guard.
- Added committed release-integrity verification to CI.
- Added architecture, methodology, and data-release documentation.
- Updated the main plan to record the implemented architecture.

## 4. Verification record

The current implementation was checked with:

- Ruff: passed.
- Python tests: 35 passed.
- Svelte diagnostics: 0 errors and 0 warnings.
- Vite production build: passed.
- Playwright Chromium test: passed.
- Active release integrity verification: passed.
- Production npm dependency audit: 0 vulnerabilities.

A live WITS pilot was also completed for USA and Germany using direct exports
and imports for 2002, 2012, and 2022:

- 3,744 observations.
- Export and import partner unions completed for both reporters.
- No unresolved request failures.
- No duplicate canonical keys.
- No reconciliation failures.
- No invalid values.
- No missing flows.
- No staging-shape or partner-union failures.

The pilot is stored under the ignored staging directory:
`data/staging/20260727T092448Z`.

## 5. Current published state

The active release is `2026-07.1`.

It is an immutable schema-v2 compatibility release generated from the existing
`2026-07` canonical matrix. It corrects projection semantics, adds names and
availability fields, and supplies the new browser contract. It does **not**
claim that the old canonical matrix was recollected with coordinated direct
flows.

This distinction matters:

- The application is now honest about unavailable bilateral values.
- The collector is now capable of creating fully coordinated direct-flow
  data.
- A full historical recollection is still required before activating a new
  canonical data release produced by that collector.

## 6. Immediate next work

### 6.1 Review and checkpoint the refactor — Next

Before starting the long data operation:

1. Review the current Git diff for accidental or unrelated changes.
2. Review the generated `2026-07.1` manifest and representative country files.
3. Confirm no cache, staging, raw, secret, or oversized file is staged.
4. Commit the implementation separately from the future full data release.
5. Push the branch and let both CI jobs complete.

Keeping the code refactor and the large historical data refresh in separate
commits makes review and rollback substantially safer.

### 6.2 Run the full historical collection — Next

Run all intended reporters across the complete 2002–2022 period with both
flows and the agreed top-K:

```bash
make data-collect ARGS="--reporters TOP50 --years 2002-2022 --flows both --top-k 15"
```

The configured reporter set currently contains 30 dashboard reporters even
though the legacy argument is named `TOP50`. Confirm this naming before the
run; it should eventually be replaced by a clearer configured-set name.

This is a network-intensive manual operation. Preserve its ignored staging
directory until the release is reviewed and published.

### 6.3 Validate and inspect the full run — Next

Run the strict validation gate:

```bash
make data-validate STAGING=data/staging/<run-id>
```

Then inspect:

- Every expected reporter has export and import manifests.
- Export/import partner-code sets match per reporter.
- There are no unresolved HTTP, retry, or parse outcomes.
- WLD reconciliation succeeds separately for both flows.
- Coverage minima and worst observations are plausible.
- Product and year coverage match the requested range.
- Values and total magnitudes are plausible for several known reporters.
- ROW is not dominating because of a collection or code-mapping error.
- The resulting file sizes remain suitable for Git and browser delivery.

Do not publish merely because the validation command exits successfully;
perform the analytical spot checks as well.

### 6.4 Publish the first fully coordinated release — Next

Choose a new immutable dataset version and publish from the reviewed staging
run:

```bash
make data-release STAGING=data/staging/<run-id> VERSION=<new-version>
make data-verify VERSION=<new-version>
make test
make build
```

Inspect representative country pages and `/all`, then commit these together:

- `data/releases/<new-version>/`
- `web/static/data/<new-version>/`
- `web/static/data/current.json`

Never overwrite `2026-07` or `2026-07.1`.

### 6.5 Post-release review — Next

After activation:

1. Compare headline totals against WITS for several reporter/year pairs.
2. Compare the old and new release for discontinuities.
3. Review reporters with the lowest partner coverage.
4. Review the balance direction and magnitude for known cases.
5. Confirm production deployment can fetch all active projection files.
6. Record the release date, source range, validation result, and any accepted
   caveats in the methodology documentation.

### 6.6 Establish the first Vercel baseline — Implemented; field metrics pending

Treat deployment as the next validation environment, not as the last step
after the revised frontend is complete:

1. Commit and push the current refactor separately from the full data refresh.
2. Configure a Vercel project with `web/` as its root.
3. Confirm Node, `npm ci`, and `npm run build` use the pinned toolchain.
4. Deploy a branch preview.
5. Verify `/`, `/all`, direct entry, refresh, error handling, and static data
   fetches.
6. Record production response headers for compiled assets, versioned data, and
   `current.json`.
7. Capture initial JavaScript, CSS, and compressed data transfer sizes.
8. Capture mobile and desktop LCP, INP, CLS, and long-task baselines.
9. Enable Vercel Speed Insights after reviewing sampling, privacy, and plan
   limits.

The intended production architecture is static-first:

- prerender the finite public route set;
- serve immutable release projections from Vercel's CDN;
- perform scene navigation in the browser;
- lazy-load or prefetch advanced detail artifacts;
- avoid WITS, Python, databases, and per-interaction server functions.

Full requirements and phased deployment work are recorded in
[deployment-performance.md](./deployment-performance.md).

Baseline progress:

- Production Git/Vercel deployment is live at `trade-chord.vercel.app`.
- The production interaction journey passes in Chromium.
- Initial compressed page and country transfers are inside provisional
  budgets.
- Production data resolves schema 2 release `2026-07.1`.
- The persistent Vercel project settings use `web/` as the root and Node 22.
- Differentiated cache rules in `web/vercel.json` are verified in production:
  versioned projections receive `public, max-age=31536000, immutable`, while
  `current.json` receives `public, max-age=0, must-revalidate`.
- The bilateral relationship journey passes against production in Chromium.
- Field Core Web Vitals still require Speed Insights traffic and are not yet
  complete.

## 7. Revised frontend direction: one continuous visual scene

### 7.1 Product vision — Planned

The revised frontend is not a dashboard made of separate charts and
drill-down pages. It is one continuous visual scene that changes form as the
user asks narrower questions.

The user should experience an entity being opened, compared, or transformed,
not one chart disappearing while another chart loads. Visual continuity is
therefore part of the information architecture, not decorative animation.

Svelte is a strong fit for this interaction model because keyed elements,
`crossfade`, `animate:flip`, tweens, springs, and transition primitives can
preserve the perceived identity of an object while its geometry and role
change.

### 7.2 Stable analytical entities

Every visual state is a projection of the same underlying entities:

- country;
- partner;
- flow;
- product group;
- year;
- value;
- share;
- balance.

Every rendered analytical object must have a stable semantic identity that is
independent of its current chart or geometry. Examples:

```text
country:USA
partner:CHN
flow:USA:CHN:export
flow:USA:CHN:import
product:USA:CHN:84-85_MachElec
year:2022
```

A China ribbon keyed as `partner:CHN` should retain that identity wherever it
appears. Position, shape, scale, color emphasis, and annotation can change;
the identity does not.

This requires a distinction between:

- **semantic identity** — what the object represents;
- **visual representation** — ribbon, arc, bar, line, cell, label, or total;
- **scene state** — the current question and level of detail;
- **geometry** — the calculated position and shape for that scene.

### 7.3 Central interaction model

The main interaction begins with a country and progressively narrows:

```text
Country overview
  → select partner
  → inspect bilateral export/import flows
  → select product group
  → inspect composition and balance
  → inspect change over time
  → inspect contribution to the change
```

A partner ribbon can transform into:

1. a selected chord ribbon;
2. a full-width bilateral flow;
3. paired export and import bars;
4. a product composition view;
5. a time-series line;
6. a contribution waterfall.

These are not six independent widgets. They are six scene representations of
the selected semantic object and its related entities.

Selection should also be reversible. Moving back up the question hierarchy
should return objects to their earlier forms rather than replacing the entire
interface.

### 7.4 Required user journeys

These journeys define the intended analytical model. They are not a
requirement to build every representation in the first frontend milestone.
Each journey must first have a valid data contract, stable entity identities,
and a reversible state transition.

#### Journey A: chord ribbon → stacked bars → treemap

Purpose: reveal the composition of one bilateral flow while visibly
preserving its origin in the network.

1. The user opens UAE and selects China.
2. The China ribbon isolates and straightens into a horizontal bilateral bar.
3. The bar splits into reported exports and reported imports.
4. The user selects imports.
5. The import bar divides into product-group segments.
6. Those same segments reposition into a treemap.
7. Labels appear after the geometry settles.
8. The user selects Machinery.
9. The Machinery tile expands to occupy the main canvas.
10. Its child categories arrange inside it.

A product segment keeps a stable identity throughout:

```text
flow:import|partner:CHN|product:machinery
```

Its visual encoding changes from ribbon thickness, to bar width, to rectangle
area. The underlying object does not.

Data dependency: child product categories are not part of the current
high-level product projection. Before implementing the final step, define the
product hierarchy and measure the additional payload or detail-fetch cost.

#### Journey B: chord → ranked partner view

Purpose: switch from structural understanding to exact comparison without
introducing a disconnected bar chart.

1. The user sees the national chord and selects **Rank partners**.
2. Circular partner arcs detach and move into a vertical ranked list.
3. Each ribbon straightens into an inline bar.
4. Exact values and shares appear after reordering.
5. The user selects China.
6. China moves into a pinned comparison area.
7. Remaining partners re-rank around the pinned selection.
8. Selecting **Network** reverses the transformation.

The chord and ranked list are two representations of the same partner
relationships. Partner IDs, selection, values, and unavailable states must be
identical in both.

#### Journey C: chord → time series

Purpose: show that the selected-year ribbon is one point in a longer bilateral
history.

1. The user selects Germany–Poland.
2. The bilateral ribbon isolates.
3. Its centreline stretches horizontally.
4. That line becomes the time-series x-axis.
5. Ribbon thickness at the selected year anchors the final selected point.
6. Historical exports and imports grow backward from that point.
7. The user scrubs through years.
8. The background chord reconstructs for the active year.
9. Partner ranking, balance, and product mix update with the same year state.

This creates two related time controls:

- **country time** — scrub the complete national network;
- **relationship time** — inspect the selected partner history.

These controls must share one authoritative year rather than drifting into
independent chart state.

#### Journey D: chord → change decomposition

Purpose: answer “Why did total trade change?”

1. The user selects a base year and comparison year.
2. The chord shows the current structure and subtle change markers.
3. The user selects **Explain change**.
4. Ribbons detach and reorder into a reconciled waterfall.
5. Positive and negative partner contributions explain the total difference.
6. Selecting a partner expands its bar into product contributions.
7. Selecting a product expands into detailed product groups.
8. Breadcrumbs preserve the analytical path, for example:

```text
Germany → Total imports → Change since 2019 → China → Machinery
```

The waterfall must reconcile exactly to the displayed change, subject only to
an explicitly documented rounding policy. The implementation must define:

- whether change refers to exports, imports, total trade, or balance;
- how ROW contributes;
- how entering and leaving partners are represented;
- how unavailable observations affect comparison;
- how product hierarchy totals reconcile.

This is among the most analytically valuable journeys and should not be
implemented until those definitions are settled.

#### Journey E: chord → geography

Purpose: move from network structure to spatial concentration without losing
the selected relationships.

1. The user selects **Geography**.
2. Partner arcs move from circular positions to geographic centroids.
3. Chord ribbons become geographic route arcs.
4. The reporter remains anchored.
5. The selected China flow retains its emphasis.
6. Hover or keyboard focus exposes value, share, balance, and five-year
   change.
7. The user selects East Asia.
8. The map zooms and country flows recompose into a regional mini-chord or
   equivalent regional relationship view.

The map and chord answer different questions—where versus how the network is
structured—but represent the same flow entities.

Data dependency: add a reviewed country/region/centroid metadata source and
define treatment for aggregates, territories, and ROW. ROW has no honest
geographic centroid and must not be plotted as if it were a country.

#### Journey F: product lens transformation

Purpose: pivot between “Who does the country trade with?” and “What does the
country trade?” without abandoning context.

1. The national chord begins grouped by partner.
2. The user selects **Group by product**.
3. Partner arcs contract.
4. Product arcs emerge into the same analytical scene.
5. Existing flows are regrouped from reporter → partner into
   product → partner relationships.
6. The user selects Vehicles.
7. Only vehicle flows remain and partners re-rank.
8. The user selects Japan.
9. The scene becomes the reporter–Japan vehicle relationship.

The projection must retain enough partner × product × flow information to
support this pivot without changing values or losing availability semantics.

#### Journey G: balance transformation

Purpose: turn the calculated balance measure into an explainable pathway
rather than leaving it as a KPI card.

1. The user selects the balance figure.
2. Export relationships move to one side and imports to the other.
3. Each partner becomes a diverging pair.
4. Surplus partners rise and deficit partners fall.
5. The centre chord contracts into a balance spine.
6. Selecting China’s deficit opens the products contributing to it.
7. Selecting a product reveals the historical source of the imbalance.

Balance remains explicitly:

```text
reported exports − reported imports
```

for the selected reporter and year. Representation changes must never change
that definition or silently substitute mirror trade.

#### Journey H: Rest-of-World reveal

Purpose: make aggregation transparent rather than presenting ROW as a dead
residual category.

1. The user selects **Other countries**.
2. Its ribbon expands into a temporary holding area.
3. Detail separates into:
   - named countries for which explicit data was collected;
   - unreconciled residual;
   - unavailable or suppressed detail.
4. The user changes **Show top** between top 10, 25, and 50.
5. Countries move between explicit relationships and the aggregate.
6. The world total remains visually and numerically constant.

This journey requires a deeper data decision. The current release collects a
fixed top-K and computes ROW from the remainder. It cannot reveal named
countries that were never collected. Supporting interactive top-N therefore
requires collecting and projecting a larger partner universe, or publishing a
separate on-demand detail artifact. The UI must never pretend that an
unreconciled residual can be decomposed.

#### Journey I: data-quality lens

Purpose: expose reported-flow discrepancies as a serious analytical feature.

1. The user opens Germany-reported imports from China.
2. The user activates **Compare mirror**.
3. The import flow duplicates.
4. One mark represents Germany-reported imports.
5. The other represents China-reported exports to Germany.
6. The physical gap encodes the discrepancy.
7. Selecting the gap reveals:
   - absolute discrepancy;
   - percentage discrepancy;
   - historical discrepancy;
   - possible methodological explanations.
8. Product selection shows where the mismatch is concentrated.

Mirror values remain a comparison and validation signal. They never replace
the reporter’s direct import value. This journey needs a new mirror-flow
artifact, explicit provenance in its schema, and careful handling of CIF/FOB,
timing, re-export, partner attribution, and unavailable data.

#### Flagship reversible journey

The strongest end-to-end demonstration is:

1. Open UAE in 2024.
2. See the national chord.
3. Select China.
4. Transform to the bilateral relationship.
5. Select imports.
6. Transform the import flow into product composition.
7. Select Machinery.
8. Transform the product into history.
9. Select 2019–2024.
10. Transform history into a change waterfall.
11. Select the largest contributor.
12. Open mirror-flow comparison.
13. Press Back repeatedly.
14. Reverse every transformation smoothly to the original chord.

This journey is the integration target for the eventual complete experience.
It crosses several features that need new data, so it should be delivered in
independently verified increments rather than one large frontend rewrite.

### 7.5 Explorer state — Foundation implemented

Use one explicit scene/navigation model rather than allowing every component
to keep unrelated local selection state. A conceptual state shape is:

```ts
type ExplorerState = {
  reporter: string;
  partner: string | null;
  product: string | null;
  year: number;
  comparisonYear: number | null;
  flow: 'export' | 'import' | 'both';
  level:
    | 'country'
    | 'relationship'
    | 'product'
    | 'history'
    | 'change'
    | 'quality';
  representation:
    | 'chord'
    | 'rank'
    | 'map'
    | 'treemap'
    | 'timeline'
    | 'waterfall';
};
```

The production foundation now implements this model as a normalized
`SceneState` plus a discriminated `SceneAction` reducer. It:

- have one authoritative source of truth;
- be serializable into the URL;
- support browser back and forward navigation;
- distinguish persistent selection from transient hover;
- express unavailable states without inventing zeroes;
- make every scene reproducible from a link;
- allow transitions to derive their start and end states.

Every durable user action changes this state. The visual layer derives nodes,
links, dimensions, labels, opacity, selected paths, and annotation copy from
it. No representation owns a separate filter state.

Meaningful analytical state belongs in SvelteKit routing. Scene actions now
use shallow URL pushes, so they create browser history and shareable URLs
without rerunning the page loader. Direct entry remains SSR-compatible and
country changes still load a new projection. Transient interface state
remains local:

- hovered entity;
- tooltip position;
- transition progress;
- open annotation;
- pointer position.

A URL such as:

```text
/country/DEU/2024/imports/CHN/machinery?view=history
```

should reproduce the same analytical scene without forcing a hard document
navigation at every step.

### 7.6 Scene architecture — Foundation implemented

The frontend is now organized around this scene graph:

```text
TradeScene
├── SceneController
│   ├── navigation state
│   ├── transition direction
│   └── reduced-motion policy
├── GeometryEngine
│   ├── country overview layout
│   ├── bilateral layout
│   ├── product layout
│   ├── history layout
│   └── contribution layout
├── EntityLayer
│   ├── partner entities
│   ├── flow entities
│   ├── product entities
│   └── labels and annotations
└── SceneChrome
    ├── question/breadcrumb trail
    ├── year and measure controls
    ├── contextual explanation
    └── accessible scene summary
```

The geometry engine should return declarative geometry keyed by semantic
identity. Svelte components render and transition that geometry. Data
aggregation should remain upstream in the projection generator where
possible.

Use D3 for calculations:

- chord, arc, and ribbon geometry;
- scales and stacks;
- hierarchies and treemaps;
- line and area geometry;
- path interpolation.

Use Svelte for:

- DOM ownership;
- explorer state;
- event handling;
- component lifecycle;
- transitions;
- accessibility;
- routing;
- narrative and explanatory panels.

D3 should calculate geometry from data, not directly mutate the DOM.

### 7.7 Stable semantic keys

Centralize key construction rather than allowing representations to invent
their own identifiers:

```ts
function entityKey(entity: TradeEntity) {
  return [
    entity.reporter,
    entity.partner ?? 'all',
    entity.flow ?? 'both',
    entity.product ?? 'total'
  ].join(':');
}
```

The production key may add entity type, year independence, hierarchy level,
or namespace separators. Its contract must establish:

- which attributes define identity;
- which attributes are measures that may change;
- whether year changes preserve identity;
- how ROW and aggregate entities are keyed;
- how a parent product and child product differ;
- how direct and mirror measures remain distinct.

Without stable keys, representations will fade out and back in. With stable
keys, Svelte can preserve entity lifecycle while D3 interpolates geometry.

### 7.8 Three movement mechanisms

Motion must communicate analytical continuity:

1. **Layout movement** uses keyed lists and FLIP when the same object changes
   position or size. Examples: ranking, reordering, expanding ROW, switching
   top-N, and moving labels or comparison cards.
2. **Cross-view movement** uses coordinated send/receive transitions when an
   object leaves one visual container and appears in another. Examples: a
   ribbon becoming a detail header, an arc becoming a ranked row, a product
   segment becoming a treemap tile, or a selection entering a comparison
   tray.
3. **Geometry interpolation** morphs SVG paths when the same mark changes
   shape. Examples: ribbon to band, arc angle changes, ribbon thickness
   changes, line evolution through time, and year-scrub reconstruction.

Svelte transitions manage lifecycle. D3 path interpolation manages geometry.

Additional rules:

- Preserve keys whenever an entity persists between scenes.
- Use keyed blocks only when semantic state genuinely changes.
- Keep entering and exiting secondary objects subordinate to the selection.
- Animate geometry and emphasis, not every decorative property.
- Resolve interrupted animations to the newest state cleanly.
- Provide a non-spatial reduced-motion path.

### 7.9 Visual grammar

Transitions must use consistent meanings:

| Transition | Analytical meaning |
|---|---|
| Expand | Drill into |
| Contract | Roll up |
| Move right | Advance into detail |
| Move left | Return to parent |
| Split | Reveal composition |
| Merge | Aggregate |
| Reorder | Compare or rank |
| Stretch horizontally | Reveal history |
| Duplicate | Compare two measures |
| Fade | Remove context temporarily |

This grammar is a constraint, not decoration. A direction or motion should not
mean “drill down” in one scene and “go back” in another.

### 7.10 Staged transition choreography

Do not animate every element simultaneously. A default drill sequence is:

| Time | Action |
|---|---|
| 0–150 ms | Dim irrelevant flows and preserve the selected object |
| 150–450 ms | Move or reshape the selection and major structure |
| 350–650 ms | Reveal supporting marks and update headline values |
| 550–800 ms | Introduce labels and explanation; enable the next action |

The selected object moves first, supporting detail follows, and labels arrive
last. Exact durations should be tested and adjusted for distance, device
performance, interruption, and reduced-motion preferences.

Transition choreography should be defined centrally. Individual chart
components should not invent conflicting durations, easings, or navigation
semantics.

### 7.11 Data requirements

The existing route projections were designed for independent chart
components. The continuous scene may need a revised browser projection that
supports adjacent scene transitions without loading a large canonical matrix.

Before changing the data contract:

1. Inventory every value needed in each proposed scene.
2. Identify which values are shared across neighboring scenes.
3. Determine which next-scene data must already be available to begin an
   immediate transition.
4. Keep per-country payloads bounded and measure them.
5. Add contribution data only after defining the exact decomposition.
6. Preserve availability flags, direct-flow provenance, ROW identity, and
   schema-version rejection.

Possible strategies include:

- enriching the existing country projection;
- splitting a country projection into an initial scene payload and
  partner-specific detail payloads;
- prefetching likely next states after the initial scene becomes interactive.

The decision should be based on measured payload and transition latency, not a
desire to minimize the number of files.

Production delivery adds these constraints:

- keep the initial country payload small enough for mobile use;
- publish immutable, version-addressed detail resources;
- prefetch only likely next states after the current scene is interactive;
- allow stale or superseded fetches to be cancelled or ignored;
- keep the current scene usable when optional detail loading fails;
- lazy-load advanced representation code as well as its data;
- never make a visual transition depend on WITS or canonical-matrix parsing.

### 7.12 Interaction and URL semantics

Every narrowing action should answer a visible question:

- “Who does this country trade with?”
- “What is the relationship with China?”
- “Is that relationship export- or import-heavy?”
- “Which products explain it?”
- “How has it changed?”
- “What contributed to the change?”

The current question should be readable in the interface and reflected in the
URL. A breadcrumb or question trail should allow users to return to any prior
level. Browser back should perform the same conceptual reverse transition as
the visible back control.

Hover is explanatory and temporary. Click/tap changes the durable scene.
Keyboard focus must expose the same durable actions.

### 7.13 Accessibility and motion constraints

The continuous scene must remain understandable without animation:

- Every scene needs a concise textual summary.
- Persistent semantic objects need stable accessible names.
- Keyboard navigation must follow the analytical hierarchy.
- Focus must move deliberately when a selected object changes form.
- Color cannot be the only indicator of export, import, balance, selection, or
  unavailable data.
- `prefers-reduced-motion` must produce immediate or simple opacity changes.
- Screen-reader output should announce the new question and key values rather
  than every intermediate animation frame.
- Touch targets and selection behavior must work without hover.

### 7.14 Implementation sequence — Planned

#### Phase A: interaction prototype — Implemented; human assistive-tech review remains

Build an isolated prototype using a small fixed fixture:

1. Country partner overview.
2. Select one partner ribbon.
3. Transform it into bilateral export/import bars.
4. Return to the overview with preserved identity.
5. Test interruption, resize, keyboard operation, and reduced motion.

The prototype should prove semantic-key continuity and transition quality
before the production dashboard is reorganized.

Current increment:

- A dedicated `/motion-lab` route now isolates one production-data chord in a
  full-viewport scene. It deliberately removes dashboard cards and analytical
  drill-downs so ribbon response can be judged on its own.
- The laboratory exposes two interruptible motion studies: **Focus & breathe**
  continuously recalculates chord geometry so the selected relationship
  gains visual weight while its peers contract; **Ribbon extraction** carries
  that same keyed relationship outward without replacing the SVG scene.
- Selecting a new ribbon retargets from the current interpolated state,
  selecting it again or pressing Escape resets the chord, and changing motion
  mode while selected interpolates rather than snapping.
- The study uses production projection data, stable partner keys, D3 layout
  calculation, Svelte-owned SVG, Svelte motion stores, keyboard activation,
  ARIA selection state, responsive geometry, and the shared reduced-motion
  duration policy.
- Browser coverage verifies geometry change, retargeting, mode change, reset,
  keyboard operation, reduced motion, and a narrow viewport. A manual visual,
  physical-touch, and assistive-technology review remains required.
- Network ↔ ranked partners is implemented against production projection data.
- Partner ribbons and ranked bars share semantic partner keys.
- Ranked selection pins the chosen partner and re-ranks the remainder with
  FLIP.
- A keyboard-activated partner ribbon now opens a bilateral relationship scene
  with reported export/import bars and the explicitly defined reported
  balance.
- The partner band retains its semantic key across the network and bilateral
  representations; export and import marks have stable flow keys.
- Returning to the network preserves the partner selection, and direct
  `?view=relationship&partner=<code>` URLs restore the scene.
- Either reported-flow bar opens a partner-and-flow-specific product
  composition using the committed `crossCells` projection. The flow band and
  product tiles retain stable semantic keys.
- Product tiles are keyboard-selectable, disclose value and share, and can be
  restored through
  `?view=products&partner=<code>&flow=<export|import>&product=<code>`.
- The composition reports how much of the bilateral flow is represented by
  published product detail and shows an explicit unavailable state.
- URL restoration and browser history are covered by Playwright.
- Keyboard-operable network marks and ranked controls are present.
- Reduced-motion duration policy is shared by FLIP and cross-view movement.
- Rapid representation reversal is covered under reduced motion.
- Entity-based focus transfer is implemented across partner, flow, and product
  transformations.
- Scene changes produce concise atomic screen-reader announcements.
- Desktop and narrow-viewport layouts have been visually inspected; the scene
  stage exposes compact, standard, and wide responsive modes.

Still required before Phase A is complete:

- compare the two `/motion-lab` studies on real desktop and touch hardware and
  choose the motion grammar that should become the production ribbon response;
- decide whether a selected relationship should remain within the chord
  envelope or begin the future ribbon-to-bilateral transformation;
- manual VoiceOver/NVDA reading-order and announcement review;
- physical touch-device review;
- richer ribbon-to-band and band-to-tile geometry interpolation after the
  interaction and accessibility behavior are proven.

Current data boundary:

- Partner×product detail is currently published only for `crossYear` (the
  release headline year). Historical product composition and product history
  must be backed by a future versioned detail projection; the client must not
  infer those values from national product totals.

Acceptance criteria:

- The selected partner is visibly perceived as the same object.
- No full page or scene flash occurs.
- Back navigation reverses the conceptual transition.
- Fast repeated selection does not leave stale geometry.
- The interaction remains complete with reduced motion enabled.

#### Phase B: formalize scene state and geometry — Foundation implemented

Implemented:

1. Production `SceneState`, normalized reducer, discriminated actions, and URL
   encoding.
2. Durable selection in scene state; hover and tooltip state remain local.
3. A derived `TradeSceneGraph` for country, partner, flow, and product
   entities.
4. Renderer-independent rectangle, path, line, and scene-mark geometry
   contracts.
5. Stable country, partner, flow, and product entity-key helpers.
6. Shared direction vocabulary, choreography timing, crossfade, and
   reduced-motion policy.
7. Shallow routing for local analytical changes and full navigation only for
   data-boundary changes.
8. Playwright coverage for deep links, Back, focus transfer, reduced motion,
   rapid reversal, and responsive mode.

Still to extract as representations evolve:

- pure chord path generation currently remains inside `ChordChart`;
- pure rank/bar layout currently remains inside `RankedPartners`;
- geometry identity should gain direct unit tests when a lightweight unit-test
  runner is added.

#### Phase C: migrate the country experience — Primary shell implemented

1. The shared `SceneStage` shell is implemented.
2. Network, rank, bilateral relationship, and bilateral product composition
   render from the shared graph.
3. Preserve current data correctness and unavailable-value handling.
4. The former dashboard grid is now one full-width, question-led
   `TradeExplorer`. Partner, product, and trend views form one contextual
   evidence tray driven by the same selection.
5. Wide scenes receive expanded chord, bilateral, and product geometry.
   Narrow scenes retain a compact primary canvas and a horizontally
   snap-scrolling evidence tray.
6. The current production route is the compatibility surface; every migration
   must retain its direct-link and data-correctness tests.

Still to migrate:

- treat contextual evidence marks as transformable scene entities rather than
  embedded legacy chart renderers;
- extend the implemented history evidence → primary-canvas pattern to partner
  and product composition evidence;
- replace the temporary representation pill with scene-aware question and
  measure controls;

#### Phase D: add product and history transformations — Bilateral history implemented

Implemented:

1. Bilateral flows transform into product composition.
2. Partner history evidence opens a full-width bilateral export/import
   timeline.
3. The selected year is authoritative across hero totals, scene values,
   partner context, URL state, and accessible descriptions.
4. Timeline points, keyboard arrow movement, and a range scrubber update the
   same state. Scrubbing replaces the current shallow URL entry.
5. Direct `?view=history&partner=<code>&year=<year>` entry, forward
   transformation, relationship return, browser Back, focus transfer, and
   slider focus retention are covered by Playwright.
6. The complete country projection already supplies partner history, so no
   extra fetch or projection split was introduced.

Still required:

- carry product identity into history after publishing a versioned
  partner×product history detail artifact;
- add a comparison year and change interval;
- reconstruct or ghost the national network behind year scrubbing only after
  profiling the interaction cost.

#### Phase E: add comparison representations

1. Add the reversible chord/ranked transformation.
2. Add the partner/product lens pivot.
3. Add the balance-spine representation.
4. Validate that all representations derive from the same explorer state.
5. Preserve entity keys, exact values, and accessible names across each
   transformation.

#### Phase F: add contribution analysis

Define the analytical meaning before building the waterfall. Candidate
questions include:

- Which partners contributed to a country’s balance change?
- Which products contributed to a bilateral balance change?
- Was the change driven by exports, imports, or both?

The decomposition must reconcile to the displayed total change and state how
ROW and unavailable observations are treated.

#### Phase G: add geography, ROW detail, and quality lenses

Treat these as data-backed features, not presentation-only work:

1. Add reviewed geographic metadata and geography transitions.
2. Expand collection/projections before offering interactive ROW top-N.
3. Add a separately versioned mirror-flow comparison artifact.
4. Test direct-versus-mirror provenance and unavailable states.

#### Phase H: consolidate and remove the legacy presentation

After parity and accessibility review:

1. Remove superseded independent chart orchestration.
2. Retain reusable marks, scales, formatters, and geometry utilities.
3. Measure JavaScript, projection payload, interaction latency, and layout
   stability.
4. Update architecture, interaction, and contributor documentation.

### 7.15 Frontend acceptance criteria

The revised experience is ready when:

- A semantic entity keeps a stable identity across adjacent scenes.
- Narrowing and returning feel like transformations of one scene.
- Direct links reconstruct the complete selected scene.
- Browser back and forward follow the same scene hierarchy.
- Values never change merely because representation changes.
- Unavailable data remains visibly distinct from zero.
- Resize and responsive layout do not break transition identity.
- Rapid input does not leave orphaned marks or stale selection.
- Keyboard and touch users can perform the same analytical journey.
- Reduced-motion users receive the same information and navigation.
- Initial and transition payload sizes meet an agreed performance budget.
- Deployed P75 Core Web Vitals meet the agreed targets.
- Versioned data and build assets use verified immutable CDN caching.
- A direct analytical URL loads correctly from a cold browser session.
- Automated tests cover the primary journey and failure states.

### 7.16 Open frontend decisions

#### Scene container technology — Open

- **Question:** SVG-only, HTML/SVG hybrid, or Canvas-assisted?
- **Recommendation:** begin with SVG and HTML overlays because current scale,
  D3 geometry, Svelte transitions, accessibility, and entity counts favor
  inspectable DOM elements. Consider Canvas only after profiling identifies a
  real rendering limit.

#### URL representation — Open

- **Question:** path segments, query parameters, or a hybrid?
- **Recommendation:** keep country and major focus in the path when useful for
  sharing; use query parameters for year, comparison year, measure, and
  optional selections. Finalize after writing example URLs for every scene.

#### Detail payload strategy — Open

- **Question:** one enriched country projection or progressive
  partner-specific payloads?
- **Recommendation:** prototype the complete scene model, measure its payload,
  and choose based on interaction latency. Avoid premature fragmentation.

#### Contribution definition — Open

- **Question:** partner, product, or flow contribution to which change?
- **Recommendation:** choose one explicit analytical question and reconciliation
  equation before designing the waterfall.

#### Legacy `/all` relationship — Open

- **Question:** should `/all` remain a separate comparative scene, become the
  entry state of the same scene system, or be redesigned later?
- **Recommendation:** keep it stable during the first country-scene prototype,
  then assess whether country objects can transition naturally from the
  overview into the country scene.

#### ROW expansion policy — Open

- **Question:** collect a larger fixed partner universe, publish reporter
  detail artifacts, or keep ROW non-expandable?
- **Recommendation:** measure a larger-universe pilot and only offer expansion
  for data that can reconcile honestly.

#### Geographic metadata — Open

- **Question:** which maintained source defines country centroids, regions,
  aggregates, and territories?
- **Recommendation:** choose and version the metadata source before building
  the map transition.

#### Mirror-flow release contract — Open

- **Question:** include mirror comparison data in country projections or
  publish optional detail artifacts?
- **Recommendation:** keep direct reporter flows primary and namespace mirror
  observations explicitly in a separate contract.

#### Static route shape — Open

- **Question:** which analytical URL segments should be finite prerendered
  routes and which should be query state?
- **Recommendation:** prerender reporter paths; keep year, flow, partner,
  product, and representation in shareable query state until direct-entry
  prototypes demonstrate a better route structure.

#### Detail prefetch policy — Open

- **Question:** preload complete country history or fetch partner/comparison
  details progressively?
- **Recommendation:** measure on a deployed mobile preview. Prefer an immediate
  first scene followed by idle or intent-based prefetch of likely next states.

## 8. Near-term improvements

These are useful once the full coordinated release is published.

### 8.1 Rename ambiguous collection presets — Later

Replace `TOP50` and similarly historical names with explicit configured sets,
for example `DASHBOARD_REPORTERS`. Expose a command that lists the resolved
reporters before a long collection starts.

### 8.2 Add a collection estimate/dry run — Later

Add `collect --plan` or `collect --dry-run` to print:

- reporters, flows, products, and years;
- estimated request count;
- cache hit/miss estimate;
- expected staging path;
- approximate runtime at the selected request rate.

This would reduce accidental long WITS jobs and make operational planning
clearer.

### 8.3 Improve resumability — Later

The cache already limits repeated work, but a reporter-level resume command
would make long runs easier to recover. It should reuse successful
reporter-flow artifacts only when their configuration fingerprint matches the
new run.

### 8.4 Validate schemas explicitly in CI — Later

The application and generator enforce schema version 2, while checksums verify
bytes. Add direct JSON Schema validation of newly generated manifests and
projections so schema drift fails with a precise contract error.

### 8.5 Add a release comparison report — Later

Generate an offline report comparing two releases by:

- reporter and flow totals;
- year-over-year discontinuities;
- partner and product coverage;
- ROW share;
- largest absolute and percentage changes;
- records added, removed, or changed.

This would be more valuable than automating publication because historical
source revisions are infrequent and deserve manual review.

### 8.6 Improve UI accessibility coverage — Later

Add focused checks for:

- keyboard operation of country and chart controls;
- focus visibility and focus restoration;
- screen-reader labels and chart summaries;
- contrast in positive, negative, neutral, and unavailable states;
- reduced-motion behavior.

### 8.7 Add visual regression snapshots selectively — Later

Use a few stable representative states rather than snapshotting every chart:

- initial USA view;
- a country with negative balance;
- an unavailable legacy bilateral selection;
- `/all` overview.

The test should tolerate insignificant D3 antialiasing differences.

## 9. Longer-term possibilities

These ideas should be evaluated against actual use before implementation.

### 9.1 Mirror-trade quality reporting — Idea

Compare reporter imports against partner-reported exports as a quality signal.
Do not substitute mirror values into the primary balance calculation. Publish
discrepancies with clear CIF/FOB, timing, re-export, and reporting caveats.

### 9.2 Richer provenance — Idea

Record source request configuration, resolved reporter/product sets, collector
version, cache policy, and a reproducibility fingerprint in the manifest. Do
not include secrets, machine-specific paths, or nondeterministic timestamps in
artifact checksums.

### 9.3 Configurable coverage policy — Idea

The current top-K plus ROW design is appropriate for the dashboard. If users
need stronger bilateral completeness, allow release policy to require a
minimum explicit-partner share or increase top-K for reporters whose coverage
falls below a threshold.

### 9.4 More scalable canonical formats — Idea

CSV gzip is transparent, deterministic, compact enough, and dependency-light.
Consider Parquet only if analytical consumers or release size justify the
additional format and dependency. The web application should continue using
JSON projections regardless.

### 9.5 Release automation — Idea

A manual `workflow_dispatch` job could collect or publish data, but automated
PR creation should wait until regeneration becomes frequent. Network-based
WITS collection should not become a required per-push CI job.

### 9.6 Broader application tests — Idea

Add tests for URL restoration, empty reporters, unsupported schemas, failed
projection fetches, mobile layout, and deployment-specific routing when those
areas begin changing regularly.

### 9.7 Observability for deployed static data — Idea

If the project gains meaningful traffic, monitor missing projection requests,
client-side schema rejection, and route-load failures without collecting
sensitive user data.

## 10. Deliberate non-goals

- Do not make Python a dependency of `npm install`, `npm run dev`, or the web
  production build.
- Do not regenerate WITS data on every push or pull request.
- Do not infer primary imports by reversing export records.
- Do not use a filesystem symlink between canonical and browser artifacts.
- Do not serve the canonical CSV directly to the browser.
- Do not silently coerce unavailable observations to zero.
- Do not overwrite immutable published release directories.
- Do not commit staging data, caches, raw responses, or timestamped shards.
- Do not add a release bot or large test matrix until recurring maintenance
  demonstrates the need.

## 11. Open decisions

Keep unresolved choices here. Each entry should record context, options,
recommendation, decision, and date.

### Full-release version name — Open

- **Context:** `2026-07.1` is a projection compatibility release, not a newly
  collected canonical dataset.
- **Recommendation:** use a new date-based version for the first fully
  coordinated historical recollection.
- **Decision needed:** exact version after the full run is reviewed.

### Reporter preset naming — Open

- **Context:** the `TOP50` token currently resolves to the configured dashboard
  reporter set, which contains 30 reporters.
- **Recommendation:** rename it to describe its purpose instead of an outdated
  count.
- **Decision needed:** preferred public CLI name and whether `TOP50` remains as
  a temporary alias.

### Coverage acceptance threshold — Open

- **Context:** release manifests now expose distribution and worst-case
  coverage, but publication does not enforce a project-specific minimum.
- **Recommendation:** inspect the full run before choosing a threshold; avoid
  inventing one from the two-country pilot.
- **Decision needed:** whether low coverage blocks publication or is reported
  as a caveat.

## 12. How to extend this roadmap

When adding feedback:

1. Put new concrete work under **Immediate next work**, **Near-term
   improvements**, or **Longer-term possibilities**.
2. Put choices that change data meaning or contracts under **Open decisions**.
3. State whether the item is correctness, reliability, performance, user
   experience, or maintenance work.
4. Include acceptance criteria where possible.
5. Move an item to **Completed implementation** only after implementation and
   verification are both finished.
6. Preserve rejected ideas under **Deliberate non-goals** when the reason may
   matter later.

Related documents:

- [Architecture](./architecture.md)
- [Data methodology](./data-methodology.md)
- [Data release procedure](./data-release.md)
- [Vercel deployment and performance](./deployment-performance.md)
- [Original monorepo and data-product plan](../plan.md)
