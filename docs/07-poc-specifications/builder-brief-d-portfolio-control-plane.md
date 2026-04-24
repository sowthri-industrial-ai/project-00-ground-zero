# Builder Brief · D · Portfolio Control Plane

```
Brief ID     · BRIEF-D
Block        · D · Portfolio Control Plane (PCP)
Project      · genai-portfolio-hub  (site lives in hub, not project repo)
Wave         · 2 (parallel with Brief C)
Dependencies · Brief A (repo scaffold) · reads ledger schema from Brief C
Deliver to   · Architect chat for review
```

---

## § 01 · Context · You are here

You are Builder-D. Self-contained Brief. Architectural choices locked in Charter + ADRs.

You are the Portfolio Control Plane block. Your job: build the public-facing site that renders the portfolio's state of the world. This is the URL on the architect's resume — `<user>.github.io` per ADR-0012.

**Unique among the Briefs, your output lives in `genai-portfolio-hub`, not `project-00-ground-zero`.** The PCP is portfolio-wide, not project-specific. Individual project pages under the PCP are assembled from project-repo markdown at build time.

**You run in parallel with Brief C.** You define the ledger rendering contract; C produces the ledger entries. You read Brief C's schema.

**Remember ADR-0003**: PCP hosts on GitHub Pages, not Azure. Monitoring must be independent of monitored. The site stays up when Azure is down — that's the point.

---

## § 02 · Goals

1. Author Astro 5 project in `genai-portfolio-hub/control-plane/`
2. Implement 7+1 zones (Home · Architecture · Principles · Projects · Governance · As-Built · TCO · Review)
3. Implement ledger renderer (JSONL → HTML timeline)
4. Implement `metadata.json` renderer (project-card generator)
5. Implement live status widget (UP · SLEEPING · SPIN-UP-REQUESTED · DOWN)
6. Implement drift detection (Local vs Git vs HF SHAs)
7. Implement honest placeholder components (for projects not yet started)
8. Deploy to GitHub Pages on `<user>.github.io`
9. Author editorial design tokens consistent with ARGOS aesthetic (paper-cream + Fraunces + teal/amber)
10. Document in `docs/05-runbook.md` §§ 10–12

---

## § 03 · Non-Goals

- ❌ Do NOT modify Brief A's or C's contracts (only consume them)
- ❌ Do NOT build project-content authoring tools (markdown files suffice)
- ❌ Do NOT implement auth / admin panel (this is a public static site)
- ❌ Do NOT implement analytics tracking (GH Pages provides basic stats · privacy preferred)
- ❌ Do NOT implement search (Wave 5 polish if needed)
- ❌ Do NOT build the `architecture.html` files — those are architect-authored per ADR-0008 exception
- ❌ Do NOT implement comments / discussions (out of scope)

---

## § 04 · Deliverables (exhaustive)

### Deliverable 1 · Astro project scaffold

At `genai-portfolio-hub/control-plane/`:

```
control-plane/
├── package.json
├── astro.config.mjs
├── tsconfig.json
├── .nvmrc                          (node 20)
├── public/
│   ├── favicon.svg
│   └── fonts/                      (Fraunces, Geist Sans, JetBrains Mono self-hosted)
├── src/
│   ├── content/
│   │   ├── config.ts               (content collections schema)
│   │   ├── projects/               (.md per project · frontmatter schema enforced)
│   │   ├── principles/             (.md per principle)
│   │   └── adrs/                   (.md per ADR · hub-level if portfolio-wide)
│   ├── components/
│   │   ├── ZoneNav.astro
│   │   ├── ProjectCard.astro
│   │   ├── LedgerTimeline.astro
│   │   ├── LiveStatusBadge.astro
│   │   ├── DriftIndicator.astro
│   │   ├── HonestPlaceholder.astro
│   │   ├── TcoTable.astro
│   │   └── EditorialFooter.astro
│   ├── layouts/
│   │   └── PageLayout.astro
│   ├── pages/
│   │   ├── index.astro             (Home)
│   │   ├── architecture.astro      (Architecture)
│   │   ├── principles/[...slug].astro
│   │   ├── projects/[...slug].astro
│   │   ├── governance.astro
│   │   ├── as-built.astro          (ledger render)
│   │   ├── tco.astro
│   │   └── review/[project].astro  (post-close narrative)
│   ├── scripts/
│   │   ├── fetch-ledger.ts         (reads from project repos at build time)
│   │   ├── fetch-metadata.ts
│   │   └── check-drift.ts
│   └── styles/
│       ├── tokens.css              (design tokens · ARGOS palette)
│       └── global.css
└── README.md
```

### Deliverable 2 · Seven primary zones + Review

#### Zone 1 · Home (`/`)
- **Role**: 30-second attention budget · who/what/why
- **Above the fold**: Architect name · one-sentence thesis · 8 badges from project-00 · link to CV PDF
- **Fold 2**: Current state snapshot — `Ground Zero: in-progress · Wave 2 · 10 of 13 DoD criteria ✅`
- **Fold 3**: Project list (card grid) · each card shows name · status · live-demo link · drift indicator

#### Zone 2 · Architecture (`/architecture`)
- **Role**: 3-minute budget · the thesis visualized
- **Content**: Embedded `architecture.html` from `project-00-ground-zero/html/architecture.html` (Wave 5 artifact)
- **Fallback while Wave 5 incomplete**: Honest placeholder — *"Architecture visualization shipping Wave 5"*

#### Zone 3 · Principles (`/principles`)
- **Role**: What the architect believes · timeless
- **Content**: Markdown files in `content/principles/` · rendered with Prose typography
- **Initial content** (seeded by you): P-SelfDescribing · Platform-before-Payload · Monitor-Outside-Monitored · Honest-Over-Polished

#### Zone 4 · Projects (`/projects`)
- **Role**: The portfolio itself
- **Content**: Grid of cards · one per project · clicking a card goes to `/projects/<slug>`
- **Project detail page** pulls from:
  - Project repo's `metadata.json` (status · URLs · cost · stack)
  - Project repo's `README.md` (overview)
  - Project repo's `docs/01-HLD.md` (architecture summary)
  - Project repo's `as-built/ledger.jsonl` (recent activity)
- **For projects not yet started**: Honest Placeholder component renders — *"Project 1 · Not started · ETA month"*

#### Zone 5 · Governance (`/governance`)
- **Role**: How the architect builds · process transparency
- **Content**: Renders the Charter template · the Builder Brief contract · the Stage Gate definitions · the Test Tier taxonomy · the Responsible AI thresholds
- Shows the *invisible* infrastructure · signals maturity

#### Zone 6 · As-Built (`/as-built`)
- **Role**: What actually happened · portfolio-wide ledger
- **Content**: Aggregated `ledger.jsonl` from all project repos · sorted reverse-chronological · rendered as a timeline table
- Includes REJECTED entries · NOT curated to success · honest history
- Filters by project · action · status

#### Zone 7 · TCO (`/tco`)
- **Role**: Money spent · financial transparency
- **Content**: Portfolio-wide cost summary · per-project breakdown · pulled from project `docs/06-tco.md` and `tco.xlsx` (rendered via SheetJS) and `metadata.json.cost.spent_usd`
- Initial state: Ground Zero TCO only · Project 1+ fields populated as projects progress

#### Zone 8 (+1) · Review (`/review/<project>`)
- **Role**: Post-close narrative · "what I learned"
- **Content**: Project repo's `html/review.html` OR `docs/review.md`
- Only visible for projects in `status: closed`

### Deliverable 3 · Components

#### `ZoneNav.astro`
Sticky top nav with zone links · active-zone highlighted · mobile-responsive hamburger.

#### `ProjectCard.astro`
```astro
---
import type { CollectionEntry } from 'astro:content';
import LiveStatusBadge from './LiveStatusBadge.astro';
import DriftIndicator from './DriftIndicator.astro';
interface Props { project: CollectionEntry<'projects'>; }
const { project } = Astro.props;
const meta = project.data;
---
<article class="project-card" data-status={meta.status}>
  <header>
    <h3>{meta.name}</h3>
    <span class="phase">{meta.phase}</span>
  </header>
  <p>{meta.description}</p>
  <footer>
    <LiveStatusBadge url={meta.urls.live_demo} />
    <DriftIndicator local={meta.sync.local_sha} git={meta.sync.github_sha} hf={meta.sync.hf_sha} />
    <a href={`/projects/${project.slug}`}>View →</a>
  </footer>
</article>
```

#### `LedgerTimeline.astro`
Renders JSONL entries · reverse-chronological · grouped by day · failure entries in red accent.

#### `LiveStatusBadge.astro`

**This is the ADR-0013 ephemeral-endpoint UX.** Fetches `<url>/health` on page load · 3-second timeout · renders:

- ✅ **LIVE** · green · endpoint returned 200
- 💤 **SLEEPING** · grey · timeout or 503 · "wake this up" button triggers HF Space (or shows ephemeral-endpoint message for Azure)
- 🔄 **SPIN-UP-REQUESTED** · amber · button was clicked · polling every 5 sec
- ❌ **DOWN** · red · error response or unreachable

Client-side JS (Astro island):

```typescript
// src/components/LiveStatusBadge.ts
export async function checkStatus(url: string): Promise<Status> {
  if (!url) return 'not-deployed';
  try {
    const res = await fetch(`${url}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) return 'live';
    if (res.status === 503) return 'sleeping';
    return 'down';
  } catch (e) {
    return 'sleeping';  // timeout typically means HF Space cold / Azure torn down
  }
}
```

**Critical copy decision**: For Azure endpoints showing SLEEPING, the "wake this up" UX says:

> *"This endpoint is ephemeral (see ADR-0013). For a live demo, schedule an interview — Azure spins up in ~8 minutes, burn rate ~$0.50. HuggingFace Space below is always-available."*

This is an architect-signal moment. Explain the pattern, not mask it.

#### `DriftIndicator.astro`
Compares SHAs across Local / Git / HF Space · shows `✅ in sync` or `⚠️ drift detected` with details. Data source: `metadata.json.sync.*` fields populated by `deploy.sh`.

#### `HonestPlaceholder.astro`
Renders a first-class placeholder · not a 404 · not a "coming soon." Shows:
- What the project is planned to be (1-line)
- Why it's not started (1-line — optional)
- ETA or dependency (if known)
- Link to Charter (where the project is specified)

Example:
> *Project 1 · Industrial RAG · Not started · Planned after Ground Zero closes · [See Charter](…)*

### Deliverable 4 · Content collections schema

`src/content/config.ts`:

```typescript
import { defineCollection, z } from 'astro:content';

const projects = defineCollection({
  type: 'content',
  schema: z.object({
    project_id: z.string(),
    name: z.string(),
    status: z.enum(['not-started', 'in-progress', 'closed']),
    phase: z.string(),
    order: z.number(),
    description: z.string(),
    urls: z.object({
      github: z.string().url(),
      hf_space: z.string().url().nullable(),
      hf_model: z.string().url().nullable(),
      live_demo: z.string().url().nullable(),
      docs: z.string(),
    }),
    stack: z.array(z.string()),
    tco_budget_usd: z.number(),
    tco_spent_usd: z.number().default(0),
  }),
});

const principles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    order: z.number(),
    summary: z.string(),
  }),
});

export const collections = { projects, principles };
```

### Deliverable 5 · Build-time data fetchers

`src/scripts/fetch-ledger.ts` — fetches `as-built/ledger.jsonl` from each project repo via raw GitHub URL · concatenates · sorts · outputs to `src/data/ledger-aggregate.json`.

`src/scripts/fetch-metadata.ts` — fetches `metadata.json` from each project repo · outputs to `src/data/metadata-aggregate.json`.

`src/scripts/check-drift.ts` — polls GitHub API and HF Hub API for latest commit SHA · compares against `metadata.json.sync.*` · outputs drift report.

Run at build time as Astro integration · cached per build.

### Deliverable 6 · Design tokens · editorial aesthetic

`src/styles/tokens.css`:

```css
:root {
  /* Palette — paper-cream editorial per ARGOS inheritance */
  --paper: #FAF6EC;
  --paper-soft: #EFEADC;
  --ink: #1B1916;
  --ink-mute: #6B6559;
  --teal: #0D3B52;
  --teal-italic: #1A5F7A;
  --amber: #B35C00;
  --amber-soft: #F3E6D2;
  --red: #9E2A2F;
  --red-soft: #F5D8D8;

  /* Typography */
  --font-serif: 'Fraunces', 'Iowan Old Style', Georgia, serif;
  --font-sans:  'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono:  'JetBrains Mono', 'SF Mono', Monaco, monospace;

  /* Spacing scale */
  --s-1: 0.25rem;
  --s-2: 0.5rem;
  --s-3: 0.75rem;
  --s-4: 1rem;
  --s-5: 1.5rem;
  --s-6: 2rem;
  --s-7: 3rem;
  --s-8: 4rem;

  /* Layout */
  --content-w: 72ch;
  --wide-w: 100ch;

  /* Texture — subtle grid on background */
  --grid: linear-gradient(var(--paper-soft) 1px, transparent 1px) 0 0 / 40px 40px,
          linear-gradient(90deg, var(--paper-soft) 1px, transparent 1px) 0 0 / 40px 40px;
}

body {
  background: var(--paper);
  background-image: var(--grid);
  color: var(--ink);
  font-family: var(--font-sans);
  font-feature-settings: 'ss01', 'cv11';
}

h1, h2, h3 { font-family: var(--font-serif); font-weight: 500; }
code, pre { font-family: var(--font-mono); }
em { color: var(--teal-italic); font-style: italic; }
```

Mirror the v1.1 distillation aesthetic · inherit don't redesign.

### Deliverable 7 · GitHub Pages deploy

`pcp-update.yml` in `genai-portfolio-hub/.github/workflows/`:

```yaml
name: "🏛️ PCP · Rebuild"

on:
  push:
    branches: [main]
    paths:
      - 'control-plane/**'
      - 'charters/**'
      - 'shared/**'
  schedule:
    - cron: '0 */6 * * *'   # rebuild every 6hr to catch project-repo changes
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd control-plane && npm ci
      - run: cd control-plane && npm run build
        env:
          GITHUB_PAT: ${{ secrets.PCP_READ_PAT }}   # scoped to read project repos
      - uses: actions/upload-pages-artifact@v3
        with: { path: control-plane/dist }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - id: deploy
        uses: actions/deploy-pages@v4
```

Then enable GitHub Pages in `genai-portfolio-hub` settings · source = GitHub Actions · custom domain left blank per ADR-0012.

**The `PCP_READ_PAT` secret** — a fine-grained GitHub PAT scoped to Read-Only access to project repos (needed at build time to fetch `metadata.json` and `ledger.jsonl`). One-time setup in runbook § 10.

### Deliverable 8 · Runbook §§ 10–12

- § 10 · PCP architecture overview · zones · component patterns
- § 11 · Content model · how to add a new project (write markdown · push · PCP rebuilds)
- § 12 · Deploy · GitHub Pages setup · PAT scope · DNS-not-needed (free tier)

---

## § 05 · Interface Contracts

### Contract IN · From Brief A

- `genai-portfolio-hub` repo exists and is yours to populate `control-plane/`

### Contract IN · From Brief C

- Ledger JSONL schema · you render it
- `metadata.json` schema · you render project cards from it
- Workflow run URLs · deep-link format stable

### Contract IN · From Brief B (indirect)

- Health endpoint contract · Live Status Badge pings this at runtime (client-side)

### Contract OUT · To all future projects

- Project repos add a `metadata.json` + `README.md` + `docs/01-HLD.md` + `as-built/ledger.jsonl` → auto-appear in PCP on next build
- Project repos adhere to the `project-<nn>-<slug>` naming convention so PCP discovery works

### Contract OUT · To hiring reviewers

- `https://<user>.github.io` lands on Home zone · clear thesis · project grid · live status
- Every other zone linked from main nav · attention budgets respected

---

## § 06 · Step-by-Step Implementation Guidance

### Step 1 · Node + Astro scaffold

```bash
cd genai-portfolio-hub
mkdir control-plane && cd control-plane
npm create astro@latest . -- --template minimal --typescript strict --no-install --no-git
npm install
npm install @astrojs/sitemap @astrojs/mdx
```

### Step 2 · Design tokens + fonts

Install self-hosted font files in `public/fonts/` (Fraunces, Geist, JetBrains Mono · via `fontsource` or direct download). Author `tokens.css` + `global.css`.

### Step 3 · Content collections schema

Author `src/content/config.ts` per Deliverable 4. Validate by running `npm run astro sync`.

### Step 4 · PageLayout + ZoneNav

Author base layout + top-nav. Get to "empty but stylistically correct" state first.

### Step 5 · Home page

`src/pages/index.astro` · render architect info · project grid · Ground Zero status badge. Fetch from `src/data/metadata-aggregate.json`.

### Step 6 · Projects zone

Dynamic route `src/pages/projects/[...slug].astro` · renders per-project page from content collection + fetched `metadata.json`.

### Step 7 · As-Built zone (ledger)

`src/pages/as-built.astro` · renders `LedgerTimeline` from aggregated JSONL.

### Step 8 · Architecture zone

`src/pages/architecture.astro` · iframes or embeds `project-00-ground-zero/html/architecture.html` when available · otherwise renders `HonestPlaceholder`.

### Step 9 · Principles + Governance + TCO zones

Markdown-driven content collection renders via `src/pages/principles/[...slug].astro` and single-page Governance and TCO pages.

### Step 10 · Live Status Badge (island)

Client-side fetcher. Test locally with `docker compose up` in the project-00 repo · point PCP to `http://localhost:8080` during dev.

### Step 11 · Drift Indicator

Build-time check (runs in Actions) · result baked into static HTML. Low accuracy acceptable (rebuild every 6hr).

### Step 12 · PCP deploy workflow

Commit `.github/workflows/pcp-update.yml`. Set PAT secret. Enable GitHub Pages on the hub repo.

### Step 13 · First deploy

```bash
git push origin main
gh workflow watch pcp-update.yml
# Wait for GitHub Pages to issue cert · visit https://<user>.github.io
```

### Step 14 · Runbook §§ 10-12

Author with screenshots of PCP zones and one dispatch example.

### Step 15 · Self-test

- [ ] Astro builds locally (`npm run build` · no errors)
- [ ] All 8 zones render
- [ ] Home shows project grid · Ground Zero card present
- [ ] Project grid uses `HonestPlaceholder` for Project 1+ (not-started)
- [ ] Ledger timeline renders (initially with 1–2 entries from Brief C tests)
- [ ] Live Status Badge hits local endpoint · shows LIVE · handles timeout → SLEEPING
- [ ] Drift Indicator renders based on static data
- [ ] PCP deploys to `<user>.github.io` · SSL active
- [ ] First page-load under 1 second (static + minimal JS)
- [ ] Lighthouse score > 90 on all 4 axes

---

## § 07 · Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| D-01 | Astro project builds clean (`npm run build`) | Build output |
| D-02 | All 8 zones render with content | Screenshots |
| D-03 | Editorial aesthetic applied (paper-cream · Fraunces · teal/amber) | Visual review |
| D-04 | `<user>.github.io` loads with SSL active | URL + cert inspection |
| D-05 | Ledger timeline renders · newest first · REJECTED entries visible | Screenshot |
| D-06 | Live Status Badge handles LIVE · SLEEPING · DOWN states | Manual testing |
| D-07 | Ephemeral-endpoint copy present for Azure URLs (ADR-0013) | Component inspection |
| D-08 | Honest placeholder renders for Project 1+ | Screenshot |
| D-09 | Drift indicator compares Local · Git · HF SHAs | Component inspection |
| D-10 | `pcp-update.yml` configured · PAT scope minimal | Workflow + secret audit |
| D-11 | Rebuild every 6hr cron active | Workflow YAML |
| D-12 | First page-load under 1s | Browser dev tools |
| D-13 | Lighthouse score > 90 on Performance · Accessibility · Best Practices · SEO | Lighthouse report |
| D-14 | Runbook §§ 10-12 authored | File read |
| D-15 | No auth · no admin panel · no comments (scope respected) | Feature inventory |

---

## § 08 · Review Rubric (Architect's checks)

1. Visit `<user>.github.io` · 30-second attention test · does thesis land?
2. Click through all 8 zones · check attention budget for each
3. Test Live Status Badge with known-live URL · known-dead URL · test SLEEPING UX
4. Read ephemeral-endpoint copy aloud · does it sound like architect signal or excuse?
5. Check editorial aesthetic fidelity to v1.1 distillation
6. Run Lighthouse · scores > 90
7. Check ledger timeline · failures visible · not curated away
8. Dispatch a `pcp-update.yml` run · watch build · verify rebuild reflects new ledger entry

---

## § 09 · Risks & Your Mitigations

| Risk | Mitigation |
|---|---|
| PCP shows "empty portfolio" reading as "not started" | Honest placeholders are first-class · Ground Zero always visible from day 1 · Hello AI demo linked prominently |
| Live Status Badge fires too many cross-origin fetches on page load | Lazy-load below fold · client-side cache with 60s TTL · batch checks in one request when possible |
| HF Space "sleeping" misreads as "broken" | Explicit SLEEPING state · ADR-0013 copy explains |
| GitHub Pages build time minutes cap (2000/mo for private · unlimited for public) | Repo public · no concern |
| PAT secret leak | Fine-grained PAT · read-only scope · limited repos · 1-year expiry documented for rotation |
| Project-repo `metadata.json` missing/malformed breaks build | Zod schema on content collection rejects at build time · clear error |

---

## § 10 · Escalation Contract

Same format as prior Briefs.

---

## § 11 · Expected Output Format

1. **Hub repo URL** with `control-plane/` populated
2. **Published PCP URL** · `<user>.github.io`
3. **Screenshots** of all 8 zones
4. **Lighthouse report** (PDF or JSON)
5. **Self-assessment** · 15 acceptance criteria with evidence
6. **Open escalations** (if any)

---

## § 12 · Closure

Brief D closes when Architect signs off. On closure:
- PCP live · `<user>.github.io` functional
- Brief E's Hello AI deploys feed the Ground Zero project card
- Future projects inherit the PCP surface · no re-work needed to integrate

---

**End of Builder Brief · D · Portfolio Control Plane**

`Dammam · 2026-04-24 · Rev 1.0`
