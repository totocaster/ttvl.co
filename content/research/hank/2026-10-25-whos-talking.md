---
title: "Who's talking?"
description: "OpenClaw decides who you are from how an app reaches the Gateway. On mine, I was two people."
date: 2026-10-25T19:04:41+09:00
slug: whos-talking
category: finding
image: /visuals/research/hank/2026-10-25-hank-senders.png
---

In OpenClaw's own interface, some of my messages showed up as someone else's. The ones I'd sent from [Hank](/research/hank/why-im-building-hank/) carried one name and avatar; the ones typed in the OpenClaw app carried another, on the other side of the conversation. I assumed Hank was missing a step: some way to tell the Gateway that the person on the iPhone is the same one at the desk.

There is no such step. An OpenClaw Gateway decides who a connection is from how it arrives, and it ignores what the app says about itself. Hank's name and client ID are never treated as identity. A route that proves who you are gives you your own profile. The Gateway's token, a password, or a device key gives a shared owner profile, the same one for every app that signs in that way. The rules are spread across OpenClaw's [multi-user](https://docs.openclaw.ai/concepts/multi-user), [user model](https://docs.openclaw.ai/concepts/user-model), and [operator scopes](https://docs.openclaw.ai/gateway/operator-scopes) pages; I checked them against the 2026.10.7 source.

| How the app reaches the Gateway | Who the Gateway says it is |
|---|---|
| Through Tailscale Serve, with Tailscale identity on | You, from your Tailscale login |
| Through a sign-in proxy such as Cloudflare Access | You, from the proxy's email |
| With the token, a password, or a device key | The shared owner, the same for every such app |
| With a device key alone, on a Gateway with roles | Refused |

On my Gateway, the Mac mini called nemo, I'm two people. Hank on the iPhone and the Mac, and the dashboard in my browser, all come through Tailscale and arrive as my own profile. The OpenClaw app on nemo connects over loopback with the token and arrives as the shared owner, named after the Mac's user account. OpenClaw never merges the shared owner with a person, so the two stay apart, and each sees the other as a stranger.

{{< drawing src="/visuals/research/hank/2026-10-25-two-of-me.svg" narrow="/visuals/research/hank/2026-10-25-two-of-me-narrow.svg" alt="Four apps on the left and how each reaches nemo. Hank on the iPhone, Hank on the Mac, and the dashboard come through Tailscale Serve and arrive as one profile, totocaster. The OpenClaw app on nemo connects over loopback with the token and arrives as Toto Tvalavadze, the shared owner, drawn dashed because it isn't a person." caption="Four apps, two people. The Gateway names each app by the route it took." >}}

The other half of the problem was in Hank. Every message the Gateway sends carries its sender: the profile, a name, a picture, and the app it came from. Hank ignored all of it and drew every message that wasn't the agent's as mine. That's harmless while I'm alone in a conversation, and wrong as soon as anyone else writes in it. A message from Ludo, or one relayed from Slack, would arrive in my coral bubble.

{{< compare first="/visuals/research/hank/2026-10-25-hank-senders.png" second="/visuals/research/hank/2026-10-25-hank-today.png" first-label="With senders" second-label="Hank today" ratio="1.6" alt="The same Hank conversation about a ryokan in Hakone, drawn two ways" caption="A conversation Ludo has joined. Today every message that isn't Hank's is drawn as mine. With senders, hers are gray on the left with her name and initial, and the one she typed in the dashboard says so." >}}

The fix on Hank's side starts with knowing who it is. After every connection it will ask the Gateway (`users.self`) and keep the answer: my own profile, the shared owner, or nobody. Settings shows it under the Gateway's name, and a Signed In As section names how the Gateway knows, or says plainly that the shared owner isn't a personal sign-in. Nothing there is a setting. Hank reads it each time it connects.

{{< figure src="/visuals/research/hank/2026-10-25-signed-in-as.png" alt="Two iPhone screens of Hank's Gateway page. On the left, Signed In As shows totocaster, verified by Tailscale. On the right, it shows Shared Owner, Toto Tvalavadze, not a personal sign-in, verified by nobody, with a note on how to sign in as yourself." caption="The Gateway page signed in as my own profile, and as the shared owner." loading="lazy" >}}

In the conversation, a message is mine when its profile is mine. Anyone else gets their name and picture in a gray bubble on the left, as in a group in Messages, and a small caption says when a message came from another app. On a Gateway with one person, the shared owner's messages are mine as well, with a small "Shared owner" caption: OpenClaw's docs say it doesn't count as a person. As soon as a second person has a profile, it becomes someone else again. When anyone besides me has written in a conversation, its details list the people who took part.

Two things Hank can't fix. The agent learns who I am but not which app I used, so it can't tell a message from my phone from one typed at the desk. And the OpenClaw app on nemo will stay the shared owner unless it, too, reaches nemo through Tailscale.

One result I didn't expect: a second person on one Gateway is closer than I'd assumed. Through Tailscale, Ludo's devices would arrive as her. OpenClaw still treats a Gateway as one trust domain, so that keeps our messages apart, not our data.
