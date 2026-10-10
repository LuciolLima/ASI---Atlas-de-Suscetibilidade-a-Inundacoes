#!/bin/bash
# scripts/rollback.sh — Rollback seguro de tag para release anterior

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== ASI Rollback Script ===${NC}"
echo

# Pega tag atual
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "nenhuma")
echo -e "Tag atual: ${GREEN}$CURRENT_TAG${NC}"

# Pega tag anterior
PREV_TAG=$(git tag --sort=-v:refname | sed -n '2p')
if [ -z "$PREV_TAG" ]; then
    echo -e "${RED}Erro: Nao ha tag anterior para rollback${NC}"
    exit 1
fi
echo -e "Tag anterior: ${GREEN}$PREV_TAG${NC}"

echo
read -p "Confirmar rollback de $CURRENT_TAG para $PREV_TAG? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cancelado pelo usuario${NC}"
    exit 0
fi

echo -e "${YELLOW}Fazendo checkout da tag anterior...${NC}"
git checkout "$PREV_TAG"

echo -e "${YELLOW}Forçando push da tag anterior como latest...${NC}"
git push origin "$PREV_TAG" --force

echo
echo -e "${GREEN}Rollback concluido!${NC}"
echo
echo "Proximos passos:"
echo "  1. O Streamlit Cloud deve detectar a mudanca e fazer rebuild automatico"
echo "  2. Se nao rebuildar, faca rebuild manual no painel do Streamlit Cloud"
echo "  3. Verifique se a aplicacao esta funcionando em https://asi-app.streamlit.app"
echo
echo -e "${YELLOW}Para voltar para a tag anterior (reverter o rollback):${NC}"
echo "  git checkout $CURRENT_TAG"
echo "  git push origin $CURRENT_TAG --force"