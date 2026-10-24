"""Install the bundled common rules without replacing personal instructions."""
import argparse
import os
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone

BEGIN = "<!-- BEGIN CODEX COMMON OPTIMIZATION v1 -->"
END = "<!-- END CODEX COMMON OPTIMIZATION v1 -->"

def install(source, home):
    common = source.read_text(encoding="utf-8")
    if common.count(BEGIN) != 1 or common.count(END) != 1:
        raise ValueError("Invalid common rule markers")
    home.mkdir(parents=True, exist_ok=True)
    override = home / "AGENTS.override.md"
    if override.exists() and override.read_text(encoding="utf-8-sig").strip():
        raise ValueError("Non-empty AGENTS.override.md takes precedence; review it first")
    target = home / "AGENTS.md"
    old = target.read_text(encoding="utf-8-sig") if target.exists() else ""
    if old.count(BEGIN) != old.count(END) or old.count(BEGIN) > 1:
        raise ValueError("Ambiguous markers; no changes made")
    if BEGIN in old:
        start, stop = old.index(BEGIN), old.index(END) + len(END)
        if stop < start:
            raise ValueError("Invalid marker order")
        new = old[:start] + common.strip() + old[stop:]
    else:
        new = old + ("\n\n" if old and not old.endswith("\n\n") else "") + common.strip() + "\n"
    if old == new:
        print("Already current:", target)
        return
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        shutil.copy2(target, home / ("AGENTS.md.backup-" + stamp))
    fd, name = tempfile.mkstemp(dir=home, prefix=".agents-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(new)
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    print("Installed common optimization v1:", target)
    print("Start a new Codex session to load it.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    args = parser.parse_args()
    install(Path(__file__).with_name("COMMON.md"), args.codex_home)
