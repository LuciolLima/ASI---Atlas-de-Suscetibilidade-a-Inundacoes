from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading('ASI \u2014 Atlas de Suscetibilidade a Inunda\u00e7\u00f5es', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('SIGWeb \u2014 Vers\u00e3o 3.3.0')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0, 180, 216)

doc.add_paragraph()

# Header
header = doc.add_heading('TERMOS DE USO, LICENCIAMENTO E RESPONSABILIDADE', level=1)
header.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Documento Oficial \u2014 Leia integralmente antes de instalar, executar ou distribuir este software.')
run.bold = True
run.font.size = Pt(11)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Vers\u00e3o do documento: 3.3 | Vig\u00eancia: a partir da data de publica\u00e7\u00e3o no reposit\u00f3rio oficial')
run.font.size = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Desenvolvido e regido sob as leis da Rep\u00fablica Federativa do Brasil')
run.font.size = Pt(10)

doc.add_page_break()

def add_section(doc, title, paragraphs):
    if title:
        doc.add_heading(title, level=2)
    for para in paragraphs:
        if para == '':
            doc.add_paragraph()
        elif para.startswith('\u2022') or para.startswith('1.') or para.startswith('2.') or para.startswith('3.') or para.startswith('4.') or para.startswith('5.') or para.startswith('6.') or para.startswith('7.') or para.startswith('8.') or para.startswith('9.') or para.startswith('10.') or para.startswith('11.') or para.startswith('12.') or para.startswith('13.') or para.startswith('14.') or para.startswith('15.') or para.startswith('16.') or para.startswith('17.'):
            p = doc.add_paragraph(para, style='List Bullet')
            p.paragraph_format.space_after = Pt(4)
        elif para.startswith('|'):
            p = doc.add_paragraph(para)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.size = Pt(9)
        else:
            p = doc.add_paragraph(para)
            p.paragraph_format.space_after = Pt(6)

# Section 1
add_section(doc, '1. Identifica\u00e7\u00e3o do Software e do Desenvolvedor', [
    'O presente documento constitui os Termos de Uso, Licenciamento e Responsabilidade do software denominado ASI \u2014 Atlas de Suscetibilidade a Inunda\u00e7\u00f5es, desenvolvido e mantido por seu criador, Lucio Luiz de Lima, doravante denominado simplesmente Desenvolvedor. O ASI \u00e9 um sistema de informa\u00e7\u00e3o geogr\u00e1fica para a Web (SIGWeb) de car\u00e1ter educacional, cient\u00edfico e t\u00e9cnico, constru\u00eddo sob uma arquitetura modular de pipeline de engenharia de dados geoespaciais, com foco na visualiza\u00e7\u00e3o interativa, an\u00e1lise estat\u00edstica geoespacial e comunica\u00e7\u00e3o de \u00edndices de suscetibilidade hidrol\u00f3gica a partir de par\u00e2metros topogr\u00e1ficos, geomorfom\u00e9tricos e meteorol\u00f3gicos.',
    'Este software foi concebido, projetado e desenvolvido integralmente no Brasil, sendo portanto regido, interpretado e protegido exclusivamente pelas leis da Rep\u00fablica Federativa do Brasil, independentemente da localidade geogr\u00e1fica do usu\u00e1rio, do dispositivo em que o software esteja instalado ou do territ\u00f3rio a partir do qual seja acessado ou executado. A jurisdi\u00e7\u00e3o brasileira \u00e9 soberana e incontest\u00e1vel no que diz respeito a este produto, sem qualquer exce\u00e7\u00e3o territorial.',
    'O reposit\u00f3rio oficial do projeto, que serve como \u00fanico canal leg\u00edtimo de distribui\u00e7\u00e3o, atualiza\u00e7\u00e3o, documenta\u00e7\u00e3o t\u00e9cnica e comunica\u00e7\u00e3o entre o Desenvolvedor e os usu\u00e1rios, encontra-se dispon\u00edvel em:',
    'https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Qualquer distribui\u00e7\u00e3o do software realizada fora deste reposit\u00f3rio oficial deve ser considerada n\u00e3o autorizada e potencialmente irregular, sendo de responsabilidade exclusiva de quem a promoveu.'
])

# Section 2
add_section(doc, '2. Natureza, Finalidade e Escopo do Software', [
    'O ASI \u00e9 um software de natureza estritamente t\u00e9cnica, acad\u00eamica, educacional e de pesquisa aplicada. Sua fun\u00e7\u00e3o prim\u00e1ria \u00e9 a visualiza\u00e7\u00e3o cartogr\u00e1fica interativa de alta performance (WebGL 60fps via Deck.gl + MapLibre), a an\u00e1lise estat\u00edstica e geoestat\u00edstica de dados geoespaciais relacionados ao \u00cdndice Topogr\u00e1fico de Umidade (TWI \u2014 Topographic Wetness Index), aplicados \u00e0 identifica\u00e7\u00e3o de zonas de suscetibilidade a inunda\u00e7\u00f5es, ao planejamento territorial de suporte \u00e0 tomada de decis\u00e3o e \u00e0 correla\u00e7\u00e3o multi-fonte de dados hidrol\u00f3gicos, demogr\u00e1ficos, socioecon\u00f4micos e de eventos hist\u00f3ricos.',
    'O sistema integra, em tempo de execu\u00e7\u00e3o, as seguintes capacidades t\u00e9cnicas:',
    '\u2022 C\u00e1lculo e classifica\u00e7\u00e3o de TWI a partir de MDE (SRTM 30m) via pipeline DuckDB + Polars + GeoParquet (queries sub-ms);',
    '\u2022 Renderiza\u00e7\u00e3o de mapa WebGL com componente React customizado (AsiMap) + Folium/Leaflet fallback;',
    '\u2022 Cross-filtering espacial sem loops via m\u00e1quina de estados (SelectionState + EventOrigin + debounce);',
    '\u2022 Dashboards geoestat\u00edsticos (Plotly) com ranking IRA por bairro, s\u00e9ries hist\u00f3ricas de precipita\u00e7\u00e3o (APAC/INMET/NASA POWER), correla\u00e7\u00e3o TWI \u00d7 Defesa Civil;',
    '\u2022 Diagn\u00f3stico ponto-clique com buffer 500m, heatmap de risco, hidrografia, malha territorial oficial;',
    '\u2022 Observabilidade completa: OpenTelemetry (traces/metrics), Prometheus/Grafana, Loki, Tempo, Pyroscope;',
    '\u2022 Conformidade WCAG 2.1 AA, reduced motion, high contrast, design tokens + atomic components.',
    'ESTE SISTEMA N\u00c3O FOI DESENVOLVIDO, N\u00c3O EST\u00c1 HOMOLOGADO E N\u00c3O DEVE SER UTILIZADO PARA QUAISQUER DAS SEGUINTES FINALIDADES:',
    '\u2022 Manipula\u00e7\u00e3o, modifica\u00e7\u00e3o ou edi\u00e7\u00e3o de dados geoespaciais para fins n\u00e3o previstos nestes termos;',
    '\u2022 Uso em sistemas de alerta de emerg\u00eancia, evacua\u00e7\u00e3o ou defesa civil sem valida\u00e7\u00e3o t\u00e9cnica independente por profissional habilitado e registro no CREA/CAU;',
    '\u2022 Substitui\u00e7\u00e3o de laudos, vistorias geot\u00e9cnicas, an\u00e1lises de risco ou estudos de impacto ambiental emitidos por profissionais legalmente habilitados;',
    '\u2022 Aplica\u00e7\u00f5es comerciais, governamentais ou institucionais sem autoriza\u00e7\u00e3o pr\u00e9via, expressa e documentada do Desenvolvedor;',
    '\u2022 Fins militares, de vigil\u00e2ncia, rastreamento, monitoramento de pessoas ou qualquer uso que represente risco \u00e0 privacidade de terceiros;',
    '\u2022 Tomada de decis\u00e3o em situa\u00e7\u00f5es de risco de vida, emerg\u00eancia clim\u00e1tica ou gest\u00e3o de desastres sem valida\u00e7\u00e3o independente;',
    '\u2022 Engenharia reversa com finalidade de replicação comercial ou concorrencial.',
    'ATEN\u00c7\u00c3O: O uso do software fora das finalidades descritas acima \u00e9 de responsabilidade exclusiva do usu\u00e1rio, eximindo completamente o Desenvolvedor de qualquer responsabilidade civil, criminal ou administrativa decorrente.'
])

# Section 3
add_section(doc, '3. Requisitos T\u00e9cnicos M\u00ednimos e Consci\u00eancia do Usu\u00e1rio', [
    'Este software \u00e9 destinado a um p\u00fablico t\u00e9cnico espec\u00edfico. Ao instalar, executar, acessar ou distribuir o ASI, o usu\u00e1rio declara e garante, de forma irrevog\u00e1vel, que possui conhecimento t\u00e9cnico equivalente ou superior a:',
    '\u2022 N\u00edvel intermedi\u00e1rio a avan\u00e7ado em an\u00e1lise de dados geoespaciais, com dom\u00ednio de ferramentas e linguagens como Python 3.12+, Pandas 2.x, Polars, DuckDB, PyArrow, GeoPandas e bibliotecas correlatas;',
    '\u2022 Fundamentos de desenvolvimento de sistemas web modernos, com compreens\u00e3o de arquiteturas cliente-servidor, frameworks reativos (Streamlit 1.35+), WebSockets, WebGL, WebAssembly;',
    '\u2022 No\u00e7\u00f5es s\u00f3lidas de engenharia de dados, incluindo pipelines ETL/ELT, transforma\u00e7\u00e3o e carregamento de bases geoespaciais (GeoParquet, Shapefile, GeoJSON), valida\u00e7\u00e3o de schemas (Pandera);',
    '\u2022 Conhecimento em ci\u00eancia da computacao ou engenharia da computacao, suficiente para compreender o fluxo logico, a estrutura modular (src/api, src/core, src/processing, src/sigweb, src/analysis) e a maquina de estados de cross-filtering;',
    '\u2022 Capacidade de interpretar dados geoespaciais, coordenadas geogr\u00e1ficas, projecoes cartograficas (UTM SIRGAS 2000 EPSG:31985 <-> WGS84 EPSG:4326), indices geomorfometricos (TWI, slope, flow accumulation) e estatistica espacial;',
    '\u2022 Nocoes de observabilidade (OpenTelemetry, Prometheus, Grafana, Loki, Tempo) e CI/CD (GitHub Actions) para ambientes de producao.',
    'AVISO FORMAL: Caso o usuario nao possua os conhecimentos tecnicos descritos acima, fica expressamente proibido instalar, executar, modificar, distribuir ou tentar utilizar este software de qualquer forma que nao seja estritamente a execucao conforme as instrucoes oficiais documentadas (launch.bat, INSTRUCTIONS.md, README.md). O nao cumprimento desta clausula configura uso indevido e sujeita o infrator as penalidades previstas neste documento e na legislacao brasileira aplicavel.'
])

# Section 4
add_section(doc, '4. Licenciamento e Propriedade Intelectual', [
    'O ASI e distribuido sob a Licenca Apache 2.0 (codigo-fonte), cujos termos completos encontram-se disponiveis em: https://www.apache.org/licenses/LICENSE-2.0 e no arquivo LICENSE na raiz do repositorio. Os dados derivados e documentacao estao sob CC-BY-4.0, respeitando as licencas das fontes originais.',
    'Embora a Licenca Apache 2.0 permita uso, reproducao, distribuicao e criacao de trabalhos derivados, o presente documento impõe restricoes adicionais de natureza contratual, aceitas automaticamente pelo usuario no momento de qualquer interacao com o software (download, clone, execucao, distribuicao), conforme detalhado a seguir. Estas restricoes sao compativeis com a Secao 4(d) e Secao 9 da Apache 2.0.',
    '4.1 O que e permitido',
    '\u2022 Executar o software para fins educacionais, de pesquisa, analise pessoal e planejamento territorial nao-critico, conforme as instrucoes oficiais;',
    '\u2022 Compartilhar o software gratuitamente, desde que por meio do repositorio oficial ou com link direto a ele, sem alterar seu conteudo;',
    '\u2022 Citar o software em trabalhos academicos, relatorios tecnicos, teses, dissertacoes e publicacoes cientificas, com os devidos creditos ao Desenvolvedor e referencia ao repositorio oficial (formato sugerido: "Lima, L.L. (2026). ASI \u2014 Atlas de Suscetibilidade a Inundacoes v3.3. https://github.com/LuciolLima/ASI");',
    '\u2022 Sugerir melhorias e contribuicoes, exclusivamente por meio dos canais oficiais do repositorio (Issues, Pull Requests ou contato direto via e-mail institucional);',
    '\u2022 Utilizar trechos de codigo (snippets) em projetos proprios, desde que mantidos os avisos de copyright, licenca e atribuicao original (conforme Apache 2.0 Secao 4).',
    '4.2 O que e expressamente proibido',
    '\u2022 Vender, sublicenciar, cobrar ou atribuir qualquer valor monetario ao software ou a produtos derivados dele, mesmo que modificados;',
    '\u2022 Remover, alterar ou ocultar os creditos, avisos de copyright, licenca ou qualquer identificacao do Desenvolvedor original;',
    '\u2022 Distribuir versoes modificadas do software sem autorizacao previa, expressa e documentada do Desenvolvedor;',
    '\u2022 Publicar o software ou trechos dele em plataformas de terceiros como se fosse de autoria propria (plagio de software);',
    '\u2022 Utilizar o nome, marca, imagem, identidade visual (design tokens, logotipo, paleta de cores) ou identidade do software ou do Desenvolvedor para fins comerciais sem autorizacao;',
    '\u2022 Incorporar o ASI (total ou parcialmente) em produtos SaaS, plataformas pagas, consultorias comerciais ou servicos que gerem receita direta ou indireta sem autorizacao contratual previa;',
    '\u2022 Remover ou desabilitar mecanismos de telemetria, health checks, observabilidade ou validacao de integridade (checksums SHA256);',
    '\u2022 Realizar engenharia reversa do componente React/TypeScript (AsiMap) para extracao de logica proprietaria de renderizacao WebGL.',
    'O descumprimento das proibicoes acima configura violacao de propriedade intelectual, podendo acarretar responsabilizacao civil e criminal nos termos da Lei n\u00ba 9.610/1998 (Lei de Direitos Autorais), Lei n\u00ba 9.609/1998 (Lei do Software) e demais dispositivos legais aplicaveis.'
])

# Section 5
add_section(doc, '5. Gratuidade e Vedacao a Comercializacao', [
    'O ASI e, em sua totalidade, um produto gratuito e de codigo aberto (open source). Sua distribuicao sem custo e uma decisao deliberada e irrevogavel do Desenvolvedor, fundamentada nos principios de democratizacao do conhecimento tecnico, ciencia aberta (Open Science), reprodutibilidade computacional e compromisso com a mitigacao de riscos de inundacao em territorios vulneraveis.',
    'Sendo assim, fica expressamente vedado, sob qualquer hipotese, circunstancia ou justificativa:',
    '\u2022 Cobrar qualquer valor pelo acesso, instalacao, uso, suporte, treinamento, customizacao ou distribuicao do software, ainda que parcialmente;',
    '\u2022 Incluir o software ou partes dele em produtos pagos, assinaturas, pacotes comerciais ou servicos de terceiros sem autorizacao previa, expressa e por escrito;',
    '\u2022 Utilizar o software como isca, atrativo ou diferencial em modelos de negocio que gerem receita direta ou indireta ao usuario ou a terceiros (incluindo modelos "freemium", "open core" ou "dual licensing" nao autorizados).',
    'A comercializacao nao autorizada deste software, ainda que disfarçada de servico, consultoria, suporte, implantacao, treinamento ou customizacao, constitui violacao contratual grave e pode configurar crimes previstos no Codigo Penal Brasileiro (art. 184, 185, 195), na Lei n\u00ba 9.610/1998, Lei n\u00ba 9.609/1998 e na legislacao de protecao ao consumidor (Lei n\u00ba 8.078/1990 \u2014 CDC).'
])

# Section 6
add_section(doc, '6. Transferencia e Assuncao de Responsabilidade pelo Usuario', [
    'A partir do momento em que o usuario realiza o download, clona o repositorio, executa o software ou interage com qualquer componente do ASI (incluindo APIs externas consumidas pelo sistema), ele automaticamente e de forma irrevogavel assume para si plena responsabilidade pelo uso que fizer do sistema, pelos dados que processar, pelas conclusoes que extrair e por todas as consequencias, diretas ou indiretas, que desse uso possam resultar.',
    'Esta assuncao de responsabilidade inclui, sem se limitar a:',
    '\u2022 Responsabilidade por danos causados a terceiros em decorrencia de interpretacoes equivocadas, uso inadequado ou extrapolacao indevida das informacoes geradas pelo sistema;',
    '\u2022 Responsabilidade por alteracoes, modificacoes, adulteracoes ou desativacao de validacoes no codigo-fonte, nos dados processados ou nos schemas de validacao (Pandera);',
    '\u2022 Responsabilidade por violacoes de privacidade, seguranca de dados, LGPD (Lei n\u00ba 13.709/2018) ou direitos de terceiros praticadas com o auxilio do software;',
    '\u2022 Responsabilidade por danos ao proprio sistema do usuario, perda de dados, instabilidades, vazamento de credenciais (API keys CARTO, etc.) decorrentes de uso incompativel com os requisitos tecnicos ou de ma configuracao de ambiente;',
    '\u2022 Responsabilidade pelo uso de dados de terceiros (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Prefeitura Cabo, SEINFRA-PE, CONDEPE-FIDEM) em desacordo com os termos de uso de cada fonte original;',
    '\u2022 Responsabilidade por decisoes urbanisticas, imobiliarias, securitarias ou de gestao publica baseadas unicamente nos outputs do ASI sem validacao tecnica independente.',
    'O Desenvolvedor nao podera, em nenhuma circunstancia, ser responsabilizado por danos diretos, indiretos, incidentais, especiais, exemplares, punitivos ou consequenciais (incluindo lucros cessantes, perda de dados, interrupcao de negocio, danos morais, danos a reputacao) resultantes do uso ou da impossibilidade de uso do software, mesmo que advertido da possibilidade de tais danos.'
])

# Section 7
add_section(doc, '7. Proibicao de Uso Indevido e Ilegal', [
    'E terminantemente proibido o uso do ASI para fins ilicitos, imorais, antieticos ou que violem qualquer dispositivo da legislacao brasileira ou do direito internacional. Mais especificamente:',
    '\u2022 Fica proibido o uso para manipulacao de dados publicos com fins fraudulentos, para induzir autoridades a erro ou para fundamentar atos administrativos viciados;',
    '\u2022 Fica proibido o uso para criacao de desinformacao, noticias falsas, analises tendenciosas ou relatorios enganosos com dados gerados pelo sistema;',
    '\u2022 Fica proibido o uso para fins de vigilancia, espionagem, rastreamento de pessoas, geolocalizacao nao autorizada ou coleta de dados pessoais/sensiveis sem consentimento livre, informado e especifico (LGPD art. 7o);',
    '\u2022 Fica proibido o uso que configure qualquer forma de concorrencia desleal (Lei n\u00ba 9.279/1996 art. 195), parasitismo, aproveitamento indevido da reputacao do software ou passing off;',
    '\u2022 Fica proibido o uso para instrumentalizacao de politicas publicas sem transparencia metodologica e validacao por comissao tecnica multidisciplinar;',
    '\u2022 Fica proibido o uso em processos licitatórios, contratos administrativos ou concessões publicas sem divulgacao previa da metodologia, limitacoes e incertezas do modelo.',
    'O uso indevido sera tratado com o maximo rigor legal disponivel, incluindo notificacao extrajudicial, acao civil de indenizacao por danos materiais e morais, acao de obrigacao de fazer/nao fazer (tutela de urgencia), representacao ao MPF/MPPE, e, quando cabivel, representacao criminal perante as autoridades competentes (Policia Federal, Delegacia de Crimes Ciberneticos).'
])

# Section 8
add_section(doc, '8. Estado do Software \u2014 Versao 3.3.0 (Estavel, Operacional e Auditable)', [
    'O ASI, na versao 3.3.0 ora disponibilizada, encontra-se em estado estavel, operacional e auditable. Esta afirmacao baseia-se em:',
    '\u2022 59 testes automatizados passando (unitarios + integracao) via pytest com cobertura >70%;',
    '\u2022 CI/CD completo no GitHub Actions (6 jobs: lint, type-check, test, security, build, deploy);',
    '\u2022 Validacao de schemas Pandera em 100% dos DataFrames de entrada/saida;',
    '\u2022 Verificacao de integridade SHA256 em todos os assets de dados (data_V3.0-System.zip);',
    '\u2022 Health checks expostos em /_health e metricas Prometheus em /metrics;',
    '\u2022 Build reproduzivel do componente React (Vite + TypeScript) com bundle inlined no Streamlit;',
    '\u2022 Documentacao tecnica completa: README.md, INSTRUCTIONS.md, DTM (docs/academic_context/DTM_doc.md), Instituicoes (docs/academic_context/institutions.md), Changelog.',
    'Esta versao NAO E:',
    '\u2022 Um produto comercial homologado para venda ou licenciamento em mercado de software;',
    '\u2022 Um software de codigo-fonte aberto para edicao irrestrita \u2014 embora o codigo seja visivel no repositorio, sua edicao e redistribuicao estao sujeitas as restricoes contratuais deste documento (Secao 4.2), alem da Apache 2.0;',
    '\u2022 Um sistema projetado para uso em producao critica, emergencias climaticas, evacuações, decisoes de alto impacto financeiro ou risco de vida sem validacao tecnica independente, homologacao por orgao competente e termo de responsabilidade assinado;',
    '\u2022 Um sistema de alerta precoce (Early Warning System) certificado por orgao meteorologico ou de defesa civil oficial;',
    '\u2022 Isento de incertezas inerentes a modelos geomorfometricos baseados em DEM de 30m (SRTM), interpolados, com erros verticais conhecidos (\u00b15-10m) e limitacoes em areas urbanas densas.',
    'Eventuais bugs, limitacoes, comportamentos inesperados ou sugestoes de melhoria devem ser reportados exclusivamente pelo canal oficial do repositorio, por meio de abertura de Issues devidamente documentadas (template: bug_report.yml, feature_request.yml) ou Pull Requests referenciando Issue existente.'
])

# Section 9
add_section(doc, '9. Contribuicoes, Sugestoes e Melhorias', [
    'O Desenvolvedor valoriza a colaboracao tecnica responsavel e a ciencia aberta. No entanto, qualquer contribuicao, modificacao, melhoria ou sugestao ao codigo-fonte, a documentacao, aos dados derivados ou aos assets do ASI deve obrigatoriamente seguir o fluxo de governanca a seguir:',
    '1. Abrir uma Issue no repositorio oficial, descrevendo detalhadamente a proposta, sua motivacao tecnica, o impacto esperado, testes realizados e referencias bibliograficas (se aplicavel);',
    '2. Aguardar analise, feedback e, quando aplicavel, autorizacao previa e expressa do Desenvolvedor (labels: approved, needs-rfc, wontfix);',
    '3. Submeter as alteracoes somente apos aprovacao, por meio de Pull Request devidamente documentado, referenciando a Issue correspondente, com testes passando (CI verde) e descricao clara das mudancas;',
    '4. Aceitar que o Desenvolvedor detem a decisao final sobre inclusao, modificacao, rejeicao ou solicitacao de refatoracao de qualquer contribuicao, sem necessidade de justificativa detalhada alem do feedback tecnico;',
    '5. Assinar o CLA (Contributor License Agreement) implicito ao submeter PR: a contribuicao passa a ser licenciada sob Apache 2.0 + restricoes deste documento, com atribuicao de autoria preservada.',
    'Contribuicoes aceitas e publicadas serao devidamente creditadas no repositorio (AUTHORS.md, CHANGELOG, release notes), respeitando a autoria original e o esforco de cada colaborador. Modificacoes realizadas sem autorizacao previa, independentemente da intencao, serao tratadas como violacao destes termos (Secao 4.2).'
])

# Section 10
add_section(doc, '10. Uso de Imagem, Publicacoes e Referencias Externas', [
    'O uso da imagem, identidade visual (design tokens: cores #080C10, #00B4D8, #00F5D4, tipografia IBM Plex Mono/Sans), nome, marca, logotipo ou qualquer elemento identificavel do ASI em publicacoes, redes sociais, materiais de marketing, videos, artigos, teses, relatorios tecnicos ou qualquer outro meio de comunicacao deve respeitar as seguintes diretrizes:',
    '\u2022 Citacoes academicas e cientificas sao livres e incentivadas, desde que acompanhadas dos devidos creditos ao Desenvolvedor e referencia ao repositorio oficial (DOI/Zenodo se disponivel);',
    '\u2022 Publicacoes em redes sociais que demonstrem o uso legitimo do software sao permitidas, desde que nao impliquem endosso comercial nao autorizado, parceria institucional inexistente ou certificacao oficial;',
    '\u2022 E proibida qualquer publicacao que distorca, deturpe, apresente o software de forma enganosa ao publico, omita suas limitacoes (Secao 8) ou sugira capacidades nao implementadas;',
    '\u2022 E proibida a criacao de canais, paginas, perfis, sites espelho, forks publicos nao-oficiais ou dominios que se apresentem como representantes oficiais do ASI sem autorizacao expressa e por escrito do Desenvolvedor;',
    '\u2022 E proibido o uso de capturas de tela, videos ou demos do ASI em materiais de venda de cursos, treinamentos, consultorias ou produtos terceiros sem autorizacao contratual.',
    'O descumprimento destas diretrizes podera acarretar solicitacao formal de remocao de conteudo (DMCA/takedown), notificacao as plataformas digitais envolvidas (GitHub, YouTube, LinkedIn, Instagram, TikTok, etc.), alem de acao judicial por uso indevido de imagem, marca, concorrencia desleal e danos morais/reputacionais.'
])

# Section 11
add_section(doc, '11. Fundamentacao Legal \u2014 Legislacao Brasileira Aplicavel', [
    'Este software, seus termos de uso, sua documentacao, seus dados derivados e sua identidade visual sao protegidos pelo ordenamento juridico brasileiro, compreendendo, entre outros dispositivos, as seguintes legislacoes (vigentes e consolidadas):',
    'Lei n\u00ba 9.610/1998 \u2014 Lei de Direitos Autorais (LDA): Estabelece que obras intelectuais, incluindo programas de computador, suas documentacoes, interfaces, design visual e bases de dados estruturadas, sao protegidas como criacoes do espirito humano. O ASI, como obra original, encontra-se protegido por esta lei, que assegura ao Desenvolvedor os direitos morais (inalienaveis, irrenunciaveis, perpetuos) e patrimoniais sobre sua criacao. Reproducao, distribuicao, modificacao, adaptacao, traducao ou qualquer forma de exploracao economica sem autorizacao constitui violacao passivel de indenizacao civil (arts. 101-110) e responsabilidade criminal (art. 184).',
    'Lei n\u00ba 9.609/1998 \u2014 Lei do Software (Lei de Protecao de Programas de Computador): Regula especificamente a protecao da propriedade intelectual de programas de computador no Brasil. Determina que o registro e a protecao do software independem de inscricao formal no INPI, sendo automaticos a partir da criacao (art. 2o). Uso, copia, modificacao, engenharia reversa nao autorizada (exceto interoperabilidade art. 6o), distribuicao ou comercializacao nao autorizados sao passiveis de sancoes civis (indenizacao por perdas e danos, lucros cessantes, busca e apreensao) e penais (art. 12-15), incluindo multa e reclusao.',
    'Lei n\u00ba 13.709/2018 \u2014 Lei Geral de Protecao de Dados Pessoais (LGPD): Disciplina o tratamento de dados pessoais no Brasil, garantindo transparencia, finalidade legitima, adequacao, necessidade, livre acesso, qualidade, seguranca, prevencao, nao discriminacao e prestacao de contas (art. 6o). Embora o ASI nao colete dados pessoais de forma direta (nao ha autenticacao, cadastro, tracking de usuarios, cookies de marketing), qualquer uso do software que envolva processamento de dados de pessoas identificaveis (ex: cruzamento com dados de defesa civil contendo enderecos, nomes) deve observar rigorosamente os principios da LGPD. O usuario e o unico responsavel (controlador) pelo tratamento de dados pessoais eventualmente realizados por meio do sistema, devendo atender aos direitos dos titulares (art. 18) e notificar a ANPD em caso de incidente (art. 48).',
    'Lei n\u00ba 12.965/2014 \u2014 Marco Civil da Internet (MCI): Estabelece principios, garantias, direitos e deveres para o uso da Internet no Brasil. Regula a responsabilidade por danos causados por conteudo gerado na rede (art. 19 \u2014 apenas apos ordem judicial), protege a privacidade dos usuarios (art. 7-11), neutralidade de rede (art. 9) e estabelece criterios claros de responsabilizacao. Uso do ASI para fins que violem direitos de terceiros no ambiente digital (difamacao, exposicao indevida, vazamento) estara sujeito as sancoes previstas nesta lei.',
    'Lei n\u00ba 8.078/1990 \u2014 Codigo de Defesa do Consumidor (CDC): Embora o ASI seja gratuito (nao configurando relacao de consumo stricto sensu), situacoes que envolvam praticas abusivas na distribuicao, comercializacao nao autorizada, publicidade enganosa (art. 37), praticas comerciais abusivas (art. 39) ou inducao ao erro do publico em relacao as caracteristicas, finalidade, origem, versao ou capacidades do software poderao ser enquadradas nesta lei por analogia e jurisprudencia (Súmula 481 STJ).',
    'Lei n\u00ba 9.279/1996 \u2014 Lei da Propriedade Industrial (LPI): Protege marcas, nomes comerciais, sinais distintivos, indicacoes geograficas e reprime a concorrencia desleal (art. 195). O nome "ASI \u2014 Atlas de Suscetibilidade a Inundacoes", sua identidade visual, logotipo e design tokens constituem ativos de propriedade intelectual do Desenvolvedor, protegidos independentemente de registro no INPI (direito de precedencia e uso).',
    'Codigo Penal Brasileiro \u2014 Decreto-Lei n\u00ba 2.848/1940 (e alteracoes): Tipificam como crimes condutas como: violacao de direito autoral (art. 184 \u2014 reclusao 2 a 4 anos + multa), usurpacao de nome ou pseudonimo alheio (art. 185 \u2014 detencao 3 meses a 1 ano + multa), concorrencia desleal (art. 195 LPI \u2014 reclusao 3 meses a 1 ano + multa), estelionato (art. 171 \u2014 se houver vantagem ilicita), falsidade ideologica (art. 299 \u2014 se houver documento publico/particular falso). O uso criminoso ou malicioso do ASI, incluindo plagio, venda nao autorizada, distribuicao ilegal, engenharia reversa com fim comercial, estara sujeito a inquerito policial, denuncia criminal e pena de reclusao conforme a gravidade do delito.',
    'Lei n\u00ba 12.527/2011 \u2014 Lei de Acesso a Informacao (LAI): Garante o direito de acesso a informacao publica. O ASI, ao consumir e processar dados de orgaos publicos (IBGE, APAC, SEPDEC, INMET, Prefeituras), atua em consonancia com a LAI, promovendo transparencia ativa e reutilizacao de dados abertos. O usuario deve respeitar as licencas de cada fonte (ver Secao 14 e docs/academic_context/institutions.md).',
    'Decreto n\u00ba 10.968/2022 \u2014 Estrategia Nacional de Seguranca Cibernetica (E-Ciber): O ASI implementa boas praticas de seguranca: validacao de entrada (Pandera), integridade de assets (SHA256), rate limiting em APIs externas, ausencia de coleta de dados sensiveis, health checks, observabilidade. O usuario deve manter seu ambiente (Python, dependencias, OS, rede) atualizado e seguro.'
])

# Section 12
add_section(doc, '12. Jurisdicao e Foro Competente', [
    'Todos os litigios, controversias, disputas ou questoes decorrentes ou relacionadas a estes Termos de Uso, ao software ASI, aos seus dados derivados, a sua documentacao, a sua identidade visual ou a conduta de qualquer usuario serao submetidos a jurisdição exclusiva dos tribunais brasileiros, com foro eleito na comarca de domicilio do Desenvolvedor (Recife/PE), renunciando as partes a qualquer outro foro, por mais privilegiado que seja.',
    'A legislacao brasileira e soberana e exclusivamente aplicavel, independentemente de qualquer convenção internacional, acordo bilateral, tratado multilateral ou legislacao estrangeira que eventualmente pudesse ser invocada pelo usuario com base em sua localidade geografica, nacionalidade ou sede de pessoa juridica.'
])

# Section 13
add_section(doc, '13. Aceitacao Tacita, Automatica e Irrevogavel dos Termos', [
    'Ao realizar o download, clonar o repositorio, instalar, executar, distribuir, modificar, inspecionar, compilar, empacotar ou interagir de qualquer forma com o software ASI (incluindo execucao via launch.bat, streamlit run app.py, Docker, Kubernetes, CI/CD, ou qualquer outro meio), o usuario declara, de maneira tacita, automatica e irrevogavel, que:',
    '\u2022 Leu, compreendeu e concorda integralmente com todos os termos deste documento e com a Licenca Apache 2.0;',
    '\u2022 Possui os conhecimentos tecnicos minimos exigidos descritos na Clausula 3;',
    '\u2022 Assume plena responsabilidade pelo uso que fara do software, conforme descrito na Clausula 6;',
    '\u2022 Esta ciente das proibicoes expressas neste documento e se compromete a nao viola-las;',
    '\u2022 Reconhece a jurisdicao brasileira como exclusivamente competente para quaisquer disputas;',
    '\u2022 Reconhece que os dados de terceiros (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Prefeitura Cabo, SEINFRA-PE, CONDEPE-FIDEM) possuem licencas proprias que devem ser respeitadas;',
    '\u2022 Reconhece que o software e fornecido "AS IS" (como esta), sem garantias de qualquer natureza (Apache 2.0 Secao 7).',
    'A IGNORANCIA DESTES TERMOS NAO EXIME O USUARIO DE RESPONSABILIDADE. ESTE DOCUMENTO ESTA PUBLICAMENTE DISPONIVEL NO REPOSITORIO OFICIAL (ASI_Termos_de_Uso_PT.docx) E SUA LEITURA INTEGRAL E OBRIGACAO INCONDICIONAL DO USUARIO ANTES DE QUALQUER INTERACAO COM O SOFTWARE.'
])

# Section 14
add_section(doc, '14. Fontes de Dados \u2014 Licencas e Atribuicoes Obrigatorias', [
    'O ASI consome e processa dados das seguintes fontes oficiais. O usuario deve respeitar os termos de uso de cada fonte ao utilizar, redistribuir ou derivar produtos baseados nos outputs do ASI:',
    '',
    '| Fonte | Tipo | Licenca / Termos | Atribuicao Minima |',
    '|-------|------|------------------|-------------------|',
    '| IBGE (SIDRA, Malhas, SRTM via IBGE) | Dados censitarios, limites administrativos, DEM | Dominio publico / Uso livre com atribuicao (Lei 9.610 art. 8o) | "Fonte: IBGE" + ano da publicacao |',
    '| APAC-PE | Precipitacao, hidrologia | Dados abertos governo PE | "Fonte: APAC Pernambuco" |',
    '| SEPDEC-PE | Eventos de inundacao, danos | Dados abertos governo PE | "Fonte: Defesa Civil PE \u2014 SEPDEC" |',
    '| INMET | Meteorologia de superficie | Dominio publico / CC-BY 4.0 | "Fonte: INMET" |',
    '| MapBiomas (Colecao 10, Colecao 2 beta) | Cobertura/uso da terra (LULC) | CC-BY 4.0 | "Fonte: Projeto MapBiomas" + colecao/ano |',
    '| SRTM (NASA/USGS/NGA) | DEM 30m | Dominio publico (USGS) | "Fonte: SRTM/NASA/USGS via IBGE" |',
    '| NASA POWER (MERRA-2) | Reanalise agrometeorologica | Dominio publico NASA | "Fonte: NASA POWER / MERRA-2" |',
    '| Prefeitura Cabo de Santo Agostinho | Malha bairros oficial, zoneamento | Dados abertos municipais | "Fonte: Prefeitura do Cabo de Santo Agostinho" |',
    '| SEINFRA-PE | Infraestrutura, macrozoneamento | Dados abertos governo PE | "Fonte: SEINFRA-PE" |',
    '| CONDEPE-FIDEM | Planejamento territorial, relatorios | Dados abertos governo PE | "Fonte: CONDEPE-FIDEM" |',
    '| CARTO (Basemaps Positron, Dark Matter, Voyager) | Tiles raster/vector | CC-BY 4.0 + API Key | "\u00a9 OpenStreetMap contributors \u00a9 CARTO" + key |',
    '',
    'O documento completo de atribuicoes institucionais, historico de fomento e creditos tecnicos encontra-se em: docs/academic_context/institutions.md.'
])

# Section 15
add_section(doc, '15. Fomento a Pesquisa \u2014 Reconhecimento Obrigatorio', [
    'O desenvolvimento do ASI foi viabilizado por bolsas de Iniciacao Cientifica e Tecnologica (IC/IT) e infraestrutura concedidas pelas seguintes agencias. Qualquer publicacao, tese, relatorio ou derivacao do ASI deve incluir o reconhecimento ao fomento (padrao CNPq/CAPES/FACEPE):',
    '\u2022 FACEPE \u2014 Fundacao de Amparo a Ciencia e Tecnologia do Estado de Pernambuco (PIBIC, PIBITI, BIC-JR, APQ);',
    '\u2022 CNPq \u2014 Conselho Nacional de Desenvolvimento Cientifico e Tecnologico (PIBIC, PIBITI, PIC, Bolsa Produtividade);',
    '\u2022 CAPES \u2014 Coordenacao de Aperfeicoamento de Pessoal de Nivel Superior (PROEX, DS, PROSUP, Bolsas Mestrado/Doutorado);',
    '\u2022 METRO SUL \u2014 Programa de Inovacao Metropolitana / Regiao Metropolitana do Recife;',
    '\u2022 GRE \u2014 Grupo de Recursos Educacionais / Inovacao Academica (infraestrutura, licencas, suporte).',
    'Instituicao formadora: FACEP \u2014 Faculdade de Ciencias Educacionais de Pernambuco.'
])

# Section 16
add_section(doc, '16. Documentos Correlatos e Hierarquia Normativa', [
    'Este documento deve ser lido em conjunto com (ordem de prevalencia em caso de conflito):',
    '1. Licenca Apache 2.0 (LICENSE) \u2014 base legal do codigo-fonte;',
    '2. Estes Termos de Uso PT (ASI_Termos_de_Uso_PT.docx) \u2014 restricoes contratuais adicionais;',
    '3. Terms of Use EN (ASI_Terms_of_Use_EN.docx) \u2014 versao oficial em ingles (prevalece em disputas internacionais);',
    '4. README.md \u2014 visao geral, instalacao, uso, arquitetura;',
    '5. INSTRUCTIONS.md \u2014 instrucoes detalhadas de instalacao e operacao;',
    '6. DTM \u2014 Documentacao Tecnica e Metodologica (docs/academic_context/DTM_doc.md);',
    '7. Instituicoes e Creditos (docs/academic_context/institutions.md);',
    '8. Changelog (ASI_CHANGELOG_v3.0.pdf, RELEASE_NOTES_v3.1.md);',
    '9. requirements.txt / pyproject.toml \u2014 dependencias e versoes exatas;',
    '10. launch.bat \u2014 launcher oficial Windows (validacao de ambiente, .venv, build, testes).'
])

# Section 17
add_section(doc, '17. Disposicoes Finais', [
    '17.1 Se qualquer clausula destes Termos for declarada nula, invalida ou ineficaz por autoridade competente, as demais permanecerao em pleno vigor e efeito.',
    '17.2 A tolerancia do Desenvolvedor quanto a qualquer violacao nao constitui renuncia ao direito de exigir o cumprimento futuro, nem novacao tacita.',
    '17.3 O Desenvolvedor reserva-se o direito de atualizar estes Termos a qualquer momento, mediante publicacao de nova versao no repositorio oficial com versao incremental (SemVer: MAJOR.MINOR.PATCH). O uso continuo apos publicacao implica aceitacao da nova versao.',
    '17.4 Este documento e parte integrante e indissociavel do software ASI. A ausencia deste arquivo em qualquer distribuicao caracteriza distribuicao irregular e nao autorizada.',
    '17.5 Contato para assuntos juridicos, licenciamento comercial, parcerias institucionais, denuncias de uso indevido ou solicitacoes de autorizacao: lucio.lima@facep.edu.br (e-mail institucional FACEP) ou via Issues no repositorio oficial com label legal.'
])

# Footer
doc.add_paragraph()
doc.add_paragraph()
footer_items = [
    'ASI \u2014 Atlas de Suscetibilidade a Inundacoes',
    'Termos de Uso, Licenciamento e Responsabilidade \u2014 Versao 3.3',
    'Licenca Apache 2.0 (codigo) + CC-BY-4.0 (dados/docs) + Restricoes Contratuais Adicionais',
    'Regido pelas Leis da Republica Federativa do Brasil',
    'Desenvolvedor: Lucio Luiz de Lima',
    'Instituicao: FACEP \u2014 Faculdade de Ciencias Educacionais de Pernambuco',
    'Repositorio Oficial: https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Data de publicacao desta versao: Setembro 2026'
]
for item in footer_items:
    p = doc.add_paragraph(item)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(100, 100, 100)

doc.save('ASI_Termos_de_Uso_PT.docx')
print('Documento PT salvo com sucesso!')