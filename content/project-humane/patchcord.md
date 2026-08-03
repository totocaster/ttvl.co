---
title: Patchcord
date: 2026-07-27
aliases:
  - /patchcord/
description: "agent-friendly development workflow for CircuitPython projects"
project:
  year: 2026
  category: /project-humane
  description: "agent-friendly development workflow for CircuitPython projects"
  image: /visuals/project-thumbs/proj_patchcord.png
---

[Patchcord](https://github.com/totocaster/patchcord) is an agent-friendly way to build [CircuitPython](https://circuitpython.org/) projects. It connects a normal project folder on the computer with the microcontroller board on the desk, providing one command-line interface for moving code onto the board, seeing what it does, and keeping track of the software and hardware that belong together.

The code remains ordinary Python and the board still runs ordinary CircuitPython. Patchcord takes care of the repetitive work around it and gives coding agents a predictable, cautious way to help with a physical project.

## What it does

- Keeps the code, libraries, and hardware description together in one project that can be backed up and returned to later.
- Finds the connected board, sends it the latest code, restarts it, and reports whether the program started successfully.
- Shows and saves messages from the board, making errors easier to understand and revisit.
- Manages CircuitPython libraries and diagnoses common problems with the project or connected hardware.
- Gives humans and coding agents the same cautious workflow, refusing to guess when several boards are connected.

## Why I made it

CircuitPython is appealing because it begins very simply: connect a small board, open the USB drive that appears, edit a Python file, and watch the physical thing change. I wanted to keep that immediacy.

As a project grows, however, its story gets scattered. The newest code might exist only on the board, the required libraries live somewhere else, wiring is documented in a note or not at all, and useful error messages disappear with the serial console. Returning to the project later means reconstructing how all of those pieces fit together.

Coding agents make that gap more obvious. An agent can write the code, but it also needs a safe way to identify the right board, put code onto it, observe the result, and leave enough evidence for the next attempt. It should not have to guess which removable drive to change or treat the board as the only copy of the work.

Patchcord keeps the complete project in a normal Git repository and treats the board as a deployment target. Code stays recoverable, libraries are declared, wiring assumptions are written down, and serial output becomes part of the project history. Humans and agents can then follow the same small loop: change the code, check the project, run it on the board, and inspect what happened.

## Common tasks

Start a project while a CircuitPython board is connected:

```sh
patchcord init sensor-display
cd sensor-display
git init
git add .
git commit -m "Initialize CircuitPython project"
```

Patchcord creates `device/code.py`, `hardware.yaml`, `requirements.txt`, `AGENTS.md`, and the supporting project files. From there, the main development loop is:

```sh
patchcord hardware validate --offline
patchcord deploy
patchcord monitor --seconds 10
```

The first command checks the project without touching the board. `deploy` copies the local application to `CIRCUITPY`, resets it, and checks the startup output. `monitor` then captures a bounded window of serial output. For a program that needs more time to start:

```sh
patchcord deploy --capture 15
```

Previous serial sessions remain available without reconnecting to the board:

```sh
patchcord logs
patchcord logs --tail 50
patchcord logs --since 10m
```

Patchcord can also interrupt or reset the running program and open an interactive REPL:

```sh
patchcord interrupt
patchcord reset --capture 10
patchcord repl
```

CircuitPython libraries are declared in `requirements.txt`, then installed on the selected board:

```sh
patchcord libs install
patchcord libs freeze
```

When a project or board is not behaving as expected, `doctor` checks the setup without changing it. JSON output makes the same information available to scripts and agents:

```sh
patchcord doctor
patchcord doctor --json
patchcord status --json
```

If several boards are connected, the target can be made explicit:

```sh
patchcord \
  --mount /Volumes/CIRCUITPY \
  --port /dev/cu.usbmodem101 \
  deploy
```

## A project that describes itself

`hardware.yaml` records the parts and connections that exist outside the code:

```yaml
schema_version: 1

board:
  id: adafruit_feather_rp2040

parts:
  oled:
    kind: display
    model: SSD1306 OLED
    interfaces:
      - kind: i2c
        bus: default
        address: 0x3c
    libraries:
      - adafruit_ssd1306
```

Offline validation catches broken endpoint references, invalid I²C declarations, and libraries missing from `requirements.txt` without connecting to or interrupting the board. The file does not try to become a universal component database; it only describes the project-specific facts that code cannot discover on its own.

## Built for agents, cautious around hardware

Running `patchcord init` creates an `AGENTS.md` alongside the project. It teaches coding agents how to work with the board safely, keep the Git-managed local files authoritative, and use small commits as recoverable checkpoints while the physical project changes.

Most bounded commands also support deterministic `--json` output with stable result and error codes. Automatic discovery refuses to guess when more than one drive or serial port is available, protected files such as `boot.py` and `settings.toml` require explicit permission, and deployment never deletes unrelated files already on the board.

Patchcord coordinates existing CircuitPython tools rather than replacing them. CircuitPython remains authoritative for the board runtime, `circup` handles libraries, and `pyserial` handles serial communication. Patchcord adds the project-level workflow, safety checks, logs, and machine-readable interface around them.

## Current scope

Patchcord currently supports CircuitPython boards that expose the standard `CIRCUITPY` USB drive and serial console. In v0.3, interactive REPL, deployment, monitoring, serial control, library management, and offline hardware validation are available. Bounded code execution and connected pin and I²C probes remain unavailable because the pinned execution backend did not pass Patchcord's isolation and reset checks.

## Get Patchcord

Patchcord requires Python 3.11 or newer and a board with CircuitPython already installed.

Install the latest release from PyPI:

```sh
uv tool install patchcord
```

The source, releases, full command reference, and `hardware.yaml` specification live on GitHub: [totocaster/patchcord](https://github.com/totocaster/patchcord).
