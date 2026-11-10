FILENAME = "deck.pptx"

PLAN = {
    "file_type": "pptx",
    "domain": "product",
    "language": "en",
    "title": "Send-invoice p95 is stuck on a synchronous tax call",
    "author": "Northwind Billing",
    "slides": [
        {
            "primitive": "cover",
            "kicker": "Proposal",
            "title": "Send-invoice p95 is stuck\non a synchronous tax call",
            "subtitle": "Northwind Billing · payments path · November 2026",
            "meta": ["Design review", "Staging reconstruction"],
        },
        {
            "primitive": "action",
            "title": "The wait is one downstream call, not the whole API",
            "paragraphs": [
                "In the staging traces from the week of 3 November, the median response is fine and the p95 is not. The tail is a single synchronous call to the tax engine, made after the invoice is valid and before we will say it was sent.",
                "Auth, the invoice load, and the mail handoff are each under 200 ms. PDF render is the next largest piece, and even cutting it in half would leave the p95 above the 900 ms gate this review is being asked to set.",
            ],
            "illustrative": True,
            "source": "Staging traces, week of 3 Nov 2026, reconstructed for this review",
        },
        {
            "primitive": "chart",
            "title": "Tax is 1.6 seconds of a 2.4 second response",
            "chart_type": "column",
            "unit": "milliseconds, staging p95",
            "categories": ["Auth", "Load", "Tax", "PDF", "Mail"],
            "series": [{"name": "p95", "values": [80, 140, 1600, 420, 160]}],
            "emphasis_index": 2,
            "number_format": "0",
            "insight_lead": "Only the tax bar can move the target.",
            "insight": "The other four steps sum to 800 ms. A 900 ms p95 is impossible while tax stays on the request as a remote call. Local evaluation of a compiled rule set is the change that has enough room.",
            "illustrative": True,
            "source": "Illustrative reconstruction of one staging profile, not a production SLO",
        },
        {
            "primitive": "comparison",
            "title": "Three designs, and only one keeps the word “sent”",
            "columns": [
                {
                    "title": "Leave the call",
                    "points": [
                        "No new failure mode.",
                        "The p95 stays near 2.4 s.",
                        "A spinner does not change the promise.",
                    ],
                },
                {
                    "title": "Return before tax",
                    "points": [
                        "The button feels immediate.",
                        "We would say sent while the amount can still change.",
                        "Credit notes become the common path.",
                    ],
                },
                {
                    "title": "Evaluate locally",
                    "points": [
                        "Rules compile per jurisdiction.",
                        "The amount is known before send.",
                        "A miss still calls the engine once.",
                    ],
                    "recommended": True,
                },
            ],
            "illustrative": True,
            "source": "Design review. Latencies above are the staging sketch",
        },
        {
            "primitive": "steps",
            "title": "The request path after the change",
            "steps": [
                {
                    "title": "Load the rules",
                    "detail": "Compiled set for that jurisdiction. TTL 15 minutes. Keyed by version, not by clock alone.",
                },
                {
                    "title": "Evaluate here",
                    "detail": "In process, on the request. Target under 80 ms when the set is warm.",
                },
                {
                    "title": "Refill on a miss",
                    "detail": "One remote call, then the invoice stores the rule version it used.",
                },
                {
                    "title": "Then render",
                    "detail": "PDF and the mail handoff stay after the amount is fixed.",
                },
            ],
        },
        {
            "primitive": "table",
            "title": "What has to be true before anyone builds it",
            "columns": ["Question", "Owner", "Gate"],
            "rows": [
                ["Cache key", "Tax", "Jurisdiction and rule version"],
                ["Invalidation", "Tax", "A new version drops the set"],
                ["Cold miss", "API", "Under 400 ms, or we do not ship"],
                ["Audit", "Ledger", "The invoice records the version"],
            ],
            "widths": [1.2, 0.8, 2.2],
            "illustrative": True,
            "source": "Build checklist. The 400 ms miss budget is a proposal, not a measurement",
        },
        {
            "primitive": "close",
            "kicker": "Decision",
            "title": "Approve local evaluation, and the gate that can kill it",
            "decisions": [
                {
                    "label": "Approve",
                    "text": "Compile tax rules per jurisdiction, evaluate them on the request, and stamp the rule version on the invoice. Staging p95 must come in under 900 ms.",
                },
                {
                    "label": "Do not",
                    "text": "Do not change the button copy to “sent” while tax is still running. Do not treat a spinner as the fix.",
                },
            ],
        },
    ],
}
