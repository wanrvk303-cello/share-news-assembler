# Project Context: Stock News Aggregator (RSS-driven, Real-time UI)

> Agentic Engineering Best Practices Addendum
> This document serves as the shared contract between subagents and the orchestrator. Updates should be monotonic: append new decisions and resolved items; avoid deleting historical rationale unless superseded.


## 1. What this app does
A web application that helps users quickly view news that may affect the stock prices of the stocks they hold.

The app is an **aggregator**: it **monitors external finance RSS feeds** and presents curated items. Users can click through to view the **full article** on external finance forums / sources (we do not write blog articles inside the app).

## 2. Core user experience (3 views)
The UI provides three distinct news “surfaces”:

### A) Personal View (by user’s holdings)
- Users see **all news related to the stocks they currently hold**.
- News items are grouped/filtered by the user’s selected holdings.
- Designed for quick daily scanning (morning/evening).

### B) Per-Stock View (single stock)
- Users can choose a single stock and see only news for that stock.
- Includes a filter/search UX so they can find the relevant stock quickly.

### C) Market/Generic View (whole market)
- News items that affect the **entire stock market** or broad sectors.
- Examples: geopolitical events, broad market moves, major macroeconomic commentary.
- This view is not restricted to the user’s holdings (though the user’s holdings will still be impacted indirectly).

## 3. News item data model (required fields)
Each displayed news item must include:
- **Title**
- **Date**
- **Teaser** (short summary)
- **Link** (URL to the complete external article)

## 4. Stock management (CRUD)
Users can manage their holdings with straightforward actions:
- **Add** a stock to their holdings
- **Update** stock-related settings (if applicable)
- **Delete** a stock from their holdings

(“Update” may mean renaming/mapping/metadata depending on the chosen stock identifier strategy.)

## 5. Real-time / near real-time expectations
- The app will **monitor RSS feeds continuously** (or on short intervals) and update the displayed news.
- Target: “real time” behavior from a user perspective.
- Implementation approach will likely involve:
  - a backend scheduler/worker that polls RSS feeds frequently
  - storing parsed results
  - the web UI reading from the backend via APIs
  - optional push mechanisms (WebSockets / SSE) if needed later

## 6. Aggregator behavior & source linking
- The app will ingest RSS feeds and parse each feed item.
- It will store minimal structured metadata (title/date/teaser/link + stock mapping + categories like “market-wide”).
- It will **not** create or host full articles.

## 7. UI/UX requirements
- Very easy and familiar for users.
- Quick browsing and reading.
- Fast navigation between:
  - Personal → Per-stock → Market-wide
- Stock selection should be simple and low-friction.
- News list UX improvements (v1+):
  - News age filter toggle (e.g., **Last 24h / Last 7 days / All**) to keep morning reads tight
  - In the portfolio/personal view, show a **ticker badge** on each news card for at-a-glance relevance
  - In the portfolio/personal view, show a **“Why this article” / matched: <ticker>** tag on each card

## 8. Suggested architecture (high-level)
Not implemented yet (context only), but plan should support:

### Components
- **Frontend Web App**
  - Views: Personal, Per-Stock, Market/Generic
  - Stock add/update/delete UI
  - News list components (title/date/teaser/link)
- **Backend API**
  - User holdings management endpoints (CRUD)
  - News endpoints:
    - personal news (based on user holdings)
    - per-stock news (based on a stock identifier)
    - market-wide news (category mapping)
  - RSS ingestion endpoints/workers (internal)
- **RSS ingestion subsystem**
  - Poll RSS feeds
  - Parse and normalize items
  - Map items to stocks or “market-wide”
  - Store new/updated items
- **Database**
  - Users
  - Holdings (user ↔ stock)
  - News items (normalized)
  - Mappings (how a feed item maps to stocks/market-wide)

### Real-time strategy
Start with polling + API refresh; optionally enhance with push (SSE/WebSockets) after baseline is stable.

## 9. Implementation checklist (summary)
This file intentionally includes a detailed checklist in section 10 for continuous updates.

## 10. Implementation Checklist (living document)
>This section is the “implementation checklist” for the project and must be updated as work progresses (new decisions, completed milestones, and any changed priorities).

### Phase 0 — Project & requirements alignment
- [ ] Confirm stock identifier strategy:
  - Ticker symbol (e.g., AAPL) vs ISIN/CUSIP vs exchange-specific format
- [ ] Confirm how RSS items map to stocks:
  - keywords in titles?
  - feed-specific tagging?
  - external metadata?
- [ ] Confirm definition of “market-wide” category:
  - specific RSS feeds
  - tagging rules
  - keyword rules / taxonomy

### Phase 1 — Data modeling (DB schema)
- [ ] Users table
- [ ] Holdings table (user_id, stock_id/ticker, metadata)
- [ ] News items table (title, date, teaser, link, source, hash/dedupe keys)
- [ ] Optional: item-to-stock mapping table (if one item can map to multiple stocks)
- [ ] Optional: item-to-category mapping table (market-wide vs stock-specific)

### Phase 2 — RSS ingestion
- [ ] Collect RSS feed sources to monitor
- [ ] Build RSS fetcher
  - polling interval
  - retry/backoff on failures
- [ ] Parse RSS entries
  - title, pubDate/date, link, description/body excerpt (teaser)
- [ ] Normalize and deduplicate
  - hash-based dedupe using (title+date+link) or guid
- [ ] Map items to:
  - specific stocks
  - market-wide category
- [ ] Persist to DB
- [ ] Add logging + basic monitoring

### Phase 3 — Backend APIs
- [ ] Holdings CRUD endpoints:
  - list holdings
  - add holding
  - update holding (if applicable)
  - delete holding
- [ ] News endpoints:
  - personal: aggregate news for user holdings
  - per-stock: news for a chosen stock
  - market-wide: news for market-wide category
- [ ] Pagination, sorting (likely newest first)
- [ ] Response shape consistent with required UI fields:
  - title, date, teaser, link

### Phase 4 — Frontend UI
- [ ] Create 3 navigation routes:
  - Personal View
  - Per-Stock View
  - Market/Generic View
- [ ] Stock selector component:
  - searchable list
  - ability to add stocks
- [ ] Holdings management UI:
  - add/update/delete
- [ ] News list components:
  - card/list layout with title/date/teaser/link
  - open link in new tab
- [ ] Loading/empty/error states

### Phase 5 — “Real-time” behavior validation
- [ ] Verify RSS updates propagate to UI quickly
- [ ] Add refresh strategy:
  - periodic client refresh OR server push (SSE/WebSocket) later
- [ ] Ensure no duplicates appear after refresh

### Phase 6 — Quality & operational readiness
- [ ] Security:
  - authentication (if required)
  - rate limiting
- [ ] Error handling:
  - broken RSS feeds
  - malformed entries
  - missing teaser/date
- [ ] Performance:
  - indexing in DB for queries by user/stock/category
  - caching if needed

### Phase 7 — Testing plan (to be executed once code exists)
- [ ] Unit tests for RSS parsing & mapping
- [ ] Integration tests for ingestion → DB → API
- [ ] API tests using curl for:
  - personal view
  - per-stock view
  - market-wide view
  - holdings CRUD
- [ ] Frontend smoke tests:
  - route navigation
  - stock add/delete
  - news rendering and link navigation

## 11. Open questions / decisions (to be filled)
- [ ] Which RSS feed URLs are used initially?
- [x] Polling interval target: 15 min vs 30 min (tradeoff: freshness vs API/load) → **30 min** (near-real-time with controlled load)
- [x] Stock autocomplete strategy:
  - [x] Hybrid: use a **static universe of common tickers** for fast UX + optionally fall back to an external lookup when the input doesn’t match
  - [ ] (external lookup source TBD; e.g., Yahoo Finance search or another provider)
- [x] Deduplication strategy:
  - [x] Deduplicate by URL first
  - [x] Fuzzy title similarity as a secondary fallback when URLs differ but the story is clearly the same
- [x] Read/unread state scope:
  - [x] Explicitly out of v1 (avoid DB/schema bloat now)
- [x] News retention period for cached/ingested items → **30 days**
- [x] Do we support multiple markets/exchanges? → **Keep US first**, but **design for adding Nairobi Stock Exchange (NSE) stocks later** (e.g., pluggable ticker universe + feed/source mapping per exchange)
- [x] Do we require user accounts now, or later? → **Later** (support simple per-user/per-browser holdings first; auth later)
- [x] How do we handle stock mapping ambiguity? → prefer explicit feed tagging/keywords; otherwise keyword match with a confidence threshold (manual review/tuning later)

## 12. Notes
- Keep the aggregator scope clear: users view external articles via links; our app provides discovery and relevance.
- Keep the UI fast: small payloads (title/date/teaser/link) and pagination.

---

## 13. Agent roles & responsibilities (subagents)

### Orchestrator Agent (primary)
Responsibilities:
- Own the workflow lifecycle: plan → delegate → integrate → validate.
- Enforce “monotonic updates” to this doc and prevent contradictory specs.
- Maintain traceability: every decision is linked to a phase and an acceptance criterion.
- Produce the final merged output for each iteration.

Inputs:
- Current `context.md` state (source of truth)
- Repo observations (file tree, build status)

Outputs:
- Updated `context.md`
- A set of git commits per major change

### Subagent A — Ingest/Parse Subagent
Responsibilities:
- Specify RSS fetcher behavior: polling, retry/backoff, parsing robustness.
- Define normalization + dedupe keys.
- Define mapping strategy from feed item → stock(s)/market-wide.

Inputs:
- `context.md` requirements (phases 2 and 6)

Outputs:
- Ingestion spec sections appended to `context.md`

### Subagent B — Mapper Subagent
Responsibilities:
- Provide stock identifier strategy (ticker universe vs lookup fallback).
- Define mapping confidence thresholds + ambiguity handling.
- Define taxonomy for “market-wide”.

Inputs:
- Requirements from `context.md` (phases 0 and 2)

Outputs:
- Mapping spec sections appended to `context.md`

### Subagent C — API/Backend Subagent
Responsibilities:
- Specify API endpoints for holdings CRUD and news retrieval.
- Define response schemas matching UI required fields (title/date/teaser/link + tags).
- Define persistence strategy (tables/indices) at a level consistent with future implementation.

Inputs:
- Requirements from `context.md` (phases 1, 3, 6)

Outputs:
- Backend/API spec sections appended to `context.md`

### Subagent D — UI/Frontend Subagent
Responsibilities:
- Specify three routes: Personal, Per-Stock, Market/Generic.
- Define list UI components and loading/empty/error states.
- Define filter/search UX (age filter + ticker badges + matched tags).

Inputs:
- Requirements from `context.md` (phases 4 and 7)

Outputs:
- Frontend/UI spec sections appended to `context.md`

### Subagent E — QA/Testing Subagent
Responsibilities:
- Define test matrix for parsing→DB→API and UI smoke tests.
- Provide acceptance criteria checks per phase.

Inputs:
- Requirements from `context.md` (phases 5 and 7)

Outputs:
- QA/testing checklist appended to `context.md`

---

## 14. Agent communication protocol (contracts)

### Conventions
- All subagents respond with markdown sections that can be appended to `context.md`.
- Each subagent must reference:
  - the relevant phase(s)
  - how its change satisfies at least one acceptance criterion
- No subagent may remove existing decisions unless it marks them as superseded.

### Message schema (logical)
For each delegated task, the orchestrator supplies:
- `task_id`: string (unique)
- `phase`: one of Phase 0–7
- `goal`: brief statement of required spec
- `constraints`: bullets derived from `context.md`

Subagent response must include:
- `deliverable`: spec text
- `acceptance_criteria_covered`: list of references to criteria IDs
- `open_questions`: list (may be empty)

### Handoff rules
- Orchestrator merges subagent output into `context.md`.
- If subagent outputs conflict, orchestrator:
  1) flags the conflict,
  2) selects the most recent non-breaking monotonic addition,
  3) records the reason in the Decision Log section.

---

## 15. Workflow runtime (plan → execute → validate)

### Loop structure
1) **Plan**
- Identify which phases need new spec content.
- Assign tasks to subagents.

2) **Execute**
- Subagents generate targeted spec additions.

3) **Validate**
- Validate against:
  - required UI data model fields (Title/Date/Teaser/Link)
  - monotonic contract (no deletion)
  - acceptance criteria coverage

4) **Integrate**
- Orchestrator appends sections and updates checkboxes.

5) **Retry/repair**
- If validate fails, orchestrator requests subagent refinement.
- Retry limit: 2 cycles per task_id; beyond that, orchestrator records a decision with mitigation.

### Validation checklist
- Spec additions must not be ambiguous about endpoint responsibilities.
- Dedupe rules must be explicit.
- “Market-wide” mapping must have a concrete taxonomy rule at least for v1.

---

## 16. Acceptance criteria & done-conditions (phase-oriented)

> Criteria IDs are referenced by subagents in `acceptance_criteria_covered`.

### Phase 0 — Requirements alignment
- **AC-P0-1**: Stock identifier strategy is chosen (ticker vs ISIN/CUSIP etc.).
- **AC-P0-2**: RSS→stock mapping approach is stated (keywords, tagging, or metadata).
- **AC-P0-3**: Definition of “market-wide” is explicitly stated.

Done-condition:
- `context.md` contains resolved decisions (checkboxes marked [x]) for AC-P0-1..3.

### Phase 1 — Data modeling
- **AC-P1-1**: DB tables and required fields for news items are listed.
- **AC-P1-2**: Dedupe key strategy is specified (URL + secondary fuzzy title or guid).
- **AC-P1-3**: Indexing/query patterns for UI routes are described.

Done-condition:
- `context.md` contains a coherent schema outline consistent with later APIs.

### Phase 2 — RSS ingestion
- **AC-P2-1**: Polling interval + failure retry/backoff rules are specified.
- **AC-P2-2**: Parsing outputs include Title/Date/Teaser/Link.
- **AC-P2-3**: Mapping to stock(s) and market-wide category is defined with ambiguity handling.

Done-condition:
- Dedupe + mapping rules are unambiguous.

### Phase 3 — Backend APIs
- **AC-P3-1**: Holdings CRUD endpoints are defined.
- **AC-P3-2**: News endpoints exist for personal, per-stock, and market-wide.
- **AC-P3-3**: Response shapes include required UI fields.

Done-condition:
- Endpoint list and response schemas are consistent across views.

### Phase 4 — Frontend UI
- **AC-P4-1**: Three routes exist and are described.
- **AC-P4-2**: Stock selector supports search UX for add.
- **AC-P4-3**: News list shows title/date/teaser/link and v1+ UX improvements.

Done-condition:
- UI behavior for loading/empty/error states is specified.

### Phase 5 — “Real-time” validation
- **AC-P5-1**: Refresh strategy is specified (polling vs push).
- **AC-P5-2**: Duplicate suppression strategy after refresh is specified.

Done-condition:
- Validation steps can be executed as described.

### Phase 6 — Quality & operational readiness
- **AC-P6-1**: Security plan (auth later, rate limiting) is specified.
- **AC-P6-2**: Error handling for broken RSS and malformed entries is described.
- **AC-P6-3**: Performance considerations are specified.

Done-condition:
- “Operational readiness” bullets exist for the above.

### Phase 7 — Testing plan
- **AC-P7-1**: Unit + integration test plan is specified.
- **AC-P7-2**: API test plan using curl is specified.
- **AC-P7-3**: Frontend smoke test plan is specified.

Done-condition:
- Test matrix covers ingestion→DB→API and UI navigation.

---

## 17. Risk/mitigation & decision log template

### Risks
- **R-1: Mapping ambiguity** (a single story matches multiple tickers or none)
- **R-2: Feed reliability** (broken/slow/malformed RSS feeds)
- **R-3: Dedupe drift** (URL changes or fuzzy-match false positives)
- **R-4: Query performance** (personal view requires aggregations by user holdings)

### Mitigations
- R-1: confidence thresholds + “manual review/tuning later” and explicit tagging priority.
- R-2: retries with exponential backoff + graceful degradation in UI.
- R-3: URL-first dedupe + secondary fuzzy title similarity with conservative thresholds.
- R-4: DB indexing for user/stock/category query patterns + optional caching.

### Decision Log (append-only)
- **YYYY-MM-DD** — Decision: <short>
  - Context: <why>
  - Affected phases: <Phase X..Y>
  - Subagents involved: <names>
  - Acceptance criteria satisfied: <AC-..>
  - Reversibility: <yes/no>
  - Notes: <links/rationale>

