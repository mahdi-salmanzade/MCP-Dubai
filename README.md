<div align="center">

<img src="./ae.svg" alt="UAE" width="120" height="120">

# MCP-Dubai

**خادم MCP للبيانات العامة في دبي والإمارات وللمعرفة العملية لتأسيس الأعمال**
*An MCP server for Dubai and UAE public data plus curated business setup knowledge*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.x](https://img.shields.io/badge/FastMCP-3.x-brightgreen.svg)](https://gofastmcp.com)
[![Made in Dubai](https://img.shields.io/badge/Made%20in-Dubai-red.svg)](#)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#-roadmap)
[![Knowledge Updated](https://img.shields.io/badge/knowledge_updated-April_2026-blue)](#-knowledge-freshness)
[![Tests](https://img.shields.io/badge/tests-369_passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](#)

**Connect AI agents (Claude, GPT, Cursor, Copilot) to Dubai and UAE public APIs and curated business setup knowledge.**

🔧 **90 tools** · 🏛️ **28 features** · 📚 **17 verified knowledge domains** · ✅ **9 anonymous APIs** · 💼 **15 business advisor tools** · 🤖 **2 agent skills**

[Quick Start](#-quick-start) · [Tool Catalogue](#-tool-catalogue) · [Knowledge Freshness](#-knowledge-freshness) · [Architecture](#%EF%B8%8F-architecture) · [Roadmap](#-roadmap) · [Contributing](#-contributing)

</div>

---

> Dubai gave me a life. I promised myself I'd give something back.
>
> by **Mahdi Salmanzade**, Software Developer, Dubai
> 📧 [info@mindzone.tech](mailto:info@mindzone.tech) · 📅 April 2026

---

> ⚠️ **Knowledge Date: April 2026**
>
> Business rules in the UAE (corporate tax, visas, free zone pricing, accelerator cycles, API migrations) change frequently. Always verify with the official source before making real decisions. Every `biz/*` tool returns a `knowledge_date` field with its own per-domain freshness stamp, and you can call `get_knowledge_status()` at any time to see which domains were verified when.

---

## 📋 Table of Contents

1. [What is this?](#-what-is-this)
2. [Why MCP-Dubai exists](#-why-mcp-dubai-exists)
3. [Quick Start](#-quick-start)
4. [Tool Catalogue](#-tool-catalogue)
5. [Data Sources](#-data-sources)
6. [Configuration](#%EF%B8%8F-configuration)
7. [Knowledge Freshness](#-knowledge-freshness)
8. [Architecture](#%EF%B8%8F-architecture)
9. [Example Queries](#-example-queries)
10. [Roadmap](#-roadmap)
11. [Contributing](#-contributing)
12. [Disclaimer](#%EF%B8%8F-disclaimer)
13. [Acknowledgments](#-acknowledgments)
14. [License](#-license)

---

## 🌟 What is this?

MCP-Dubai is a [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents a single, well-typed interface to two distinct kinds of knowledge about Dubai and the UAE:

1. **Public Dubai and UAE government data**, like prayer times, exchange rates, school ratings, real estate transactions, transport networks, and more.
2. **Curated business setup knowledge** that no other MCP server has, like which free zone to choose for a SaaS startup, which visa to apply for as a freelance developer, how to estimate corporate tax under the QFZP rules, the full Hague-not-an-option attestation chain, the 11 most common founder mistakes, and a 14-bank matrix with DUL fast-track eligibility.

Drop it into Claude Desktop, Cursor, VS Code, or any MCP-compatible client and your AI assistant can answer questions like *"what time is Fajr tomorrow in Dubai Marina?"* or *"where should I set up my SaaS company in Dubai with a 25K AED budget?"* with grounded, source-cited answers instead of SEO spam.

---

## 💡 Why MCP-Dubai exists

Dubai's public data lives across at least a dozen platforms (`api.dubaipulse.gov.ae`, `opendata.fcsc.gov.ae`, `bayanat.ae`, `centralbank.ae`, `aladhan.com`, `web.khda.gov.ae`, `aviationweather.gov`, and more) each with its own auth, format, and rate limits. Most agencies do not expose self-serve APIs. The few that do are gated behind email-issued OAuth credentials or paywalled at AED 31,500/year per product.

On top of that, founders coming to Dubai face the same questions over and over: which license, which visa, which bank, how much, how long. The web answers are SEO-spam from agency setup firms.

**MCP-Dubai is the honest, code-first answer.**

- Built around 9 anonymous APIs that work today (Al-Adhan, Quran Cloud, FCSC CKAN, CBUAE Umbraco, KHDA XLSX, aviationweather.gov, OSM Overpass, WAQI air quality, curated UAE holidays).
- Layered with 6 curated business knowledge domains that compress 8,600+ lines of source-cited research into structured tools.
- Uses the same `KnowledgeMetadata` envelope on every business response so the LLM (and you) can always see when each domain was last verified.
- Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil). Aligned with Dubai Data Law (Law 26 of 2015). Run as a community contribution.

---

## 🚀 Quick Start

### Install via uvx (recommended)

```bash
uvx mcp-dubai
```

### Or install with pip

```bash
pip install mcp-dubai
python -m mcp_dubai
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "dubai": {
      "command": "uvx",
      "args": ["mcp-dubai"]
    }
  }
}
```

### Claude Desktop with Dubai Pulse credentials (unlocks Tier 1 tools)

Tier 1 (Dubai Pulse OAuth) features are not yet wired up but the auth scaffolding is ready. When they ship, set:

```json
{
  "mcpServers": {
    "dubai": {
      "command": "uvx",
      "args": ["mcp-dubai"],
      "env": {
        "MCP_DUBAI_PULSE_CLIENT_ID": "your-client-id",
        "MCP_DUBAI_PULSE_CLIENT_SECRET": "your-client-secret",
        "MCP_DUBAI_WAQI_TOKEN": "optional-waqi-token"
      }
    }
  }
}
```

Get Dubai Pulse credentials by requesting dataset access at [data.dubai](https://data.dubai). Get a WAQI token (free) at [aqicn.org/data-platform/token](https://aqicn.org/data-platform/token/).

### Cursor / VS Code

Create `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "dubai": {
      "command": "uvx",
      "args": ["mcp-dubai"]
    }
  }
}
```

### Claude Code CLI

```bash
claude mcp add dubai -- uvx mcp-dubai
```

---

## 🧰 Tool Catalogue

**51 tools across 15 features.** All Tier 0 features ship today and work without any credentials. Tier 2 business knowledge tools are also live. Tier 1 (Dubai Pulse OAuth) features are scaffolded and ship after credentials are obtained. Use `recommend_tools(query)` to find the right tool for any natural-language question.

### ✅ Tier 0: anonymous APIs (no auth, ship today)

| Feature | Tools | What it does |
|---|---|---|
| `al_adhan` | `prayer_times_for`, `prayer_times_calendar`, `qibla_direction`, `hijri_to_gregorian`, `gregorian_to_hijri` | Prayer times for any UAE city or coords, Qibla compass bearing, Hijri/Gregorian conversion. Method 8 (Gulf Region) is the default; method 16 (Dubai experimental) matches Dubai mosque announcements. |
| `quran_cloud` | `quran_surah`, `quran_ayah`, `quran_juz`, `quran_search` | Full Quran text and translations. Multiple editions (Arabic Uthmani, Sahih International English, Urdu, etc.). |
| `cbuae` | `cbuae_exchange_rates`, `cbuae_base_rate` | Central Bank of UAE exchange rates against AED for 76 currencies (today or historical), bilingual rows with ISO 4217 codes. Sourced from the undocumented Umbraco endpoints, no auth. |
| `fcsc_ckan` | `fcsc_search_dataset`, `fcsc_get_dataset`, `fcsc_list_organizations`, `fca_trade_stats` | Anonymous read against the UAE federal open data CKAN portal. Includes a convenience wrapper for Federal Customs Authority trade statistics (the easiest no-auth path for UAE trade data). |
| `khda` | `khda_search_school`, `khda_list_curricula`, `khda_list_areas` | Search Dubai private schools by name, area, curriculum, KHDA inspection rating, or fee ceiling. Backed by a curated snapshot of well-known schools; full XLSX refresh script in roadmap. |
| `aviation_weather` | `weather_uae_icao`, `weather_uae_all` | METAR (current observation) and TAF (forecast) for the 6 UAE international airports (OMDB Dubai International, OMDW Al Maktoum, OMSJ Sharjah, OMAA Abu Dhabi, OMAL Al Ain, OMRK RAK). The standard substitute for the missing NCM public API. |
| `air_quality` | `air_quality_dubai`, `air_quality_by_coords`, `air_quality_dubai_stations` | Real-time air quality (AQI, PM2.5, PM10, NO2, SO2, CO, O3) for Dubai stations via WAQI/AQICN. Requires a free token from `aqicn.org`. Uses the graceful degradation pattern: returns a structured help error if the token is missing. |
| `osm_overpass` | `osm_search_poi`, `osm_list_categories` | Find OpenStreetMap POIs near a Dubai location: restaurants, pharmacies, mosques, ATMs, metro stations, malls, parking, etc. 22 curated categories. |
| `holidays` | `uae_holidays`, `uae_next_holiday`, `is_uae_holiday` | UAE federal public holidays. Lunar holidays (Eid Al Fitr, Eid Al Adha, Hijri New Year, Mawlid, Arafat Day) are flagged as `provisional` until officially announced by MoHRE. |

### 💼 Tier 2: curated business knowledge (no external API, ship today)

| Feature | Tools | What it does |
|---|---|---|
| `setup_advisor` | `setup_advisor` | The headline tool. Recommends mainland vs free zone vs offshore for a Dubai business setup. Cross-references curated free zones, visas, banks, and tax rules. Gives jurisdiction, candidate free zones, reasoning, warnings, cost range, timeline, and next steps. Surfaces the SaaS-is-not-QFZP-Qualifying warning automatically. |
| `free_zones` | `list_free_zones`, `free_zone_details`, `compare_free_zones`, `list_offshore` | All 12 major Dubai free zones (DMCC, DIFC Innovation, JAFZA, DAFZA, IFZA, Meydan, Dubai South, DSO/Dtec, TECOM, DHCC, DPC/DSC, DIFC full FS) with cost, office options, visa quota, and bank acceptance reputation. Plus JAFZA Offshore and RAK ICC. Renewal cost myth is corrected here: it is NOT 20-30% higher than setup. |
| `visas` | `list_visa_types`, `visa_details`, `visa_recommend`, `golden_visa_check` | All 13 UAE visa types. Green Visa is correctly split into the AED 15K/month skilled employee track and the AED 360K/24-month freelancer track. Golden Visa specialized talent salary tightened to AED 30,000 basic monthly verified over 24 months (early 2026 update). |
| `banking` | `list_banks`, `bank_details`, `bank_recommendation`, `dul_eligibility` | 14-bank matrix (Wio, Mashreq NEOBiz, Zand, ruya, Emirates NBD, RAKBANK, ADCB, FAB, CBD, ADIB, HSBC, StanChart, Citi, Liv) on onboarding speed, minimum balance, and crypto stance. Plus DUL (Dubai Unified Licence) fast-track eligibility check listing the 7 participating banks and 3 participating free zones. |
| `founder_essentials` | `attestation_guide`, `pro_services_estimate`, `legal_translation_estimate`, `chamber_of_commerce_info`, `setup_timeline_estimate`, `common_founder_mistakes` | The boring stuff that breaks setups. Full 5-step UAE legalization chain (UAE is NOT a Hague Apostille member, despite what some sources claim), PRO service cost estimator, MOJ legal translation calculator, Dubai Chamber of Commerce membership and CoO fees, realistic 1-to-16-week banking timelines, and the 11 most common founder mistakes with impact and fix for each. |
| `tax_compliance` | `corporate_tax_estimate`, `vat_filing_calendar`, `qfzp_check`, `esr_status` | UAE Corporate Tax (Federal Decree-Law 47 of 2022, 9% above AED 375,000), VAT (5%), QFZP (Qualifying Free Zone Person under Ministerial Decision 229 of 2025, with the explicit SaaS-not-qualifying warning), and ESR status (DEAD for periods after Dec 2022 per Cabinet Resolution 98 of 2024). |

### 🧠 Tier 3: meta-tools

| Tool | What it does |
|---|---|
| `recommend_tools(query, top_k=5)` | BM25-powered tool discovery. Pass a natural-language query, get a ranked list of the most relevant tools so the LLM does not have to scan all 51 at once. |
| `list_features()` | List every registered feature with its tier, auth requirement, and tool count. |
| `get_knowledge_status()` | Read the freshness registry. Returns every registered business knowledge domain with its `knowledge_date`, `volatility`, `verify_at` URL, and disclaimer. |

### 🔐 Tier 1: Dubai Pulse OAuth (planned)

The auth scaffolding is in place (graceful credential degradation, token caching, env-overridable base URL for the data.dubai migration). The actual feature wrappers ship once the maintainer obtains Dubai Pulse credentials. Planned: `dld` (real estate), `rta` (transport + GTFS), `dha` (health facilities), `dewa`, `dtcm`, `det` (business activities), `dm_food`, `dm_permits`, `dubai_customs`, `dubai_airports` (FIDS).

---

## 📊 Data Sources

| Source | Auth | What we use | Tools |
|---|---|---|---|
| [Al-Adhan API](https://aladhan.com/prayer-times-api) | ✅ Open | Prayer times, Qibla, Hijri calendar | `al_adhan` |
| [Al-Quran Cloud](https://alquran.cloud/api) | ✅ Open | Quran text and translations | `quran_cloud` |
| [CBUAE Umbraco endpoints](https://www.centralbank.ae) | ✅ Open (undocumented) | FX rates, base rate | `cbuae` |
| [FCSC Open Data](https://opendata.fcsc.gov.ae) | ✅ Open (CKAN) | UAE federal datasets, FCA trade | `fcsc_ckan` |
| [KHDA Resources](https://web.khda.gov.ae/en/Resources/KHDA-data-statistics) | ✅ Open (XLSX) | Dubai schools | `khda` |
| [aviationweather.gov](https://aviationweather.gov/data/api/) | ✅ Open | METAR / TAF for UAE ICAOs | `aviation_weather` |
| [OSM Overpass](https://overpass-api.de) | ✅ Open | POI fallback | `osm_overpass` |
| [WAQI / AQICN](https://aqicn.org/api/) | 🔑 Free key | Air quality | `air_quality` |
| Curated UAE federal calendar | 📚 Static | Public holidays | `holidays` |
| Curated business knowledge files | 📚 Static | Free zones, visas, banks, founder essentials, tax | `setup_advisor`, `free_zones`, `visas`, `banking`, `founder_essentials`, `tax_compliance` |
| [Dubai Pulse Gateway](https://api.dubaipulse.gov.ae) | 🔐 OAuth (planned) | DLD, RTA, DHA, DEWA, DET, DTCM, DM, Dubai Airports | Tier 1 (Phase 4) |
| [DLD API Gateway](https://dubailand.gov.ae/en/eservices/api-gateway/) | 💰 Paid (~AED 31,500/yr per product) | Ejari, Mollak, Trakheesi, Rental Index | Not built (we use Dubai Pulse open data instead) |

**Things we will NOT build** (full list in [DISCLAIMER.md](DISCLAIMER.md)): Salik account/balance/trips (private app), NABIDH clinical data (vendor-only PHI), DMCC public-search scraping (ToS-banned), NCM weather wrapper (no public API), DM zoning/parcels (request-only paid), CBUAE Open Finance regulated TPP framework. We also explicitly do not promise A-to-F food grades from the open feed (the consumer app shows them but the open dataset schema is unconfirmed).

### Upstream Status

Some government endpoints have deployed bot protection (Cloudflare) since v0.1.0 released. These tools return a structured `success: false` with `error.status` of `upstream_blocked` instead of crashing. The rest of the package is unaffected.

| Tool | Endpoint | Status as of 2026-04-13 |
|---|---|---|
| `cbuae_exchange_rates` | `centralbank.ae` Exchange endpoint | ✅ Working (scraper updated in v0.1.2 for the new Arabic three-cell DOM) |
| `cbuae_base_rate` | `centralbank.ae` InterestRate endpoint | 🔶 Cloudflare-blocked |
| `fcsc_search_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked |
| `fcsc_get_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked |
| `fcsc_list_organizations` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked |
| `fca_trade_stats` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked (delegates to fcsc_search_dataset) |

`cbuae_exchange_rates` rows now include `currency` (English), `currency_ar` (Arabic as returned by CBUAE), `iso_code` (ISO 4217), and `rate_aed`. Unknown currencies pass through with `iso_code: null` and `currency: null` so new CBUAE entries are never silently dropped.

Clients should check `result["success"]` and read `result["error"]["status"]` / `result["error"]["reason"]` for a user-facing message. We track these endpoints and will restore data access when the upstream blocks are lifted or alternative sources are wired up.

---

## ⚙️ Configuration

| Env Var | Required | Default | Unlocks |
|---|---|---|---|
| `MCP_DUBAI_PULSE_CLIENT_ID` | Tier 1 only | `None` | Tier 1 Dubai Pulse OAuth tools (when shipped) |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Tier 1 only | `None` | Tier 1 Dubai Pulse OAuth tools (when shipped) |
| `MCP_DUBAI_PULSE_API_BASE` | No | `https://api.dubaipulse.gov.ae` | Override base URL for the data.dubai migration |
| `MCP_DUBAI_DATA_PORTAL_BASE` | No | `https://data.dubai` | Override portal URL |
| `MCP_DUBAI_WAQI_TOKEN` | Air quality only | `None` | `air_quality_dubai`, `air_quality_by_coords` |
| `MCP_DUBAI_CALENDARIFIC_KEY` | No | `None` | Future Calendarific holiday refresh |
| `MCP_DUBAI_LOG_LEVEL` | No | `INFO` | Log verbosity |
| `MCP_DUBAI_HTTP_TIMEOUT` | No | `30.0` | HTTP timeout in seconds |
| `MCP_DUBAI_HTTP_MAX_RETRIES` | No | `3` | Tenacity retry budget |

Every variable is optional. The server starts and runs all 9 Tier 0 features and all 6 Tier 2 business features without any of them.

---

## 📅 Knowledge Freshness

The hardest thing about a Dubai business-knowledge MCP is that **the rules move**. Tax thresholds, visa criteria, free zone pricing, and even API base URLs all change inside a single quarter. This project handles that with seven mechanisms:

1. **Top-of-file timestamp** on every curated JSON file (`knowledge_date: 2026-04-13`).
2. **Per-domain `KNOWLEDGE` constant** in every `biz/*` module, registered with the shared `KnowledgeRegistry` at import time.
3. **`knowledge` block on every business tool response** with `knowledge_date`, `volatility`, `verify_at` URL, and `disclaimer`.
4. **`get_knowledge_status()` meta-tool** that reads from the registry, so a single update flows through automatically.
5. **README badge** + ⚠️ callout under the maintainer's note.
6. **Volatility tags by domain**: 🟢 stable (yearly re-verify), 🟡 medium (quarterly), 🔴 high (quarterly or monthly).
7. **Verification queue** of open items tracked by maintainers.

**Volatility map** (current):

| Domain | Volatility | Re-verify cadence |
|---|---|---|
| `setup_advisor`, `free_zones`, `visas`, `tax_compliance` | 🔴 high | quarterly |
| `banking`, `founder_essentials` | 🟡 medium | quarterly |
| Tier 0 anonymous APIs | 🟢 stable | yearly |
| Dubai Pulse dataset slugs (when wired) | 🟡 medium | quarterly (data.dubai migration in progress) |
| Accelerator cohort dates, event calendar (when shipped) | 🔴 high | monthly |

**Recent rule changes captured** (as of 2026-04-13):

- QFZP Qualifying Activities updated by Ministerial Decision 229/2025 (SaaS still excluded).
- CT late-registration penalty waived if first return filed within 7 months (FTA, April 2025).
- Golden Visa specialized talent salary tightened to AED 30,000 basic monthly verified over 24 months (early 2026).
- ESR repealed for periods after 31 December 2022 (Cabinet Resolution 98/2024).
- VARA V2.0 Rulebook compliance deadline 19 June 2025.
- Dubai parking spun out of RTA into Parkin Company PJSC, December 2023, with variable tariffs live since 4 April 2025. Note: "Mawaqif" is Abu Dhabi, not Dubai.
- Ministry of Economy rebranded to Ministry of Economy and Tourism (MOET) in 2025.
- Federal health insurance mandate kicked in January 2025 (UAE-wide).

---

## 🏗️ Architecture

```
src/mcp_dubai/
├── __init__.py
├── __main__.py                 # python -m mcp_dubai entry point
├── server.py                   # FastMCP root + meta-tools + explicit feature mounts
├── _shared/
│   ├── auth.py                 # Dubai Pulse OAuth + availability() pattern
│   ├── constants.py            # All base URLs env-overridable
│   ├── discovery.py            # BM25 ToolDiscovery + ToolMeta + tier constants
│   ├── http_client.py          # async httpx + tenacity retry + typed errors
│   ├── knowledge.py            # KnowledgeRegistry singleton
│   └── schemas.py              # ToolResponse envelope, KnowledgeMetadata, etc.
├── data/                       # Tier 0 + Tier 1 API integrations
│   ├── al_adhan/
│   ├── aviation_weather/
│   ├── air_quality/
│   ├── cbuae/
│   ├── fcsc_ckan/
│   ├── holidays/
│   ├── khda/
│   ├── osm_overpass/
│   └── quran_cloud/
└── biz/                        # Tier 2 curated business knowledge
    ├── _data/                  # Curated JSON files (loaded via importlib.resources)
    │   ├── free_zones.json
    │   ├── visas.json
    │   ├── banks.json
    │   ├── founder_essentials.json
    │   ├── tax_compliance.json
    │   └── loader.py
    ├── banking/
    ├── founder_essentials/
    ├── free_zones/
    ├── setup_advisor/
    ├── tax_compliance/
    └── visas/
```

**Conventions every feature follows:**

- `__init__.py` exports a `FEATURE_META` dict with name, description, tier, requires_auth, source URL.
- `tools.py` holds pure async functions with no FastMCP imports, so unit tests hit the real logic without going through the MCP wrapping layer.
- `server.py` defines a `FastMCP("feature_name")` instance, decorates wrappers, and registers `ToolMeta` records with the shared discovery on import.
- `biz/*` features additionally expose a per-domain `KNOWLEDGE = KnowledgeMetadata(...)` constant and call `register_domain_knowledge(domain, KNOWLEDGE)` so `get_knowledge_status()` reflects current freshness automatically.
- `data/*` features that need OAuth or a free API key use the **graceful credential degradation pattern**: tools never crash when env vars are missing. They call `availability()` and return a structured `ToolResponse.fail({status, reason, docs})` so the MCP client renders a help message instead of a stack trace. This is what lets `python -m mcp_dubai` start cleanly on a fresh machine with no env file.
- Curated JSON files use the **Pattern 3 envelope**: top-level `domain`, `knowledge_date`, `volatility`, `verify_at`, `source_brief_section`, `disclaimer`. The shared loader's `extract_knowledge()` builds the `KnowledgeMetadata` directly from these fields, so a single update in a JSON file flows through to every tool that uses it.

---

## 💬 Example Queries

Ask your AI assistant any of these. The agent will route to the right tool via `recommend_tools` and return a grounded answer:

**Daily life:**
- *"What time is Fajr prayer tomorrow in Dubai Marina?"*
- *"Convert 10 Ramadan 1447 to Gregorian."*
- *"What's the current AED to USD exchange rate?"*
- *"Find restaurants within 500m of these coordinates."*
- *"Is 2 December 2026 a UAE public holiday?"*
- *"What's today's air quality in Karama?"*

**Schools:**
- *"Find Outstanding rated schools in Jumeirah with British curriculum."*
- *"Which Indian / CBSE schools are under AED 20,000/year?"*

**Founder questions** (the headline value):
- *"Where should I set up my SaaS company in Dubai with a 25K AED budget?"*
- *"Compare DMCC and IFZA for a 2-visa consultancy."*
- *"What visa should I get if I'm a freelance developer earning AED 400,000/year?"*
- *"Estimate my corporate tax if my free zone SaaS makes AED 1.5M revenue."*
- *"Do I qualify for the Golden Visa with a 32K monthly basic salary?"*
- *"Open a UAE business bank account fast for a solo founder."*
- *"Am I eligible for the Dubai Unified Licence fast-track with Emirates NBD and DMCC?"*
- *"How do I attest my degree certificate from India for use in Dubai?"*
- *"How much do PRO services cost per year for 3 visas?"*
- *"What are the most common mistakes founders make in Dubai?"*

---

## 🗺️ Roadmap

| Phase | Status | Scope |
|---|---|---|
| **Phase 1: Scaffold + Shared** | ✅ Complete | `_shared/` (auth, http, schemas, discovery, knowledge), root server, conftest. |
| **Phase 2: Tier 0 features** | ✅ Complete | 9 anonymous APIs: al_adhan, quran_cloud, cbuae, fcsc_ckan, khda, aviation_weather, air_quality, osm_overpass, holidays. |
| **Phase 3: Tier 2 priority biz** | ✅ Complete | setup_advisor, free_zones, visas, banking, founder_essentials, tax_compliance. |
| **Phase 3b: Tier 2 deferred biz** | ✅ Complete | compliance, funding, gov_portals, dcde, events, parkin, ip_trademark, halal, createapps. |
| **Phase 4: Tier 1 Dubai Pulse scaffolding** | ✅ Complete | dubai_pulse base client + dld + rta example features with credential-missing pattern. Ready to wire more features when credentials arrive. |
| **Phase 5: Polish** | ✅ Complete | README, CONTRIBUTING, CI, PyPI publish workflow, issue templates. |
| **Phase 6: Agent skills** | ✅ Complete | arabic_writer (bilingual letter templates) + data_analyst (cross-tool plans + Markdown report synthesis with knowledge-freshness footer). |
| **Phase 7: More Tier 1 features** | 🔐 Blocked on credentials | dha, dewa, det, dtcm, dm_food, dm_permits, dubai_customs, dubai_airports. The dubai_pulse base client and dld + rta examples are ready as the template. |
| **Phase 8: Quarterly knowledge refresh** | ♻️ Ongoing | Re-verify the 17 curated knowledge domains every quarter, bump knowledge_date in the JSON files. Tax rules and visa thresholds move fastest. |

---

## 🤝 Contributing

We welcome contributions. Priority areas right now:

1. **Ship the deferred Tier 2 features** (`funding`, `events`, `parkin`, `ip_trademark`, `halal`, etc.). They follow the same pattern as the existing 6, just need curated JSON + thin tools/server modules + tests.
2. **Wire up Tier 1 Dubai Pulse features** once credentials are obtained. Auth and base client are already in `_shared/auth.py` and the `DubaiPulseAuth` graceful-degradation contract is the canonical pattern.
3. **Refresh business knowledge quarterly.** Each curated JSON file has a `knowledge_date` and `verify_at` URL. Tax rules, visa thresholds, and free zone pricing change frequently.
4. **Improve `recommend_tools` BM25 quality** by tuning tags. Current quirk: in small sub-corpora, BM25 length normalization can favour shorter tools when queries collide on common tokens.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the dev setup, test/lint commands, and PR checklist.

```bash
git clone https://github.com/mahdi-salmanzade/MCP-Dubai.git
cd MCP-Dubai
make dev      # editable install with dev + data extras
make check    # ruff + mypy + pytest
```

---

## ⚠️ Disclaimer

This project is not affiliated with, endorsed by, or sponsored by the Government of Dubai, the United Arab Emirates, or any specific authority (DLD, RTA, KHDA, DSC, DHA, DET, DEWA, CBUAE, Dubai Pulse, MOET, MOIAT, or any other). All data is the property of its respective publisher. We provide a unified interface, nothing more.

Upstream APIs change without warning. If a tool returns wrong, empty, or error results, please [open a GitHub issue](https://github.com/mahdi-salmanzade/MCP-Dubai/issues) instead of assuming malice. We rely on the community to keep integrations fresh.

Read the full [DISCLAIMER.md](DISCLAIMER.md) for nature of project, trademarks, compliance responsibilities, removal requests, and personal data handling.

---

## 🌟 Acknowledgments

- Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil), which proved the pattern for a country-specific public-data MCP server.
- Built on [FastMCP 3.x](https://gofastmcp.com), the standalone Pythonic MCP framework maintained by Prefect.
- Thanks to the UAE government agencies that publish open data, especially the Federal Competitiveness and Statistics Centre (FCSC) for the truly anonymous CKAN portal.
- Built for the Dubai developer community.

---

## 📬 Contact

- **Maintainer**: Mahdi Salmanzade, Software Developer, Dubai
- **Email**: [info@mindzone.tech](mailto:info@mindzone.tech)
- **Issues**: <https://github.com/mahdi-salmanzade/MCP-Dubai/issues>
- **Pull requests welcome**: see [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 License

[MIT](LICENSE). Use it, fork it, ship it. Just keep the attribution and the disclaimer.

---

<div align="center">

<img src="./ae.svg" alt="UAE" width="48" height="48">

**Made with ❤️ in Dubai by Mahdi Salmanzade**

📧 [info@mindzone.tech](mailto:info@mindzone.tech) · 📅 April 2026

> هذا المشروع مبادرة مجتمعية مفتوحة المصدر، مرحبًا بمساهماتكم

</div>
