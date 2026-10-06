---
title: "One brain, five surfaces"
date: 2026-10-06T09:30:00+04:00
slug: studio-brain
category: progress
---

The studio system splits into layers. Home Assistant is the device layer: it talks to the Hue bridge, the Aqara hub, and later the IR blasters and printers, and it keeps the automations that must work when everything else is off.

Beside it runs a small service, the studio brain. It holds what Home Assistant doesn't: the 3D model and its 73 places, the catalog and its photos, Claude's readings and who confirmed them, the position of every Home Assistant entity in the model, and an event log. It mirrors Home Assistant's state and serves every screen in the studio: a wall screen, touch panels, phones, a Stream Deck, and a management site.

{{< figure src="/visuals/research/ambient-computing/2026-10-06-studio-brain.jpg" link="/visuals/research/ambient-computing/2026-10-06-studio-brain.jpg" alt="Diagram: devices in the studio feed Home Assistant as the device layer, which exchanges states and calls with the studio brain, which serves the wall screen, iPads, phones, a management site, and a Stream Deck, with Claude reading drawer photos" caption="How it fits together, from the studio-system mockup. Open the image for full size." loading="lazy" >}}

The brain runs on the Mac mini for now and moves to the NAS later. Keeping it apart from Home Assistant means an update to the brain never takes the lights down.
