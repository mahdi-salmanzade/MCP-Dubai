# 🔑 API Keys & Credentials Setup Guide

**Every key in MCP-Dubai is provided by the user. We never embed, bundle, or share credentials.**

MCP-Dubai is designed so that each user obtains their own API keys. This keeps you in control of your data, respects the terms of every upstream provider, and means no single key gets rate-limited by community traffic.

---

## Quick Reference

| Env Variable | Required? | Cost | Unlocks | Time to Get |
|---|---|---|---|---|
| *(none)* | no | Free | **82 tools**: prayer times, Quran, exchange rates, schools, aviation weather, OSM POIs, holidays, every business advisor tool, and the meta tools | Instant |
| `MCP_DUBAI_WAQI_TOKEN` | Optional | Free | Air quality tools (`air_quality_dubai`, `air_quality_by_coords`, `air_quality_dubai_stations`) | ~2 minutes |
| `MCP_DUBAI_PULSE_CLIENT_ID` | Optional | Free | Tier 1 tools: DLD real estate, RTA transport, DHA health, DEWA, DTCM tourism, and more | ~14 days (approval) |
| `MCP_DUBAI_PULSE_CLIENT_SECRET` | Optional | Free | (same as above, used together with CLIENT_ID) | (same as above) |
| `MCP_DUBAI_CALENDARIFIC_KEY` | Optional | Free tier | Future: automated holiday calendar refresh | ~2 minutes |

**Zero keys = 81 fully working tools.** Keys only unlock additional features.

---

## Tier 0: No Keys Needed (works immediately)

These 9 API integrations and 6 business knowledge modules require **zero configuration**:

**Live APIs (anonymous):**
- **Al-Adhan**: Prayer times, Qibla direction, Hijri/Gregorian conversion
- **Quran Cloud**: Full Quran text and translations
- **CBUAE**: Central Bank exchange rates (76 currencies against AED)
- **FCSC CKAN**: UAE federal open data portal *(currently Cloudflare-blocked; returns structured error)*
- **KHDA**: Dubai private school search by rating, curriculum, area, fees
- **Aviation Weather**: METAR/TAF for all 6 UAE international airports
- **OSM Overpass**: Find nearby restaurants, pharmacies, mosques, ATMs, metro stations (22 categories)
- **UAE Holidays**: Federal public holidays with provisional lunar date flagging

**Curated business knowledge (static, no API):**
- Setup Advisor, Free Zones, Visas, Banking, Founder Essentials, Tax Compliance
- 15 tools total, all with source citations and knowledge freshness dates

Just install and run:
```bash
uvx mcp-dubai
```

---

## 🌬️ WAQI Token (Air Quality)

**What it unlocks:** Real-time air quality data (AQI, PM2.5, PM10, NO₂, SO₂, CO, O₃) for Dubai monitoring stations.

**Cost:** Free forever. Default quota is 1,000 requests per second.

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

**What it unlocks:** This is the big one. Dubai Pulse is the unified API gateway for Dubai government data. With credentials, MCP-Dubai can access:

- **DLD**: Real estate transactions, land registry, property developers, rental index
- **RTA**: Transport routes, bus stops, taxi stands, tram stations, metro data
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

### Step 1: Create a Dubai Pulse account

1. Go to [https://www.dubaipulse.gov.ae](https://www.dubaipulse.gov.ae)
2. Sign up / log in (you may need a UAE Pass or email registration)

### Step 2: Request access to open datasets

Each dataset has its own access request. Navigate to any dataset page and click **"Get Access"** then **"Request Permission"**, agree to terms, and click **"Send Request"**.

**Recommended datasets to request first** (all labeled "open", all free):

| Dataset | URL path on dubaipulse.gov.ae | Agency |
|---|---|---|
| Real estate transactions | `/data/dld-transactions/dld_transactions-open-api` | DLD |
| Land registry | `/data/dld-registration/dld_land_registry-open-api` | DLD |
| Property developers | `/data/dld-registration/dld_developers-open` | DLD |
| Free zone company licensing | `/data/dld-licenses/dld_free_zone_companies_licensing-open-api` | DLD |
| DLD projects | `/data/dld-registration/dld_projects-open-api` | DLD |
| Bus stops | `/data/rta-registers/rta_public_transportation_routes_stops-open` | RTA |
| Taxi stand locations | `/data/rta-registers/rta_taxi_stand_locations-open-api` | RTA |
| Private schools (live) | `/data/khda-registers/khda_dubai_private_schools-open-api` | KHDA |
| Business licenses | `/data/ded-licenses/ded_license_master-open` | DET/DED |
| Business permits | `/data/ded-permits/ded_permits-open` | DET/DED |
| DEWA customer data | `/data/dewa-general/dewa_customers_master_data-open-api` | DEWA |
| Dubai Pulse data catalog | `/data/smartdubai-general/smart_dubai_dubai_pulse_data_catalog_open-open-api` | Smart Dubai |

**Tip:** Request all of them in one sitting. Each takes about 30 seconds.

### Step 3: Wait for approval

Dubai Pulse states confirmation within 14 days. Open datasets are often approved faster. You will receive **two separate emails**:
- Email 1: Your **API Key** (this is your `client_id`)
- Email 2: Your **API Secret** (this is your `client_secret`)

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
   POST https://api.dubaipulse.gov.ae/oauth/client_credential/accesstoken?grant_type=client_credentials
   Body: client_id={API Key}&client_secret={API Secret}
   ```
2. Receives a Bearer token (valid ~30 minutes)
3. Includes `Authorization: Bearer {token}` on every API call
4. Auto-refreshes when the token expires

**Without these credentials:** Tier 1 tools return a structured help message explaining how to get credentials. Nothing crashes.

### Troubleshooting

| Problem | Solution |
|---|---|
| Never received the emails | Check spam/junk folders. Both emails come separately. Contact `help@digitaldubai.ae` or call 600 56 0000 |
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
| `MCP_DUBAI_PULSE_API_BASE` | `https://api.dubaipulse.gov.ae` | Override Dubai Pulse API base URL (for the data.dubai migration) |
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
- If you suspect a credential has been compromised, revoke it at the original provider and generate a new one.

---

## 💬 Need Help?

- **MCP-Dubai issues:** [github.com/mahdi-salmanzade/MCP-Dubai/issues](https://github.com/mahdi-salmanzade/MCP-Dubai/issues)
- **Dubai Pulse support:** `help@digitaldubai.ae`, 600 56 0000 (7 days/week, 7AM to 12AM GMT+4)
- **WAQI support:** [aqicn.org/api/](https://aqicn.org/api/)
