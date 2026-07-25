<!-- mcp-name: io.github.mahdi-salmanzade/mcp-dubai -->

<div align="center">

<img src="./ae.svg" alt="UAE" width="120" height="120">

# MCP-Dubai

**خادم MCP للبيانات العامة في دبي والإمارات وللمعرفة العملية لتأسيس الأعمال**
*An MCP server for Dubai and UAE public data plus curated business setup knowledge*

[![PyPI](https://img.shields.io/pypi/v/mcp-dubai?color=blue)](https://pypi.org/project/mcp-dubai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 3.x](https://img.shields.io/badge/FastMCP-3.x-brightgreen.svg)](https://gofastmcp.com)
[![Made in Dubai](https://img.shields.io/badge/Made%20in-Dubai-red.svg)](#)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#%EF%B8%8F-roadmap)
[![Knowledge Updated](https://img.shields.io/badge/knowledge_updated-July_2026-blue)](#-knowledge-freshness)
[![Tests](https://img.shields.io/badge/tests-691_passing-brightgreen.svg)](#)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](#)

**Connect AI agents (Claude, GPT, Cursor, Copilot) to Dubai and UAE public APIs and curated business setup knowledge.**

🔧 **120 tools** · 🏛️ **37 features** · 📚 **19 verified knowledge domains** · ✅ **14 keyless APIs** · 💼 **56 business advisor tools** · 🤖 **2 agent skills**

[Quick Start](#-quick-start) · [Tool Catalogue](#-tool-catalogue) · [Knowledge Freshness](#-knowledge-freshness) · [Architecture](#%EF%B8%8F-architecture) · [Roadmap](#%EF%B8%8F-roadmap) · [Contributing](#-contributing)

</div>

---

> Dubai gave me a life. I promised myself I'd give something back.
>
> by **Mahdi Salmanzade**, Software Developer, Dubai
> 📧 [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com) · 📅 April 2026

---

> ⚠️ **Knowledge Date: not uniform. Check per domain.**
>
> Freshness is **per pack, not project-wide**. As of 25 July 2026:
>
> | Verified | Packs |
> |---|---|
> | **2026-07-25** | `compliance`, `tax_compliance` (partial), `visas`, `tenancy`, `createapps` |
> | **2026-07-02** | `banks`, `cost_of_living`, `events`, `free_zones`, `parkin` |
> | **2026-04-13** ⚠️ | `dcde`, `founder_essentials`, `funding`, `gov_portals`, `halal`, `ip_trademark` |
>
> The six packs stamped **2026-04-13 are over three months stale** and are the ones most likely to be wrong: accelerator cohort dates, free-zone and trademark fee schedules, and government portal URLs all move quickly. Treat them as leads to verify, not as current fact.
>
> Business rules in the UAE (corporate tax, visas, free zone pricing, accelerator cycles, API migrations) change frequently. Always verify with the official source before making real decisions. Every `biz/*` tool returns its own `knowledge_date`, and `get_knowledge_status()` reports which domains were verified when.

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
2. **Curated business setup knowledge** that no other MCP server has, like which free zone to choose for a SaaS startup, which visa to apply for as a freelance developer, how to estimate corporate tax under the QFZP rules, the full Hague-not-an-option attestation chain, the 11 most common founder mistakes, and a 14-bank matrix with DUL fast-track eligibility.

Drop it into Claude Desktop, Cursor, VS Code, or any MCP-compatible client and your AI assistant can answer questions like *"what time is Fajr tomorrow in Dubai Marina?"* or *"where should I set up my SaaS company in Dubai with a 25K AED budget?"* with grounded, source-cited answers instead of SEO spam.

---

## 💡 Why MCP-Dubai exists

Dubai's public data lives across at least a dozen platforms (`data.dubai` and its `apis.data.dubai` gateway, `opendata.fcsc.gov.ae`, `bayanat.ae`, `centralbank.ae`, `aladhan.com`, `web.khda.gov.ae`, `aviationweather.gov`, and more) each with its own auth, format, and rate limits. Most agencies do not expose self-serve APIs. The few that do are gated behind email-issued OAuth credentials or paywalled at AED 31,500/year per product.

On top of that, founders coming to Dubai face the same questions over and over: which license, which visa, which bank, how much, how long. The web answers are SEO-spam from agency setup firms.

**MCP-Dubai is the honest, code-first answer.**

- Built around 14 keyless APIs that work today (Al-Adhan, Quran Cloud, CBUAE Umbraco, KHDA XLSX, aviationweather.gov, Open-Meteo, ExchangeRate-API, OSM Overpass, DFM market data, Makani geo-addressing, Dubai City of Gold, the data.dubai catalog, FCSC CKAN when unblocked, and a curated UAE holiday calendar), plus WAQI air quality with a free token.
- Layered with curated business knowledge domains that compress 8,600+ lines of source-cited research into structured tools.
- Uses the same `KnowledgeMetadata` envelope on every business response so the LLM (and you) can always see when each domain was last verified.
- Inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil). Aligned with Dubai Data Law (Law 26 of 2015). Run as a community contribution.

---

## 🚀 Quick Start

Works in any MCP client. Zero API keys needed for 112 of 120 tools. The recommended runner is `uvx` (ships with [uv](https://docs.astral.sh/uv/)); plain `pip install mcp-dubai` works too.

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

Every release is published to the [official MCP Registry](https://registry.modelcontextprotocol.io) as `io.github.mahdi-salmanzade/mcp-dubai`, so registry-aware clients can discover and install it by name. For manual setups, any client that speaks stdio MCP only needs:

```json
{
  "command": "uvx",
  "args": ["mcp-dubai"]
}
```

---

## 🧰 Tool Catalogue

**120 tools across 37 features.** All Tier 0 features ship today; every one except `air_quality` (free WAQI token) works with zero credentials. Tier 2 business knowledge and agent-skill tools are also live. Tier 1 (Dubai Pulse OAuth) DLD and RTA feature wrappers ship with graceful credential-missing fallbacks. Use `recommend_tools(query)` to find the right tool for any natural-language question.

### ✅ Tier 0: anonymous APIs (no auth, ship today)

| Feature | Tools | What it does |
|---|---|---|
| `al_adhan` | `prayer_times_for`, `prayer_times_calendar`, `qibla_direction`, `hijri_to_gregorian`, `gregorian_to_hijri` | Prayer times for any UAE city or coords, Qibla compass bearing, Hijri/Gregorian conversion. Method 8 (Gulf Region) is the default; method 16 (Dubai experimental) matches Dubai mosque announcements. |
| `quran_cloud` | `quran_surah`, `quran_ayah`, `quran_juz`, `quran_search` | Full Quran text and translations. Multiple editions (Arabic Uthmani, Sahih International English, Urdu, etc.). |
| `cbuae` | `cbuae_exchange_rates`, `cbuae_base_rate` | Central Bank of UAE exchange rates against AED for 76 currencies (today or historical), bilingual rows with ISO 4217 codes. Sourced from the undocumented Umbraco endpoints, no auth. |
| `fcsc_ckan` | `fcsc_search_dataset`, `fcsc_get_dataset`, `fcsc_list_organizations`, `fca_trade_stats` | Anonymous read against the UAE federal open data CKAN portal. Includes a convenience wrapper for Federal Customs Authority trade statistics (the easiest no-auth path for UAE trade data). |
| `khda` | `khda_search_school`, `khda_list_curricula`, `khda_list_areas` | Search Dubai private schools by name, area, curriculum, KHDA inspection rating, or fee ceiling. Backed by a curated snapshot of well-known schools; full XLSX refresh script in roadmap. |
| `aviation_weather` | `weather_uae_icao`, `weather_uae_all` | METAR (current observation) and TAF (forecast) for the 6 UAE international airports (OMDB Dubai International, OMDW Al Maktoum, OMSJ Sharjah, OMAA Abu Dhabi, OMAL Al Ain, OMRK RAK). The standard substitute for the missing NCM public API. |
| `open_meteo` | `uae_weather`, `uae_weather_forecast`, `weather_by_coords`, `list_uae_weather_cities` | Keyless human-friendly weather: current temperature, feels-like, humidity, wind, and a multi-day forecast (highs, lows, rain chance, UV) for 8 UAE cities or any coordinate, via Open-Meteo. The everyday companion to the pilot-oriented `aviation_weather` METAR/TAF tools. |
| `currency` | `currency_rates`, `currency_convert` | Keyless everyday currency conversion on an AED base via the ExchangeRate-API open endpoint. The convenient companion to the official `cbuae` central-bank rates. |
| `air_quality` | `air_quality_dubai`, `air_quality_by_coords`, `air_quality_dubai_stations` | Real-time air quality (AQI, PM2.5, PM10, NO2, SO2, CO, O3) for Dubai stations via WAQI/AQICN. Requires a free token from `aqicn.org`. Uses the graceful degradation pattern: returns a structured help error if the token is missing. |
| `osm_overpass` | `osm_search_poi`, `osm_list_categories` | Find OpenStreetMap POIs near a Dubai location: restaurants, pharmacies, mosques, ATMs, metro stations, malls, parking, etc. 22 curated categories. |
| `holidays` | `uae_holidays`, `uae_next_holiday`, `is_uae_holiday` | UAE federal public holidays for 2026 (observed dates confirmed through Hijri New Year, including the 15 June transfer) and a provisional 2027 calendar. Lunar holidays are flagged `provisional` until officially announced by MoHRE/FAHR. Commemoration Day is correctly NOT a day off. |
| `dfm` | `dfm_index`, `dfm_stock_quote`, `dfm_list_securities` | Dubai Financial Market live market data: the DFM General Index snapshot and quotes for ~454 listed securities via the anonymous JSON endpoints behind dfm.ae. Undocumented and best-effort; data may be delayed; not investment advice. |
| `makani` | `makani_reverse_geocode`, `makani_details`, `makani_validate` | Dubai Municipality's official Makani geo-addressing service: turn coordinates into Makani numbers and building info (EN+AR), look up a 10-digit Makani number, or validate one. Covers all seven emirates. |
| `gold_rate` | `dubai_gold_rate` | Dubai Jewellery Group suggested retail gold rates (24K to 14K, AED per gram) from Dubai City of Gold, published around 09:00, 13:30, and 18:00 UAE time. Jewellery reference rates, not spot bullion. |
| `data_dubai` | `data_dubai_search`, `data_dubai_themes`, `data_dubai_entities` | Search the data.dubai catalog (617 datasets from 76 Dubai entities), the portal that replaced Dubai Pulse. Credential-free metadata: dataset descriptions, formats, licences, update frequency, and API endpoints. The dataset APIs themselves still need credentials. |

### 💼 Tier 2: curated business knowledge (no external API, ship today)

| Feature | Tools | What it does |
|---|---|---|
| `setup_advisor` | `setup_advisor` | The headline tool. Recommends mainland vs free zone vs offshore for a Dubai business setup. Cross-references curated free zones, visas, banks, and tax rules. Gives jurisdiction, candidate free zones, reasoning, warnings, cost range, timeline, and next steps. Surfaces the SaaS-is-not-QFZP-Qualifying warning automatically. |
| `free_zones` | `list_free_zones`, `free_zone_details`, `compare_free_zones`, `list_offshore` | All 12 major Dubai free zones (DMCC, DIFC Innovation, JAFZA, DAFZA, IFZA, Meydan, Dubai South, DSO/Dtec, TECOM, DHCC, DPC/DSC, DIFC full FS) with cost, office options, visa quota, and bank acceptance reputation. Plus JAFZA Offshore and RAK ICC, the free-zone-to-mainland permit regime (Executive Council Resolution 11 of 2025), and the 2026 developments block (District IO, Meydan remote setup, DMCC at 26,000+ members). Renewal cost myth is corrected here: it is NOT 20-30% higher than setup. |
| `visas` | `list_visa_types`, `visa_details`, `visa_recommend`, `golden_visa_check` | UAE visa types including the 2026 additions: the Dubai 2-year property investor visa (AED 750K minimum removed for sole owners), the expanded visa-on-arrival list, and the GDRFA-DLD single-channel process note. Green Visa correctly split into the AED 15K/month skilled employee track and the freelancer track. Golden Visa specialized talent at AED 30,000 basic monthly. Includes a myth-buster on the non-existent AED 100K lifetime Golden Visa. |
| `banking` | `list_banks`, `bank_details`, `bank_recommendation`, `dul_eligibility` | 14-bank matrix (Wio, Mashreq NEOBiz, Zand, ruya, Emirates NBD, RAKBANK, ADCB, FAB, CBD, ADIB, HSBC, StanChart, Citi, Liv) on onboarding speed, minimum balance, and crypto stance. Plus DUL (Dubai Unified Licence) fast-track eligibility, the CBUAE Open Finance (Al Tareq) live-bank status, the 2026 licensing wave (Tabby, Mal, Revolut, Alaan), and the CMA-replaces-SCA regulator note. |
| `founder_essentials` | `attestation_guide`, `pro_services_estimate`, `legal_translation_estimate`, `chamber_of_commerce_info`, `setup_timeline_estimate`, `common_founder_mistakes` | The boring stuff that breaks setups. Full 5-step UAE legalization chain (UAE is NOT a Hague Apostille member, despite what some sources claim), PRO service cost estimator, MOJ legal translation calculator, Dubai Chamber of Commerce membership and CoO fees, realistic 1-to-16-week banking timelines, and the 11 most common founder mistakes with impact and fix for each. |
| `tax_compliance` | `corporate_tax_estimate`, `vat_filing_calendar`, `qfzp_check`, `esr_status`, `einvoicing_timeline`, `late_payment_penalty_estimate` | UAE Corporate Tax (Federal Decree-Law 47 of 2022, 9% above AED 375,000), VAT (5%, plus the FDL 16/2025 amendments effective January 2026), QFZP (Ministerial Decision 229 of 2025, with the explicit SaaS-not-qualifying warning), ESR status (DEAD for periods after Dec 2022), the e-invoicing rollout with the pilot LIVE since 1 July 2026 (ASP appointment deadline 30 October 2026 for AED 50M+ revenue per Ministerial Resolution 66 of 2026, 41 pre-approved service providers), and the unified 14% per-year late-payment penalty (effective 14 April 2026). |
| `compliance` | `aml_requirements`, `ubo_filing_guide`, `pdpl_compliance`, `emiratisation_requirements` | UAE AML/CFT obligations under the new Federal Decree-Law 10 of 2025 (fines AED 5M-100M for legal persons, virtual assets covered) with DNFBP detection routing to goAML. UBO filing rules (Cabinet Decision 58/2020). PDPL compliance for UAE federal, DIFC DPL, and ADGM DPR. Plus Emiratisation targets and the AED 10,000/month charge per unfilled position from 1 July 2026. |
| `funding` | `accelerator_search`, `vc_list`, `grant_programs` | Accelerator program search filtered by sector, free/paid, and location. Active UAE VC list. Grant programs including Mohammed bin Rashid Innovation Fund and Khalifa Fund. |
| `gov_portals` | `portal_guide` | Cross-linked guide to UAE government portals (MOHRE, ICP, FTA, EmaraTax, GDRFA, Dubai Now, TAS HEEL, Tamm, Tawjeeh) with what each does and which service sits where. |
| `dcde` | `dcde_programs`, `chamber_membership` | Dubai Chamber of Digital Economy programs (Dubai Unified Licence fast-track, DIIC, Techstars Dubai) and chamber membership benefits and fees. |
| `events` | `startup_events`, `gitex_info`, `ens_calendar` | Dubai events calendar refreshed for H2 2026 and 2027: GITEX Global 2026 (7-11 December at Expo City), Expand North Star, Dubai AI Festival, FinTech Summit, Fitness Challenge, the retail festival calendar, World Governments Summit 2027, Dubai Airshow 2027, and the DWTC-to-Expo-City venue shift. |
| `parkin` | `parking_zones`, `nol_card_guide` | Dubai Parkin zone tariffs (now VAT-inclusive: 5% VAT since 1 June 2026), the cashless-meter transition, the new International City and Discovery Gardens paid zones, Parkin's 2026 mall-parking expansion, and the Nol Card system with cap rules and RTA coverage. |
| `ip_trademark` | `trademark_registration`, `ip_protection` | UAE trademark registration process via MOIAT (MOE migration complete), classes, timeline, and the three protection routes for software and brand IP. |
| `halal` | `halal_certification`, `moiat_requirements` | Halal certification process via ESMA/UAE.S Halal National Mark, MOIAT import requirements for food, beverages, cosmetics, and pharmaceuticals. |
| `createapps` | `createapps_championship`, `submission_guide` | Dubai Create Apps Championship entry rules, prize structure, timeline, and a submission-ready step-by-step guide. |
| `cost_of_living` | `cost_of_living_overview`, `rent_estimate`, `dewa_bill_estimate`, `salik_toll_estimate`, `grocery_estimate`, `school_fee_estimate`, `fuel_price_guide` | Ballpark Dubai living costs (rent ranges by area and bedroom, grocery baskets by household) plus the deterministic rules: DEWA tariff slabs and the 5% residential housing fee, the Salik variable-toll windows (VAT-inclusive since June 2026), the KHDA fee freeze for 2026-27, and monthly UAE fuel prices (July 2026 snapshot with the committee mechanism). H1 2026 inflation context (Dubai CPI 5.5% in May) is flagged throughout. |
| `tenancy` | `ejari_guide`, `rera_rent_increase`, `rental_dispute_guide` | The Dubai tenancy loop. Ejari registration (documents, fees by channel, timeline, common mistakes), the RERA rent-increase calculator under Dubai Decree 43 of 2013 (bands verified unchanged as of July 2026, plus the 90-day notice rule), Rental Disputes Centre filing (3.5% of annual rent, AED 500 floor, AED 20,000 cap), the new DLD Flexi Rent instalment initiative, and Dubai's shared-housing Law 4 of 2026. |

### 🤖 Tier 2 agent skills

| Feature | Tools | What it does |
|---|---|---|
| `arabic_writer` | `list_honorifics`, `addressee_block`, `business_letter_template`, `list_salutations` | Bilingual Arabic/English business letter templates with correct UAE honorifics (HH, HE, HRH, Sheikh, Sheikha), addressee blocks, salutations, and closings. Useful when writing to government entities and senior family. |
| `data_analyst` | `plan_query`, `list_plan_categories`, `synthesize_report`, `analyze_setup_decision` | Cross-tool planning and Markdown report synthesis. Hands back a sequenced plan (founder_setup, market_research, compliance_checkup, relocation) that the LLM executes step by step, then renders the results as a structured report. |

### 🧠 Tier 3: meta-tools

| Tool | What it does |
|---|---|
| `recommend_tools(query, top_k=5)` | BM25-powered tool discovery. Pass a natural-language query, get a ranked list of the most relevant tools so the LLM does not have to scan all 100-plus at once. |
| `list_features()` | List every registered feature with its tier, auth requirement, and tool count. |
| `get_knowledge_status()` | Read the freshness registry. Returns every registered business knowledge domain with its `knowledge_date`, `volatility`, `verify_at` URL, and disclaimer. |
| `about()` | Return the package version, knowledge date, live tool count, and repo URL. Useful for clients that want to confirm which version is running without scanning the full catalogue. |
| `get_upstream_status()` | Live upstream endpoint health registry: each tracked endpoint (CBUAE, FCSC CKAN, RTA GTFS, DFM, Makani, gold rate, data.dubai catalog, WAQI, Dubai Pulse) with its status and reason, matching the Upstream Status table below. |

### 🔐 Tier 1: Dubai Pulse OAuth

Feature wrappers for `dld` (real estate) and `rta` (transport) ship today with the graceful credential-missing pattern: tools return a structured `success: false` with setup instructions until you set `MCP_DUBAI_PULSE_CLIENT_ID` and `MCP_DUBAI_PULSE_CLIENT_SECRET`. See [CREDENTIALS.md](./CREDENTIALS.md) for the full walkthrough.

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
| [CBUAE Umbraco endpoints](https://www.centralbank.ae) | ✅ Open (undocumented) | FX rates, base rate | `cbuae` |
| [FCSC Open Data](https://opendata.fcsc.gov.ae) | ✅ Open (CKAN) | UAE federal datasets, FCA trade | `fcsc_ckan` |
| [KHDA Resources](https://web.khda.gov.ae/en/Resources/KHDA-data-statistics) | ✅ Open (XLSX) | Dubai schools | `khda` |
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
| Curated business knowledge files | 📚 Static | Free zones, visas, banks, founder essentials, tax, cost of living, tenancy | `setup_advisor`, `free_zones`, `visas`, `banking`, `founder_essentials`, `tax_compliance`, `cost_of_living`, `tenancy` |
| [Dubai Pulse Gateway](https://api.dubaipulse.gov.ae) (now [data.dubai](https://data.dubai), API host `apis.data.dubai`) | 🔐 OAuth (planned) | DLD, RTA, DHA, DEWA, DET, DTCM, DM, Dubai Airports | Tier 1 (Phase 4) |
| [DLD API Gateway](https://dubailand.gov.ae/en/eservices/api-gateway/) | 💰 Paid (~AED 31,500/yr per product) | Ejari, Mollak, Trakheesi, Rental Index | Not built (we use Dubai Pulse open data instead) |

**Things we will NOT build** (full list in [DISCLAIMER.md](DISCLAIMER.md)): Salik account/balance/trips (private app), NABIDH clinical data (vendor-only PHI), DMCC public-search scraping (ToS-banned), NCM weather wrapper (no public API), DM zoning/parcels (request-only paid), CBUAE Open Finance regulated TPP framework. We also explicitly do not promise A-to-F food grades from the open feed (the consumer app shows them but the open dataset schema is unconfirmed).

### Upstream Status

Some government endpoints have deployed bot protection (Cloudflare) since v0.1.0 released. These tools return a structured `success: false` with `error.status` of `upstream_blocked` instead of crashing. The rest of the package is unaffected.

| Tool | Endpoint | Status as of 2026-07-02 |
|---|---|---|
| `cbuae_exchange_rates` | `centralbank.ae` Exchange endpoint | ✅ Working (scraper updated in v0.1.2 for the new Arabic three-cell DOM) |
| `cbuae_base_rate` | `centralbank.ae` InterestRate endpoint | 🔶 Cloudflare-blocked |
| `fcsc_search_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked (the same FCSC datasets are browsable on [bayanat.ae](https://bayanat.ae), which exposes a per-resource REST endpoint) |
| `fcsc_get_dataset` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked |
| `fcsc_list_organizations` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked |
| `fca_trade_stats` | `opendata.fcsc.gov.ae` CKAN | 🔶 Cloudflare-blocked (delegates to fcsc_search_dataset) |
| `rta_gtfs_static_url` | Dubai Pulse direct file download | ✅ Working again (anonymous 7z download; the transit.land mirror it previously pointed at now returns 401) |

**Portal migration note (2026):** the Dubai Pulse portal (`www.dubaipulse.gov.ae`) was decommissioned between December 2025 and January 2026 and now redirects to [data.dubai](https://data.dubai), run by the Dubai Data and Statistics Establishment. The API gateway moved to `apis.data.dubai` (same endpoint pattern, still OAuth); the legacy `api.dubaipulse.gov.ae` host still resolves. The new `data_dubai` feature searches the portal's credential-free catalog API.

`cbuae_exchange_rates` rows now include `currency` (English), `currency_ar` (Arabic as returned by CBUAE), `iso_code` (ISO 4217), and `rate_aed`. Unknown currencies pass through with `iso_code: null` and `currency: null` so new CBUAE entries are never silently dropped.

Clients should check `result["success"]` and read `result["error"]["status"]` / `result["error"]["reason"]` for a user-facing message. We track these endpoints and will restore data access when the upstream blocks are lifted or alternative sources are wired up.

---

## ⚙️ Configuration

**Zero keys required to run 112 of 120 tools.** For the full walkthrough of every environment variable, where to get each credential, and step-by-step setup for Dubai Pulse, WAQI, and Calendarific, see **[CREDENTIALS.md](./CREDENTIALS.md)**.

| Env Var | Required | Default | Unlocks |
|---|---|---|---|
| `MCP_DUBAI_PULSE_CLIENT_ID` | Tier 1 only | `None` | The `dld` and `rta` Tier 1 tools (live queries instead of setup instructions) |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Tier 1 only | `None` | The `dld` and `rta` Tier 1 tools (used together with CLIENT_ID) |
| `MCP_DUBAI_PULSE_API_BASE` | No | `https://api.dubaipulse.gov.ae` | Override base URL for the data.dubai migration |
| `MCP_DUBAI_DATA_PORTAL_BASE` | No | `https://data.dubai` | Override portal URL |
| `MCP_DUBAI_WAQI_TOKEN` | Air quality only | `None` | `air_quality_dubai`, `air_quality_by_coords` |
| `MCP_DUBAI_CALENDARIFIC_KEY` | No | `None` | Future Calendarific holiday refresh |
| `MCP_DUBAI_LOG_LEVEL` | No | `INFO` | Log verbosity |
| `MCP_DUBAI_HTTP_TIMEOUT` | No | `30.0` | HTTP timeout in seconds |
| `MCP_DUBAI_HTTP_MAX_RETRIES` | No | `3` | Tenacity retry budget |

Every variable is optional. The server starts and runs all 15 Tier 0 features, all 17 Tier 2 business features, and both agent skills without any of them.

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
| `setup_advisor`, `free_zones`, `visas`, `tax_compliance`, `cost_of_living` | 🔴 high | quarterly |
| `banking`, `founder_essentials`, `tenancy` | 🟡 medium | quarterly |
| Tier 0 anonymous APIs | 🟢 stable | yearly |
| Dubai Pulse dataset slugs (when wired) | 🟡 medium | quarterly (portal migrated to data.dubai in early 2026; slugs unchanged on the API gateway) |
| Accelerator cohort dates, event calendar | 🔴 high | monthly |

**Recent rule changes captured** (as of 2026-07-02):

- UAE e-invoicing pilot is LIVE: the MoF/FTA launched the pilot phase on 1 July 2026 with a Taxpayer Working Group, voluntary adoption open from the same date. The ASP appointment deadline for AED 50M+ revenue businesses was extended to 30 October 2026 (Ministerial Resolution 66 of 2026); go-live stays 1 January 2027. The official MoF register lists 41 pre-approved service providers.
- VAT Law amended by Federal Decree-Law 16 of 2025 (effective 1 January 2026): reverse-charge self-invoicing removed, excess recoverable VAT capped at 5 years, evasion-linked input VAT denial.
- Tax Procedures and Excise laws amended by Federal Decree-Law 17 of 2025 (effective 1 January 2026): audit window extendable to 15 years for evasion, 5-year refund claim limit with a 31 December 2026 transition for older balances.
- New AML/CFT/CPF framework: Federal Decree-Law 10 of 2025 (in force 14 October 2025) raises fines for legal persons to AED 5M-100M, adds tax evasion as a predicate offence, and explicitly covers virtual assets. Executive regulations in Cabinet Resolution 134 of 2025.
- Emiratisation: the H1 2026 deadline for 50+ employee private firms passed 30 June 2026; AED 10,000/month per unachieved position is charged from 1 July 2026.
- 5% VAT applies to Salik tolls (AED 4.00 to 4.20 standard, AED 6.00 to 6.30 peak) and Parkin parking tariffs from 1 June 2026; cash phased out at Dubai parking meters the same day.
- KHDA froze all Dubai private school fees for the 2026-27 academic year (announced 22 May 2026): no ECI increase.
- Dubai Law 4 of 2026 regulates shared housing / co-living (operator permits, registry, fines up to AED 1M). The DLD launched Flexi Rent (monthly/quarterly instalments) in June 2026.
- Dubai 2-year property investor visa: the AED 750,000 minimum was removed for sole owners (April 2026); co-owners need an AED 400,000 registered share each.
- The Dubai Pulse portal was decommissioned (December 2025 to January 2026) and redirects to data.dubai; the API gateway moved to apis.data.dubai. The RTA GTFS feed remains anonymously downloadable as a direct 7z file.
- UAE Capital Market Authority (CMA) replaced the SCA effective 1 January 2026 (FDL 32 and 33 of 2025). CBUAE Open Finance (Al Tareq) went live at CBD, FAB, and ADIB; the FDL 6/2025 compliance deadline is 16 September 2026.
- 2026 holiday observances confirmed through Hijri New Year: Eid Al Fitr ran 19-22 March (30-day Ramadan), Eid Al Adha 27-29 May with Arafat Day 26 May, and the Hijri New Year day off was moved to Monday 15 June under the transferable-holiday rule. Commemoration Day (1 December) is a remembrance, not a day off.
- UAE e-invoicing legislated by Ministerial Decisions 243 and 244 of 2025 (PINT AE on a DCTCE model). Phased rollout: mandatory for revenue at or above AED 50M from 1 January 2027, below AED 50M from 1 July 2027, government entities from 1 October 2027. Penalties under Cabinet Decision 106 of 2025. Verify dates with the FTA/MoF.
- Unified late-payment penalty: flat 14% per year on unpaid tax (Cabinet Decision 129 of 2025, effective 14 April 2026), replacing the previous escalating monthly model across VAT, Excise, and Corporate Tax.
- Small Business Relief: as of June 2026 no extension announced; relief ends for tax periods ending 31 December 2026, standard Corporate Tax applies thereafter.
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
| **Phase 7: Credential-free expansion** | ✅ Complete (v0.3.0) | open_meteo (human weather), currency (AED-base converter), cost_of_living pack, tenancy pack (Ejari + RERA rent-increase + RDC), and a tax_compliance refresh (e-invoicing + the unified 14% late-payment penalty). All ship without credentials. |
| **Phase 8: More Tier 1 features** | 🔐 Blocked on credentials | dha, dewa, det, dtcm, dm_food, dm_permits, dubai_customs, dubai_airports. The dubai_pulse base client and dld + rta examples are ready as the template. The RTA GTFS path was re-discovered in v0.4.0 (anonymous direct 7z download); the DLD-from-CSV path remains dead because the new data.dubai portal exposes no anonymous file downloads. |
| **Phase 9: Quarterly knowledge refresh** | ♻️ Ongoing | Re-verify the 19 curated knowledge domains every quarter, bump knowledge_date in the JSON files. Tax rules and visa thresholds move fastest. July 2026 refresh done in v0.4.0. |
| **Phase 10: July 2026 expansion** | ✅ Complete (v0.4.0) | Four new credential-free features (dfm market data, makani geo-addressing, gold_rate, data_dubai catalog search), corrected 2026 holiday observances plus a provisional 2027 calendar, the GTFS download fix, a fuel-price tool, an Emiratisation tool, and a full knowledge refresh across the tax, visas, free zones, banking, tenancy, parkin, cost-of-living, events, and compliance packs. |

---

## 🤝 Contributing

We welcome contributions. Priority areas right now:

1. **Wire up the Phase 8 Tier 1 features** (`dha`, `dewa`, `det`, `dtcm`, `dubai_customs`, `dubai_airports`) once Dubai Pulse credentials land; the base client and the dld/rta examples are the template. The KHDA full-XLSX refresh script is another good starter.
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
- **Email**: [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com)
- **Issues**: <https://github.com/mahdi-salmanzade/MCP-Dubai/issues>
- **Pull requests welcome**: see [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 License

[MIT](LICENSE). Use it, fork it, ship it. Just keep the attribution and the disclaimer.

---

<div align="center">

<img src="./ae.svg" alt="UAE" width="48" height="48">

**Made with ❤️ in Dubai by Mahdi Salmanzade**

Built at [CLRT Studio](https://clrtstudio.com)

📧 [mahdi@clrtstudio.com](mailto:mahdi@clrtstudio.com) · 📅 April 2026

> هذا المشروع مبادرة مجتمعية مفتوحة المصدر، مرحبًا بمساهماتكم

</div>
