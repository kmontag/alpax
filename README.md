# alpacks

[![PyPI - Version](https://img.shields.io/pypi/v/alpacks.svg)](https://pypi.org/project/alpacks)

---

`alpacks` allows you to generate custom Ableton Live packs. It supports
adding audio previews and Live 12 tags to the pack content.

Currently, only directory-based packs can be created - **generating
`.alp` files is not supported.**

Packs can be added to Live by dragging them into the Places pane.

_This is alpha software. It works for my use cases but hasn't been
extensively tested, and is missing plenty of functionality. APIs are
subject to change. Please submit issues and/or PRs if
you run into trouble._

## Installation

```console
pip install alpacks
```

## Usage

```python
from alpacks import DirectoryPackWriter
from time import time

with DirectoryPackWriter(
    "/path/to/output_dir",
    name="My Pack",
    unique_id="my.unique.id",
    # Tell Live to re-index the pack when it gets regenerated.
    revision=int(time()),
) as p:
    p.set_file("Preset.adg", "/path/to/Preset.adg")
    p.set_preview("Preset.adg", "/path/to/Preset.adg.ogg")
    p.set_tags("Preset", [
        ("Sounds", "Lead"),
        ("Custom", "Tag", "Subtag")
    ])

```

An async variant is also available:

```python
import asyncio
from alpacks import DirectoryPackWriterAsync
from time import time

async def run():
    async with DirectoryPackWriterAsync(
        "/path/to/output_dir",
        name="My Pack",
        unique_id="my.unique.id",
        revision=int(time()),
    ) as p:
        await p.set_file("Preset.adg", "/path/to/Preset.adg")
        # ...
asyncio.run(run())
```
