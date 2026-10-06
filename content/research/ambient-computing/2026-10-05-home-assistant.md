---
title: "Smart home is the low-hanging fruit"
date: 2026-10-05T10:20:00+04:00
slug: home-assistant
category: progress
---

The most ambient computing a studio already has is its smart home. Lamps, door and window sensors, and climate sensors sit in the walls and on the ceiling, quietly doing their job. I'll use Home Assistant integrations to talk to all of them, in two directions:

- Actions, such as turning on lights or running a scene.
- Reports, such as warnings about open doors and windows, and room temperatures.

The Hue Bridge Pro, with 16 lamps and 2 controls, and the Aqara Hub M200, with contact sensors on both doors and the WC window and a temperature and humidity sensor in the Lab, are installed in the Darkroom. Home Assistant itself will run on a Home Assistant Green.

{{< figure src="/visuals/research/ambient-computing/2026-10-05-touch-panel.jpg" alt="A tablet panel with scene keys, a grid of Lab lamp keys with brightness and color temperature, a room plan with lamp positions, air conditioner controls, and door states" caption="The touch panel in the studio-system mockup: scenes, every Lab lamp as a key, the room plan, the air conditioner, and doors and windows. Simulated; nothing is connected yet." loading="lazy" >}}
