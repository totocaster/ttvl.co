---
title: "Places get names I can say aloud"
date: 2026-10-19T22:20:13+09:00
slug: places-get-names
category: progress
---

The [first addresses](/research/ambient-computing/addresses/) gave every shelf and drawer a code. Now they have names I can say to someone: Bookshelf c3, Tower a4, Chest 3, Alex 2·3. The names follow what we already call the furniture, what it holds, or its shape. Each is unique in the studio, so the room doesn't need to be part of the address.

The grid stays the same: columns from the left as you face the unit, rows from the floor up. Where a shelf and a drawer share a position, they get a final letter: Bookshelf a2s for the shelf and a2d for the drawer.

{{< figure src="/visuals/research/ambient-computing/2026-10-19-place-names.png" alt="Elevation drawing of the Bookshelf, a tall IVAR on the Lab's left wall, as a grid of columns a to e and rows 1 to 5 with every cell named; c3 is filled in black, a2 and e2 each hold a drawer above an open shelf, and the Alex carts park in b1 and c1" caption="The Bookshelf on the Lab's left wall with every place named. Bookshelf c3 is filled; a2 and e2 each hold a drawer above an open shelf." loading="lazy" >}}

Underneath, Bookshelf c3 has the permanent ID `LA-c3`. That ID never changes, even if the shelf moves and is no longer the third shelf from the floor. The name can change without the system losing track of the place. Search takes either: `bookshelf c3` or `lac3`.
