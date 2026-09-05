<!-- mcp-name: io.github.mahdi-salmanzade/mcp-dubai -->

<div align="center">

<img src="https://raw.githubusercontent.com/mahdi-salmanzade/MCP-Dubai/main/ae.svg" alt="UAE" width="120" height="120">

# MCP-Dubai

**خادم MCP للبيانات العامة في دبي والإمارات وللمعرفة العملية لتأسيس الأعمال**
*An MCP server for Dubai and UAE public data plus curated business setup knowledge*

[![PyPI](https://img.shields.io/pypi/v/mcp-dubai?color=blue)](https://pypi.org/project/mcp-dubai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.x](https://img.shields.io/badge/FastMCP-3.x-brightgreen.svg)](https://gofastmcp.com)
[![Made in Dubai](https://img.shields.io/badge/Made%20in-Dubai-red.svg)](#)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#%EF%B8%8F-roadmap)
[![Knowledge Updated](https://img.shields.io/badge/knowledge_updated-September_2026-blue)](#-knowledge-freshness)
[![Tests](https://img.shields.io/badge/tests-967_passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-93.61%25-brightgreen.svg)](#)

**Connect AI agents (Claude, GPT, Cursor, Copilot) to Dubai and UAE public APIs and curated business setup knowledge.**

🔧 **120 tools** · 🏛️ **37 features** · 📚 **19 freshness-tracked knowledge domains** · ✅ **112 credential-free tools** · 💼 **56 business advisor tools** · 🤖 **2 agent skills**

[Quick Start](#-quick-start) · [Tool Catalogue](#-tool-catalogue) · [Knowledge Freshness](#-knowledge-freshness) · [Audit 2026-09-05](AUDIT-2026-09-05.md) · [Architecture](#%EF%B8%8F-architecture) · [Roadmap](#%EF%B8%8F-roadmap) · [Contributing](#-contributing)

</div>

---

> Dubai gave me a life. I promised myself I'd give something back.
>
> by **Mahdi Salmanzade**, Software Developer, Dubai
> 📧 [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com) · 📅 April 2026

---

> ⚠️ **Knowledge Date: not uniform. Check per domain.**
>
> Freshness is **per domain, not project-wide**. As of 5 September 2026:
>
> | Latest recorded update | Domains |
> |---|---|
> | **2026-09-05** | `banking`, `compliance`, `cost_of_living`, `createapps`, `data_analyst`, `dcde`, `events`, `founder_essentials`, `free_zones`, `funding`, `gov_portals`, `halal`, `ip_trademark`, `parkin`, `setup_advisor`, `tax_compliance`, `tenancy`, `visas` |
> | **2026-04-13** | `arabic_writer` |
>
> The September audit includes targeted corrections and updates. It does not mean every field was re-verified. Every knowledge response distinguishes the latest `knowledge_date` from `full_review_date` and exposes `last_refresh_scope` and `previous_knowledge_date` where relevant. The checker covers all 19 domains and applies each alerting budget to the last full review, so a targeted update cannot hide stale untouched content.
>
> Business rules in the UAE (corporate tax, visas, free zone pricing, accelerator cycles, API migrations) change frequently. Always verify with the official source before making real decisions. Every `biz/*` tool returns its latest recorded update and full-review date, and `get_knowledge_status()` reports the prior date and targeted scope where declared.

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
10. [Roadmap](#%EF%B8%8F-roadmap)
11. [Contributing](#-contributing)
12. [Disclaimer](#%EF%B8%8F-disclaimer)
13. [Acknowledgments](#-acknowledgments)
14. [License](#-license)

---

## 🌟 What is this?

MCP-Dubai is a [Model Context Protocol](https://modelcontextprotocol.io) server that gives AI agents a single, well-typed interface to two distinct kinds of knowledge about Dubai and the UAE:

1. **Public Dubai and UAE government data**, like prayer times, exchange rates, school ratings, real estate transactions, transport networks, and more.
2. **Curated business setup knowledge** that no other MCP server has, like which free zone to choose for a SaaS startup, which visa to apply for as a freelance developer, how to estimate corporate tax under the QFZP rules, document-specific UAE attestation routes, 10 common founder mistakes, and a 14-bank matrix with a dated DUL bank-integration snapshot.

Drop it into Claude Desktop, Cursor, VS Code, or any MCP-compatible client and your AI assistant can answer questions like *"what time is Fajr tomorrow in Dubai Marina?"* or *"where should I set up my SaaS company in Dubai with a 25K AED budget?"* with structured, freshness-stamped answers and source or verification links where available.

---

## 💡 Why MCP-Dubai exists

Dubai's public data lives across at least a dozen platforms (`data.dubai` and its `apis.data.dubai` gateway, `opendata.fcsc.gov.ae`, `bayanat.ae`, `centralbank.ae`, `aladhan.com`, `web.khda.gov.ae`, `aviationweather.gov`, and more) each with its own auth, format, and rate limits. Most agencies do not expose self-serve APIs. The few that do are gated behind email-issued OAuth credentials or paywalled at AED 31,500/year per product.

On top of that, founders coming to Dubai face the same questions over and over: which license, which visa, which bank, how much, how long. The web answers are SEO-spam from agency setup firms.

**MCP-Dubai is the honest, code-first answer.**

- Ships 43 Tier 0 tools that require no credentials, backed by anonymous upstreams, bundled snapshots, and local reference data. Authentication status is separate from upstream health: the four FCSC CKAN tools and the CBUAE base-rate endpoint are recorded as blocked, while two WAQI reading tools require a free token.
- Layered with 16 curated JSON knowledge packs plus a setup advisor that composes them. Each pack carries freshness metadata and a top-level verification URL; individual records include additional source URLs where available.
- Uses the same `KnowledgeMetadata` envelope on every business response so the LLM (and you) can see the latest recorded update, prior date, and targeted scope where declared.
- Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil). Aligned with Dubai Data Law (Law 26 of 2015). Run as a community contribution.

---

## 🚀 Quick Start

Works in any MCP client. No API credentials are needed to invoke 112 of 120 tools in the current source tree. This is an authentication count, not a live-availability guarantee; five of those tools currently report blocked upstreams.

> **Release status (5 September 2026):** this repository is version 0.4.0 with 120 tools, but PyPI still serves version 0.2.0 with 91 tools. The `uvx mcp-dubai` and `pip install mcp-dubai` examples below therefore install the older public release until the maintainers publish 0.4.0. To run the current code, clone this repository and use `make dev && make run`.

The source currently supports FastMCP 3.4.7 through 3.x. FastMCP 4.0.2 is available as of 5 September 2026, but the dependency stays below 4 until its breaking API changes have been migrated and tested.

The recommended published-package runner is `uvx` (ships with [uv](https://docs.astral.sh/uv/)); plain `pip install mcp-dubai` also works.

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=dubai&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtY3AtZHViYWkiXX0%3D) [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_MCP--Dubai-0098FF?style=flat-square&logo=githubcopilot&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=dubai&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-dubai%22%5D%7D) [![Install in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Install_MCP--Dubai-24bfa5?style=flat-square&logo=githubcopilot&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=dubai&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-dubai%22%5D%7D&quality=insiders)

### Claude Code

```bash
claude mcp add dubai -- uvx mcp-dubai
```

Or commit a project-scoped `.mcp.json` at your repo root so your whole team gets it:

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

Tier 1 (Dubai Pulse OAuth) `dld` and `rta` tools ship today and return structured setup instructions until you set these credentials:

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

### Cursor

Click the install badge above, or add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project):

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

### VS Code (GitHub Copilot)

Click the install badge above, or run:

```bash
code --add-mcp '{"name":"dubai","command":"uvx","args":["mcp-dubai"]}'
```

Or create `.vscode/mcp.json` in your project root:

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

### Windsurf

Add the same `mcpServers` block as Cursor to `~/.codeium/windsurf/mcp_config.json`.

### Codex CLI

```bash
codex mcp add dubai -- uvx mcp-dubai
```

### Gemini CLI

```bash
gemini mcp add dubai uvx mcp-dubai
```

### Any other MCP client

The repository includes a validated MCP Registry manifest for `io.github.mahdi-salmanzade/mcp-dubai`, but no public registry record was found in the 5 September 2026 check. Until the maintainers complete that publication, use a manual stdio configuration:

```json
{
  "command": "uvx",
  "args": ["mcp-dubai"]
}
```

---

## 🧰 Tool Catalogue

**120 tools across 37 features.** Of 45 Tier 0 tools, 43 require no credentials; two WAQI reading tools require a free token. Credential requirements do not guarantee upstream availability: the CBUAE base-rate tool and four FCSC tools are currently recorded as blocked. Tier 2 business knowledge and agent-skill tools also ship, while the six Tier 1 live-query tools require data.dubai OAuth. Use `recommend_tools(query)` to find the right tool for any natural-language question.

### ✅ Tier 0: public-data tools

| Feature | Tools | What it does |
|---|---|---|
| `al_adhan` | `prayer_times_for`, `prayer_times_calendar`, `qibla_direction`, `hijri_to_gregorian`, `gregorian_to_hijri` | Prayer times for any UAE city or coords, Qibla compass bearing, Hijri/Gregorian conversion. Method 8 (Gulf Region) is the default; method 16 (Dubai experimental) matches Dubai mosque announcements. |
| `quran_cloud` | `quran_surah`, `quran_ayah`, `quran_juz`, `quran_search` | Full Quran text and translations. Multiple editions (Arabic Uthmani, Sahih International English, Urdu, etc.). Search is bounded and paginated: 25 results by default, 100 maximum per call, with `offset` and `next_offset` metadata. |
| `cbuae` | `cbuae_exchange_rates`, `cbuae_base_rate` | Central Bank of UAE exchange rates against AED for 77 currencies in the September 5 check (today or historical), English and Arabic labels with currency codes. The undocumented exchange-rate endpoint is anonymous; the base-rate endpoint is recorded as Cloudflare-blocked as of 5 September 2026. |
| `fcsc_ckan` | `fcsc_search_dataset`, `fcsc_get_dataset`, `fcsc_list_organizations`, `fca_trade_stats` | Credential-free wrappers for the UAE federal open-data CKAN interface, including Federal Customs Authority trade search. All four endpoints are recorded as Cloudflare-blocked as of 5 September 2026 and return structured errors. |
| `khda` | `khda_search_school`, `khda_list_curricula`, `khda_list_areas` | Search Dubai private schools by name, area, curriculum, KHDA inspection rating, or fee ceiling. Backed by a 16-school April snapshot with nine selected record corrections on 5 September; fees remain indicative and were not refreshed. A full XLSX refresh is still planned. |
| `aviation_weather` | `weather_uae_icao`, `weather_uae_all` | METAR (current observation) and TAF (forecast) for the 6 UAE international airports (OMDB Dubai International, OMDW Al Maktoum, OMSJ Sharjah, OMAA Zayed International, OMAL Al Ain, OMRK RAK). The standard substitute for the missing NCM public API. |
| `open_meteo` | `uae_weather`, `uae_weather_forecast`, `weather_by_coords`, `list_uae_weather_cities` | Keyless human-friendly weather: current temperature, feels-like, humidity, wind, and a multi-day forecast (highs, lows, rain chance, UV) for 8 UAE cities or any coordinate, via Open-Meteo. The everyday companion to the pilot-oriented `aviation_weather` METAR/TAF tools. |
| `currency` | `currency_rates`, `currency_convert` | Keyless everyday currency conversion on an AED base via the ExchangeRate-API open endpoint. The convenient companion to the official `cbuae` central-bank rates. |
| `air_quality` | `air_quality_dubai`, `air_quality_by_coords`, `air_quality_dubai_stations` | Real-time air quality (AQI, PM2.5, PM10, NO2, SO2, CO, O3) for Dubai stations via WAQI/AQICN. Requires a free token from `aqicn.org`. Uses the graceful degradation pattern: returns a structured help error if the token is missing. |
| `osm_overpass` | `osm_search_poi`, `osm_list_categories` | Find OpenStreetMap POIs near a Dubai location: restaurants, pharmacies, mosques, ATMs, metro stations, malls, parking, etc. 22 curated categories. |
| `holidays` | `uae_holidays`, `uae_next_holiday`, `is_uae_holiday` | UAE federal public holidays for 2026 (observed dates confirmed through the Prophet's Birthday, including the 15 June and 28 August transfers) and a provisional 2027 calendar. FAHR Circular 11 of 2026 confirms the Prophet's Birthday day off on Friday 28 August; 25 August was the religious date. Lunar holidays stay flagged `provisional` until officially announced by MoHRE/FAHR. Commemoration Day is correctly NOT a day off. |
| `dfm` | `dfm_index`, `dfm_stock_quote`, `dfm_list_securities` | Dubai Financial Market live market data: the DFM General Index snapshot and quotes for 458 records in the 5 September 2026 live check via the anonymous JSON endpoints behind dfm.ae. Undocumented and best-effort; data may be delayed; not investment advice. |
| `makani` | `makani_reverse_geocode`, `makani_details`, `makani_validate` | Dubai Municipality's official Makani geo-addressing service: turn coordinates into Makani numbers and building info (EN+AR), look up a 10-digit Makani number, or validate one. Covers all seven emirates. |
| `gold_rate` | `dubai_gold_rate` | Dubai Jewellery Group suggested retail gold rates (24K to 14K, AED per gram) from Dubai City of Gold, published around 09:00, 13:30, and 18:00 UAE time. Jewellery reference rates, not spot bullion. |
| `data_dubai` | `data_dubai_search`, `data_dubai_themes`, `data_dubai_entities` | Search the data.dubai catalog (610 datasets from 75 Dubai entities in the 5 September 2026 live check), the portal that replaced Dubai Pulse. Credential-free metadata: dataset descriptions, formats, licences, update frequency, and API endpoints. The dataset APIs themselves still need credentials. |

### 💼 Tier 2: curated business knowledge (no external API, ship today)

| Feature | Tools | What it does |
|---|---|---|
| `setup_advisor` | `setup_advisor` | The headline tool. Recommends mainland vs free zone vs offshore for a Dubai business setup. Cross-references curated free zones, visas, banks, and tax rules. For onshore activity, it compares a mainland DET licence with the conditional branch-licence or temporary-permit route available to eligible Dubai free zone establishments under Executive Council Resolution 11 of 2025. Flags that ordinary SaaS revenue is not automatically qualifying income; eligible copyrighted software may require separate qualifying-IP analysis. |
| `free_zones` | `list_free_zones`, `free_zone_details`, `compare_free_zones`, `list_offshore` | All 12 major Dubai free zones (DMCC, DIFC Innovation, JAFZA, DAFZA, IFZA, Meydan, Dubai South, DSO/Dtec, TECOM, DHCC, DPC/DSC, DIFC full FS) with indicative costs, office options, visa quotas, and scoped banking reports. Quote-only prices are unknown and cannot satisfy a specified budget. Plus JAFZA Offshore and RAK ICC, the free-zone-to-mainland permit regime (Executive Council Resolution 11 of 2025), and the 2026 developments block (District IO, Meydan remote setup, DMCC at 26,000+ members). Setup and renewal quotes must be compared on the same package and inclusions; no universal renewal discount is assumed. |
| `visas` | `list_visa_types`, `visa_details`, `visa_recommend`, `golden_visa_check` | UAE visa types including the 2026 additions: the Dubai 2-year property investor visa (AED 750K minimum removed for sole owners), the expanded visa-on-arrival list, and the GDRFA-DLD single-channel process note. Green Visa correctly split into the AED 15K/month skilled employee track and the freelancer track. Category-specific Golden Visa guidance distinguishes skilled professionals from other talents and ICP from Dubai entrepreneur routes. Includes a myth-buster on the non-existent AED 100K lifetime Golden Visa. |
| `banking` | `list_banks`, `bank_details`, `bank_recommendation`, `dul_eligibility` | 14-bank matrix (Wio, Mashreq NEOBiz, Zand, ruya, Emirates NBD, RAKBANK, ADCB, FAB, CBD, ADIB, HSBC, StanChart, Citi, Liv) on onboarding speed, minimum balance, and crypto stance. Wio Essential/Grow fees are sourced; older bank balance and timing estimates retain their unverified scope. Plus a dated DUL (Dubai Unified Licence) bank-integration snapshot with Dubai-wide mainland and free-zone coverage, the CBUAE Open Finance (Al Tareq) live-bank status, the 2026 licensing wave (Tabby, Mal, Revolut, Alaan), and the CMA-replaces-SCA regulator note. The reported 5-day DUL onboarding figure is an average, not a guarantee. |
| `founder_essentials` | `attestation_guide`, `pro_services_estimate`, `legal_translation_estimate`, `chamber_of_commerce_info`, `setup_timeline_estimate`, `common_founder_mistakes` | The boring stuff that breaks setups. Document-specific UAE attestation routes including eligible digital/courier processing (UAE is not a Hague Apostille member), private-market PRO and legal-translation estimates with official registry links and pricing caveats, current Dubai Chamber membership fee categories and CoO fee, realistic 1-to-16-week banking timelines, and 10 common founder mistakes with impact and fix for each. |
| `tax_compliance` | `corporate_tax_estimate`, `vat_filing_calendar`, `qfzp_check`, `esr_status`, `einvoicing_timeline`, `late_payment_penalty_estimate` | UAE Corporate Tax (Federal Decree-Law 47 of 2022, ordinarily 9% above AED 375,000), Small Business Relief through eligible periods ending 31 December 2029, VAT and QFZP rules, historical ESR scope (2019-2022 obligations and imposed penalties remain; imposed penalties are not refundable), the live e-invoicing pilot (50 accredited ASPs and 7 in final assessment as of 5 September 2026; the overall pre-approved count is no longer separately published), tobacco and vaping minimum excise prices effective 1 September 2026, and the unified 14% annual late-payment rate charged monthly for every month or part of a month. The estimator does not apply the ordinary AED 375,000 band or Small Business Relief to a QFZP. |
| `compliance` | `aml_requirements`, `ubo_filing_guide`, `pdpl_compliance`, `emiratisation_requirements` | UAE AML/CFT obligations under the new Federal Decree-Law 10 of 2025 (fines AED 5M-100M for legal persons, virtual assets covered) with DNFBP detection routing to goAML. UBO filing rules under Cabinet Decision 109 of 2023, which superseded Cabinet Decision 58 of 2020. PDPL compliance for UAE federal, DIFC DPL, and ADGM DPR. Plus Emiratisation targets and the AED 10,000/month charge per unfilled position from 1 July 2026. |
| `funding` | `accelerator_search`, `vc_list`, `grant_programs` | Targeted refresh on 5 September 2026 (last full review 14 August): accelerator and incubator search with current Hub71 Cohort 21 details and expired Cohort 20/Hi2 deadlines marked, subsidized in5 pricing, explicitly verified free-only filtering, and sourced exclusions for misclassified offerings. VC mandates are limited to what current primary sources support. Government support distinguishes MBRIF accelerator and guarantee programs, DFDF dated versus live portfolio snapshots, Dubai SME/Hi2, and Khalifa Fund interest-free loans. |
| `gov_portals` | `portal_guide` | Cross-linked government portal guide, including UAE Pass facial verification/account levels, DubaiNow Madinati, and DubaiPay Jaywan activation on 1 September 2026. |
| `dcde` | `dcde_programs`, `chamber_membership` | Dubai Chamber of Digital Economy programs including Dubai Founders HQ, Antler Founder Residency, FRWRDx, Unicorn 30, the Create Apps Championship, and the Canva SME partnership. DCDE has no standalone membership scheme. The duplicate Create Apps record reflects the ongoing Cycle 3 finalist phase and 7 October 2026 final. |
| `events` | `startup_events`, `gitex_info`, `ens_calendar` | Dubai events calendar refreshed for H2 2026 and 2027: GITEX Global 2026 (summit 7 December; expo 8-11 December at Expo City), Expand North Star, Dubai AI Festival, FinTech Summit, Fitness Challenge, the retail festival calendar, World Governments Summit 2027, Dubai Airshow 2027, and the DWTC-to-Expo-City venue shift. |
| `parkin` | `parking_zones`, `nol_card_guide` | Dubai Parkin zone tariffs (now VAT-inclusive: 5% VAT since 1 June 2026), the cashless-meter transition, the new International City and Discovery Gardens paid zones, Parkin's 2026 mall-parking expansion, and the Nol Card system with official pass prices and RTA coverage; no unsupported automatic daily cap. |
| `ip_trademark` | `trademark_registration`, `ip_protection` | UAE trademark registration via MOET: AED 6,500 in regular government fees for one class, a 20-working-day examination target, and a 30-day opposition period. Covers software and brand IP and the end of new unitary six-state GCC patent filings in 2021. The underlying JSON also records Locarno entry into force on 6 October 2026; industrial-design guidance is not yet a tool category. |
| `halal` | `halal_certification`, `moiat_requirements` | MOIAT halal conformity guidance distinguishes product certification, approved certification bodies and optional National Mark use, with corrected UAE.S standard scopes. |
| `createapps` | `createapps_championship`, `submission_guide` | Dubai Create Apps Championship rules and prize structure. Cycle 3 registration is closed, 12 finalists are in the finalist phase, and the detailed official timeline schedules the final for 7 October 2026; the pack flags a conflicting stale FAQ for reconfirmation before travel. |
| `cost_of_living` | `cost_of_living_overview`, `rent_estimate`, `dewa_bill_estimate`, `salik_toll_estimate`, `grocery_estimate`, `school_fee_estimate`, `fuel_price_guide` | Ballpark Dubai living costs (rent ranges by area and bedroom, grocery baskets by household) plus the deterministic rules: DEWA tariff slabs and the 5% residential housing fee, VAT-inclusive Salik toll windows, the KHDA fee freeze for 2026-27, and the September 2026 UAE fuel snapshot (Super 98 AED 3.80, Special 95 AED 3.69, E-Plus 91 AED 3.61, diesel AED 4.30 per litre). H1 2026 inflation context is flagged throughout. |
| `tenancy` | `ejari_guide`, `rera_rent_increase`, `rental_dispute_guide` | The Dubai tenancy loop. Ejari registration (documents, fees by channel, timeline, common mistakes), the RERA rent-increase calculator under Dubai Decree 43 of 2013 (including the corrected no-increase boundary at exactly 10% below market, plus the 90-day notice rule), Rental Disputes Centre filing (3.5% of annual rent, AED 500 floor, AED 20,000 cap), the new DLD Flexi Rent instalment initiative, and Dubai's shared-housing Law 4 of 2026, effective 8 September 2026. |

### 🤖 Tier 2 agent skills

| Feature | Tools | What it does |
|---|---|---|
| `arabic_writer` | `list_honorifics`, `addressee_block`, `business_letter_template`, `list_salutations` | Bilingual Arabic/English business letter templates with correct UAE honorifics (HH, HE, HRH, Sheikh, Sheikha), addressee blocks, salutations, and closings. Useful when writing to government entities and senior family. |
| `data_analyst` | `plan_query`, `list_plan_categories`, `synthesize_report`, `analyze_setup_decision` | Cross-tool planning and Markdown report synthesis. Hands back a sequenced plan (founder_setup, market_research, compliance_checkup, relocation) that the LLM executes step by step, then renders the results as a structured report. Plans distinguish revenue from taxable income; reports accept explicit source domains instead of claiming every pack contributed. |

### 🧠 Tier 3: meta-tools

| Tool | What it does |
|---|---|
| `recommend_tools(query, top_k=5)` | BM25-powered tool discovery. Pass a natural-language query, get a ranked list of the most relevant tools so the LLM does not have to scan all 100-plus at once. |
| `list_features()` | List every registered feature with its tier, auth requirement, and tool count. |
| `get_knowledge_status()` | Read the freshness registry. Returns every registered business knowledge domain with its latest recorded `knowledge_date`, `full_review_date`, any `previous_knowledge_date` and `last_refresh_scope`, volatility, verification URL, and disclaimer. |
| `about()` | Return the package version, knowledge date, live tool count, and repo URL. Useful for clients that want to confirm which version is running without scanning the full catalogue. |
| `get_upstream_status()` | Session-aware endpoint registry for 16 tracked sources. It returns bootstrap status plus observations made by tools in the current process; it does not proactively probe every endpoint. The table below is a selected point-in-time snapshot, not a complete mirror of the registry. |

### 🔐 Tier 1: Dubai Pulse OAuth

Feature wrappers for `dld` (real estate) and `rta` (transport) ship today with the graceful credential-missing pattern: tools return a structured `success: false` with setup instructions until you set `MCP_DUBAI_PULSE_CLIENT_ID` and `MCP_DUBAI_PULSE_CLIENT_SECRET`. See the [credential guide](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/CREDENTIALS.md) for the full walkthrough.

| Feature | Tools | What it does |
|---|---|---|
| `dld` | `dld_search_transactions`, `dld_search_rent_contracts`, `dld_lookup_broker` | Dubai Land Department real estate sale transactions, Ejari rent contracts, and RERA broker lookup. |
| `rta` (Pulse) | `rta_search_metro_stations`, `rta_search_bus_routes`, `rta_salik_tariff` | RTA metro stations (red and green lines, with Blue Line and Gold Line status notes), bus routes, and the Salik toll tariff (with the 5% VAT note effective June 2026). The `rta_gtfs_static_url` tool needs no credentials: it points at the anonymous direct 7z download (feed GTFS_20250823) after the old transit.land mirror went behind auth. |

More Dubai Pulse feature wrappers (DHA health, DEWA, DTCM, DET, Dubai Municipality, Dubai Customs, Dubai Airports) are on the roadmap once specific datasets are requested.

---

## 📊 Data Sources

| Source | Auth | What we use | Tools |
|---|---|---|---|
| [Al-Adhan API](https://aladhan.com/prayer-times-api) | ✅ Open | Prayer times, Qibla, Hijri calendar | `al_adhan` |
| [Al-Quran Cloud](https://alquran.cloud/api) | ✅ Open | Quran text and translations | `quran_cloud` |
| [CBUAE Umbraco endpoints](https://www.centralbank.ae) | ⚠️ Partial, undocumented | Anonymous FX rates; base-rate endpoint recorded blocked | `cbuae` |
| [FCSC Open Data](https://opendata.fcsc.gov.ae) | 🔶 Anonymous CKAN, recorded blocked | UAE federal dataset and FCA-trade wrappers | `fcsc_ckan` |
| [KHDA Resources](https://web.khda.gov.ae/en/Resources/KHDA-data-statistics) | 📚 Bundled snapshot | Curated Dubai school reference data | `khda` |
| [aviationweather.gov](https://aviationweather.gov/data/api/) | ✅ Open | METAR / TAF for UAE ICAOs | `aviation_weather` |
| [Open-Meteo](https://open-meteo.com/en/docs) | ✅ Open | Human weather and forecast for UAE cities | `open_meteo` |
| [OSM Overpass](https://overpass-api.de) | ✅ Open | POI fallback | `osm_overpass` |
| [WAQI / AQICN](https://aqicn.org/api/) | 🔑 Free key | Air quality | `air_quality` |
| [ExchangeRate-API (open endpoint)](https://www.exchangerate-api.com/docs/free) | ✅ Open | Everyday AED-base currency rates and conversion | `currency` |
| [DFM market data](https://marketwatch.dfm.ae/) | ✅ Open (undocumented) | DFM index and stock quotes | `dfm` |
| [Makani public web service](https://www.makani.ae/) | ✅ Open (SOAP) | Geo-addressing: Makani numbers, reverse geocoding | `makani` |
| [Dubai City of Gold](https://dubaicityofgold.com/) | ✅ Open (HTML) | DJG retail gold rates, AED per gram | `gold_rate` |
| [data.dubai catalog](https://data.dubai) | ✅ Open (metadata only) | Dataset catalog search across 76 Dubai entities | `data_dubai` |
| Curated UAE federal calendar | 📚 Static | Public holidays (2026 confirmed, 2027 provisional) | `holidays` |
| Curated business knowledge files | 📚 Static | Sixteen JSON packs covering free zones, visas, banking, founder essentials, tax compliance, compliance, funding, government portals, DCDE, events, Parkin, IP and trademarks, halal, Create Apps, cost of living, and tenancy; `setup_advisor` composes relevant packs in code | All 17 Tier 2 business features |
| [data.dubai API gateway](https://apis.data.dubai) (successor to Dubai Pulse) | 🔐 OAuth | DLD and RTA wrappers today; additional authority wrappers planned | Tier 1 (Phase 4) |
| [DLD API Gateway](https://dubailand.gov.ae/en/eservices/api-gateway/) | 💰 Paid (~AED 31,500/yr per product) | Ejari, Mollak, Trakheesi, Rental Index | Not built (we use Dubai Pulse open data instead) |

**Things we will NOT build** (full list in the [disclaimer](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/DISCLAIMER.md)): Salik account/balance/trips (private app), NABIDH clinical data (vendor-only PHI), DMCC public-search scraping (ToS-banned), NCM weather wrapper (no public API), DM zoning/parcels (request-only paid), CBUAE Open Finance regulated TPP framework. We also explicitly do not promise A-to-F food grades from the open feed (the consumer app shows them but the open dataset schema is unconfirmed).

### Upstream Status

Some government endpoints have deployed bot protection (Cloudflare) since v0.1.0 released. These tools return a structured `success: false` with `error.status` of `upstream_blocked` instead of crashing. The selected table below is a recorded snapshot. `get_upstream_status()` does not run active probes; it starts from the 16-source bootstrap registry and incorporates observations made by tools during the current process.

| Tool or feature | Endpoint | Recorded status | Last checked |
|---|---|---|---|
| `cbuae_exchange_rates` | `centralbank.ae` Exchange endpoint | ✅ Working (77 currencies; English/Arabic parsing corrected) | 2026-09-05 |
| `cbuae_base_rate` | `centralbank.ae` InterestRate endpoint | 🔶 Cloudflare-blocked | 2026-09-05 |
| `fcsc_search_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked (the same FCSC datasets are browsable on [bayanat.ae](https://bayanat.ae), which exposes a per-resource REST endpoint) | 2026-09-05 |
| `fcsc_get_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked | 2026-09-05 |
| `fcsc_list_organizations` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked | 2026-09-05 |
| `fca_trade_stats` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked (delegates to `fcsc_search_dataset`) | 2026-09-05 |
| `rta_gtfs_static_url` | Dubai Pulse direct file download | 🔶 Intermittent (HTTP 400 directly; valid 7z via apex-host redirect; still the 2025-08-23 build) | 2026-09-05 |
| `dfm` | `api2.dfm.ae` | ✅ Working (458 securities, with all `name` values null upstream) | 2026-09-05 |
| `data_dubai` | `data.dubai/o/c` | ✅ Working metadata catalog (610 datasets, 11 themes, 75 issuers) | 2026-09-05 |
| `makani` | Dubai Municipality SOAP service | ✅ Working | 2026-09-05 |
| `gold_rate` | `dubaicityofgold.com` | ✅ Working server-rendered rates page | 2026-09-05 |

**Portal migration note (2026):** the Dubai Pulse portal (`www.dubaipulse.gov.ae`) was decommissioned between December 2025 and January 2026 and now redirects to [data.dubai](https://data.dubai), run by the Dubai Data and Statistics Establishment. The API gateway moved to `apis.data.dubai` (same endpoint pattern, still OAuth); the legacy `api.dubaipulse.gov.ae` host still resolves. The new `data_dubai` feature searches the portal's credential-free catalog API.

`cbuae_exchange_rates` rows now include `currency` (English), `currency_ar` (Arabic label), `iso_code` (currency code), `source_currency` (exact upstream label), and `rate_aed`. The parser handles both English and Arabic responses; unknown names pass through with a null code so new CBUAE entries are never silently dropped. Offshore yuan uses the market code CNH, which is not a separate ISO 4217 currency.

Clients should check `result["success"]` and read `result["error"]["status"]` / `result["error"]["reason"]` for a user-facing message. We track these endpoints and will restore data access when the upstream blocks are lifted or alternative sources are wired up.

---

## ⚙️ Configuration

**No API credentials are required for 112 of 120 tools in the current source tree.** That describes authentication only: the CBUAE base-rate tool and four FCSC tools are currently recorded as blocked upstream. For the full walkthrough of every environment variable, where to get each credential, and step-by-step setup for data.dubai, WAQI, and Calendarific, see the **[credential guide](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/CREDENTIALS.md)**.

| Env Var | Required | Default | Unlocks |
|---|---|---|---|
| `MCP_DUBAI_PULSE_CLIENT_ID` | Tier 1 only | `None` | The `dld` and `rta` Tier 1 tools (live queries instead of setup instructions) |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Tier 1 only | `None` | The `dld` and `rta` Tier 1 tools (used together with CLIENT_ID) |
| `MCP_DUBAI_PULSE_API_BASE` | No | `https://apis.data.dubai` | Override the data.dubai API base URL |
| `MCP_DUBAI_DATA_PORTAL_BASE` | No | `https://data.dubai` | Override portal URL |
| `MCP_DUBAI_WAQI_TOKEN` | Air quality only | `None` | `air_quality_dubai`, `air_quality_by_coords` |
| `MCP_DUBAI_CALENDARIFIC_KEY` | No | `None` | Future Calendarific holiday refresh |
| `MCP_DUBAI_LOG_LEVEL` | No | `INFO` | Log verbosity |
| `MCP_DUBAI_HTTP_TIMEOUT` | No | `30.0` | HTTP timeout in seconds |
| `MCP_DUBAI_HTTP_MAX_RETRIES` | No | `3` | Tenacity retry budget |

Every variable is optional. The server starts and registers all 15 Tier 0 features, all 17 Tier 2 business features, and both agent skills without any of them. Individual calls can still depend on a token, OAuth entitlement, or live upstream availability.

---

## 📅 Knowledge Freshness

The hardest thing about a Dubai business-knowledge MCP is that **the rules move**. Tax thresholds, visa criteria, free zone pricing, and even API base URLs all change inside a single quarter. This project handles that with seven mechanisms:

1. **Two freshness timestamps** on every curated JSON file: `knowledge_date` for the latest material update and `full_review_date` for the last complete domain review. Targeted refreshes also record `previous_knowledge_date` and `last_refresh_scope` without advancing `full_review_date`.
2. **Per-domain `KNOWLEDGE` constant** in every `biz/*` module, registered with the shared `KnowledgeRegistry` at import time.
3. **`knowledge` block on every business tool response** with `knowledge_date`, `full_review_date`, optional `previous_knowledge_date` and `last_refresh_scope`, `volatility`, `verify_at` URL, and `disclaimer`.
4. **`get_knowledge_status()` meta-tool** that reads from the registry, so a single update flows through automatically.
5. **README badge** + ⚠️ callout under the maintainer's note.
6. **Volatility tags by domain** tied to full-review budgets: 🟢 stable (365 days), 🟡 medium (190 days), 🔴 high (100 days). The checker covers the 16 JSON packs plus `setup_advisor`, `data_analyst`, and `arabic_writer`. Monthly snapshots and event dates should still be reviewed monthly inside the high-volatility ceiling.
7. **Verification queue** of open items tracked by maintainers.

**Volatility map** (current):

| Domain | Volatility | Re-verify cadence |
|---|---|---|
| `setup_advisor`, `cost_of_living`, `events`, `free_zones`, `funding`, `tax_compliance`, `visas` | 🔴 high | 100-day alerting ceiling; monthly for dated snapshots and events |
| `banking`, `compliance`, `createapps`, `dcde`, `founder_essentials`, `ip_trademark`, `parkin`, `tenancy` | 🟡 medium | 190-day alerting ceiling |
| `gov_portals`, `halal` | 🟢 stable | 365-day alerting ceiling |
| `arabic_writer` | 🟢 stable | yearly |
| `data_analyst` | 🟡 medium | re-verify with its underlying tools |
| Tier 0 public-data tools | runtime health | bootstrapped from the source registry and updated through session observations, not the pack-age script |
| Dubai Pulse dataset slugs (when wired) | manual | re-check after portal or gateway changes; not covered by the pack-age script |

**Recent rule changes captured** (latest targeted refresh 2026-09-05; check each pack's `last_refresh_scope`):

- September additions include Ministerial Decision 133 of 2026 on Pillar Two Information Returns, the FTA VAT directive inventory, and Decision 13 of 2026 listed on the VAT legislation register. The latter's operative conditions were unavailable for review and are not inferred.
- Dubai Executive Council Resolution 11 of 2025 took effect on publication in Official Gazette issue 707 on 21 March 2025. Its one-year regularisation period therefore ended on 21 March 2026, not 3 March. The Director General may grant one same-length extension where necessary; the pack does not assume an automatic extension.
- DUL is issued across Dubai mainland and free-zone businesses. The official 12 November 2025 update named seven integrated banks and reported a 5-day average account-opening time; a bank missing from that announcement is not proven non-integrated, and the average is not an individual guarantee.
- Dubai Chamber membership fees currently span AED 50 to AED 2,200 across official categories. The applicable category depends on legal form, owner nationality, and activity; statutory exemptions and a separate free-zone approval route apply.
- UAE e-invoicing pilot is LIVE: the MoF/FTA launched the pilot phase on 1 July 2026 with a Taxpayer Working Group, voluntary adoption open from the same date. The ASP appointment deadline for AED 50M+ revenue businesses was extended to 30 October 2026 (Ministerial Resolution 66 of 2026); go-live stays 1 January 2027. As of 5 September, the [official MoF register](https://mof.gov.ae/en/about-us/initiatives/einvoicing/einvoicing-accredited-service-providers-asps/) listed 50 accredited providers and 7 in final assessment. The overall pre-approved count is no longer separately published and remains unknown.
- VAT Law amended by Federal Decree-Law 16 of 2025 (effective 1 January 2026): reverse-charge self-invoicing removed, excess recoverable VAT capped at 5 years, evasion-linked input VAT denial.
- Tax Procedures and Excise laws amended by Federal Decree-Law 17 of 2025 (effective 1 January 2026): audit window extendable to 15 years for evasion, 5-year refund claim limit with a 31 December 2026 transition for older balances.
- New AML/CFT/CPF framework: Federal Decree-Law 10 of 2025 (in force 14 October 2025) raises fines for legal persons to AED 5M-100M, adds tax evasion as a predicate offence, and explicitly covers virtual assets. Executive regulations in Cabinet Resolution 134 of 2025.
- Emiratisation: the H1 2026 deadline for 50+ employee private firms passed 30 June 2026; AED 10,000/month per unachieved position is charged from 1 July 2026.
- 5% VAT applies to Salik tolls (AED 4.00 to 4.20 standard, AED 6.00 to 6.30 peak) and Parkin parking tariffs from 1 June 2026; cash phased out at Dubai parking meters the same day.
- KHDA froze all Dubai private school fees for the 2026-27 academic year (announced 22 May 2026): no ECI increase.
- Dubai Law 4 of 2026 takes effect on 8 September 2026, following its 12 March Official Gazette publication, and regulates shared housing / co-living (operator permits, registry, fines up to AED 1M). The DLD launched Flexi Rent (monthly/quarterly instalments) in June 2026.
- Dubai 2-year property investor visa: the AED 750,000 minimum was removed for sole owners (April 2026); co-owners need an AED 400,000 registered share each.
- The Dubai Pulse portal was decommissioned (December 2025 to January 2026) and redirects to data.dubai; the API gateway moved to apis.data.dubai. The RTA GTFS archive was downloadable through the apex-host redirect on 5 September, but direct requests were intermittent; its contents still identify the 2025-08-23 build.
- UAE Capital Market Authority (CMA) replaced the SCA effective 1 January 2026 (FDL 32 and 33 of 2025). CBUAE Open Finance (Al Tareq) went live at CBD, FAB, and ADIB; the FDL 6/2025 compliance deadline is 16 September 2026.
- 2026 holiday observances are confirmed through the Prophet's Birthday: Eid Al Fitr ran 19-22 March (30-day Ramadan), Eid Al Adha 27-29 May with Arafat Day 26 May, Hijri New Year was observed Monday 15 June, and the Prophet's Birthday day off was Friday 28 August under [FAHR Circular 11 of 2026](https://www.fahr.gov.ae/wp-content/uploads/2026/08/Circular-No.-11-of-2026-Regarding-The-Holiday-of-the-Prophet-Mohammads-Birthday-1448-AH.pdf), issued 7 August. This corrects the August audit's erroneous claim that no observance had been announced. Commemoration Day (1 December) is a remembrance, not a day off.
- UAE e-invoicing legislated by Ministerial Decisions 243 and 244 of 2025 (PINT AE on a DCTCE model). Phased rollout: mandatory for revenue at or above AED 50M from 1 January 2027, below AED 50M from 1 July 2027, government entities from 1 October 2027. Penalties under Cabinet Decision 106 of 2025. Verify dates with the FTA/MoF.
- Unified late-payment penalty: a 14% annual rate charged monthly at 14% divided by 12 for every month or part of a month, effective 14 April 2026 under Cabinet Decision 129 of 2025.
- Small Business Relief was extended by Ministerial Decision 131 of 2026. Eligible resident persons with revenue at or below AED 3 million may elect relief for tax periods ending on or before 31 December 2029.
- Cabinet Decision 137 of 2026 sets minimum excise prices from 1 September 2026: AED 0.40 per cigarette, AED 0.10 per gram of covered water-pipe or ready-to-use tobacco, and AED 1.00 per millilitre of e-liquid.
- The August 2026 review also reconciled Create Apps Cycle 3's 7 October final, completed a full primary-source review of all retained funding records, corrected official one-class trademark government fees to AED 6,500, and fixed the post-2021 GCC patent filing position.
- QFZP Qualifying Activities were updated by Ministerial Decision 229/2025. Ordinary SaaS is not automatically qualifying; copyrighted software requires a separate qualifying-IP and nexus analysis. The calculator applies 0% to qualifying income and 9% to other taxable income without the ordinary AED 375,000 band or Small Business Relief.
- CT late-registration penalty waived if first return filed within 7 months (FTA, April 2025).
- Golden Visa salary and evidence requirements vary by category and issuing authority. The specialist route must not impose an unsupported blanket 24-month salary-history condition.
- ESR is not required for financial years ending after 31 December 2022 under Cabinet Decision 98 of 2024. Historical 2019-2022 obligations remain, and imposed penalties are not refundable.
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
├── agents/                     # Tier 2 agent skills
│   ├── arabic_writer/
│   └── data_analyst/
├── data/                       # Tier 0 + Tier 1 API integrations
│   ├── al_adhan/
│   ├── aviation_weather/
│   ├── air_quality/
│   ├── cbuae/
│   ├── currency/
│   ├── data_dubai/
│   ├── dfm/
│   ├── dld/
│   ├── dubai_pulse/
│   ├── fcsc_ckan/
│   ├── gold_rate/
│   ├── holidays/
│   ├── khda/
│   ├── makani/
│   ├── open_meteo/
│   ├── osm_overpass/
│   ├── quran_cloud/
│   └── rta/
└── biz/                        # Tier 2 curated business knowledge
    ├── _data/                  # Curated JSON files (loaded via importlib.resources)
    │   ├── free_zones.json
    │   ├── visas.json
    │   ├── banks.json
    │   ├── tax_compliance.json
    │   ├── ... (16 packs total)
    │   └── loader.py
    ├── banking/
    ├── free_zones/
    ├── setup_advisor/
    ├── tax_compliance/
    ├── visas/
    └── ... (17 features total)
```

**Conventions every feature follows:**

- `__init__.py` exports a `FEATURE_META` dict with name, description, tier, requires_auth, source URL.
- `tools.py` holds pure async functions with no FastMCP imports, so unit tests hit the real logic without going through the MCP wrapping layer.
- `server.py` defines a `FastMCP("feature_name")` instance, decorates wrappers, and registers `ToolMeta` records with the shared discovery on import.
- `biz/*` features additionally expose a per-domain `KNOWLEDGE = KnowledgeMetadata(...)` constant and call `register_domain_knowledge(domain, KNOWLEDGE)` so `get_knowledge_status()` reflects current freshness automatically.
- `data/*` features that need OAuth or a free API key use the **graceful credential degradation pattern**: tools never crash when env vars are missing. They call `availability()` and return a structured `ToolResponse.fail({status, reason, docs})` so the MCP client renders a help message instead of a stack trace. This is what lets `python -m mcp_dubai` start cleanly on a fresh machine with no env file.
- Curated JSON files use the **Pattern 3 envelope**: top-level `domain`, `knowledge_date`, `full_review_date`, `volatility`, `verify_at`, and `disclaimer`, plus `previous_knowledge_date` and `last_refresh_scope` for targeted updates. `source_brief_section` is retained as an internal research pointer and is not exposed through `KnowledgeMetadata`. The shared loader maps the supported metadata fields so a single pack update flows through to every tool that uses it.

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
- *"What's today's 22K gold rate in Dubai?"*
- *"How much is petrol in the UAE this month?"*
- *"What building is at Makani 30032 95320?"*
- *"How did the DFM index close today?"*
- *"Find open datasets about traffic on data.dubai."*

**Schools:**
- *"Find Outstanding rated schools in Jumeirah with British curriculum."*
- *"Which Indian / CBSE schools are under AED 20,000/year?"*

**Founder questions** (the headline value):
- *"Where should I set up my SaaS company in Dubai with a 25K AED budget?"*
- *"Compare DMCC and IFZA for a 2-visa consultancy."*
- *"What visa should I get if I'm a freelance developer earning AED 400,000/year?"*
- *"Estimate corporate tax on AED 500K taxable income for my free-zone SaaS, and explain which QFZP facts you need."*
- *"Do I qualify for the Golden Visa with a 32K monthly basic salary?"*
- *"Open a UAE business bank account fast for a solo founder."*
- *"Is Emirates NBD named as DUL-integrated, and does DUL cover a DMCC company?"*
- *"How do I attest my degree certificate from India for use in Dubai?"*
- *"How much do PRO services cost per year for 3 visas?"*
- *"What are the most common mistakes founders make in Dubai?"*

---

## 🗺️ Roadmap

| Phase | Status | Scope |
|---|---|---|
| **Phase 1: Scaffold + Shared** | ✅ Complete | `_shared/` (auth, http, schemas, discovery, knowledge), root server, conftest. |
| **Phase 2: Tier 0 features** | ✅ Complete | 9 initial public-data features: 6 anonymous upstream integrations, 2 bundled static datasets (`khda` and `holidays`), and 1 token-gated integration (`air_quality`). |
| **Phase 3: Tier 2 priority biz** | ✅ Complete | setup_advisor, free_zones, visas, banking, founder_essentials, tax_compliance. |
| **Phase 3b: Tier 2 deferred biz** | ✅ Complete | compliance, funding, gov_portals, dcde, events, parkin, ip_trademark, halal, createapps. |
| **Phase 4: Tier 1 Dubai Pulse scaffolding** | ✅ Complete | dubai_pulse base client + dld + rta example features with credential-missing pattern. Ready to wire more features when credentials arrive. |
| **Phase 5: Polish** | ✅ Complete | README, CONTRIBUTING, CI, PyPI publish workflow, issue templates. |
| **Phase 6: Agent skills** | ✅ Complete | arabic_writer (bilingual letter templates) + data_analyst (cross-tool plans + Markdown report synthesis with knowledge-freshness footer). |
| **Phase 7: Credential-free expansion** | ✅ Complete (v0.3.0) | open_meteo (human weather), currency (AED-base converter), cost_of_living pack, tenancy pack (Ejari + RERA rent-increase + RDC), and a tax_compliance refresh (e-invoicing + the unified 14% annual late-payment rate charged monthly). All ship without credentials. |
| **Phase 8: More Tier 1 features** | 🔐 Blocked on credentials | dha, dewa, det, dtcm, dm_food, dm_permits, dubai_customs, dubai_airports. The dubai_pulse base client and dld + rta examples are ready as the template. The RTA GTFS path was re-discovered in v0.4.0 (anonymous direct 7z download); the DLD-from-CSV path remains dead because the new data.dubai portal exposes no anonymous file downloads. |
| **Phase 9: Scheduled knowledge refresh** | ♻️ Ongoing | Review the 19 curated knowledge domains on their declared schedules and advance `knowledge_date` only for a material update. The checker uses 100-day, 190-day, and 365-day alerting ceilings against `full_review_date` for high, medium, and stable domains. The September 2026 audit refreshed the domains named in the freshness table above; their full-review clocks remain separate. |
| **Phase 10: July 2026 expansion** | ✅ Complete (v0.4.0 source) | Four new credential-free features (dfm market data, makani geo-addressing, gold_rate, data_dubai catalog search), corrected holiday handling plus a provisional 2027 calendar, the GTFS download fix, a fuel-price tool, an Emiratisation tool, and targeted knowledge corrections. The public PyPI release remains 0.2.0 pending maintainer publication. |

---

## 🤝 Contributing

We welcome contributions. Priority areas right now:

1. **Wire up the Phase 8 Tier 1 features** (`dha`, `dewa`, `det`, `dtcm`, `dubai_customs`, `dubai_airports`) once Dubai Pulse credentials land; the base client and the dld/rta examples are the template. The KHDA full-XLSX refresh script is another good starter.
2. **Wire up Tier 1 Dubai Pulse features** once credentials are obtained. Auth and base client are already in `_shared/auth.py` and the `DubaiPulseAuth` graceful-degradation contract is the canonical pattern.
3. **Refresh business knowledge on its declared cadence.** Each curated JSON file has `knowledge_date`, `full_review_date`, a volatility-based alerting budget, and a `verify_at` URL. Tax rules, visa thresholds, and free zone pricing change frequently.
4. **Improve `recommend_tools` BM25 quality** by tuning tags. Current quirk: in small sub-corpora, BM25 length normalization can favour shorter tools when queries collide on common tokens.

Read the [contribution guide](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/CONTRIBUTING.md) for the dev setup, test/lint commands, and PR checklist.

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

Read the full [disclaimer](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/DISCLAIMER.md) for nature of project, trademarks, compliance responsibilities, removal requests, and personal data handling.

---

## 🌟 Acknowledgments

- Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil), which proved the pattern for a country-specific public-data MCP server.
- Built on [FastMCP 3.x](https://gofastmcp.com), the standalone Pythonic MCP framework maintained by Prefect.
- Thanks to the UAE government agencies that publish open data, especially the Federal Competitiveness and Statistics Centre (FCSC) for its credential-free CKAN interface, which is currently recorded as blocked by upstream bot protection.
- Built for the Dubai developer community.

---

## 📬 Contact

- **Maintainer**: Mahdi Salmanzade, Software Developer, Dubai
- **Email**: [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com)
- **Issues**: <https://github.com/mahdi-salmanzade/MCP-Dubai/issues>
- **Pull requests welcome**: see the [contribution guide](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/CONTRIBUTING.md)

---

## 📜 License

[MIT](https://github.com/mahdi-salmanzade/MCP-Dubai/blob/main/LICENSE). Use it, fork it, ship it. Just keep the attribution and the disclaimer.

---

<div align="center">

<img src="./ae.svg" alt="UAE" width="48" height="48">

**Made with ❤️ in Dubai by Mahdi Salmanzade**

Built at [CLRT Studio](https://clrtstudio.com)

📧 [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com) · 📅 April 2026

> هذا المشروع مبادرة مجتمعية مفتوحة المصدر، مرحبًا بمساهماتكم

</div>
