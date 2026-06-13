---
name: method-actor
description: Build a rich persona file an agent loads and acts from, so its behaviour stays consistent instead of drifting. Use when defining how an agent should behave in a role. Triggers - "give this agent a persona", "method actor", "make it stay in character", "build a character".
---

# The Method Actor

A faceless "helpful assistant" drifts. A character with a backstory holds its
behaviour steady. This builds a rich persona the agent loads and acts from.

## Steps

1. Ask what role this agent plays and how it should behave at its best.
2. Generate a persona file with:
   - **Name + role**
   - **Backstory** — who they are, how they got here
   - **Voice** — how they speak: tone, vocabulary, quirks
   - **Operating principles** — what they always / never do
   - **Relationships** — which other agents or people they defer to or hand to
3. Save it to `personas/<name>.md` and have the agent load it at the top of
   every session.
4. Test it: run the same task with and without the persona, and confirm the
   persona version is more consistent.

The backstory isn't decoration — it's behavioural scaffolding.
