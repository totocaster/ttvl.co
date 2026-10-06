---
title: "Software gets malleable when describing it is enough"
date: 2026-10-06
category: thinking
---

LLM-based software engineering keeps pushing the threshold of implementation down. Small tools I would never have built, because building them cost more than they were worth, now take an afternoon. I describe what should happen, and the code gets written, run, and corrected.

It is still programming. I just do it in a different language: I describe the behavior, and the model translates it into a language the computer runs. [AI coding took off because the tooling was already there](/notes/ai-coding-took-off-because-the-tooling-was-already-there/), and now that tooling sits between my sentences and the machine.

Below that threshold, software starts to feel malleable. It stops being a product I adapt to and becomes material I can bend to fit a room, a habit, or a single afternoon's problem.

That is also what makes ambient computing approachable for one person. [Dynamicland](https://dynamicland.org/) needed a research group and a whole new system to make a room computational. But a room is full of small, specific needs that no product will ever cover: [a shelf light](/research/ambient-computing/find-on-phone/) that comes on when I ask where the soldering iron is, [a key](/research/ambient-computing/stream-deck/) that asks twice before switching the studio off while a door is open, [a wall screen](/research/ambient-computing/wall-screen/) that swings the model's door when the real one opens. None of these is worth a product. Each is worth an afternoon. I'm trying this in our studio now and logging it in [Ambient Computing](/research/ambient-computing/).

We don't have systems for this yet. Today it is a codebase, a 3D model, and a lot of glue. But if it materializes as some kind of harness, a place where you describe a behavior and the room takes it on, then given the right control surfaces and output devices it could start to feel like Dynamicland-level manipulation of the environment, without everyone having to build their own Realtalk.
