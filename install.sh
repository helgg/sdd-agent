#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# SDD Agent Installer
# https://github.com/helgg/sdd-agent
# ─────────────────────────────────────────────

REPO="helgg/sdd-agent"
BRANCH="master"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

AGENTS=(
  ".claude/agents/spec-writer.md"
  ".claude/agents/spec-verifier.md"
  ".claude/agents/tdd-reviewer.md"
  ".claude/agents/contract-writer.md"
  ".claude/agents/context-writer.md"
  ".claude/agents/spec-dev.md"
)

COMMANDS=(
  ".claude/commands/ideia.md"
  ".claude/commands/verify.md"
  ".claude/commands/review.md"
  ".claude/commands/contract.md"
  ".claude/commands/sprint.md"
  ".claude/commands/yolo.md"
)

CLI=(
  "sdd.py"
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BOLD="\033[1m"
RESET="\033[0m"

info()    { echo -e "${GREEN}✔${RESET} $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET} $*"; }
error()   { echo -e "${RED}✖${RESET} $*" >&2; }
heading() { echo -e "\n${BOLD}$*${RESET}"; }

check_dependencies() {
  for cmd in curl mkdir python3; do
    if ! command -v "$cmd" &>/dev/null; then
      error "Dependência não encontrada: $cmd"
      exit 1
    fi
  done

  if ! python3 -c "import rich" &>/dev/null; then
    warn "Biblioteca 'rich' não encontrada. Instalando..."
    pip install rich --break-system-packages -q || pip install rich -q || {
      error "Não foi possível instalar 'rich'. Execute: pip install rich"
      exit 1
    }
    info "rich instalado"
  fi
}

is_project_root() {
  local dir="$1"
  git -C "$dir" rev-parse --git-dir &>/dev/null && return 0
  [[ -f "$dir/package.json" ]]   && return 0
  [[ -f "$dir/pyproject.toml" ]] && return 0
  [[ -f "$dir/go.mod" ]]         && return 0
  [[ -f "$dir/Cargo.toml" ]]     && return 0
  [[ -f "$dir/Gemfile" ]]        && return 0
  return 1
}

confirm_target() {
  local target_dir="${1:-.}"

  if [[ ! -d "$target_dir" ]]; then
    error "Diretório não encontrado: $target_dir"
    exit 1
  fi

  echo -e "Instalando em: ${YELLOW}$(realpath "$target_dir")${RESET}"

  if ! is_project_root "$target_dir"; then
    warn "Nenhum projeto detectado neste diretório."
    local confirm
    read -r -p "Continuar mesmo assim? [s/N] " confirm </dev/tty
    [[ "${confirm,,}" == "s" ]] || { echo "Instalação cancelada."; exit 0; }
  fi
}

download_file() {
  local src="$1"
  local dst="$2"

  mkdir -p "$(dirname "$dst")"

  if [[ -f "$dst" ]]; then
    warn "Já existe: $dst (sobrescrevendo)"
  fi

  if curl -fsSL "${BASE_URL}/${src}" -o "$dst"; then
    info "$dst"
  else
    error "Falha ao baixar: ${BASE_URL}/${src}"
    exit 1
  fi
}

create_output_dirs() {
  local target_dir="$1"
  local dirs=(
    ".claude/prds"
    ".claude/prompts"
    ".claude/tdd"
    ".claude/verify"
    ".claude/context"
  )

  for dir in "${dirs[@]}"; do
    mkdir -p "$target_dir/$dir"
    if [[ -z "$(ls -A "$target_dir/$dir" 2>/dev/null)" ]]; then
      touch "$target_dir/$dir/.gitkeep"
    fi
  done

  info "Diretórios criados"
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

main() {
  local target_dir="${1:-.}"

  heading "SDD Agent Installer"
  echo "Repositório: https://github.com/${REPO}"
  echo ""

  check_dependencies
  confirm_target "$target_dir"

  heading "Baixando agentes..."
  for file in "${AGENTS[@]}"; do
    download_file "$file" "$target_dir/$file"
  done

  heading "Baixando commands..."
  for file in "${COMMANDS[@]}"; do
    download_file "$file" "$target_dir/$file"
  done

  heading "Baixando CLI..."
  for file in "${CLI[@]}"; do
    download_file "$file" "$target_dir/$file"
  done
  chmod +x "$target_dir/sdd.py" 2>/dev/null || true

  heading "Criando diretórios..."
  create_output_dirs "$target_dir"

  heading "Instalação concluída!"
  echo ""
  echo "  Pipeline manual (sprint a sprint, task a task):"
  echo ""
  echo "  1. ${BOLD}/idea \"sua ideia\"${RESET}        spec-writer → PRD + sprints + tasks"
  echo "  2. ${BOLD}/contract --task 1.1${RESET}      contrato spec-dev ↔ QA da task"
  echo "  3. ${BOLD}/sprint start 1.1${RESET}         executor inicia"
  echo "  4. ${BOLD}/sprint done 1.1${RESET}          executor conclui"
  echo "  5. ${BOLD}/verify --task 1.1${RESET}        valida aderência"
  echo "  6. ${BOLD}/review --task 1.1${RESET}        audita testes + captura cost USD"
  echo "  7. próxima task..."
  echo ""
  echo "  Modo autônomo:"
  echo "  ${BOLD}/yolo${RESET}                        pipeline completa task por task"
  echo "  ${BOLD}/yolo --stop${RESET}                 interrompe o ciclo atual"
  echo ""
  echo "  Dashboard:"
  echo "  ${BOLD}python3 sdd.py${RESET}               live com sprints e tasks expandidas"
  echo "  ${BOLD}python3 sdd.py status${RESET}        snapshot estático"
  echo "  ${BOLD}python3 sdd.py task 1.3${RESET}      detalhes de uma task específica"
  echo "  ${BOLD}python3 sdd.py log${RESET}           activity log completo"
  echo ""
  echo "  Documentação: https://github.com/${REPO}#readme"
}

main "$@"