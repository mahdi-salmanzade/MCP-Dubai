---
name: Broken upstream API
about: An MCP-Dubai tool is returning errors, empty results, or nonsense (likely upstream change)
title: "[API BROKEN] "
labels: ["bug", "upstream"]
assignees: ""
---

## Tool name

<!-- Which MCP-Dubai tool is failing? e.g., dld_search_transactions, prayer_times_for, cbuae_exchange_rates -->

## What you called

<!-- The exact arguments you passed. Paste the full call. -->

```python
tool_name(arg1=..., arg2=...)
```

## What you got

<!-- The error message, empty result, or unexpected output. -->

```
<paste here>
```

## What you expected

<!-- What the response should have looked like. -->

## Upstream endpoint (if known)

<!-- e.g., https://api.dubaipulse.gov.ae/open/dld/dld_transactions-open-api -->

## Have you verified the upstream is working?

- [ ] Yes, the upstream returns data when called directly
- [ ] No, the upstream is also returning errors
- [ ] Not sure how to check

## Notes

<!-- Anything else. We cannot fix upstream outages but we CAN update our integration when an endpoint moves, changes shape, or gets replaced. -->
