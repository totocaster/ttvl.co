---
title: "Ship the tool, not the agent"
date: 2026-08-29
category: thinking
---

Many AI products right now follow the same recipe: take one bounded capability, wrap a model and a chat loop around it, and call it an agent with a hip `.ai` domain. Truth is, it is still just a tool, only now with a probabilistic interface. It cannot decline the job or reach for another capability. The model inside is just parsing intent, not the smarts.

The more valuable thing to build is the opposite: the capability itself, exposed as a clear tool — a CLI, an API, a documented interface — that works for people and agents alike. I can run it by hand, and an agent can discover it and drive it as part of a larger job. One interface serves both. A general agent with [ten such tools](/project-humane/#digital-tools) can chain them toward a goal.

The division of labor is clean: the tool holds the mechanics, validation, and permissions; whoever drives it brings the intent, judgment, and orchestration. [AI coding took off because the tooling was already there](/notes/ai-coding-took-off-because-the-tooling-was-already-there/): tools built for people turned out to be exactly what agents needed.
