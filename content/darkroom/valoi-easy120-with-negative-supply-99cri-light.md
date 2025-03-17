---
title: 'Valoi easy120 with Negative Supply 99 CRI Light Source'
date: 2025-02-27
---

**Preamble**: Valoi's [easy35][ve35] system has been a godsend for 35mm black-and-white photographers. It's compact enough to [travel][travel] with, has simple controls, an integrated battery, and is incredibly easy to operate since it requires no alignment with a camera.

When Valoi announced [easy120][ve120], I immediately jumped on it without even checking the specifications, because of my great experience with the 35mm version.

The easy120 is certainly not just a larger version of the 35mm, however. Firstly, it doesn't come with a built-in battery. Secondly, it's enormous and not travel-friendly. However, the best parts of the system are still the tubes and generally its all-in-oneness.

But the showstopper for me is that my medium format shooting is mostly color, and the easy120 comes with a suboptimal light source.

**The Problem**: For color negative films, the Valoi easy120 light source causes a non-trivial amount of color casts in shadows and mid-tones that are difficult to adjust in post-production.

**The Solution**: Modify the Valoi easy120 to use a high-quality light source, reducing the need for extensive color processing after correction.

99 CRI light sources are uncommon, but the best-known one is available from Negative Supply: [4x5 Light Source Basic MK2 - 99 CRI][lsb], so I went with one.

Both Valoi and Negative Supply products have simple constructions with many 3D printed parts, making them easy to disassemble and investigate.

I designed an adapter that mounts directly onto the Negative Supply light source, uses a few parts from the Valoi carrier system, and enables the Valoi tube system to fit on top. Essentially, I combined the best of both products: a superior light source, a good carrier, and the alignment system.

![The VNS Adapter](/visuals/darkroom/vns_adapter_parts.jpeg)

I call it the **VNS Adapter**. You can grab STL files and print one for yourself too.

{{< download-section >}}
- [Download STL for printing](https://www.printables.com/model/1215933-vns-adapter-for-valoi-easy120-and-negative-supply)
{{< /download-section >}}

The VNS adapter can be printed in two parts. You need to disassemble the easy120 and reuse some of its parts, namely the carrier holder and the bearing balls that center the film holder in the carrier. Everything screws together using screws from both products. The only additional material needed is brass threaded inserts, but these are optional if you print the base plate with a smaller hole to screw directly into the plastic. Nothing is glued, so you can disassemble and reassemble both Negative Supply and Valoi again.

![The complete setup](/visuals/darkroom/vns_adapter_with_camera.jpeg)

Using a good light source did eliminate the annoying color casts in the shadows and made the work of Negative Lab Pro much easier (or so I believe).

The Negative Supply light source is not as bright as the Valoi light, so I have to use slower shutter speeds.

---

## F.A.Q.

**Does CRI really matter that much?**

I'm aware of discussions on the internet that CRI 95 is plenty enough, and I wish that was my experience too -- but it is not. In fact, the whole reason I had to come up with the VNS adapter was the frustration with the original Valoi setup, specifically its light source (an enclosed $35 CineStill CS-Lite). I was having quite a frustrating experience fixing different color casts in shadows, mids, and highlights.

**Does this VNS adapter with CRI 99 make a difference for black and white negatives?**

I do not think so. I use the factory easy35, which is also CRI 95+ rated, on all my black and white negatives and all look great. I wouldn't modify the original easy120 if I were shooting only black and white negatives.

**Is VNS compatible with duster and advancer units?**

No, not yet. I'll be working on an updated design so both can work in the future.

**Is this the best way to scan film?**

Who knows? For me, for the purpose of scanning entire rolls of film _fast_, it is. Would I use a photo in a book or exhibition scanned through this system? Perhaps, although I'd prefer to make a C-print that fits my flatbed and scan that, but that's not feasible when ingesting dozens of rolls into the archive.

**Any new features in plans, upgrades, or versions?**

I'm curious to make a true CRI 100 scanning setup. I have some ideas which I might come back to, but for now, my focus is making photographs. So [stay tuned][flaneur], but I'm not sure when.

[lsb]:https://www.negative.supply/shop-all/4x5-light-source-basic-99-cri?utm_medium=email&utm_source=customer_notification
[ve120]: https://www.valoi.co/easy120
[ve35]: https://www.valoi.co/easy35
[travel]: https://ttvl.co/darkroom/travel-dev-kit
[flaneur]: https://ttvl.co/newsletter