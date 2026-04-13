# Disclaimer

Hey there, and welcome to **MCP-Dubai**. Before you dive in, please take a minute to read this. It's short, it's friendly, and it explains what this project is (and isn't).

## 1. What this project is

MCP-Dubai is an **independent, community-driven** open-source project. It is a Model Context Protocol (MCP) server that provides a unified interface to public Dubai and UAE government data sources.

It is **not affiliated with, endorsed by, sponsored by, or officially connected to** the Government of Dubai, the United Arab Emirates, or any specific authority, including but not limited to DLD, RTA, KHDA, DSC, DHA, DET, DEWA, CBUAE, Dubai Pulse, or Dubai Now. We're just builders who want the region's open data to be easier to work with.

This project is inspired by and modeled on [mcp-brasil](https://github.com/jxnxts/mcp-brasil).

## 2. Public APIs only

MCP-Dubai only consumes APIs and datasets that are **already publicly available**. We do not:

- Scrape content behind authentication walls
- Circumvent rate limits, captchas, or access controls
- Access private, internal, or restricted endpoints
- Redistribute paywalled or licensed data

If an endpoint requires a free public API key, you bring your own.

## 3. We don't own the data

All data returned by this server is the property of its **respective publisher**. We just provide a convenient interface on top. We make no claim to the underlying datasets, APIs, or any rights associated with them.

## 4. Best-effort accuracy

Upstream APIs change. They get deprecated, renamed, rate-limited, or simply break, sometimes without warning. We do our best to keep integrations fresh, but we cannot guarantee that every tool will return correct, complete, or up-to-date results at every moment.

**If something looks wrong, please don't assume malice. Open a GitHub issue.** We're a community project and we rely on you to tell us when things break.

## 5. No warranty (in plain English)

This software is provided **"as is"**, under the MIT License. It might have bugs. It might go down. It might give you the wrong answer. Use it at your own risk, and don't build life-or-death systems on top of it without independent verification. We're not liable for anything that happens as a result of using it.

## 6. Trademarks and names

Names like **Dubai Pulse, RTA, DLD, KHDA, DSC, DHA, DET, DEWA, CBUAE**, and any related logos or marks, belong to their respective owners. We use these names **only nominatively**, that is, to identify which public data source a given tool talks to. No endorsement or partnership is implied.

## 7. Your compliance responsibilities

When you use MCP-Dubai, **you** are responsible for:

- Complying with each upstream API's Terms of Service
- Complying with **Dubai's Data Law (Law No. 26 of 2015)** and any applicable UAE regulations
- Using retrieved data lawfully in your own applications

We provide the pipe. What flows through it and what you do with it is on you.

## 8. Personal data

MCP-Dubai is a **stateless proxy**. It does **not** collect, store, log, or transmit personal user data. Your queries go to the upstream API and the response comes back. That's it. No analytics, no tracking, no telemetry baked in.

## 9. Reporting a broken API or bad result

Found a tool that's returning errors, empty results, or nonsense? Please help us fix it:

1. Go to the GitHub repo issues page: **https://github.com/intzero/MCP-Dubai/issues**
2. Click **"New Issue"**
3. Include:
   - The **tool name** (e.g., `rta_nol_balance`)
   - The **error message** or unexpected output
   - A **minimal reproduction** (the arguments you passed)
   - Optionally, the upstream endpoint if you know it

Heads up: we **cannot fix upstream outages**. If RTA's API is down, it's down. But we *can* update our integration when an endpoint moves, changes shape, or gets replaced.

## 10. Removal requests

If you represent a Dubai or UAE government agency and you'd like your API removed from this project, or you have concerns about how it's being used, we'd love to hear from you. Please open a GitHub issue or contact the maintainers directly. We'll respond promptly and in good faith.

---

Thanks for reading, and thanks for being part of the open-data community.

> هذا المشروع مبادرة مجتمعية مفتوحة المصدر، مرحبًا بمساهماتكم
