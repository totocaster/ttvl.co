---
title: Project Humane Notebook System
---

The **Project Humane Notebook System (PHNS)** is an evolving framework for integrating digital and analog note-taking. It’s an exploration of how we can make the processes of capturing, searching, and exploring knowledge more flexible and enjoyable.

PHNS is a work in progress—a research project. It’s an adaptable, non-rigid approach to thinking, exploring, retrieving, and evolving ideas and thoughts, leveraging various mediums.

{{< toc >}}

## Philosophy

Analog and digital tools alone are not enough to fully support the way our brains think and work. Analog systems are less rigid and mirror the brain’s elasticity, supporting freeform thinking and idea development. Digital systems, while excellent for organization and scalability, can feel too structured for creative exploration. Further, I will argue the value of organization altogether too.

The system is software- and brand-agnostic, although it does have some preferences for certain types of analog tools over others.

## Loose Leafs

The notebook system, rather unfashionably, is based on loose leafs rather than bound notebooks. It’s a pragmatic decision central to the system’s flexibility and functionality rather than some kind of bias towards one type of stationery. The following sections will dive into the reasons behind this choice.

## Pagination

Since PHNS notebooks are unbound, traditional page numbers do not make much sense. However, having a way to identify a page and its place in a sequence is quite valuable for referencing as well as lookup purposes. Because of this, I use dates as a replacement for page numbers. No matter how leaves migrate between notebooks or archives, they remain easily searchable using dates, as dates are naturally ordered by timeline.

I find adding additional page numbers per day unnecessary since I rarely write more than half a dozen pages in one day—an amount that trivial to flip though. If you write more than a dozen pages per day, consider adding `/` and a page number so that the 24th page written on January 6, 2025, would be labeled `2025.01.06/24`.

I use a rubber stamp with changing dates to page my notes, but the simple act of writing the date on the trailing edge of the page would suffice.

## Grouping

I avoid grouping pages by project, topic, or "area" (per GTD). The loose leaf system is incredibly flexible when you want to migrate a page from one part of the notebook to another—or even to a dedicated notebook for logging or project ideas. However, I find excessive grouping creates silos of neglect, where notes that might be useful during casual browsing are overlooked.

## Peripheral Vision

Andy Matuschak coining [_Peripheral Vision_][pv]:

> My physical workspace is full of subtle cues. The books I read or bought most recently are lying out. Papers I’ve accumulated are lying in stacks on my desk, very roughly arranged by their relationship to each other. I notice a broken door every time I walk by it. These cues together give me a kind of “peripheral vision”: when I’m doing one thing, it’s easy for me to fluidly notice other nearby things. [...] Software systems, by contrast, often lack this kind of peripheral vision. [...] Digital task lists live in a dedicated app. I have no natural reason to look at the contents of that app.

PHNS is designed to keep notes you want to be reminded of in the notebook, no matter how old, small, or plain they are. Simply having the ability to indefinitely keep pages you want to be reminded during _browsing_ keeps them in your peripheral vision.

## Searching and Browsing

**Browsing** is an _open-ended activity_, more akin to walking in the city—exploring like a flâneur—whereas **searching** is _information retrieval_, a brisk walk to a set destination. We may browse with or without a goal, and plans may change as the process unfolds. However, when searching, we need information quickly and reliably.

PHNS is designed to excel at both. Browsing can be easily accomplished by flipping through the pages of a PHNS notebook in either direction, or even accidentally opening it to a random page every so often. Searching, on the other hand, is where its digital counterpart comes into play.

## Bridging to Digital

Whereas PHNS is primarily analog, its digital tools serve as an extension, enhancing searchability, archival integrity, and overall workflow.

I find ChatGPT-4 with vision to be an incredibly reliable transcription tool for PHNS. I have an open chat with the following prompt, and I simply upload photos from my notes for transcription:

> "You are an assistant who helps me manage my paper notes. You help me transcribe, describe and categorize my notes. Transcribe text from this loose leaf note. Include only text from the paper. Do not add your comments. If you find a typo in the transcribed word, please fix it, but do not change the sentence. When you see a list of items, please describe them. If the image has a sketch, describe what it is. Format everything in Markdown format, including tables."

The resulting text is copied and pasted into my note-taking app of choice along with the loose leaf photo—though you could discard it since you can always reprint the note. Loose leaf sheets are as printer-friendly as any standard piece of paper.

Having a completely digital version of the note opens several options for fast and precise searches. It could be as simple as searching for a keyword on a page or as advanced as storing notes in a database and performing AI-powered chat with it (e.g., Notion).

Since pages are unbound, you can use any flatbed or document scanner for digitization. Most high-end document scanners can adjust skew and run automations on scanned pages (e.g., Fujitsu/Ricoh ScanSnap series). You can simplify workflows by leveraging various automation tools.

## Soma.app

Some of you can already see dozens of automation and app opportunities. I’m one of those too. I'm working on a simple PHNS phone scanner app with a macOS counterpart—[**Soma**](/project-humane/soma/)—that provides a clean and simple way to take pictures of loose leaf sheets with corrected colors and skew adjustment, transcribe them into a digital version, identify the dates they were made (since all pages have dates), and then export the resulting text and image into a note-taking app of choice.

Perhaps one day Soma will become the ultimate knowledge base app. One can dream.

## Bridging back to Analog

Since loose leaves are essentially pieces of paper with a bunch of holes, they can work in printers as well as normal paper, which means you can print any content and put it in your notebook for further thinking or even as part of your peripheral vision. I usually print my highlights from books and essays I read online and then annotate them further with pencil in the notebook.

Abstract and "airy" photos also make a nice writing surface for thoughts or poetry.

## Linking

At a minimum, it’s possible to link notes using their dates. The system is designed to be compatible with **Zettelkasten**, where individual notes (or "leaves") can act as index cards. By adding page numbers after dates, you can ensure uniqueness.

However, I don’t find linking notes particularly useful. Instead, I prefer to **browse** my notes while thinking, allowing connections to emerge organically. When I need to retrieve specific information, I rely on **search**. (see "Searching and Browsing")

For focused work, you can also group notes into their own notebook or a “bunch” for an intense focus session. I do not keep bunched notes together for long time.

## Index

There’s no necessity to use a paper index in PHNS. Since all your notes will eventually be digitized and transcribed, they’ll become easily **searchable**, eliminating the need for a traditional paper index.

However, if you’re an analog purist, you can still maintain a traditional index on paper. Instead of listing page numbers alongside subjects, you could write the _dates_ you worked on them. This approach not only functions as an index but also transforms it into a concise **interstitial work log**.

## Archiving

Archiving pages in PHNS is very easy and painless since pages never get retired—they simply migrate from one place to another. Archiving is as simple as moving a leaf into a long-term binder. I use thick cardboard binders labeled `2023`, `2024`, `2025` for loose leafs from those years. All leaves are ordered chronologically, so even if a binder has hundreds of pages, they are extremely easy to find.

I never move pages to the archive without first scanning them. But you could do whatever you like, especially since moving pages back to an active notebook is so easy.

## Personalization

The canonical PHNS version is designed so that covers are also loose and **DO NOT** wrap the binder part of the notebook as Filofax, Davinci and Plotter planners. Any thick paper, cloth, leather, or fabric that protects the pages beneath and gives the notebook a pleasing tactile quality can serve as a cover.

I have two active notebooks: one with a 1mm yellow-tanned leather cover and another cut from a Freitag F08 DAN pouch I got for $5 because it had a broken zipper. All it takes to make new covers are scissors and a hole punch.

Since covers are essentially the first and last "pages," you can change them as frequently as you want without starting a new notebook. Or, you could keep the same one and have the "same" notebook for decades.

## Notebook Sizes

The size of the notebook is a very personal choice, and as long as you can get pages in the size you like, you're set. I like small notebooks, but pocket notebooks like Field Notes are too small for my taste, whereas A5 is a bit too big to carry everywhere. I was lucky to live in Japan and discover _System Techō_ (システム手帳) and its _bible_ size paper (also known as _Personal_ or _Compact_ in the Filofax universe; Plotter USA uses the same terminology as Japan).

In practice, anything that can be kept as a loose leaf notebook can work—even something as accessible and simple as [Kokuyo Campus][kc] loose leaf paper.

## Templates

I strongly encourage starting simple with plain, dotted, or ruled paper for everyday notebook use without overcomplicating the setup. For some niche types of logging and thinking, I’ve created several templates that can be printed on any standard printer. Most of these are tailored to my line of work.

- [Templates for General Use](/notebook-system/general-templates)
- [Templates for Analog Photography](/notebook-system/analog-photography-templates)

## Make Your Own

I have a separate guide on how to start and create your own PHNS notebook from scratch:

- [Make Your Own PHNS: A DIY Guide](/notebook-system/make-your-own-phns)

## Accessories

I have been using PHNS for more than two years at the time of publishing this, and I’ve accumulated some experience with it. Below are a few tips and tricks that I find useful when using the system:

- I glue a Traveler's Notebook **Pocket Sticker 006** onto the backside of the back cover. It needs a bit of trimming since the pocket is an inch or so taller than Bible-size paper.
- I keep a flat **TOHKIN PC-8S-3 Clip** on the back cover. It can act as a paper holder, transforming the back cover into a writing pad for loose leaf pages.
- I have a single **Coco Fusen Sticky Notes** (small size) glued on the inside of the front cover. They are useful for marking pages of importance in the notebook or book I'm reading.
- If you are an architect or designer, consider keeping a bunch of tracing paper in your notebook. You can layer it _in front_ of a base sketch to iterate easily and quickly. The rings will act as somewhat loose but reliable registration pins.

## Tips & Tricks

- I write only on one side of the paper. This makes leaves easy to scan and digitize.
- I do not mix notebook sizes; this gives me ultimate flexibility in migrating notes. Although some sizes like Japanese _Narrow_, _Bible_, and _HB-WA5_ are compatible with each-other.
- I tape all business cards I collect onto a page, adding the person's name and _where and how I met them_. For a goldfish like me, this has been invaluable.

## Companion Tools

Below are a few tools and toys I use with my PHNS notebook to make it more useful for my work and to add a touch of character:

- **Multi-pen** — I use a clear version of the Hi-Tech-C Coleto pen with black, red, highlighter, and mechanical pencil inserts.
- **Date Stamper** — Absolutely unnecessary, as writing a date on a page is trivial, but I like the uniform look of stamped dates.
- **Hole Punch** — For making inserts from collected matter. I have both heavy duty and travel versions.
- **Clear Pocket Insert** — For collecting memorabilia, event tickets, or tree leaves from the ground.
- **Canon ZINK Mini Printer** — For printing photos. ZINK (Zero Ink) paper requires no ink and has a sticker backing, making it easy to create photo sequences in the notebook or just print a nice moment to accompany a journal entry.
- **Glue Stick** - For things that do not have adhesive backing.

## Resources

Collection of links from and around the notebook system.

- [Make Your Own PHNS: A DIY Guide](/notebook-system/make-your-own-phns)
- [Templates for General Use](/notebook-system/general-templates)
- [Templates for Analog Photography](/notebook-system/analog-photography-templates)
- [Selection of some of my loose leafs](/leafs)

[pv]: https://notes.andymatuschak.org/Peripheral_vision
[kc]: https://www.kokuyostore.com/en/stationery/stationery-binder/stationery-binder-loose_leaf_paper
