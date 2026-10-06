---
title: "Could AprilTags turn the Mega Alex into a screen?"
date: 2026-10-06T14:02:00+04:00
slug: tags-on-mega-alex
category: question
---

When the carts are assembled, the [Mega Alex](/research/ambient-computing/mega-alex/) is the biggest free surface in the studio: 118 × 118 cm of birch. With fiducial tags on it, the [projector and camera overhead](/research/ambient-computing/steerable-projector/) could find the surface, know exactly where it is, and use it as an ambient screen while I work there: a quick lookup, the steps of an instruction guide, whatever the work needs, without bringing a phone or a laptop to the table.

The candidate is [AprilTag 3](https://github.com/AprilRobotics/apriltag) with the tagStandard41h12 family, which its README calls "the correct choice" for the vast majority of applications. Tags at the four corners would give the surface's position even when hands or objects cover some of them. They would also tell the twin that the carts are assembled, so the layout switch could update itself.

Open: how large the tags need to be for a camera on the ceiling, whether projected light washes them out, and how to fix them to the birch top without glare.
