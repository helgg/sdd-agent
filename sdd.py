#!/usr/bin/env python3
"""
sdd — Spec-Driven Development CLI
Monitora o estado dos sprints em tempo real lendo .claude/context/
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import re

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.align import Align
from rich.style import Style
from rich.console import Group

# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────

CONTEXT_DIR = Path(".claude/context")
SPRINTS_FILE = CONTEXT_DIR / "sprints.md"
CURRENT_FILE = CONTEXT_DIR / "current.md"
REFRESH_RATE = 2  # segundos entre refreshes

STATUS_STYLE = {
    # Contract
    "AGREED":      ("✓ AGREED",      "bold green"),
    "VIOLATED":    ("✗ VIOLATED",    "bold red"),
    "pending":     ("  pending",     "dim"),
    # Build / QA
    "in_progress": ("… running",     "bold yellow"),
    "done":        ("✓ done",        "bold green"),
    "verified":    ("✓ verified",    "bold green"),
    "failed":      ("✗ failed",      "bold red"),
    "passed":      ("✓ passed",      "bold green"),
    "blocked":     ("⊘ blocked",     "bold red"),
    "—":           ("  —",           "dim"),
}

console = Console()


# ─────────────────────────────────────────────
# Parsing dos arquivos de contexto
# ─────────────────────────────────────────────

def parse_sprints(path: Path) -> dict:
    """Lê sprints.md e retorna dados estruturados."""
    result = {
        "feature": "—",
        "prd": "—",
        "updated_at": "—",
        "sprints": [],
    }

    if not path.exists():
        return result

    content = path.read_text(encoding="utf-8")

    # Metadata
    for line in content.splitlines():
        if line.startswith("**Última atualização**"):
            result["updated_at"] = line.split(":", 1)[-1].strip()
        elif line.startswith("**Feature**"):
            result["feature"] = line.split(":", 1)[-1].strip()
        elif line.startswith("**PRD de referência**"):
            result["prd"] = line.split(":", 1)[-1].strip().strip("`")

    # Tabela de sprints — linhas que começam com "| N"
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p != ""]
        if len(parts) < 6:
            continue
        # Ignora cabeçalho e separador
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
    """Lê current.md e retorna o contexto atual."""
    result = {
        "sprint_num": "—",
        "goal": "—",
        "next_step": "—",
        "done": [],
        "updated_at": "—",
    }

    if not path.exists():
        return result

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    section = None
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("**Atualizado em**"):
            result["updated_at"] = stripped.split(":", 1)[-1].strip()
        elif stripped.startswith("**Goal**"):
            result["goal"] = stripped.split(":", 1)[-1].strip()
        elif stripped.startswith("**Próximo passo**"):
            result["next_step"] = stripped.split(":", 1)[-1].strip()
        elif stripped.startswith("## Sprint Atual"):
            m = re.search(r"#(\d+)", stripped)
            if m:
                result["sprint_num"] = m.group(1)
        elif stripped == "## O que foi feito até aqui":
            section = "done"
        elif stripped.startswith("## ") and section == "done":
            section = None
        elif section == "done" and stripped.startswith("- "):
            result["done"].append(stripped[2:])

    return result


def get_activity(context_dir: Path) -> str:
    """Retorna a última linha de atividade lendo o sprint atual."""
    current = context_dir / "current.md"
    if not current.exists():
        return "Waiting for agent activity..."

    content = current.read_text(encoding="utf-8")
    for line in reversed(content.splitlines()):
        line = line.strip()
        if line.startswith("- `") and "—" in line:
            # Linha de histórico: `YYYY-MM-DD HH:MM` — evento
            return line.lstrip("- ").strip()

    return "Waiting for agent activity..."


# ─────────────────────────────────────────────
# Componentes visuais
# ─────────────────────────────────────────────

def render_status(value: str) -> Text:
    label, style = STATUS_STYLE.get(value, (value, "default"))
    return Text(label, style=style)


def build_sprints_table(sprints: list) -> Table:
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1),
    )

    table.add_column("#",        style="bold cyan",  width=3,  no_wrap=True)
    table.add_column("Goal",     style="white",       ratio=3)
    table.add_column("Contract", width=14, no_wrap=True)
    table.add_column("Build",    width=14, no_wrap=True)
    table.add_column("QA",       width=14, no_wrap=True)
    table.add_column("Score",    width=7,  no_wrap=True, justify="right")
    table.add_column("Cost",     width=5,  no_wrap=True, justify="right")

    if not sprints:
        table.add_row("—", "Nenhum sprint encontrado", "—", "—", "—", "—", "—")
        return table

    for s in sprints:
        score_text = Text(s["score"])
        try:
            score_val = int(s["score"])
            if score_val >= 90:
                score_text = Text(s["score"], style="bold green")
            elif score_val >= 70:
                score_text = Text(s["score"], style="bold yellow")
            else:
                score_text = Text(s["score"], style="bold red")
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


def build_activity_panel(activity: str, current: dict) -> Panel:
    lines = []

    if current["next_step"] != "—":
        lines.append(Text.assemble(
            ("Próximo passo: ", "bold yellow"),
            (current["next_step"], "white"),
        ))
        lines.append(Text(""))

    lines.append(Text.assemble(
        ("↳ ", "dim"),
        (activity, "italic dim"),
    ))

    return Panel(
        Group(*lines),
        title="[bold]Activity[/bold]",
        border_style="grey50",
        padding=(0, 1),
    )


def build_header(feature: str, prd: str) -> Text:
    t = Text()
    t.append("sdd", style="bold cyan")
    t.append("  —  ", style="dim")
    t.append("Spec-Driven Development", style="bold white")
    t.append("\n")
    t.append(f"feature: ", style="dim")
    t.append(feature, style="white")
    t.append("   prd: ", style="dim")
    t.append(prd, style="dim italic")
    return t


def build_footer(data: dict, current: dict, start_time: float) -> Text:
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)

    active_sprint = current["sprint_num"]
    total = len(data["sprints"])

    scores = [s["score"] for s in data["sprints"] if s["score"] not in ("—", "")]
    avg_score = f"{sum(int(s) for s in scores) // len(scores)}" if scores else "—"

    t = Text()
    t.append("  sprint ", style="dim")
    t.append(f"{active_sprint} / {total}", style="bold white")
    t.append("   score ", style="dim")
    t.append(avg_score, style="bold green" if avg_score != "—" else "dim")
    t.append(f"   elapsed ", style="dim")
    t.append(f"{mins}m {secs:02d}s", style="white")
    t.append(f"   updated ", style="dim")
    t.append(data["updated_at"], style="dim italic")
    return t


def build_layout(data: dict, current: dict, activity: str, start_time: float) -> Panel:
    header = build_header(data["feature"], data["prd"])
    sprints_table = build_sprints_table(data["sprints"])
    activity_panel = build_activity_panel(activity, current)
    footer = build_footer(data, current, start_time)

    return Panel(
        Group(
            header,
            Text(""),
            Panel(sprints_table, title="[bold]Sprints[/bold]", border_style="grey50", padding=(0, 1)),
            activity_panel,
            Text(""),
            footer,
        ),
        box=box.ROUNDED,
        border_style="cyan",
        padding=(0, 1),
    )


# ─────────────────────────────────────────────
# Comandos
# ─────────────────────────────────────────────

def cmd_watch(args):
    """Modo live — atualiza em tempo real."""
    if not CONTEXT_DIR.exists():
        console.print(
            Panel(
                "[yellow]Diretório .claude/context/ não encontrado.[/yellow]\n\n"
                "Execute [bold cyan]/idea[/bold cyan] no Claude Code para inicializar o projeto.",
                title="[bold red]sdd[/bold red]",
                border_style="red",
            )
        )
        sys.exit(1)

    start_time = time.time()

    with Live(console=console, refresh_per_second=1 / REFRESH_RATE, screen=True) as live:
        while True:
            data = parse_sprints(SPRINTS_FILE)
            current = parse_current(CURRENT_FILE)
            activity = get_activity(CONTEXT_DIR)
            layout = build_layout(data, current, activity, start_time)
            live.update(layout)
            time.sleep(REFRESH_RATE)


def cmd_status(args):
    """Exibe status atual sem modo live."""
    if not SPRINTS_FILE.exists():
        console.print("[yellow]Nenhum sprint encontrado em .claude/context/sprints.md[/yellow]")
        sys.exit(1)

    data = parse_sprints(SPRINTS_FILE)
    current = parse_current(CURRENT_FILE)
    activity = get_activity(CONTEXT_DIR)
    start_time = time.time()

    layout = build_layout(data, current, activity, start_time)
    console.print(layout)


def cmd_sprint(args):
    """Exibe detalhes de um sprint específico."""
    sprint_file = CONTEXT_DIR / f"sprint-{args.n}.md"
    if not sprint_file.exists():
        console.print(f"[red]Sprint #{args.n} não encontrado em {sprint_file}[/red]")
        sys.exit(1)

    content = sprint_file.read_text(encoding="utf-8")
    console.print(Panel(content, title=f"[bold cyan]Sprint #{args.n}[/bold cyan]", border_style="cyan"))


def cmd_context(args):
    """Exibe o current.md — contexto para nova sessão."""
    if not CURRENT_FILE.exists():
        console.print("[yellow]current.md não encontrado. Nenhum sprint inicializado ainda.[/yellow]")
        sys.exit(1)

    content = CURRENT_FILE.read_text(encoding="utf-8")
    console.print(Panel(content, title="[bold cyan]Contexto Atual[/bold cyan]", border_style="cyan"))


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="sdd",
        description="Spec-Driven Development — monitor de sprints",
    )
    sub = parser.add_subparsers(dest="command")

    # watch (padrão)
    sub.add_parser("watch", help="Monitor em tempo real (padrão)")

    # status
    sub.add_parser("status", help="Exibe status atual sem live update")

    # sprint N
    p_sprint = sub.add_parser("sprint", help="Detalhes de um sprint específico")
    p_sprint.add_argument("n", type=int, help="Número do sprint")

    # context
    sub.add_parser("context", help="Exibe contexto atual para nova sessão")

    args = parser.parse_args()

    # Padrão: watch
    if args.command is None or args.command == "watch":
        cmd_watch(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "sprint":
        cmd_sprint(args)
    elif args.command == "context":
        cmd_context(args)


if __name__ == "__main__":
    main()