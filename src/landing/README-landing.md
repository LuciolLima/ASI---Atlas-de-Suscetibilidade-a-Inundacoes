# ASI Landing Page

Landing page oficial do **ASI — Atlas de Suscetibilidade a Inundações** (v3.0).

## 🚀 Deploy no Netlify

### Opção 1: Via Interface Web (Recomendado)
1. Acesse [app.netlify.com](https://app.netlify.com)
2. Clique em **"Add new site"** → **"Import an existing project"**
3. Conecte seu GitHub e selecione o repositório `ASI---Atlas-de-Suscetibilidade-a-Inundacoes`
4. Configure:
   - **Base directory**: `src/landing`
   - **Build command**: *(deixe vazio)*
   - **Publish directory**: `.` (ponto)
5. Clique em **"Deploy site"**

### Opção 2: Via CLI
```bash
cd src/landing
npm install -g netlify-cli
netlify login
netlify init --manual
# Selecione "Create & configure a new site"
# Team: sua conta
# Site name: asi-atlas (ou seu preferido)
# Deploy path: .
netlify deploy --prod
```

### Variáveis de Ambiente (Configure no painel Netlify → Site settings → Environment variables)
| Variável | Valor | Descrição |
|----------|-------|-----------|
| `STREAMLIT_URL` | `https://asi-atlas.streamlit.app` | URL do seu app no Streamlit Cloud |
| `SITE_URL` | `https://asi.netlify.app` | URL final da landing (após primeiro deploy) |

## 🔧 Personalização

### Atualizar URL do Streamlit
Edite `index.html`, linha ~58:
```html
<a href="https://SUA-URL.streamlit.app/?from_landing=1&v=3.0" ...>
```

### Atualizar Versão
Edite duas ocorrências em `index.html`:
```html
<span class="version-badge">v3.0</span>  <!-- Header -->
...
?from_landing=1&v=3.0  <!-- Link do botão -->
```

### Cores (Design System)
Edite `:root` em `styles.css`:
```css
:root {
  --accent-cyan:    #00B4D8;  /* Cor principal */
  --accent-blue:    #2E86C1;  /* Cor secundária */
  --bg-deep:        #080C10;  /* Fundo principal */
  /* ... */
}
```

### Textos e Conteúdo
Todos os textos estão diretamente no `index.html` — edite as seções:
- Hero (título, subtítulo)
- Cards informativos (6 cards: Objetivo, Metodologia, Dados, Recursos, Contexto, Licença)
- Footer (links, contato)

## 📁 Estrutura
```
src/landing/
├── index.html          # HTML semântico, SEO-ready
├── styles.css          # Design system completo (CSS custom properties)
├── scripts.js          # Canvas particles + parallax + micro-interações
├── netlify.toml        # Config Netlify (headers, cache, redirects, CSP)
├── assets/
│   ├── asi-logo.svg    # Logo vetorial (hexágono = grade geoespacial)
│   ├── manifest.json   # PWA manifest
│   └── og-image.png    # (Opcional) Imagem 1200x630 para Open Graph
```

## 🎨 Design System

### Tipografia
- **IBM Plex Mono**: Labels, valores, código, version badge
- **IBM Plex Sans**: Corpo de texto, UI

### Cores (Dark Theme)
| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-deep` | `#080C10` | Background principal |
| `--bg-card` | `#0E141B` | Cards, superficies elevadas |
| `--fg-primary` | `#E8EBF0` | Texto principal |
| `--fg-secondary` | `#B8C0CC` | Texto secundário |
| `--fg-muted` | `#8B95A3` | Texto desabilitado/mudo |
| `--accent-cyan` | `#00B4D8` | Ação primária, links, highlights |
| `--accent-blue` | `#2E86C1` | Ação secundária, bordas de foco |
| `--border` | `#1E2A3A` | Bordas padrão |
| `--border-bright` | `#2E86C1` | Bordas hover/foco |

### Espaçamento
Base: `0.25rem` (4px) — scale: xs, sm, md, lg, xl, 2xl, 3xl

### Raio
`--radius-sm: 6px`, `--radius-md: 12px`, `--radius-lg: 20px`, `--radius-full: 100px`

## ♿ Acessibilidade
- Semântica HTML5 (`header`, `main`, `section`, `article`, `footer`, `nav`)
- `aria-label` / `aria-labelledby` em elementos interativos
- `visually-hidden` para títulos de seção só para screen readers
- `prefers-reduced-motion` respeitado (animações desligadas)
- `focus-visible` styles em todos os elementos interativos
- Contraste WCAG AA em todos os textos
- `lang="pt-BR"` no `<html>`

## ⚡ Performance
- Zero dependências externas (exceto Google Fonts)
- CSS custom properties — sem runtime
- Canvas particles: ~55 partículas, 60fps em mobile
- IntersectionObserver para animação de entrada dos cards
- Cache headers configurados no `netlify.toml`
- CSP configurado para segurança

## 🔗 Integração com Streamlit

A landing redireciona para o Streamlit com query params:
```
https://asi-atlas.streamlit.app/?from_landing=1&v=3.0
```

No `app.py` (Streamlit), detecte a origem:
```python
import streamlit as st
from urllib.parse import parse_qs

query = st.query_params
if query.get("from_landing") == "1":
    st.toast("Bem-vindo ao ASI v3.0!", icon="🌊")
    # Opcional: st.session_state.from_landing = True
```

## 📝 Licença
Mesma licença do projeto principal: Apache 2.0 + Termos de Uso próprios.

## 👨‍💻 Autor
Lúcio Lima — [github.com/LuciolLima](https://github.com/LuciolLima)