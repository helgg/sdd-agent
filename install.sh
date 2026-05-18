#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# SDD Agent Installer
# https://github.com/helgg/sdd-agent
# ─────────────────────────────────────────────

REPO="helgg/sdd-agent"
BRANCH="master"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# Agentes
AGENTS=(
  ".claude/agents/spec-writer.md"
  ".claude/agents/spec-verifier.md"
  ".claude/agents/tdd-reviewer.md"
  ".claude/agents/contract-writer.md"
  ".claude/agents/context-writer.md"
)

# Commands
COMMANDS=(
  ".claude/commands/ideia.md"
  ".claude/commands/verify.md"
  ".claude/commands/review.md"
  ".claude/commands/contract.md"
  ".claude/commands/sprint.md"
)

# CLI
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

confirm_target() {
  local target_dir="${1:-.}"

  if [[ ! -d "$target_dir" ]]; then
    error "Diretório não encontrado: $target_dir"
    exit 1
  fi

  echo -e "Instalando em: ${YELLOW}$(realpath "$target_dir")${RESET}"

  if [[ ! -f "$target_dir/.git/config" ]] && \
     [[ ! -f "$target_dir/package.json" ]] && \
     [[ ! -f "$target_dir/pyproject.toml" ]] && \
     [[ ! -f "$target_dir/go.mod" ]]; then
    warn "Nenhum arquivo de projeto detectado. Tem certeza que este é o diretório correto?"
    read -r -p "Continuar mesmo assim? [s/N] " confirm
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
    # Cria .gitkeep apenas se o diretório estiver vazio
    if [[ -z "$(ls -A "$target_dir/$dir" 2>/dev/null)" ]]; then
      touch "$target_dir/$dir/.gitkeep"
    fi
  done

  info "Diretórios de saída criados"
}

make_executable() {
  local target_dir="$1"
  chmod +x "$target_dir/sdd.py" 2>/dev/null || true
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
  make_executable "$target_dir"

  heading "Criando diretórios de saída..."
  create_output_dirs "$target_dir"

  heading "Instalação concluída!"
  echo ""
  echo "  Pipeline completa:"
  echo ""
  echo "  1. /idea \"sua ideia\"      → spec-writer gera PRD + sprints"
  echo "  2. /contract --sprint 1   → contrato executor ↔ QA"
  echo "  3. /sprint start 1        → executor começa"
  echo "  4. /sprint done 1         → executor conclui"
  echo "  5. /verify \"feature\"      → spec-verifier valida aderência"
  echo "  6. /review \"feature\"      → tdd-reviewer audita testes"
  echo "  7. /sprint               → visão geral de todos os sprints"
  echo ""
  echo "  Monitor em tempo real:"
  echo "  ${BOLD}python3 sdd.py${RESET}            → dashboard live no terminal"
  echo "  ${BOLD}python3 sdd.py status${RESET}     → snapshot estático"
  echo "  ${BOLD}python3 sdd.py context${RESET}    → contexto para nova sessão"
  echo ""
  echo "  Documentação: https://github.com/${REPO}#readme"
}

main "$@"