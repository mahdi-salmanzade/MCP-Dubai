<!-- mcp-name: io.github.mahdi-salmanzade/mcp-dubai -->

<div align="center">

<img src="https://raw.githubusercontent.com/mahdi-salmanzade/MCP-Dubai/main/ae.svg" alt="UAE" width="80" height="80">

# MCP-Dubai

**Dubai and UAE public data and business setup knowledge for MCP clients.**

خادم MCP للبيانات العامة في دبي والإمارات وللمعرفة العملية لتأسيس الأعمال

[![PyPI](https://img.shields.io/pypi/v/mcp-dubai?color=blue)](https://pypi.org/project/mcp-dubai/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![CI](https://github.com/mahdi-salmanzade/MCP-Dubai/actions/workflows/ci.yml/badge.svg)](https://github.com/mahdi-salmanzade/MCP-Dubai/actions/workflows/ci.yml)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#project-status)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Quick start](#quick-start) · [Tools](#tool-catalogue) · [Configuration](#configuration) · [Data freshness](#knowledge-freshness) · [Development](#development) · [Latest audit](AUDIT-2026-09-05.md)

</div>

MCP-Dubai is a [Model Context Protocol](https://modelcontextprotocol.io) server that connects AI assistants to public APIs, bundled reference datasets, and curated business knowledge. It runs locally over stdio and returns structured results with source and freshness metadata where available.

The current source includes **120 tools across 37 features**:

| Area | Tools | Coverage |
|---|---:|---|
| Public data and reference datasets | 45 | Weather, prayer times, currencies, schools, holidays, market data, locations, and dataset discovery |
| Dubai government dataset queries | 6 | DLD real estate and RTA transport through data.dubai OAuth |
| Business knowledge | 56 | Company setup, free zones, visas, banking, tax, compliance, funding, and living costs |
| Writing and analysis | 8 | Arabic/English letter templates, query plans, and report synthesis |
| Discovery and diagnostics | 5 | Tool recommendations, feature inventory, version, knowledge dates, and upstream status |

**112 tools require no credentials.** Two air-quality tools need a free WAQI token; six government dataset tools need OAuth credentials and dataset access. Credential-free tools can still depend on an unavailable upstream service; see [availability and limitations](#availability-and-limitations).

## Quick start

### Run the current source

Requires Python 3.11 or newer and Git. The September 5 audit tested Python 3.11 through 3.14.

```bash
git clone https://github.com/mahdi-salmanzade/MCP-Dubai.git
cd MCP-Dubai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, create the environment with `py -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1`.

Configure your MCP client to launch the environment's Python executable:

```json
{
  "mcpServers": {
    "dubai": {
      "command": "/absolute/path/to/MCP-Dubai/.venv/bin/python",
      "args": ["-m", "mcp_dubai"]
    }
  }
}
```

Replace `command` with your actual absolute path. On Windows, use the environment's `.venv\Scripts\python.exe` path, escaping backslashes in JSON.

| Client | Configuration file |
|---|---|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS; `%APPDATA%\Claude\claude_desktop_config.json` on Windows |
| Cursor | `.cursor/mcp.json` in the project, or `~/.cursor/mcp.json` globally |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |

For VS Code, use `.vscode/mcp.json` with a `servers` key:

```json
{
  "servers": {
    "dubai": {
      "command": "/absolute/path/to/MCP-Dubai/.venv/bin/python",
      "args": ["-m", "mcp_dubai"]
    }
  }
}
```

For another MCP client, use the same command and arguments in its stdio server settings. After connecting, call `about()` to check the running version and tool count, then `recommend_tools(query)` to find relevant tools.

To launch the server directly from the activated environment:

```bash
python -m mcp_dubai
```

This starts an MCP stdio process that waits for client messages.

### Use the published package

**Release snapshot, September 5, 2026:** the repository is version **0.4.0 with 120 tools**; the public PyPI release is **0.2.0 with 91 tools**. Use the source installation above for the catalogue documented here.

To run the published release with [uv](https://docs.astral.sh/uv/):

```bash
uvx mcp-dubai
```

In a client configuration, set `command` to `uvx` and `args` to `["mcp-dubai"]`. Alternatively, install it in a virtual environment with `python -m pip install mcp-dubai` and run `mcp-dubai`.

## Tool catalogue

Tools are grouped by purpose below. All names are exposed without a feature prefix. `list_features()` returns the registered groups, tool counts, tiers, and authentication requirements.

### Public data and reference datasets

| Feature | Tools | Coverage |
|---|---|---|
| `al_adhan` | `prayer_times_for`, `prayer_times_calendar`, `qibla_direction`, `hijri_to_gregorian`, `gregorian_to_hijri` | Prayer times, Qibla bearings, and Hijri/Gregorian conversion. |
| `quran_cloud` | `quran_surah`, `quran_ayah`, `quran_juz`, `quran_search` | Quran text and translations with bounded, paginated search. |
| `cbuae` | `cbuae_exchange_rates`, `cbuae_base_rate` | CBUAE exchange rates with English/Arabic labels and currency codes. The base-rate endpoint is recorded as blocked. |
| `fcsc_ckan` | `fcsc_search_dataset`, `fcsc_get_dataset`, `fcsc_list_organizations`, `fca_trade_stats` | Federal dataset discovery and trade-data search. The CKAN endpoint is recorded as blocked. |
| `khda` | `khda_search_school`, `khda_list_curricula`, `khda_list_areas` | Search a bundled 16-school sample by area, curriculum, rating, or indicative fee ceiling. This is not a complete school directory. |
| `aviation_weather` | `weather_uae_icao`, `weather_uae_all` | METAR observations and TAF forecasts for six UAE airports. |
| `open_meteo` | `uae_weather`, `uae_weather_forecast`, `weather_by_coords`, `list_uae_weather_cities` | Current weather and forecasts for eight UAE cities or supplied coordinates. |
| `currency` | `currency_rates`, `currency_convert` | AED-based exchange rates and currency conversion. |
| `air_quality` | `air_quality_dubai`, `air_quality_by_coords`, `air_quality_dubai_stations` | WAQI air-quality readings and a station reference list. Readings require a free token; the list does not. |
| `osm_overpass` | `osm_search_poi`, `osm_list_categories` | Nearby OpenStreetMap points of interest across 22 categories. |
| `holidays` | `uae_holidays`, `uae_next_holiday`, `is_uae_holiday` | UAE federal holidays for 2026 and a provisional 2027 calendar, with announced observances distinguished from estimates. |
| `dfm` | `dfm_index`, `dfm_stock_quote`, `dfm_list_securities` | DFM index snapshots, quotes, and securities from undocumented public endpoints. Data may be delayed or incomplete. |
| `makani` | `makani_reverse_geocode`, `makani_details`, `makani_validate` | Makani address lookup, reverse geocoding, and number validation. |
| `gold_rate` | `dubai_gold_rate` | Dubai Jewellery Group suggested retail gold rates in AED per gram. |
| `data_dubai` | `data_dubai_search`, `data_dubai_themes`, `data_dubai_entities` | Public dataset metadata, themes, and publishers. Access to dataset records is separate. |
| `rta` (GTFS) | `rta_gtfs_static_url` | Link and metadata for the anonymous GTFS archive, including its dated build and intermittent availability. |

### Government dataset queries

These six tools require `MCP_DUBAI_PULSE_CLIENT_ID`, `MCP_DUBAI_PULSE_CLIENT_SECRET`, and access to the requested datasets. Without credentials, they return structured setup instructions. See [CREDENTIALS.md](CREDENTIALS.md).

| Feature | Tools | Coverage |
|---|---|---|
| `dld` | `dld_search_transactions`, `dld_search_rent_contracts`, `dld_lookup_broker` | Property sales, Ejari rental contracts, and registered brokers. |
| `rta` | `rta_search_metro_stations`, `rta_search_bus_routes`, `rta_salik_tariff` | Metro stations, bus routes, and Salik tariff data. |

### Business knowledge

These tools use **16 bundled JSON packs** and a setup advisor that combines relevant records. Successful responses include knowledge metadata. Prices, eligibility rules, and estimates retain their documented scope and verification dates.

| Feature | Tools | Coverage |
|---|---|---|
| `setup_advisor` | `setup_advisor` | Compare mainland, free-zone, and offshore setup options using budget, activity, visa, banking, and tax considerations. |
| `free_zones` | `list_free_zones`, `free_zone_details`, `compare_free_zones`, `list_offshore` | Twelve curated free-zone entries, offshore options, indicative costs, and package details. Unknown prices cannot satisfy a budget filter. |
| `visas` | `list_visa_types`, `visa_details`, `visa_recommend`, `golden_visa_check` | Visa routes and category-specific eligibility guidance, including authority and evidence requirements. |
| `banking` | `list_banks`, `bank_details`, `bank_recommendation`, `dul_eligibility` | Fourteen bank entries, fees, onboarding estimates, and dated Dubai Unified Licence integration information. |
| `founder_essentials` | `attestation_guide`, `pro_services_estimate`, `legal_translation_estimate`, `chamber_of_commerce_info`, `setup_timeline_estimate`, `common_founder_mistakes` | Document attestation, provider cost estimates, Chamber membership, setup timelines, and common filing mistakes. |
| `tax_compliance` | `corporate_tax_estimate`, `vat_filing_calendar`, `qfzp_check`, `esr_status`, `einvoicing_timeline`, `late_payment_penalty_estimate` | Corporate tax estimates, QFZP conditions, VAT calendars, ESR history, e-invoicing milestones, and penalty estimates. |
| `compliance` | `aml_requirements`, `ubo_filing_guide`, `pdpl_compliance`, `emiratisation_requirements` | AML, beneficial ownership, data-protection, and Emiratisation requirements. |
| `funding` | `accelerator_search`, `vc_list`, `grant_programs` | Accelerator and investor discovery, government support, and dated application windows. |
| `gov_portals` | `portal_guide` | Government portal guidance, including UAE Pass, DubaiNow, and DubaiPay. |
| `dcde` | `dcde_programs`, `chamber_membership` | Dubai Chamber of Digital Economy programs and Chamber membership guidance. |
| `events` | `startup_events`, `gitex_info`, `ens_calendar` | Startup events, GITEX, and Expand North Star dates and venues. |
| `parkin` | `parking_zones`, `nol_card_guide` | Parking zones, tariffs, and Nol card fares and passes. |
| `ip_trademark` | `trademark_registration`, `ip_protection` | Trademark registration, patent, and copyright guidance. Industrial-design guidance is not yet a tool category. |
| `halal` | `halal_certification`, `moiat_requirements` | Halal conformity, certification bodies, National Mark use, and MOIAT requirements. |
| `createapps` | `createapps_championship`, `submission_guide` | Create Apps Championship rules, application guidance, and dated competition milestones. |
| `cost_of_living` | `cost_of_living_overview`, `rent_estimate`, `dewa_bill_estimate`, `salik_toll_estimate`, `grocery_estimate`, `school_fee_estimate`, `fuel_price_guide` | Indicative household budgets, utility and toll calculations, school fee estimates, and monthly fuel-price snapshots. |
| `tenancy` | `ejari_guide`, `rera_rent_increase`, `rental_dispute_guide` | Ejari registration, RERA rent-increase calculations, and rental-dispute procedures. |

### Writing and analysis

| Feature | Tools | Coverage |
|---|---|---|
| `arabic_writer` | `list_honorifics`, `addressee_block`, `business_letter_template`, `list_salutations` | Arabic/English business letter templates, honorifics, addressees, and salutations. |
| `data_analyst` | `plan_query`, `list_plan_categories`, `synthesize_report`, `analyze_setup_decision` | Cross-tool query plans and Markdown report synthesis. The calling agent executes the plan; these tools do not run it autonomously. |

### Discovery and diagnostics

| Tool | Purpose |
|---|---|
| `recommend_tools(query, top_k=5)` | Rank tools relevant to a natural-language query using BM25 search and aliases. |
| `list_features()` | List registered features, tiers, authentication requirements, and tools. |
| `get_knowledge_status()` | Inspect dates, review scope, volatility, and verification links for all 19 tracked knowledge domains. |
| `about()` | Check the running package version, tool count, repository URL, and latest recorded knowledge update. |
| `get_upstream_status()` | Read the 16-source status registry and observations from the current process. This does not actively probe every endpoint. |

## Configuration

No environment variables are required to start the server. Set credentials in the MCP client's server environment to enable the relevant calls.

```json
{
  "mcpServers": {
    "dubai": {
      "command": "/absolute/path/to/MCP-Dubai/.venv/bin/python",
      "args": ["-m", "mcp_dubai"],
      "env": {
        "MCP_DUBAI_PULSE_CLIENT_ID": "your-client-id",
        "MCP_DUBAI_PULSE_CLIENT_SECRET": "your-client-secret",
        "MCP_DUBAI_WAQI_TOKEN": "your-waqi-token"
      }
    }
  }
}
```

| Variable | Default | Purpose |
|---|---|---|
| `MCP_DUBAI_PULSE_CLIENT_ID` | Unset | OAuth client ID for the six government dataset tools |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Unset | OAuth client secret, used with the client ID |
| `MCP_DUBAI_WAQI_TOKEN` | Unset | Token for the two air-quality reading tools |
| `MCP_DUBAI_PULSE_API_BASE` | `https://apis.data.dubai` | Government dataset API base URL |
| `MCP_DUBAI_DATA_PORTAL_BASE` | `https://data.dubai` | Public metadata portal base URL |
| `MCP_DUBAI_LOG_LEVEL` | `INFO` | Log verbosity |
| `MCP_DUBAI_HTTP_TIMEOUT` | `30.0` | HTTP timeout in seconds |
| `MCP_DUBAI_HTTP_MAX_RETRIES` | `3` | HTTP retry budget |

Request dataset access at [data.dubai](https://data.dubai) and a free WAQI token at [AQICN](https://aqicn.org/data-platform/token/). Keep credentials out of committed configuration files. The [credential guide](CREDENTIALS.md) covers setup and troubleshooting. `MCP_DUBAI_CALENDARIFIC_KEY` is reserved for a future holiday refresh integration and currently enables no additional tool.

## Data sources

| Source | Used for | Access |
|---|---|---|
| [Al-Adhan](https://aladhan.com/prayer-times-api), [Al-Quran Cloud](https://alquran.cloud/api) | Prayer times, calendar conversion, Quran text | Anonymous APIs |
| [CBUAE](https://www.centralbank.ae), [ExchangeRate-API](https://www.exchangerate-api.com/docs/free) | Exchange rates and currency conversion | Anonymous endpoints; CBUAE endpoints are undocumented |
| [FCSC Open Data](https://opendata.fcsc.gov.ae) | Federal dataset discovery | Anonymous CKAN API, recorded as blocked |
| [KHDA](https://web.khda.gov.ae/en/Resources/KHDA-data-statistics) | School reference data | Bundled sample |
| [Aviation Weather Center](https://aviationweather.gov/data/api/), [Open-Meteo](https://open-meteo.com/en/docs) | Airport and general weather | Anonymous APIs |
| [WAQI / AQICN](https://aqicn.org/api/) | Air quality | Free token |
| [OpenStreetMap Overpass](https://overpass-api.de), [Makani](https://www.makani.ae/) | Points of interest and address lookup | Anonymous services |
| [DFM](https://marketwatch.dfm.ae/), [Dubai City of Gold](https://dubaicityofgold.com/) | Market data and retail gold rates | Public JSON endpoints and HTML; DFM endpoints are undocumented |
| [data.dubai](https://data.dubai), [API gateway](https://apis.data.dubai) | Dataset discovery, DLD and RTA queries | Anonymous metadata; OAuth for dataset records |
| UAE federal holiday announcements | Public holidays | Bundled calendar with provisional dates marked |
| [Business knowledge packs](src/mcp_dubai/biz/_data/) | Business setup and reference guidance | Bundled JSON with source links and review metadata |

The former Dubai Pulse portal redirects to data.dubai. The project retains `PULSE` in credential variable names; its default API gateway is `apis.data.dubai`.

## Availability and limitations

The [September 5, 2026 audit](AUDIT-2026-09-05.md) records representative service checks, source verification, and remaining limits. These observations are a dated snapshot:

| Integration | Recorded result |
|---|---|
| CBUAE exchange rates | Working; 77 currencies returned |
| CBUAE base rate and four FCSC tools | Blocked by upstream access protection |
| data.dubai catalogue | Working; 610 datasets, 11 themes, and 75 issuers |
| DFM | Working; 458 securities, with names missing upstream |
| RTA GTFS archive | Intermittent access; retrieved archive still identifies the August 23, 2025 build |
| Other anonymous integrations | Successful representative calls for prayer times, Quran text, weather, currencies, gold, Makani, and Overpass |
| OAuth datasets and WAQI readings | Not live-tested in the audit without representative credentials |

The school dataset contains 16 selected records from an April 2026 snapshot. Nine records received targeted attribute corrections on September 5; school fees were not refreshed. Business costs and onboarding timelines can also be dated estimates, as indicated in the underlying records.

Clients should inspect `success` before using a result and read the returned `error` when a call fails. Credential and upstream failures include structured status and reason fields where applicable. Use `get_upstream_status()` for the recorded baseline and observations from tools used during the current session.

## Knowledge freshness

Freshness is tracked across **19 domains**: 16 JSON packs, `setup_advisor`, `data_analyst`, and `arabic_writer`. Successful business responses include a `knowledge` block; `get_knowledge_status()` exposes the complete registry.

| Field | Meaning |
|---|---|
| `knowledge_date` | Latest material update to the domain |
| `full_review_date` | Last complete domain review |
| `previous_knowledge_date` | Prior update date, when recorded for a targeted refresh |
| `last_refresh_scope` | Fields or topics covered by a targeted update |
| `volatility` | Review-budget category: high, medium, or stable |
| `verify_at` | Domain verification or source URL |
| `disclaimer` | Domain-specific scope and use limitations |

As of **September 5, 2026**, 18 domains have a latest update of `2026-09-05`; `arabic_writer` remains at `2026-04-13`. September updates were targeted: untouched fields and full-review dates retain their earlier verification scope. Detailed corrections and source links are in the [audit report](AUDIT-2026-09-05.md).

The freshness checker uses the last **full review**, with alerting budgets of 100 days for high-volatility domains, 190 for medium, and 365 for stable. Monthly prices, deadlines, and events still need review on their own schedules. Passing the age check does not establish that every fact is current.

```bash
python scripts/check_knowledge_freshness.py --strict
```

Verify the linked official requirements before relying on tax, visa, legal, or pricing guidance for a decision.

## Example queries

Ask a connected assistant to use MCP-Dubai for requests such as:

| Request | Relevant tools |
|---|---|
| What time is Fajr tomorrow in Dubai? | `prayer_times_for` |
| Find pharmacies within 500 metres of these coordinates. | `osm_search_poi` |
| Find public datasets about Dubai traffic. | `data_dubai_search` |
| Compare DMCC and IFZA for a consultancy with two visas. | `free_zone_details`, `compare_free_zones`, `setup_advisor` |
| Estimate corporate tax on AED 500,000 of taxable income and explain the QFZP information needed. | `corporate_tax_estimate`, `qfzp_check` |
| What is the attestation route for an Indian degree certificate? | `attestation_guide` |
| Estimate monthly living costs for a family of four. | `cost_of_living_overview`, `rent_estimate` |
| Prepare an Arabic/English letter addressed to a government department. | `business_letter_template`, `addressee_block` |

Tool selection and follow-up questions depend on the client. These examples describe lookups and estimates; the server does not submit applications or open accounts.

## Development

From the activated source environment created in [Quick start](#run-the-current-source):

```bash
python -m pip install -e ".[dev,data]"
make check
```

`make check` runs Ruff lint and format checks, strict mypy, pytest with coverage, and the informational freshness report. Use the `--strict` freshness command above to fail on overdue domains.

The [September 5 audit](AUDIT-2026-09-05.md#verification) recorded **967 passing tests** on each supported Python version tested, with **93.61% coverage** in the primary run. Packaging, type checks, lint, and security scans also passed; the audit documents their scope.

### Architecture

```text
src/mcp_dubai/
├── __main__.py       # stdio entry point
├── server.py         # feature mounts and diagnostic tools
├── _shared/          # HTTP, auth, discovery, response models, freshness
├── data/             # public APIs, OAuth integrations, reference datasets
├── biz/
│   ├── _data/        # 16 bundled JSON knowledge packs
│   └── ...           # 17 business features
└── agents/           # Arabic writing and data-analysis tools
```

Feature `tools.py` modules implement the logic; `server.py` modules expose FastMCP wrappers and register discovery metadata. Shared response models carry results, errors, and knowledge metadata. The source supports `fastmcp>=3.4.7,<4`; dependencies and supported Python versions are declared in [pyproject.toml](pyproject.toml).

Read [CONTRIBUTING.md](CONTRIBUTING.md) for feature conventions, tests, and the review checklist. Report reproducible errors or source corrections through [GitHub issues](https://github.com/mahdi-salmanzade/MCP-Dubai/issues).

## Project status

MCP-Dubai is **alpha software**. Version 0.4.0 is available in this repository. As recorded in the September 5 audit, PyPI publication remains at 0.2.0 and the validated [MCP Registry manifest](server.json) has no published registry record.

Current priorities:

- Publish the current source release to PyPI and the MCP Registry.
- Rebuild the KHDA dataset from an authoritative full workbook, including current fees.
- Add live contract checks for credential-dependent datasets and improve blocked or intermittent integrations.
- Extend government dataset coverage when access and schemas can be verified.
- Continue source-backed knowledge updates while preserving partial-review scope.
- Improve tool discovery tags and Arabic/English aliases.

## License and attribution

Licensed under [MIT](LICENSE). Upstream data remains subject to its publishers' terms and attribution requirements.

This is an independent project, unaffiliated with the Government of Dubai, the UAE government, or the agencies whose data it uses. See [DISCLAIMER.md](DISCLAIMER.md) for scope, data handling, and third-party rights.

Built with [FastMCP](https://gofastmcp.com). The country-focused server structure was inspired by [mcp-brasil](https://github.com/jxnxts/mcp-brasil).
