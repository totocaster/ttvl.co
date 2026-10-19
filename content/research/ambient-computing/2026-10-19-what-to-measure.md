---
title: "The model can tell me what to measure next"
date: 2026-10-19T22:20:38+09:00
slug: what-to-measure
category: progress
---

I already [recorded the model's guesses](/research/ambient-computing/drawing-and-photos/) on its objects. Now the studio's dimensions, furniture, places, and lights live in one specification, and the recorded facts carry their source and status: measured, confirmed, taken from a product specification or the CAD drawing, derived, or estimated.

That makes the uncertainty useful. Running `just facts` lists the derived and estimated values: a list of things to check when I'm back in the studio with a tape measure. In the current build, that's 116 of 179 recorded facts.

{{< figure src="/visuals/research/ambient-computing/2026-10-19-facts.png" alt="179 squares, one for each fact in the studio specification: 63 filled in grays for the measured, confirmed, product, and CAD values, and 116 open squares for the derived and estimated ones" caption="Every recorded fact as one square: 2 measured, 34 confirmed, 16 from product specifications, and 11 from the CAD drawing. The open ones are still derived or estimated." loading="lazy" >}}

The Tower is a good example. Its two columns have four and seven shelves; those counts are confirmed. The heights of the intermediate shelves are still estimates from a photograph. The model can look quite convincing while that distinction remains unresolved.

```toml {title="storage.toml"}
[units.SB]
name = "Tower"
# …
levels_a_m = { value = [0.15, 0.44, 0.73, 1.21], status = "estimated", source = "Count confirmed; heights from photos" }
levels_b_extra_m = { value = [1.55, 1.89, 2.23], status = "estimated", source = "Count confirmed; heights from photos" }
```

When I measure one, I can replace the estimate, record where the measurement came from, and rebuild. The model and the viewers follow the same specification. The next visit to the studio now comes with a checklist.
