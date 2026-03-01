# ASI — Atlas de Suscetibilidade a Inundações
## `INSTRUCTIONS.md` — Guia Oficial de Instalação, Configuração e Regras de Uso

> **Leitura obrigatória antes de qualquer interação com o sistema.**
> Este documento contém todas as etapas necessárias para a correta instalação e execução do ASI,
> bem como as regras de conduta que regem o uso do software. O não cumprimento de qualquer
> diretriz aqui estabelecida é de responsabilidade exclusiva do usuário.

---

## ⚠️ AVISO LEGAL — LEIA ANTES DE PROSSEGUIR

> Antes de executar qualquer etapa descrita neste documento, é **obrigatória** a leitura integral
> dos **Termos de Uso, Licenciamento e Responsabilidade** do ASI, disponíveis nos arquivos:
>
> - 📄 `ASI_Termos_de_Uso_PT.docx` — versão em **Português**
> - 📄 `ASI_Terms_of_Use_EN.docx` — versão em **Inglês**
>
> Ao prosseguir com a instalação ou execução do software, o usuário declara, de forma tácita
> e irrevogável, que leu, compreendeu e concorda integralmente com todos os termos e condições
> neles estabelecidos. **A ignorância dos termos não exime o usuário de responsabilidade.**

---

---

# PARTE I — INSTRUÇÕES DE INSTALAÇÃO E CONFIGURAÇÃO

---

## Passo 1 — Aquisição da Base de Dados Geoespaciais (`data_V2.7`)

O sistema ASI opera sobre uma base de dados geoespaciais estruturada, denominada `data_V2.7`,
que contém os vetores de atributos, exportações cartográficas e demais arquivos necessários
para o processamento e a visualização dos índices de suscetibilidade.

Essa base de dados **não está incluída diretamente no repositório** por questões de volume e
integridade dos arquivos binários. Ela deve ser obtida separadamente, por meio do link oficial
abaixo:

---

### 📥 Link oficial de download da pasta `data_V2.7`:

```
https://drive.google.com/drive/folders/1Q1vuKcCAeF25g3T3yhBaT8fNwMxejsc0?usp=drive_link
```

---

### Procedimento de download:

1. **Copie o link acima na íntegra** e cole diretamente na barra de endereços do seu navegador
   de internet (Google Chrome, Firefox, Edge ou equivalente);
2. Aguarde o carregamento da página do Google Drive;
3. Clique com o botão direito sobre a pasta `data_V2.7` e selecione a opção **"Fazer download"**;
4. O Google Drive compactará automaticamente a pasta no formato `.zip`.
   Aguarde a conclusão do processo de compactação — **não interrompa o download**;
5. Após a conclusão, localize o arquivo `.zip` na pasta de downloads do seu dispositivo;
6. **Extraia o conteúdo** do arquivo `.zip` utilizando qualquer descompactador (Windows Explorer
   nativo, WinRAR, 7-Zip ou equivalente);
7. Certifique-se de que, após a extração, existe uma pasta chamada exatamente **`data_V2.7`**
   (respeitando maiúsculas, minúsculas e o ponto na versão).

> **Atenção:** Não renomeie a pasta. O sistema de lançamento (`launch_asi.bat`) realiza a
> detecção e o renomeamento automaticamente durante a execução. Qualquer alteração manual
> no nome da pasta poderá impedir o funcionamento correto do sistema.

---

## Passo 2 — Posicionamento da Pasta no Projeto

Após a extração, a pasta `data_V2.7` deve ser movida para o **diretório raiz do projeto**,
ou seja, para o mesmo local onde se encontram os demais arquivos e pastas principais do ASI.

### A estrutura raiz do projeto deve ser a seguinte:

```
📁 ASI/  (pasta raiz do projeto)
│
├── 📄 app.py
├── 📄 launch_asi.bat               ← arquivo de lançamento principal
├── 📄 install_dependences.py
├── 📄 requeriments.txt
├── 📄 ASI_Termos_de_Uso_PT.docx
├── 📄 ASI_Terms_of_Use_EN.docx
├── 📄 INSTRUCTIONS.md              ← este arquivo
│
├── 📁 data_V2.7/                   ← pasta que você acabou de mover
│   ├── 📁 curated/
│   └── 📁 raw/
│
├── 📁 docs/
├── 📁 outputs/
├── 📁 references/
└── 📁 src/
```

> **Verificação:** Antes de prosseguir, confirme visualmente que a pasta `data_V2.7` está
> **no mesmo nível** que `app.py` e `launch_asi.bat` — e não dentro de nenhuma subpasta.
> Posicionamentos incorretos resultarão em falha de detecção pelo sistema de lançamento.

---

## Passo 3 — Execução do Launcher (`launch_asi.bat`)

Com a pasta `data_V2.7` corretamente posicionada, o sistema está pronto para ser inicializado.
Todo o processo restante — verificação de estrutura, instalação de dependências e lançamento
da aplicação — é gerenciado automaticamente pelo arquivo de lançamento.

### Procedimento:

1. Localize o arquivo **`launch_asi.bat`** na raiz do projeto;
2. **Dê um duplo clique** sobre o arquivo para executá-lo;
3. Uma janela de terminal será aberta automaticamente;
4. **Leia atentamente todas as mensagens exibidas** no terminal durante o processo;
5. O launcher executará, em sequência, as seguintes verificações automáticas:

| Passo | Ação Executada |
|-------|----------------|
| 1/8 | Verificação da versão do Python instalado (mínimo: 3.12) |
| 2/8 | Detecção da pasta `data_V2.7` no diretório raiz |
| 3/8 | Validação da integridade interna da pasta `data_V2.7` |
| 4/8 | Renomeamento automático: `data_V2.7` → `data` |
| 5/8 | Verificação da estrutura completa do projeto |
| 6/8 | Instalação das bibliotecas e dependências via `requeriments.txt` |
| 7/8 | Validação das bibliotecas instaladas |
| 8/8 | Solicitação de confirmação para iniciar o SIGWeb |

6. Ao término de todas as verificações, o launcher exibirá a pergunta:

   ```
   Deseja iniciar o SIGWeb agora? [S/n]:
   ```

   Digite **`S`** e pressione **Enter** para iniciar a aplicação, ou **`N`** para encerrar
   sem executar o sistema;

7. Caso opte por iniciar, o SIGWeb será carregado automaticamente no navegador padrão do
   seu dispositivo, na URL local `http://localhost:8501`.

---

---

# PARTE II — REGRAS DE CONDUTA DURANTE A EXECUÇÃO

---

> As diretrizes a seguir foram estabelecidas para garantir a **integridade do processo de
> instalação**, a **estabilidade do sistema** e a **segurança dos dados processados**.
> O descumprimento de qualquer uma destas regras poderá resultar em falhas, corrupção de
> arquivos, comportamento inesperado do sistema ou perda de dados.

---

## Regra 1 — Não Interromper o Processo de Execução do Launcher

Durante toda a execução do `launch_asi.bat` — desde a abertura da janela do terminal até
a conclusão do Passo 7/8 — **é terminantemente vedado**:

- Fechar a janela do terminal manualmente (clicando no "X" ou utilizando atalhos de teclado);
- Pressionar `Ctrl+C` ou qualquer combinação de teclas que interrompa o processo em andamento;
- Reiniciar ou desligar o dispositivo durante a execução;
- Suspender ou hibernar o sistema operacional enquanto o processo estiver ativo.

> **Justificativa técnica:** O launcher executa operações críticas e sequenciais, incluindo
> renomeamento de diretórios e instalação de pacotes via `pip`. A interrupção abrupta dessas
> operações pode deixar o ambiente em um estado inconsistente, exigindo reinstalação completa
> do Python, das dependências ou, em casos mais graves, corrompendo a estrutura de pastas do projeto.

---

## Regra 2 — Manter o Dispositivo Ativo e Operante

Durante o processo de instalação e durante toda a sessão de uso do SIGWeb, recomenda-se
fortemente que o usuário:

- **Não coloque o dispositivo em modo de suspensão, hibernação ou economia de energia**
  enquanto o sistema estiver em execução;
- **Mantenha a conexão com a internet estável** durante o Passo 6/8 (instalação de dependências),
  pois os pacotes são baixados em tempo real dos servidores do PyPI;
- **Não execute outros processos de alta demanda computacional** simultaneamente (como
  renderização de vídeo, compilação de software ou jogos), pois podem comprometer o desempenho
  do sistema e causar timeouts durante a instalação.

---

## Regra 3 — Não Manipular, Editar ou Mover Arquivos Durante a Execução

Enquanto o `launch_asi.bat` estiver em execução ou enquanto o SIGWeb estiver ativo no navegador,
**é expressamente proibido**:

- Mover, renomear, copiar ou excluir qualquer arquivo ou pasta dentro do diretório do projeto;
- Abrir, editar ou salvar arquivos do projeto em editores de texto, IDEs ou qualquer outra
  ferramenta externa;
- Executar scripts Python, comandos `pip` ou quaisquer outras operações no terminal que
  interfiram no ambiente virtual ou nas dependências do projeto;
- Modificar as variáveis de ambiente do sistema operacional relacionadas ao Python ou ao `pip`.

> **Justificativa técnica:** O sistema de verificação de estrutura e o servidor Streamlit
> mantêm referências ativas aos arquivos do projeto durante toda a sessão. Alterações em tempo
> real podem causar erros de importação, falhas de carregamento de dados, comportamento
> indefinido nos mapas e na análise estatística, ou quebra do pipeline ETL geoespacial.

---

## Regra 4 — Não Tentar Contornar as Verificações Automáticas do Launcher

O launcher realiza verificações sequenciais e interdependentes. **É vedado**:

- Tentar pular etapas do processo manipulando ou deletando o arquivo `.asi_launcher_state`;
- Interferir nos processos do `pip` abrindo um segundo terminal para instalar ou remover
  pacotes simultaneamente;
- Forçar a execução de `app.py` diretamente (via `python app.py` ou `streamlit run app.py`)
  antes que o launcher tenha concluído todas as verificações com sucesso ao menos uma vez.

---

## Regra 5 — Encerramento Correto do Sistema

Para encerrar o SIGWeb de forma segura e ordenada:

1. Retorne à janela do terminal onde o launcher está em execução;
2. Pressione **`Ctrl+C`** uma única vez para enviar o sinal de encerramento ao servidor Streamlit;
3. Aguarde a mensagem de confirmação de encerramento exibida no terminal;
4. Somente então feche a janela do terminal.

> **Atenção:** Fechar diretamente a aba do navegador onde o SIGWeb está aberto **não encerra**
> o servidor. O processo Python continuará ativo em segundo plano até que o terminal seja
> encerrado corretamente conforme descrito acima.

---

---

# PARTE III — SUPORTE, CONTRIBUIÇÕES E CONTATO

---

## Canal Oficial

Dúvidas técnicas, reportes de bugs, sugestões de melhoria e solicitações de colaboração
devem ser encaminhadas **exclusivamente** pelo repositório oficial do projeto:

```
https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes
```

Utilize os seguintes recursos disponíveis no repositório:

- **Issues** — para reporte de erros, dúvidas e sugestões formais;
- **Pull Requests** — para submissão de contribuições, somente após autorização prévia do Desenvolvedor;
- **Discussions** (se disponível) — para debate técnico e acadêmico sobre o sistema.

> Modificações realizadas no código sem autorização prévia e expressa do Desenvolvedor
> constituem violação dos Termos de Uso. Consulte o documento `ASI_Termos_de_Uso_PT.docx`
> ou `ASI_Terms_of_Use_EN.docx` para mais informações sobre o processo de contribuição
> e as penalidades aplicáveis ao descumprimento.

---

---

# PARTE IV — REFERÊNCIA RÁPIDA

---

## Checklist de Instalação

Use esta lista para verificar cada etapa antes de prosseguir:

- [ ] Li integralmente o documento `ASI_Termos_de_Uso_PT.docx` ou `ASI_Terms_of_Use_EN.docx`
- [ ] Realizei o download da pasta `data_V2.7` pelo link oficial do Google Drive
- [ ] Extraí o conteúdo do arquivo `.zip` sem alterar o nome da pasta
- [ ] Movi a pasta `data_V2.7` para a raiz do projeto (mesmo nível de `app.py` e `launch_asi.bat`)
- [ ] Confirmei que o Python 3.12 ou superior está instalado no dispositivo
- [ ] Executei o `launch_asi.bat` com duplo clique
- [ ] Aguardei a conclusão de todos os 8 passos sem interromper o processo
- [ ] O SIGWeb abriu corretamente no navegador

---

## Estrutura Esperada Após Instalação Completa

```
📁 ASI/
│
├── 📄 app.py
├── 📄 launch_asi.bat
├── 📄 install_dependences.py
├── 📄 requeriments.txt
├── 📄 ASI_Termos_de_Uso_PT.docx
├── 📄 ASI_Terms_of_Use_EN.docx
├── 📄 INSTRUCTIONS.md
├── 📄 .asi_launcher_state          ← criado automaticamente após 1ª execução
│
├── 📁 data/                        ← renomeada automaticamente pelo launcher
│   ├── 📁 curated/
│   │   └── 📁 attribute_tables/
│   │       ├── 📄 data_table.txt
│   │       ├── 📄 Data_Table.xls
│   │       ├── 📄 schema.ini
│   │       └── 📁 info/
│   └── 📁 raw/
│       └── 📁 arcmap_exports/
│
├── 📁 docs/
├── 📁 outputs/
├── 📁 references/
└── 📁 src/
    ├── 📁 analysis/
    ├── 📁 processing/
    ├── 📁 scripts/
    └── 📁 sigweb/
```

---

## Requisitos do Sistema

| Requisito | Especificação Mínima |
|-----------|----------------------|
| Sistema Operacional | Windows 10 (64-bit) ou superior |
| Python | 3.12 ou superior (3.14 recomendado) |
| Memória RAM | 4 GB (8 GB recomendado) |
| Espaço em Disco | 500 MB livres |
| Conexão com a Internet | Necessária apenas na 1ª execução (instalação de dependências) |
| Navegador | Google Chrome, Firefox ou Edge (versões recentes) |

---

*ASI — Atlas de Suscetibilidade a Inundações | SIGWeb v2.7*
*Documento: INSTRUCTIONS.md v1.0*
*Regido pelas leis da República Federativa do Brasil | Licença Apache 2.0 + Restrições Contratuais*
*Para dúvidas ou contribuições: github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes*
