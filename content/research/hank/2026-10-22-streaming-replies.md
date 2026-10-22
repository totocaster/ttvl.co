---
title: "Follow the first paragraph of a streaming reply, then let go"
description: "How Hank shows a reply while it streams, from Messages-style bubbles to a view that follows the first paragraph and stops."
date: 2026-10-22T18:32:20+09:00
slug: streaming-replies
category: finding
image: /visuals/research/hank/2026-10-22-reply-following.png
draft: true
---

[Hank](/research/hank/why-im-building-hank/) shows the agent's reply while it's being written. I want one I can glance at and use as it arrives, on a screen that stays calm. Six steps so far:

1. **Bubbles on both sides,** as in Messages, in the first build on 2026-10-10.
2. **Bubbles cramp an agent.** Its headings, lists, tables, and code break into pieces in a narrow column.
3. **Plain text for Hank.** On 2026-10-13 his replies went full width without a bubble, as in the ChatGPT and Codex apps; mine stayed bubbles. Then the type did the bubble's work: loose leading, modest headings, and a short hairline between his consecutive replies.
4. **Streaming that holds still.** Raw chunks came in bursts, half-written Markdown flashed its asterisks and pipes, and the transcript snapped to the end a line or five at a time. The fixes, picked in a lab and shipped on 2026-10-22: whole words fade in over 0.28 s, paced 0.45 s behind the network; a steady copy of the Markdown closes unfinished syntax, as Vercel's [remend](https://vercel.com/changelog/new-npm-package-for-automatic-recovery-of-broken-streaming-markdown) does, and holds tables until they're complete; one glide that can change its target replaces the snaps; and my question moves to the top, the reply writing below it.
5. **Too much still moved.** Every message I sent pushed the conversation up to the top of the screen.
6. **Follow the first paragraph, then stop.** In the version being built now, my bubble stays just above the composer. The view follows Hank's first paragraph and stops, never pushing my message off the top, and resumes only from the very bottom or the jump button. Pacing will track Hank's real token rate, keeping the fade close to what has arrived, and the same change smooths streaming on the Mac.

{{< reply-following alt="Four Hank screens at the end of the same reply about last night's backup. Raw chunks and Follow the end have scrolled the question off the top. Question on top holds it under the header, with the rest of the reply below the fold. First paragraph stopped once the first paragraph was written, with the question still in view and the jump button for the rest." caption="One simulated reply, arriving in uneven bursts. Raw chunks shows each chunk as it lands and snaps to the end; the other three fade whole words in at Hank's pace and differ only in where the view goes." >}}

Three rules come out of it. Follow what the reader is reading: the first paragraph tells me whether the answer is right, and then I set the pace. People ask other chat apps for the same ([Open WebUI](https://github.com/open-webui/open-webui/discussions/10725), [Codex](https://github.com/openai/codex/issues/34303)). Stop before my own words leave the screen, and resume only when I come back to the end. And keep the motion I didn't cause small: Google's [layout-shift metric](https://web.dev/articles/cls) counts it because it loses a reader's place, leaving out shifts within 500 ms of input; motion at the edge of vision [catches the eye and distracts](https://scholars.unh.edu/ccom/979) (Bartram, Ware, and Calvert, 2003); and Apple's guidelines advise against [motion on interactions that happen often](https://developer.apple.com/design/human-interface-guidelines/motion). A short fade on new words is enough; the lines above them stay put.
