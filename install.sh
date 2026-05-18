#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────
# SDD Agent Installer
# https://github.com/helgg/sdd-agent
# ─────────────────────────────────────────────

REPO="helgg/sdd-agent"
BRANCH="master"
BASE_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# Arquivos a instalar: <origem no repo> → <destino no projeto>
declare -A FILES=(
  [".claude/commands/idea.md"]=".claude/commands/idea.md"
  [".claude/commands/review.md"]=".claude/commands/review.md"
  [".claude/agents/spec-writer.md"]=".claude/agents/spec-writer.md"
  [".claude/agents/tdd-reviewer.md"]=".claude/agents/tdd-reviewer.md"
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()    { echo -e "${GREEN}✔${RESET} $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET} $*"; }
error()   { echo -e "${RED}✖${RESET} $*" >&2; }
heading() { echo -e "\n${GREEN}$*${RESET}"; }

check_dependencies() {
  for cmd in curl mkdir; do
    if ! command -v "$cmd" &>/dev/null; then
      error "Dependência não encontrada: $cmd"
      exit 1
    fi
  done
}

confirm_target() {
  local target_dir="${1:-.}"

  if [[ ! -d "$target_dir" ]]; then
    error "Diretório não encontrado: $target_dir"
    exit 1
  fi

  echo -e "Instalando em: ${YELLOW}$(realpath "$target_dir")${RESET}"

  # Avisa se não parece ser raiz de um projeto
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
  mkdir -p "$target_dir/.claude/prds"
  mkdir -p "$target_dir/.claude/prompts"
  mkdir -p "$target_dir/.claude/tdd"
  info ".claude/prds/ .claude/prompts/ .claude/tdd/ criados"
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

main() {
  local target_dir="${1:-.}"

  heading "SDD Agent Installer"
  echo "Repositório: https://github.com/${REPO}"

  check_dependencies
  confirm_target "$target_dir"

  heading "Baixando arquivos..."
  for src in "${!FILES[@]}"; do
    dst="${target_dir}/${FILES[$src]}"
    download_file "$src" "$dst"
  done

  heading "Criando diretórios de saída..."
  create_output_dirs "$target_dir"

  heading "Instalação concluída!"
  echo ""
  echo "  Próximos passos:"
  echo "  1. Abra o projeto no Claude Code"
  echo "  2. Execute: /idea \"descrição da sua ideia\""
  echo "  3. Após implementar, execute: /review \"nome da feature\""
  echo ""
  echo "  Documentação: https://github.com/${REPO}#readme"
}

main "$@"