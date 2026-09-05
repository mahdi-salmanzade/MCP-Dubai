# 🔑 API Keys & Credentials Setup Guide

**Every key in MCP-Dubai is provided by the user. We never embed, bundle, or share credentials.**

MCP-Dubai is designed so that each user obtains their own API keys. This keeps you in control of your data, respects the terms of every upstream provider, and means no single key gets rate-limited by community traffic.

---

## Quick Reference

| Env Variable | Required? | Cost | Unlocks | Time to Get |
|---|---|---|---|---|
| *(none)* | no | Free | **112 of 120 tools require no credentials**: public-data tools, every business advisor tool, both agent skills, and meta tools. Live availability still depends on each upstream. | None |
| `MCP_DUBAI_WAQI_TOKEN` | Optional | Free | Air quality readings (`air_quality_dubai`, `air_quality_by_coords`); the station list tool works without it | ~2 minutes |
| `MCP_DUBAI_PULSE_CLIENT_ID` | Optional | Free for entitled open datasets | Tier 1 tools: DLD real estate + RTA transport (6 tools); more agencies planned in Phase 8 | Manual approval; timing varies |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Optional | Free | (same as above, used together with CLIENT_ID) | (same as above) |
| `MCP_DUBAI_CALENDARIFIC_KEY` | Optional | Free tier | Future: automated holiday calendar refresh | ~2 minutes |

**Zero keys means 112 credential-free tools, not 112 guaranteed live tools.** The CBUAE base-rate tool and four FCSC tools are recorded as upstream-blocked as of 5 September 2026. They return structured errors, and adding a key does not bypass those blocks.

---

## Credential-Free Tools (no setup)

The server registers the following credential-free tools and knowledge modules with **zero configuration**. Upstream availability can still change.

**Anonymous upstreams:**
- **Al-Adhan**: Prayer times, Qibla direction, Hijri/Gregorian conversion
- **Quran Cloud**: Full Quran text and translations
- **CBUAE exchange rates**: Central Bank exchange rates (76 currencies against AED)
- **Aviation Weather**: METAR/TAF for all 6 UAE international airports
- **Open-Meteo**: Human-friendly weather and forecasts for UAE cities
- **ExchangeRate-API**: Everyday AED-base currency conversion
- **OSM Overpass**: Find nearby restaurants, pharmacies, mosques, ATMs, metro stations (22 categories)
- **DFM**: Dubai Financial Market index and stock quotes (undocumented, best-effort)
- **Makani**: Dubai Municipality geo-addressing (Makani numbers, reverse geocoding)
- **Dubai City of Gold**: DJG retail gold rates, AED per gram
- **data.dubai catalog**: Dataset search across 76 Dubai government entities (metadata only)
- **RTA GTFS archive**: Anonymous direct 7z download URL for the recorded static feed

**Recorded blocked anonymous upstreams:**
- **CBUAE base rate**: The InterestRate endpoint returns a structured `upstream_blocked` error
- **FCSC CKAN**: All four federal dataset and FCA-trade wrappers return structured `upstream_blocked` errors

**Bundled static/reference data:**
- **KHDA**: Curated Dubai private school snapshot by rating, curriculum, area, and fees
- **UAE Holidays**: Federal public holidays with provisional lunar date flagging

**Curated business knowledge (static, no API):**
- Setup Advisor, Free Zones, Visas, Banking, Founder Essentials, Tax Compliance, Compliance, Funding, Gov Portals, DCDE, Events, Parkin, IP/Trademark, Halal, Create Apps, Cost of Living, Tenancy
- 56 tools total. Every business response includes per-domain update metadata, including the prior date and targeted scope where declared; curated records include authoritative source URLs where available.

Just install and run:
```bash
uvx mcp-dubai
```

---

## 🌬️ WAQI Token (Air Quality)

**What it unlocks:** Real-time air quality data (AQI, PM2.5, PM10, NO₂, SO₂, CO, O₃) for Dubai monitoring stations.

**Cost:** A community API token is available without charge. Quotas and permitted uses are set by WAQI and may change, so review its current terms before deploying.

**How to get it:**

1. Go to [https://aqicn.org/data-platform/token/](https://aqicn.org/data-platform/token/)
2. Fill in your email address and a short reason (e.g. "Open-source Dubai MCP server")
3. Check your inbox and click the confirmation link
4. Copy the token string from the confirmation page

**Set it:**

```bash
# In your .env file or shell
export MCP_DUBAI_WAQI_TOKEN="your-token-here"
```

Or in Claude Desktop config:
```json
{
  "mcpServers": {
    "dubai": {
      "command": "uvx",
      "args": ["mcp-dubai"],
      "env": {
        "MCP_DUBAI_WAQI_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Usage terms to know:**
- Data cannot be sold or included in paid packages
- Data cannot be used in paid applications or services
- Data cannot be redistributed as cached or archived data
- Full terms: [https://aqicn.org/api/](https://aqicn.org/api/)

**Without this token:** The `air_quality_*` tools return a helpful error message pointing you to this setup guide instead of crashing.

---

## 🏛️ Dubai Pulse Credentials (Government Data)

**What it unlocks:** This is the big one. Dubai Pulse (now the data.dubai / apis.data.dubai gateway) is the unified API layer for Dubai government data.

**Available now** (built and wired in MCP-Dubai):

- **DLD**: Real estate sale transactions, Ejari rent contracts, RERA broker lookup (3 tools)
- **RTA**: Metro stations, bus routes, Salik tariff (3 tools; the GTFS download tool needs no credentials)

**Planned (Phase 8, not yet built)** so credentials alone will not surface these today:

- **DHA**: Health facilities and services
- **DEWA**: Utilities (electricity & water) data
- **DTCM**: Tourism statistics
- **DET/DED**: Business licenses, permits, economic activities
- **KHDA**: Live school data (upgrades the current curated snapshot)
- **Dubai Municipality**: Food safety, permits
- **Dubai Customs**: Trade data
- **Dubai Airports**: Flight information

**Cost:** Free for open datasets. Some commercial datasets are paid (not used by MCP-Dubai).

**How to get it:**

### Step 1: Create an account on data.dubai (formerly Dubai Pulse)

> **Portal migration (re-checked 2026-08-14):** the Dubai Pulse portal
> (www.dubaipulse.gov.ae) was decommissioned between December 2025 and
> January 2026 and now redirects to [https://data.dubai](https://data.dubai),
> run by the Dubai Data and Statistics Establishment. The API gateway moved
> to `apis.data.dubai` with the same `/open/{entity}/{dataset}-open-api`
> pattern; the legacy `api.dubaipulse.gov.ae` host still resolves, while
> `apis.data.dubai` is now the project default. Dataset slugs below are
> unchanged on the API side.

1. Go to [https://data.dubai](https://data.dubai)
2. Sign up / log in (you may need a UAE Pass or email registration)

### Step 2: Request access to open datasets

Each dataset has its own access request. Find the dataset in the data.dubai catalog and follow its access request flow, agree to terms, and submit.

Request only the datasets you intend to use. These are the exact gateway identifiers queried by the six credentialed tools in the current source tree:

| Tool data | Agency | Gateway dataset slug |
|---|---|---|
| Sale transactions | DLD | `dld_transactions-open-api` |
| Rent contracts | DLD | `dld_rent_contracts-open-api` |
| Brokers | DLD | `dld_brokers-open-api` |
| Metro stations | RTA | `rta_metro_stations-open-api` |
| Bus routes | RTA | `rta_bus_routes-open-api` |
| Salik tariff | RTA | `rta_salik_tariff-open-api` |

The client calls `https://apis.data.dubai/open/{agency}/{dataset-slug}`. Portal labels, access entitlements, and available datasets can change, so confirm each requested dataset in the current catalog rather than relying on an old Dubai Pulse `/data/...` URL.

### Step 3: Wait for approval

Approval timing and credential delivery vary by dataset and account. Follow the current instructions shown by data.dubai and do not plan around a fixed approval SLA. When issued, the API key maps to `client_id` and the API secret maps to `client_secret`.

### Step 4: Set your credentials

```bash
# In your .env file or shell
export MCP_DUBAI_PULSE_CLIENT_ID="your-api-key"
export MCP_DUBAI_PULSE_CLIENT_SECRET="your-api-secret"
```

Or in Claude Desktop config:
```json
{
  "mcpServers": {
    "dubai": {
      "command": "uvx",
      "args": ["mcp-dubai"],
      "env": {
        "MCP_DUBAI_PULSE_CLIENT_ID": "your-api-key",
        "MCP_DUBAI_PULSE_CLIENT_SECRET": "your-api-secret"
      }
    }
  }
}
```

### How authentication works under the hood

You don't need to do anything manually. MCP-Dubai handles token generation and refresh automatically. But for reference:

1. MCP-Dubai sends your `client_id` and `client_secret` to:
   ```
   POST https://apis.data.dubai/oauth/client_credential/accesstoken?grant_type=client_credentials
   Body: client_id={API Key}&client_secret={API Secret}
   ```
2. Receives a Bearer token and honours the returned `expires_in` value (falling back to 30 minutes if the field is absent)
3. Includes `Authorization: Bearer {token}` on every API call
4. Auto-refreshes when the token expires

**Without these credentials:** Tier 1 tools return a structured help message explaining how to get credentials. Nothing crashes.

### Troubleshooting

| Problem | Solution |
|---|---|
| Credentials were not issued | Check the request status in data.dubai and use the current support channel shown by the portal |
| Token expired errors | MCP-Dubai auto-refreshes. If persistent, check that your credentials are correct |
| 403 / Access Denied on a specific dataset | You need to request access to each dataset individually. Go to that dataset's page and click "Get Access" |
| Credentials work but no data | Some datasets are empty or rarely updated. Check `last_updated` in the response |

---

## 📅 Calendarific Key (Optional, Future)

**What it unlocks:** Automated refresh of UAE public holiday data. Currently, holidays are maintained as a curated static file with lunar dates flagged as provisional. A Calendarific key would enable automatic updates.

**Cost:** Free tier available (500 requests/month).

**How to get it:**

1. Go to [https://calendarific.com/signup](https://calendarific.com/signup)
2. Sign up with email
3. Copy your API key from the dashboard

**Set it:**

```bash
export MCP_DUBAI_CALENDARIFIC_KEY="your-key-here"
```

**This is not yet wired up.** It is reserved for a future quarterly refresh feature. The existing static holiday data works fine.

---

## ⚙️ Other Configuration (No Keys Required)

These environment variables tune MCP-Dubai's behavior but don't require any external signup:

| Variable | Default | What it does |
|---|---|---|
| `MCP_DUBAI_PULSE_API_BASE` | `https://apis.data.dubai` | Override the data.dubai API base URL |
| `MCP_DUBAI_DATA_PORTAL_BASE` | `https://data.dubai` | Override portal URL |
| `MCP_DUBAI_LOG_LEVEL` | `INFO` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MCP_DUBAI_HTTP_TIMEOUT` | `30.0` | HTTP timeout in seconds |
| `MCP_DUBAI_HTTP_MAX_RETRIES` | `3` | Retry budget for failed HTTP requests |

---

## 📋 Complete `.env.example`

See [.env.example](./.env.example) at the repo root for a copy-pasteable template. All variables are optional and documented inline.

---

## 🔒 Security Notes

- **Never commit your `.env` file.** It is already in `.gitignore`.
- **Never share your Dubai Pulse credentials.** They are issued to you personally and usage is tracked.
- **WAQI tokens are tied to your email.** Don't share them in public repos or issues.
- **MCP-Dubai never sends your credentials anywhere** except the official API endpoints listed above.
- **HTTP dependency logs are suppressed and credential-bearing query values are redacted** in both CLI and embedded use. Do not remove that protection or add raw request tracing in production.
- If you suspect a credential has been compromised, revoke it at the original provider and generate a new one.

---

## 💬 Need Help?

- **MCP-Dubai issues:** [github.com/mahdi-salmanzade/MCP-Dubai/issues](https://github.com/mahdi-salmanzade/MCP-Dubai/issues)
- **Dubai Pulse support:** `help@digitaldubai.ae`, 600 56 0000 (7 days/week, 7AM to 12AM GMT+4)
- **WAQI support:** [aqicn.org/api/](https://aqicn.org/api/)
