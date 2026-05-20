#!/usr/bin/env python3
"""
sdd — Spec-Driven Development CLI
Monitora o estado dos sprints em tempo real lendo .claude/context/
"""

import sys
import time
import argparse
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import re

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.console import Group
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.spinner import Spinner

# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────

CONTEXT_DIR  = Path(".claude/context")
SPRINTS_FILE = CONTEXT_DIR / "sprints.md"
CURRENT_FILE = CONTEXT_DIR / "current.md"
ACTIVITY_LOG = CONTEXT_DIR / "activity.log"
REFRESH_RATE = 1.5

# Mapa de status → (label, style)
STATUS = {
    "AGREED":      ("✓ AGREED",   "bold green"),
    "VIOLATED":    ("✗ VIOLATED", "bold red"),
    "pending":     ("—",          "dim"),
    "in_progress": ("",           "bold yellow"),   # spinner inline
    "done":        ("✓ done",     "bold green"),
    "verified":    ("✓ verified", "bold green"),
    "failed":      ("✗ failed",   "bold red"),
    "passed":      ("✓ passed",   "bold green"),
    "blocked":     ("⊘ blocked",  "bold red"),
    "—":           ("—",          "dim"),
}

# Spinner frames estilo uv
UV_FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

console = Console()
_frame_idx = 0
_frame_lock = threading.Lock()


def next_frame() -> str:
    global _frame_idx
    with _frame_lock:
        f = UV_FRAMES[_frame_idx % len(UV_FRAMES)]
        _frame_idx += 1
    return f


# ─────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────

def parse_sprints(path: Path) -> dict:
    result = {"feature": "—", "prd": "—", "updated_at": "—", "sprints": []}
    if not path.exists():
        return result

    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        if line.startswith("**Última atualização**"):
            result["updated_at"] = line.split(":", 1)[-1].strip()
        elif line.startswith("**Feature**"):
            result["feature"] = line.split(":", 1)[-1].strip()
        elif line.startswith("**PRD de referência**"):
            result["prd"] = line.split(":", 1)[-1].strip().strip("`")

    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 6:
            continue
        if parts[0] in ("#", "---", "—") or re.match(r"^-+$", parts[0]):
            continue
        try:
            num = int(parts[0])
        except ValueError:
            continue
        result["sprints"].append({
            "num":      num,
            "goal":     parts[1] if len(parts) > 1 else "—",
            "contract": parts[2] if len(parts) > 2 else "—",
            "build":    parts[3] if len(parts) > 3 else "—",
            "qa":       parts[4] if len(parts) > 4 else "—",
            "score":    parts[5] if len(parts) > 5 else "—",
            "cost":     parts[6] if len(parts) > 6 else "—",
        })
    return result


def parse_current(path: Path) -> dict:
    result = {"sprint_num": "—", "goal": "—", "next_step": "—",
              "done": [], "updated_at": "—"}
    if not path.exists():
        return result

    section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("**Atualizado em**"):
            result["updated_at"] = s.split(":", 1)[-1].strip()
        elif s.startswith("**Goal**"):
            result["goal"] = s.split(":", 1)[-1].strip()
        elif s.startswith("**Próximo passo**"):
            result["next_step"] = s.split(":", 1)[-1].strip()
        elif s.startswith("## Sprint Atual"):
            m = re.search(r"#(\d+)", s)
            if m:
                result["sprint_num"] = m.group(1)
        elif s == "## O que foi feito até aqui":
            section = "done"
        elif s.startswith("## ") and section == "done":
            section = None
        elif section == "done" and s.startswith("- "):
            result["done"].append(s[2:])
    return result


def parse_activity_log(path: Path, n: int = 8) -> list[dict]:
    """
    Lê as últimas N linhas do activity.log.
    Formato: AGENT|sprint-N|event|timestamp|message
    """
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        parts = line.split("|", 4)
        if len(parts) < 5:
            # linha livre — mostra como está
            entries.append({"agent": "—", "sprint": "—",
                             "event": "info", "ts": "", "msg": line})
        else:
            entries.append({
                "agent":  parts[0],
                "sprint": parts[1],
                "event":  parts[2],
                "ts":     parts[3],
                "msg":    parts[4],
            })
        if len(entries) >= n:
            break
    return list(reversed(entries))


def get_cost() -> str:
    """
    Extrai o custo total da sessão atual via `claude /usage`.
    Retorna string como '$3.58' ou '—' se não disponível.
    """
    try:
        result = subprocess.run(
            ["claude", "/usage"],
            capture_output=True, text=True, timeout=3
        )
        output = result.stdout + result.stderr
        m = re.search(r"Total cost:\s+\$([0-9]+\.[0-9]+)", output)
        if m:
            return f"${m.group(1)}"
    except Exception:
        pass
    return "—"


# ─────────────────────────────────────────────
# Componentes visuais
# ─────────────────────────────────────────────

def render_status(value: str, animate: bool = True) -> Text:
    if value == "in_progress" and animate:
        frame = next_frame()
        return Text(f"{frame} running", style="bold yellow")
    label, style = STATUS.get(value, (value, "default"))
    return Text(label, style=style)


def build_sprints_table(sprints: list) -> Table:
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#",        style="bold cyan", width=3,  no_wrap=True)
    table.add_column("Goal",     style="white",     ratio=3, no_wrap=True, overflow="ellipsis")
    table.add_column("Contract", width=14, no_wrap=True)
    table.add_column("Build",    width=14, no_wrap=True)
    table.add_column("QA",       width=14, no_wrap=True)
    table.add_column("Score",    width=7,  no_wrap=True, justify="right")
    table.add_column("Cost",     width=6,  no_wrap=True, justify="right")

    if not sprints:
        table.add_row("—", "Nenhum sprint encontrado", "—", "—", "—", "—", "—")
        return table

    for s in sprints:
        try:
            sv = int(s["score"])
            score_text = Text(s["score"],
                style="bold green" if sv >= 90 else
                      "bold yellow" if sv >= 70 else "bold red")
        except ValueError:
            score_text = Text("—", style="dim")

        table.add_row(
            str(s["num"]),
            s["goal"],
            render_status(s["contract"]),
            render_status(s["build"]),
            render_status(s["qa"]),
            score_text,
            Text(s["cost"], style="dim"),
        )
    return table


def build_activity_panel(entries: list) -> Panel:
    lines = []

    if not entries:
        lines.append(Text("↳ Waiting for agent activity...", style="dim italic"))
    else:
        for e in entries:
            event = e["event"]
            msg   = e["msg"]
            agent = e["agent"]
            ts    = e["ts"][11:16] if len(e["ts"]) >= 16 else e["ts"]  # HH:MM

            # Estilo por evento
            if event == "started":
                icon, style = "▶", "bold cyan"
            elif event == "in_progress":
                icon, style = next_frame(), "bold yellow"
            elif event == "progress":
                icon, style = "·", "white"
            elif event == "done":
                icon, style = "✓", "bold green"
            elif event == "verified":
                icon, style = "✓", "bold green"
            elif event == "passed":
                icon, style = "✓", "bold green"
            elif event == "failed":
                icon, style = "✗", "bold red"
            elif event == "blocked":
                icon, style = "⊘", "bold yellow"
            else:
                icon, style = "↳", "dim"

            highlight = event in ("started","done","verified","passed","failed","blocked","in_progress")
            t = Text()
            t.append(f"{ts} ", style="dim")
            t.append(f"{icon} ", style=style)
            t.append(f"[{agent}] ", style="dim cyan")
            t.append(msg, style=style if highlight else "white")
            lines.append(t)

    return Panel(
        Group(*lines),
        title="[bold]Activity[/bold]",
        border_style="grey50",
        padding=(0, 1),
    )


def build_header(feature: str, prd: str, updated_at: str = "—") -> Text:
    t = Text()
    t.append("sdd", style="bold cyan")
    t.append("  —  ", style="dim")
    t.append("Spec-Driven Development", style="bold white")
    t.append("\n")
    t.append("feature: ", style="dim")
    t.append(feature, style="white")
    t.append("   prd: ", style="dim")
    t.append(prd, style="dim italic")
    t.append("   updated: ", style="dim")
    t.append(updated_at, style="dim")
    return t


def build_current_panel(current: dict) -> Panel:
    lines = []
    goal = current.get("goal", "—")
    nxt  = current.get("next_step", "—")
    done = current.get("done", []) or []
    sprint_num = current.get("sprint_num", "—")

    header = Text()
    header.append("Sprint #", style="dim")
    header.append(str(sprint_num), style="bold white")
    header.append("   goal: ", style="dim")
    header.append(goal, style="white")
    lines.append(header)

    nxt_line = Text()
    nxt_line.append("next: ", style="dim")
    nxt_line.append(nxt, style="bold cyan")
    lines.append(nxt_line)

    if done:
        lines.append(Text("done so far:", style="dim"))
        for b in done[-4:]:
            li = Text()
            li.append("  • ", style="green")
            li.append(b, style="white")
            lines.append(li)

    return Panel(
        Group(*lines),
        title="[bold]Current Sprint[/bold]",
        border_style="grey50",
        padding=(0, 1),
    )


def build_footer(data: dict, current: dict, start_time: float, cost: str) -> Text:
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)
    total = len(data["sprints"])
    active = current["sprint_num"]

    scores = []
    for s in data["sprints"]:
        try:
            scores.append(int(s["score"]))
        except ValueError:
            pass
    avg = f"{sum(scores) // len(scores)}" if scores else "—"

    t = Text()
    t.append("  sprint ", style="dim")
    t.append(f"{active} / {total}", style="bold white")
    t.append("   score ", style="dim")
    t.append(avg, style="bold green" if avg != "—" else "dim")
    t.append("   cost ", style="dim")
    t.append(cost, style="bold yellow" if cost != "—" else "dim")
    t.append(f"   elapsed ", style="dim")
    t.append(f"{mins}m {secs:02d}s", style="white")
    return t


def build_layout(data, current, entries, start_time, cost) -> Panel:
    return Panel(
        Group(
            build_header(data["feature"], data["prd"], data.get("updated_at", "—")),
            Text(""),
            Panel(build_sprints_table(data["sprints"]),
                  title="[bold]Sprints[/bold]",
                  border_style="grey50", padding=(0, 1)),
            build_current_panel(current),
            build_activity_panel(entries),
            Text(""),
            build_footer(data, current, start_time, cost),
        ),
        box=box.ROUNDED,
        border_style="cyan",
        padding=(0, 1),
    )


# ─────────────────────────────────────────────
# Comandos
# ─────────────────────────────────────────────

def cmd_watch(args):
    if not CONTEXT_DIR.exists():
        console.print(Panel(
            "[yellow]Diretório .claude/context/ não encontrado.[/yellow]\n\n"
            "Execute [bold cyan]/idea[/bold cyan] para inicializar o projeto.",
            title="[bold red]sdd[/bold red]", border_style="red"))
        sys.exit(1)

    start_time = time.time()
    cost = "—"
    cost_last_check = 0
    COST_INTERVAL = 30  # atualiza custo a cada 30s

    with Live(console=console, refresh_per_second=1/REFRESH_RATE,
              screen=True) as live:
        while True:
            now = time.time()
            if now - cost_last_check > COST_INTERVAL:
                cost = get_cost()
                cost_last_check = now

            data    = parse_sprints(SPRINTS_FILE)
            current = parse_current(CURRENT_FILE)
            entries = parse_activity_log(ACTIVITY_LOG)
            layout  = build_layout(data, current, entries, start_time, cost)
            live.update(layout)
            time.sleep(REFRESH_RATE)


def cmd_status(args):
    if not SPRINTS_FILE.exists():
        console.print("[yellow]Nenhum sprint em .claude/context/sprints.md[/yellow]")
        sys.exit(1)

    data    = parse_sprints(SPRINTS_FILE)
    current = parse_current(CURRENT_FILE)
    entries = parse_activity_log(ACTIVITY_LOG)
    cost    = get_cost()
    console.print(build_layout(data, current, entries, time.time(), cost))


def cmd_sprint(args):
    f = CONTEXT_DIR / f"sprint-{args.n}.md"
    if not f.exists():
        console.print(f"[red]Sprint #{args.n} não encontrado[/red]")
        sys.exit(1)
    console.print(Panel(f.read_text(encoding="utf-8"),
                        title=f"[bold cyan]Sprint #{args.n}[/bold cyan]",
                        border_style="cyan"))


def cmd_context(args):
    if not CURRENT_FILE.exists():
        console.print("[yellow]current.md não encontrado.[/yellow]")
        sys.exit(1)
    console.print(Panel(CURRENT_FILE.read_text(encoding="utf-8"),
                        title="[bold cyan]Contexto Atual[/bold cyan]",
                        border_style="cyan"))


def cmd_log(args):
    """Exibe o activity log completo."""
    if not ACTIVITY_LOG.exists():
        console.print("[yellow]activity.log não encontrado.[/yellow]")
        sys.exit(1)
    entries = parse_activity_log(ACTIVITY_LOG, n=50)
    panel = build_activity_panel(entries)
    console.print(panel)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="sdd",
        description="Spec-Driven Development — monitor de sprints",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("watch",   help="Monitor live (padrão)")
    sub.add_parser("status",  help="Snapshot estático")
    sub.add_parser("context", help="Contexto para nova sessão")
    sub.add_parser("log",     help="Activity log completo")

    p = sub.add_parser("sprint", help="Detalhes de um sprint")
    p.add_argument("n", type=int)

    args = parser.parse_args()
    cmd = args.command

    if   cmd is None or cmd == "watch":   cmd_watch(args)
    elif cmd == "status":                 cmd_status(args)
    elif cmd == "sprint":                 cmd_sprint(args)
    elif cmd == "context":                cmd_context(args)
    elif cmd == "log":                    cmd_log(args)


if __name__ == "__main__":
    main()