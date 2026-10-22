---
title: "Displaying long replies"
description: "How Hank's reply view has changed to reduce jitter and unwanted scrolling."
date: 2026-10-22T18:32:20+09:00
slug: streaming-replies
category: finding
image: /visuals/research/hank/2026-10-22-reply-following.png
---

[Hank](/research/hank/why-im-building-hank/) shows the agent's reply while it's being written. I'm trying to make long answers readable as they arrive, without jitter or scrolling that makes me lose my place.

The first build, on 2026-10-10, used bubbles on both sides, as in Messages. The narrow column cramped Hank's headings, lists, tables, and code.

On 2026-10-13, I removed the bubble around his replies and gave them the full width; mine stayed in bubbles. Looser line spacing, modest headings, and a short hairline between consecutive replies kept his messages distinct.

Streaming brought another problem. Text arrived in bursts, unfinished Markdown flashed its asterisks and pipes, and the conversation jumped to the end several lines at a time.

On 2026-10-22, I changed how replies stream: whole words fade in over 0.28 s, paced 0.45 s behind their arrival. The renderer closes unfinished Markdown, as Vercel's [remend](https://vercel.com/changelog/new-npm-package-for-automatic-recovery-of-broken-streaming-markdown) does, and holds tables until they're complete. A continuous glide replaces the jumps, and my question moves to the top with the reply below it.

That reduced the jitter, but every message I sent still pushed the conversation to the top of the screen.

Then I modified the view to leave my bubble just above the composer. It followed Hank's first paragraph, then stopped, keeping my question on screen. Automatic following resumed only when I scrolled to the bottom or used the jump button. Pacing adapted to the rate at which text arrived, and the same change smoothed streaming on the Mac.

{{< reply-following alt="Four Hank screens at the end of the same reply about last night's backup. Raw chunks and Follow the end have scrolled the question off the top. Question on top holds it under the header, with the rest of the reply below the fold. First paragraph stopped once the first paragraph was written, with the question still in view and the jump button for the rest." caption="One simulated reply, arriving in uneven bursts. Raw chunks shows each chunk as it lands and snaps to the end; the other three fade whole words in at Hank's pace and differ only in where the view goes." >}}

The working rule is to let me start reading, then leave the pace to me. Reports from [Open WebUI](https://github.com/open-webui/open-webui/discussions/10725) and [OpenAI's desktop apps](https://github.com/openai/codex/issues/34303) describe the same problem: automatic scrolling carries the beginning of a long answer out of view.

The broader guidance supports keeping movement small. Google's [layout-shift guidance](https://web.dev/articles/cls) describes how unexpected shifts lose a reader's place; Bartram, Ware, and Calvert's [motion study](https://scholars.unh.edu/ccom/979) shows how movement draws attention, especially at the edge of vision; and Apple advises restraint with [motion in frequent interactions](https://developer.apple.com/design/human-interface-guidelines/motion). My aim is a short fade on new words, with the lines I'm already reading staying put.
