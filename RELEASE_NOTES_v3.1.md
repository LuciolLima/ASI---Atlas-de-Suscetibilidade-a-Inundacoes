# ASI — Atlas de Suscetibilidade a Inundações
## Release Notes v3.1 — "Landing & Legal Access"

---

**Data da Release:** 22 de Junho de 2026  
**Tag Git:** `v3.1`  
**Commit Base:** `375db43` (landing page styles + dark theme)  
**Status:** Stable Release

---

## 🎯 Visão Geral

A versão **3.1** marca um marco importante na evolução do ASI: a introdução de uma **Landing Page oficial** hospedada no Netlify e a **centralização de todos os documentos legais** (Licença Apache 2.0 e Termos de Uso PT-BR/EN) em links públicos acessíveis via Google Drive.

Esta release não altera o núcleo computacional do SIGWeb (pipeline ETL, modelo TWI, dashboards, mapas), mas resolve uma lacuna crítica de **acessibilidade, conformidade legal e experiência de onboarding** para novos usuários e colaboradores.

---

## 🌐 Novidades Principais

### 1. Landing Page Oficial — `https://asi-homepage.netlify.app/`

| Aspecto | Detalhes |
|---------|----------|
| **URL de Produção** | https://asi-homepage.netlify.app/ |
| **Tecnologia** | HTML5 + CSS3 (Vanilla) + JS (ES6+) — Zero dependências, ~3KB gzipped |
| **Deploy** | Netlify (CI/CD automático via `netlify.toml`) |
| **Design System** | IBM Plex Sans + IBM Plex Mono — Dark Theme (`#080C10`, `#2E86C1`, `#00B4D8`) |
| **Responsividade** | Mobile-first, breakpoints 480px / 768px / 1024px |
| **Acessibilidade** | WCAG 2.1 AA — `prefers-reduced-motion`, `focus-visible`, ARIA labels, landmarks semânticos |

#### Seções da Landing Page

| Seção | Conteúdo |
|-------|----------|
| **Hero** | Título, subtítulo técnico, CTA "Iniciar ASI" (abre modal de termos) + link GitHub |
| **Info Grid (6 cards)** | Objetivo, Metodologia (TWI), Dados/Fontes, Recursos v3.0, Contexto Acadêmico, Licença/Uso |
| **Sobre o Desenvolvedor** | Bio completa, quote, formação (FACEPE/CNPq, IFRS, Geoprocessamento, IA) |
| **Agradecimentos** | Orientador Dr. Renilson Ramos, Profa. Bruna Kelly, Profa. Gabrielle Simões, FACEPE, CNPq |
| **Footer** | Links projeto (GitHub, Streamlit Cloud, DTM), Recursos (README, INSTRUCTIONS, requirements), Contato |
| **Modal Termos de Uso** | Tabs PT/EN, checkbox de concordância obrigatória, countdown 10s, redirecionamento para Streamlit Cloud |

#### Recursos Técnicos do Frontend

- **Canvas Particle Background** — 55 partículas com conexões por proximidade (130px), 60fps
- **Parallax Sutil** no Hero (mouse move → transform translate ≤12px)
- **IntersectionObserver** para animações de entrada escalonadas (cards, sections)
- **Smooth Scroll** para âncoras internas
- **SPA Redirect** via `netlify.toml` (`/*` → `/index.html` status 200)
- **Security Headers** — CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Cache Strategy** — Assets imutáveis (1 ano), HTML no-cache

---

### 2. Documentos Legais — Links Públicos no Google Drive

| Documento | Link Direto | Formato |
|-----------|-------------|---------|
| **Licença Apache 2.0** | https://drive.google.com/file/d/1RFR8MS8kEjw7X0-4aMhw_2xbODbICUJO/view?usp=drive_link | PDF |
| **Termos de Uso — PT-BR** | https://docs.google.com/document/d/1PTxQpt6rbxLA89WvSxp1V4q5xGFU_I1t/edit?usp=drive_link | Google Docs |
| **Termos de Uso — EN** | https://docs.google.com/document/d/1B9Xcq1RNNzKvydqIpjD7xIPPEjuA25rN/edit?usp=drive_link | Google Docs |

> **Nota:** Os arquivos `.docx` originais (`ASI_Termos_de_Uso_PT.docx`, `ASI_Terms_of_Use_EN.docx`) permanecem no repositório para versionamento. Os links acima apontam para as versões **oficiais publicadas** (sempre sincronizadas com o repositório), garantindo que qualquer usuário — mesmo sem clone local — possa ler os termos completos antes de usar o sistema.

---

## 🤔 Por Que uma Landing Page?

### Contexto do Problema

Até a v3.0, o ASI era acessado **exclusivamente** via:
1. Clone local + `launch.bat` (usuários técnicos)
2. Streamlit Cloud direto (link "bruto" sem contexto)

Isso criava barreiras:

| Barreira | Impacto |
|----------|---------|
| **Onboarding frio** | Usuário caía direto no mapa sem entender propósito, metodologia, limitações |
| **Termos invisíveis** | Arquivos `.docx` no repo — poucos baixavam/liam antes de usar |
| **Credibilidade acadêmica** | Projeto de IC (FACEPE/CNPq) sem "cara institucional" para portfólio, editais, defesa |
| **SEO/Descoberta** | Repositório GitHub não indexa bem para buscas gerais ("susceptibilidade inundações PE") |
| **Compartilhamento** | Link do Streamlit Cloud não carrega meta tags Open Graph / Twitter Cards |

### Solução Adotada

Uma **Landing Page estática, leve, acessível e versionada** que:

1. **Apresenta o projeto** — Objetivo, metodologia (TWI), fontes de dados, recursos v3.0
2. **Exibe identidade acadêmica** — Desenvolvedor, orientador, instituições, bolsas
3. **Exige consentimento informado** — Modal com Termos PT/EN, checkbox obrigatório, countdown
4. **Centraliza links** — GitHub, Streamlit Cloud, Documentação, Download de dados
5. **Funciona como "cartão de visitas"** — URL curta, meta tags sociais, favicon, manifest PWA
6. **Separa preocupações** — App Streamlit foca em análise; Landing foca em comunicação/legal

### Decisões Técnicas

| Decisão | Justificativa |
|---------|---------------|
| **HTML/CSS/JS Vanilla** | Zero build step, zero dependências, deploy instantâneo, performance máxima |
| **Netlify (gratuito)** | CI/CD nativo, formulários, edge network, headers personalizados, domínio customizado |
| **Dark Theme por padrão** | Consistência com o SIGWeb (tema escuro `#080C10`), redução de fadiga ocular |
| **IBM Plex** | Fonte técnica, legível, open source (OFL), usada no SIGWeb v3.0 |
| **Modal com countdown** | Força leitura mínima dos termos (10s) — padrão de consentimento informado |
| **Tabs PT/EN no modal** | Usuário escolhe idioma sem recarregar — UX fluida |

---

## 📦 Assets da Release

| Asset | Descrição | Localização |
|-------|-----------|-------------|
| **Código Fonte** | Repositório completo | `github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes` |
| **Landing Page** | Pasta `src/landing/` (HTML, CSS, JS, assets, netlify.toml) | Incluída no repo |
| **Docs Legais (repo)** | `ASI_Termos_de_Uso_PT.docx`, `ASI_Terms_of_Use_EN.docx`, `LICENSE` | Raiz do repo |
| **Docs Legais (Drive)** | Versões publicadas sincronizadas | Links na tabela acima |
| **Changelog v3.0** | `ASI_CHANGELOG_v3.0.pdf` | `System Version/` |
| **Dados Geoespaciais** | `data_V3.0` (download separado) | Google Drive (link no README) |

---

## 🔗 Links Úteis

| Recurso | Link |
|---------|------|
| **Landing Page (Produção)** | https://asi-homepage.netlify.app/ |
| **Aplicação SIGWeb (Streamlit Cloud)** | https://asi---atlas-de-suscetibilidade-a-inundacoes.streamlit.app/ |
| **Repositório GitHub** | https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes |
| **Licença Apache 2.0 (Drive)** | https://drive.google.com/file/d/1RFR8MS8kEjw7X0-4aMhw_2xbODbICUJO/view?usp=drive_link |
| **Termos de Uso PT-BR (Drive)** | https://docs.google.com/document/d/1PTxQpt6rbxLA89WvSxp1V4q5xGFU_I1t/edit?usp=drive_link |
| **Termos de Uso EN (Drive)** | https://docs.google.com/document/d/1B9Xcq1RNNzKvydqIpjD7xIPPEjuA25rN/edit?usp=drive_link |
| **Download Dados (data_V3.0)** | https://drive.google.com/drive/folders/1Q1vuKcCAeF25g3T3yhBaT8fNwMxejsc0?usp=drive_link |
| **README Completo** | https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes/blob/main/README.md |
| **Guia de Instalação** | https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes/blob/main/INSTRUCTIONS.md |

---

## ✅ Checklist de Validação v3.1

- [x] Landing page deployada e acessível em `asi-homepage.netlify.app`
- [x] Redirect SPA funcionando (recarregue qualquer rota → carrega index.html)
- [x] Modal de termos abre ao clicar "Iniciar ASI"
- [x] Tabs PT/EN funcionam no modal
- [x] Checkbox habilita botão "Prosseguir" apenas quando marcado
- [x] Countdown 10s regressivo no botão "Prosseguir"
- [x] Clique em "Prosseguir" abre Streamlit Cloud em nova aba (`?from_landing=1&v=3.1`)
- [x] Links do footer (GitHub, Streamlit, README, INSTRUCTIONS, requirements) funcionais
- [x] Links dos documentos legais no Drive acessíveis publicamente
- [x] Meta tags Open Graph / Twitter Cards renderizam preview correto
- [x] Responsivo testado: mobile (375px), tablet (768px), desktop (1440px)
- [x] `prefers-reduced-motion` desativa animações (partículas, parallax, entrada)
- [x] Headers de segurança presentes (CSP, X-Frame-Options, etc.)
- [x] Cache headers corretos (assets 1 ano, HTML no-cache)
- [x] Tag `v3.1` criada e pushada para origin
- [x] Release Notes publicadas no GitHub Releases

---

## 🚀 Próximos Passos (Roadmap v3.2+)

| Área | Ideias |
|------|--------|
| **Landing** | Blog/Changelog section, newsletter signup, analytics (Plausible/Umami), dark/light toggle |
| **SIGWeb Core** | API Hub (Open-Meteo, IBGE SIDRA, NASA POWER) já implementado — expor na UI |
| **Dados** | Integração automática `sidrapy` para indicadores socioeconômicos por bairro |
| **Documentação** | MkDocs / Sphinx para docs técnicos versionados |
| **CI/CD** | GitHub Actions para lint, type-check, testes de smoke no deploy |

---

## 👨‍💻 Autoria

**Desenvolvedor:** Lúcio Luiz de Lima  
**Orientador:** Prof. Dr. Renilson Ramos (Mestre em Geografia e Análise Geoespacial)  
**Instituição:** FACEPE — Faculdade de Ciências Educacionais de Pernambuco  
**Fomento:** FACEPE / CNPq — Bolsa de Iniciação Científica e Tecnológica  
**Contato:** [Lucio0x01@proton.me](mailto:Lucio0x01@proton.me) | [github.com/LuciolLima](https://github.com/LuciolLima)

---

> **Licença:** Apache License 2.0 + Termos de Uso próprios  
> **Lei Aplicável:** República Federativa do Brasil — Foro: Comarca de Recife/PE  
> **Versão do Documento:** 1.0 (22/06/2026)