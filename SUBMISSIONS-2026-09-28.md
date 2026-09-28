# MCP-Dubai submission log — 28 September 2026

Recorded in Asia/Dubai time. Submissions were made through Chrome.
This log separates an acknowledged submission from an approved or published listing.

## Outcome

- **11 confirmed submissions:** one automatically approved listing, ten acknowledged submissions or pending reviews.
- **4 existing listings:** verified separately; not counted as new submissions.
- **3 unconfirmed attempts:** no explicit receipt captured; not counted as successful submissions.
- **6 blocked or unfinished forms:** recorded below with the observed reason.
- No payments were made. No paid listing was purchased.

## Public submission facts

- Project name: **MCP-Dubai** (also presented as MCP Dubai where a form required a display name).
- Canonical project URL: <https://github.com/mahdi-salmanzade/MCP-Dubai>.
- Public contact: **Mahdi Salmanzade**, **mahdi@clrtstudio.com**.
- Type: open-source Model Context Protocol server; MIT license; Python 3.11 or newer.
- Transport: a local stdio process, not a public hosted HTTP/SSE endpoint.
- Repository source: version **0.4.0**, **120 tools across 37 features**.
- Published PyPI package: version **0.2.0**, **91 tools**; do not describe that package as the 120-tool release.
- Use the repository's source-install instructions for the current catalogue.

## Confirmed submissions

| Portal | Result observed | Review information / reference |
| --- | --- | --- |
| [LibHunt](https://www.libhunt.com/r/MCP-Dubai) | **Automatically approved** and public detail page verified live. “Thanks for your submission! It’s been approved automatically.” | Listing ID `3892322`. A later description/homepage correction was acknowledged and is pending approval; see below. |
| [mcpservers.org](https://mcpservers.org/submit) | Submission success confirmation. | Review within two weeks; publication not confirmed. |
| [MCP.Directory](https://mcp.directory/submit) | “Server Submitted.” | Review within 24 hours; publication not confirmed. |
| [AgentNDX](https://agentndx.ai/submit?success=1) | Submission received. | Review within 48 hours; publication not confirmed. |
| [MCP Harbor](https://ai.mcpharbor.dev/servers/io.github.mahdi-salmanzade/mcp-dubai) | Entry created with **pending review** status. | Version `0.2.0` selected to match the published PyPI package. |
| [AgenticSkills](https://agenticskills.io/submit?type=mcp) | “MCP Server Submitted!” | Weekly triage; publication not confirmed. |
| [MCPizy](https://mcpizy.com/submit/thanks?ref=web_mukzm5l8_6attmx&tier=standard) | Thank-you confirmation. | Reference `web_mukzm5l8_6attmx`; Standard **FREE** tier; review up to four weeks. |
| [ProMCP](https://www.promcpservers.com/submit) | “Submission received.” | Site indicated reviewer notification and review in a few days; publication not confirmed. |
| [Dubai Startups Daily](https://dubaistartupsdaily.com/submit-story) | “Thanks! We’ll review your story and be in touch soon.” | Editorial submission acknowledged; no publication date promised. |
| [artificial.ae](https://artificial.ae/news/) | Tip modal: “Sent. We read every tip and email you if it lands.” | News tip acknowledged; publication not confirmed. |
| [DXBStart](https://www.dxbstart.com/submit/tip) | “RECEIVED — Your submission is with the desk.” | News tip acknowledged; user explicitly approved the mandatory weekly newsletter subscription before submission. |

The review windows above are the portals' stated expectations, not guarantees.
Only LibHunt displayed an approval confirmation during this session.

LibHunt imported a stale GitHub About description containing unsupported DHA/health language. A correction to describe the current 120-tool source release and local stdio transport, with the GitHub homepage, was submitted successfully. Its receipt confirmed that the suggested changes will be applied after approval. This is a pending edit to the same listing, not a twelfth destination. Updating GitHub About would also prevent the stale description from propagating elsewhere.

## Existing listings

These were already present and are not included in the 11 new submissions.

| Directory | Existing URL |
| --- | --- |
| MCP Market | <https://mcpmarket.com/server/dubai> |
| Glama | <https://glama.ai/mcp/servers/mahdi-salmanzade/MCP-Dubai> |
| MCP Market China | <https://mcpmarket.cn/server/69eb16b89b1bda315b835d39> |
| SafeMCP | <https://safemcp.info/s/mahdi-salmanzade/MCP-Dubai/> |

## Unconfirmed attempts — check before resubmitting

| Portal | Observed behavior | Status |
| --- | --- | --- |
| [aimcp](https://www.aimcp.info/en/submit) | Submitted and redirected to the homepage; no explicit receipt captured. Optional newsletter remained unchecked. A subsequent search for “MCP Dubai” returned no matching servers. | **Unknown**, not a confirmed failure or success; not resubmitted. |
| [Gulf Eye](https://gulfeyenews.com/submit-a-press-release/) | Initial attempt without an image returned “Only JPG and PNG images allowed.” A PNG rasterized from the repository's public `ae.svg` was then attached. After resubmission the form cleared, with no explicit receipt captured. | **Unknown** after corrected resubmission. |
| [MCPgee](https://www.mcpgee.com/contact) | Form reset or navigated to a GET query with no explicit receipt. | **Unknown**; the full query is intentionally omitted because it included contact data. |

Avoid immediate duplicate submissions to these three portals; first check for a receipt or listing.

## Blocked or unfinished forms

| Portal | Observed blocker / stopping point |
| --- | --- |
| [FindMCP](https://findmcp.app/submit) | Submission to `/api/submit` returned Chrome `ERR_BLOCKED_BY_CLIENT`. No bypass was attempted. |
| [MCP Vault](https://mcpvault.io/submit) | GitHub sign-in was required after page hydration. |
| [mcpservers.com](https://mcpservers.com/submit) | Required Google sign-in; distinct from the confirmed mcpservers.org submission. |
| [Cursor Directory](https://cursor.directory/plugins/new?type=mcp_server) | Redirected to login. |
| [10015 Product Finder](https://10015.io/product-finder/submit) | Required sign-in or registration. |
| [SaaSHub](https://www.saashub.com/services/submit) | User approved the Terms and Continue was clicked. The site rejected the submission: “No more submissions from github.com are allowed. Please contact us if you think this is a mistake.” No submission was completed. |

## Researched; not submitted

- **MCP.so:** observed a USD 39 paid submission option; not purchased.
- **[PulseMCP](https://www.pulsemcp.com/submit):** submissions shown as paused since September 3.
- **DubaiStartupMap:** required verified district/company information that was not available.
- **Analytics Insight UAE and ARN:** required a phone number that was not available for submission.
- **OpenHub, Product Hunt, and DevHunt:** authentication required; no submission completed.
- **Official MCP Registry:** UI search for `io.github.mahdi-salmanzade/mcp-dubai` returned “No servers found.” The repository manifest targets PyPI `0.4.0`, but that release was absent. No browser-only publishing action was performed.

## Reusable directory description

MCP-Dubai is an open-source Model Context Protocol server connecting AI assistants to Dubai and UAE public APIs, reference datasets, and curated business setup knowledge. It covers weather, currencies, prayer times, places, dataset discovery, and topics such as free zones, visas, banking, and company setup. It runs locally over stdio on Python 3.11+ and is MIT licensed. The current repository source includes 120 tools across 37 features; the published PyPI 0.2.0 release includes 91 tools. Results include source and freshness metadata where available, and some integrations require credentials or depend on upstream availability.

## Reusable UAE editorial pitch

**Suggested headline:** Open-source MCP-Dubai connects AI assistants with UAE data and business setup resources

MCP-Dubai is an open-source project that makes Dubai and UAE public data, reference datasets, and business setup knowledge accessible to AI assistants through the Model Context Protocol. Its current source includes 120 tools across 37 features, spanning practical information such as weather, currency conversion, free zones, visas, banking, and company setup. The project runs locally, is MIT licensed, and provides source and freshness metadata where available. It offers a concrete example of locally relevant infrastructure for developers building AI workflows around UAE information. Repository and installation instructions: https://github.com/mahdi-salmanzade/MCP-Dubai. Public contact: Mahdi Salmanzade, mahdi@clrtstudio.com.

This is suggested reusable copy, not a claim that every portal received identical wording. Do not present dated guidance as current official advice or imply a government affiliation.

## Follow-up checkpoints

- **September 29:** check MCP.Directory against its stated 24-hour review window.
- **September 30:** check AgentNDX against its stated 48-hour review window.
- **Early October:** check ProMCP, AgenticSkills, MCP Harbor, and the three editorial desks for responses.
- **October 12:** check mcpservers.org against its stated two-week review window.
- **October 26:** check MCPizy against its stated four-week review window, using its reference above.
- Check receipts and existing listings before repeating any unconfirmed attempt.
- Reconcile the source/PyPI release mismatch before pursuing the official registry or advertising a 120-tool PyPI install.

These are recorded checkpoints only; no reminders, automated follow-ups, or outgoing follow-up messages were scheduled by this log.
