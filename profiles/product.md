# Product

Audience: an engineering or product review that will accept or reject a design. Typical file: a short proposal deck. White pages, not a dark hero. Liberation Sans, Noto Sans CJK SC, Liberation Mono for step numbers and identifiers.

Tokens: `profiles/product.json`. Accent `#0C6B66` is for the step index and one emphasized bar.

## Grammar

The title states the constraint, not the area: "The wait is one synchronous call", not "Overview of latency". Order the story as problem, evidence, options, the option you recommend, what you will not do, the decision you need.

Prefer a chart, a comparison, or a `steps` row over bullets. Architecture is editable shapes (the `steps` primitive), not a screenshot.

Name the non-goal. A design that returns success before the expensive work finishes is a product decision, and the slide should say whether the promise allows it.

## Forbidden

Hero gradients. "Overview / Benefits / Next Steps" as the outline. Mixed metaphor icons. ALL-CAPS eyebrows. A label shaped like "LATENCY — the tax call".

## Data

A trace, a p95, or a percentage is illustrative unless the prompt supplied a measurement. Say which environment (staging, production) and that it is a reconstruction when it is one.

## Chinese

Same primitives. Mono is only for identifiers and step numbers; sentences stay in the sans.
