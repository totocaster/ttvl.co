---
title: Refmode CLI
date: 2026-08-05
aliases:
  - /refmode/
description: "macOS CLI for switching Apple display reference modes"
project:
  year: 2026
  category: /project-humane
  description: "macOS CLI for switching Apple display reference modes"
  image: /visuals/project-thumbs/proj_refmode_cli.png
resources:
  - title: 'GitHub'
    url: 'https://github.com/totocaster/refmode'
---

[Refmode](https://github.com/totocaster/refmode) is a focused macOS command-line tool for discovering, reading, switching, and resetting the reference modes available on compatible Apple displays. It gives Terminal commands, scripts, and hardware controllers such as Stream Deck a direct way to select a display preset without opening System Settings or automating its interface.

Reference modes combine settings such as color gamut, white point, transfer function, luminance, and display processing. They are the presets shown in System Settings under Displays, rather than ColorSync ICC profiles.

## What it does

Refmode provides a small command surface for inspecting displays and changing one preset at a time:

| Command | What it does |
| --- | --- |
| `refmode doctor` | Checks whether the current Mac, display, and GUI session are ready without changing anything. |
| `refmode displays` | Lists every online display and identifies those that expose reference modes. |
| `refmode presets --display builtin` | Lists the factory and custom presets available for one display. |
| `refmode current --display builtin` | Prints the active preset. |
| `refmode set --display builtin "Photography (P3-D65)"` | Selects an exact preset by name. |
| `refmode reset --display builtin` | Restores the factory-default preset reported by the display. |
{.wide}

For durable automation, displays and presets can also be selected by stable IDs rather than names:

```sh
refmode --quiet set \
  --display uuid:<display-uuid> \
  --preset-id <preset-id>
```

This is useful for Stream Deck buttons, Keyboard Maestro, Raycast, Alfred, Shortcuts, Hammerspoon, LaunchAgents, or ordinary shell scripts. `--json` returns one versioned object for machine use, while `--quiet` suppresses successful output when only the exit status matters.

## Cautious by design

Changing a display mode is simple when everything is working, but a command intended for unattended automation also needs to fail predictably. Refmode refuses ambiguous display or preset matches rather than choosing the first one. It will not change a sleeping, inactive, mirrored, or unstable target, and it checks the display identity and topology again immediately before making a change.

An already-active preset succeeds without calling the setter. A real change makes one setter call, then reads the current preset back to verify the result. If the display changes or disappears during that process, Refmode reports the failure with a non-zero exit status instead of assuming the operation worked.

No command opens System Settings, takes focus, prompts for input, uses `sudo`, or requires Accessibility, Screen Recording, Automation, Input Monitoring, or network access.

## Private API boundary

macOS does not provide a public API for switching display reference modes. Refmode dynamically loads a small set of undocumented CoreDisplay functions and validates their availability and returned data at runtime. That keeps the private boundary isolated and lets the tool fail safely if Apple changes or removes the interface, but it also means compatibility can change with a macOS update.

Support is capability-based rather than tied to a hardcoded list of models. Refmode works when CoreDisplay exposes valid presets for an active display; `refmode doctor` is the quickest way to check a particular setup. Version 1.0 has been physically qualified on an Apple Silicon MacBook Pro with a built-in Liquid Retina XDR display.

## Get Refmode

Refmode requires macOS 13 or later and a compatible Apple display. Install the Apple Silicon release through my Homebrew tap:

```sh
brew tap totocaster/tap
brew install totocaster/tap/refmode
```

The source, releases, command reference, compatibility notes, and Stream Deck integration guide live on GitHub: [totocaster/refmode](https://github.com/totocaster/refmode).
