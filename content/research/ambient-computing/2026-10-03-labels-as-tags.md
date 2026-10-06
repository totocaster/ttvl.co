---
title: "Labels can double as Home Assistant tags"
date: 2026-10-03T17:25:00+04:00
slug: labels-as-tags
category: progress
---

Every QR code on a label encodes a Home Assistant tag URL. Once Home Assistant runs, scanning a label with its companion app fires a tag event that carries the address, so a scan can open that slot's page. An NFC sticker behind the label could do the same with a tap.

{{< figure src="/visuals/research/ambient-computing/2026-10-03-labels-rev-a.jpg" alt="A sheet of shelf-edge labels reading LA·a1 to LA·b4, each with the Lab letter, bay, shelf, shelf size, and a QR code" caption="Part of sheet REV.A: 48 × 16 mm strips sized for the front edge of an IVAR shelf." loading="lazy" >}}

A first print run, REV.A, was rendered and all 94 of its QR codes decoded correctly. Then printing went on hold with the rest of the [label question](/research/ambient-computing/which-label/).
