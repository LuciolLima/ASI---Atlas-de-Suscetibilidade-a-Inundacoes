from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading('ASI — Atlas de Suscetibilidade a Inundações', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('SIGWeb — Versão 3.3.0')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0, 180, 216)

doc.add_paragraph()

# Header
header = doc.add_heading('TERMOS DE USO, LICENCIAMENTO E RESPONSABILIDADE', level=1)
header.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Documento Oficial — Leia integralmente antes de instalar, executar ou distribuir este software.')
run.bold = True
run.font.size = Pt(11)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Versão do documento: 3.3 | Vigência: a partir da data de publicação no repositório oficial')
run.font.size = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Desenvolvido e regido sob as leis da República Federativa do Brasil')
run.font.size = Pt(10)

doc.add_page_break()

def add_section(doc, title, paragraphs):
    if title:
        doc.add_heading(title, level=2)
    for para in paragraphs:
        if para == '':
            doc.add_paragraph()
        elif para.startswith('•') or para.startswith('1.') or para.startswith('2.') or para.startswith('3.') or para.startswith('4.') or para.startswith('5.') or para.startswith('6.') or para.startswith('7.') or para.startswith('8.') or para.startswith('9.') or para.startswith('10.') or para.startswith('11.') or para.startswith('12.') or para.startswith('13.') or para.startswith('14.') or para.startswith('15.') or para.startswith('16.') or para.startswith('17.'):
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
add_section(doc, '1. Identificação do Software e do Desenvolvedor', [
    'O presente documento constitui os Termos de Uso, Licenciamento e Responsabilidade do software denominado ASI — Atlas de Suscetibilidade a Inundações, desenvolvido e mantido por seu criador, Lucio Luiz de Lima, doravante denominado simplesmente Desenvolvedor. O ASI é um sistema de informação geográfica para a Web (SIGWeb) de caráter educacional, científico e técnico, construído sob uma arquitetura modular de pipeline de engenharia de dados geoespaciais, com foco na visualização interativa, análise estatística geoespacial e comunicação de índices de suscetibilidade hidrológica a partir de parâmetros topográficos, geomorfométricos e meteorológicos.',
    'Este software foi concebido, projetado e desenvolvido integralmente no Brasil, sendo, portanto, regido, interpretado e protegido exclusivamente pelas leis da República Federativa do Brasil, independentemente da localidade geográfica do usuário, do dispositivo em que o software esteja instalado ou do território a partir do qual seja acessado ou executado. A jurisdição brasileira é soberana e incontestável no que diz respeito a este produto, sem qualquer exceção territorial.',
    'O repositório oficial do projeto, que serve como único canal legítimo de distribuição, atualização, documentação técnica e comunicação entre o Desenvolvedor e os usuários, encontra-se disponível em:',
    'https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Qualquer distribuição do software realizada fora deste repositório oficial deve ser considerada não autorizada e potencialmente irregular, sendo de responsabilidade exclusiva de quem a promoveu.'
])

# Section 2
add_section(doc, '2. Natureza, Finalidade e Escopo do Software', [
    'O ASI é um software de natureza estritamente técnica, acadêmica, educacional e de pesquisa aplicada. Sua função primária é a visualização cartográfica interativa de alta performance (WebGL 60fps via Deck.gl + MapLibre), a análise estatística e geoestatística de dados geoespaciais relacionados ao Índice Topográfico de Umidade (TWI — Topographic Wetness Index), aplicados à identificação de zonas de suscetibilidade a inundações, ao planejamento territorial de suporte à tomada de decisão e à correlação multi-fonte de dados hidrológicos, demográficos, socioeconômicos e de eventos históricos.',
    'O sistema integra, em tempo de execução, as seguintes capacidades técnicas:',
    '• Cálculo e classificação de TWI a partir de MDE (SRTM 30m) via pipeline DuckDB + Polars + GeoParquet (queries sub-ms);',
    '• Renderização de mapa WebGL com componente React customizado (AsiMap) + Folium/Leaflet fallback;',
    '• Cross-filtering espacial sem loops via máquina de estados (SelectionState + EventOrigin + debounce);',
    '• Dashboards geoestatísticos (Plotly) com ranking IRA por bairro, séries históricas de precipitação (APAC/INMET/NASA POWER), correlação TWI × Defesa Civil;',
    '• Diagnóstico ponto-clique com buffer 500m, heatmap de risco, hidrografia, malha territorial oficial;',
    '• Observabilidade completa: OpenTelemetry (traces/metrics), Prometheus/Grafana, Loki, Tempo, Pyroscope;',
    '• Conformidade WCAG 2.1 AA, reduced motion, high contrast, design tokens + atomic components.',
    'ESTE SISTEMA NÃO FOI DESENVOLVIDO, NÃO ESTÁ HOMOLOGADO E NÃO DEVE SER UTILIZADO PARA QUAISQUER DAS SEGUINTES FINALIDADES:',
    '• Manipulação, modificação ou edição de dados geoespaciais para fins não previstos nestes termos;',
    '• Uso em sistemas de alerta de emergência, evacuação ou defesa civil sem validação técnica independente por profissional habilitado e registro no CREA/CAU;',
    '• Substituição de laudos, vistorias geotécnicas, análises de risco ou estudos de impacto ambiental emitidos por profissionais legalmente habilitados;',
    '• Aplicações comerciais, governamentais ou institucionais sem autorização prévia, expressa e documentada do Desenvolvedor;',
    '• Fins militares, de vigilância, rastreamento, monitoramento de pessoas ou qualquer uso que represente risco à privacidade de terceiros;',
    '• Tomada de decisão em situações de risco de vida, emergência climática ou gestão de desastres sem validação independente;',
    '• Engenharia reversa com finalidade de replicação comercial ou concorrencial.',
    'ATENÇÃO: O uso do software fora das finalidades descritas acima é de responsabilidade exclusiva do usuário, eximindo completamente o Desenvolvedor de qualquer responsabilidade civil, criminal ou administrativa decorrente.'
])

# Section 3
add_section(doc, '3. Requisitos Técnicos Mínimos e Consciência do Usuário', [
    'Este software é destinado a um público técnico específico. Ao instalar, executar, acessar ou distribuir o ASI, o usuário declara e garante, de forma irrevogável, que possui conhecimento técnico equivalente ou superior a:',
    '• Nível intermediário a avançado em análise de dados geoespaciais, com domínio de ferramentas e linguagens como Python 3.12+, Pandas 2.x, Polars, DuckDB, PyArrow, GeoPandas e bibliotecas correlatas;',
    '• Fundamentos de desenvolvimento de sistemas web modernos, com compreensão de arquiteturas cliente-servidor, frameworks reativos (Streamlit 1.35+), WebSockets, WebGL, WebAssembly;',
    '• Noções sólidas de engenharia de dados, incluindo pipelines ETL/ELT, transformação e carregamento de bases geoespaciais (GeoParquet, Shapefile, GeoJSON), validação de schemas (Pandera);',
    '• Conhecimento em ciência da computação ou engenharia da computação, suficiente para compreender o fluxo lógico, a estrutura modular (src/api, src/core, src/processing, src/sigweb, src/analysis) e a máquina de estados de cross-filtering;',
    '• Capacidade de interpretar dados geoespaciais, coordenadas geográficas, projeções cartográficas (UTM SIRGAS 2000 EPSG:31985 ↔ WGS84 EPSG:4326), índices geomorfométricos (TWI, slope, flow accumulation) e estatística espacial;',
    '• Noções de observabilidade (OpenTelemetry, Prometheus, Grafana, Loki, Tempo) e CI/CD (GitHub Actions) para ambientes de produção.',
    'AVISO FORMAL: Caso o usuário não possua os conhecimentos técnicos descritos acima, fica expressamente proibido instalar, executar, modificar, distribuir ou tentar utilizar este software de qualquer forma que não seja estritamente a execução conforme as instruções oficiais documentadas (launch.bat, INSTRUCTIONS.md, README.md). O não cumprimento desta cláusula configura uso indevido e sujeita o infrator às penalidades previstas neste documento e na legislação brasileira aplicável.'
])

# Section 4
add_section(doc, '4. Licenciamento e Propriedade Intelectual', [
    'O ASI é distribuído sob a Licença Apache 2.0 (código-fonte), cujos termos completos encontram-se disponíveis em: https://www.apache.org/licenses/LICENSE-2.0 e no arquivo LICENSE na raiz do repositório. Os dados derivados e documentação estão sob CC-BY-4.0, respeitando as licenças das fontes originais.',
    'Embora a Licença Apache 2.0 permita uso, reprodução, distribuição e criação de trabalhos derivados, o presente documento impõe restrições adicionais de natureza contratual, aceitas automaticamente pelo usuário no momento de qualquer interação com o software (download, clone, execução, distribuição), conforme detalhado a seguir. Estas restrições são compatíveis com a Seção 4(d) e Seção 9 da Apache 2.0.',
    '4.1 O que é permitido',
    '• Executar o software para fins educacionais, de pesquisa, análise pessoal e planejamento territorial não-crítico, conforme as instruções oficiais;',
    '• Compartilhar o software gratuitamente, desde que por meio do repositório oficial ou com link direto a ele, sem alterar seu conteúdo;',
    '• Citar o software em trabalhos acadêmicos, relatórios técnicos, teses, dissertações e publicações científicas, com os devidos créditos ao Desenvolvedor e referência ao repositório oficial (formato sugerido: "Lima, L.L. (2026). ASI — Atlas de Suscetibilidade a Inundações v3.3. https://github.com/LuciolLima/ASI");',
    '• Sugerir melhorias e contribuições, exclusivamente por meio dos canais oficiais do repositório (Issues, Pull Requests ou contato direto via e-mail institucional);',
    '• Utilizar trechos de código (snippets) em projetos próprios, desde que mantidos os avisos de copyright, licença e atribuição original (conforme Apache 2.0 Seção 4).',
    '4.2 O que é expressamente proibido',
    '• Vender, sublicenciar, cobrar ou atribuir qualquer valor monetário ao software ou a produtos derivados dele, mesmo que modificados;',
    '• Remover, alterar ou ocultar os créditos, avisos de copyright, licença ou qualquer identificação do Desenvolvedor original;',
    '• Distribuir versões modificadas do software sem autorização prévia, expressa e documentada do Desenvolvedor;',
    '• Publicar o software ou trechos dele em plataformas de terceiros como se fosse de autoria própria (plágio de software);',
    '• Utilizar o nome, marca, imagem, identidade visual (design tokens, logotipo, paleta de cores) ou identidade do software ou do Desenvolvedor para fins comerciais sem autorização;',
    '• Incorporar o ASI (total ou parcialmente) em produtos SaaS, plataformas pagas, consultorias comerciais ou serviços que gerem receita direta ou indireta sem autorização contratual prévia;',
    '• Remover ou desabilitar mecanismos de telemetria, health checks, observabilidade ou validação de integridade (checksums SHA256);',
    '• Realizar engenharia reversa do componente React/TypeScript (AsiMap) para extração de lógica proprietária de renderização WebGL.',
    'O descumprimento das proibições acima configura violação de propriedade intelectual, podendo acarretar responsabilização civil e criminal nos termos da Lei nº 9.610/1998 (Lei de Direitos Autorais), Lei nº 9.609/1998 (Lei do Software) e demais dispositivos legais aplicáveis.'
])

# Section 5
add_section(doc, '5. Gratuidade e Vedação à Comercialização', [
    'O ASI é, em sua totalidade, um produto gratuito e de código aberto (open source). Sua distribuição sem custo é uma decisão deliberada e irrevogável do Desenvolvedor, fundamentada nos princípios de democratização do conhecimento técnico, ciência aberta (Open Science), reprodutibilidade computacional e compromisso com a mitigação de riscos de inundação em territórios vulneráveis.',
    'Sendo assim, fica expressamente vedado, sob qualquer hipótese, circunstância ou justificativa:',
    '• Cobrar qualquer valor pelo acesso, instalação, uso, suporte, treinamento, customização ou distribuição do software, ainda que parcialmente;',
    '• Incluir o software ou partes dele em produtos pagos, assinaturas, pacotes comerciais ou serviços de terceiros sem autorização prévia, expressa e por escrito;',
    '• Utilizar o software como isca, atrativo ou diferencial em modelos de negócio que gerem receita direta ou indireta ao usuário ou a terceiros (incluindo modelos "freemium", "open core" ou "dual licensing" não autorizados).',
    'A comercialização não autorizada deste software, ainda que disfarçada de serviço, consultoria, suporte, implantação, treinamento ou customização, constitui violação contratual grave e pode configurar crimes previstos no Código Penal Brasileiro (art. 184, 185, 195), na Lei nº 9.610/1998, Lei nº 9.609/1998 e na legislação de proteção ao consumidor (Lei nº 8.078/1990 — CDC).'
])

# Section 6
add_section(doc, '6. Transferência e Assunção de Responsabilidade pelo Usuário', [
    'A partir do momento em que o usuário realiza o download, clona o repositório, executa o software ou interage com qualquer componente do ASI (incluindo APIs externas consumidas pelo sistema), ele automaticamente e de forma irrevogável assume para si plena responsabilidade pelo uso que fizer do sistema, pelos dados que processar, pelas conclusões que extrair e por todas as consequências, diretas ou indiretas, que desse uso possam resultar.',
    'Esta assunção de responsabilidade inclui, sem se limitar a:',
    '• Responsabilidade por danos causados a terceiros em decorrência de interpretações equivocadas, uso inadequado ou extrapolação indevida das informações geradas pelo sistema;',
    '• Responsabilidade por alterações, modificações, adulterações ou desativação de validações no código-fonte, nos dados processados ou nos schemas de validação (Pandera);',
    '• Responsabilidade por violações de privacidade, segurança de dados, LGPD (Lei nº 13.709/2018) ou direitos de terceiros praticadas com o auxílio do software;',
    '• Responsabilidade por danos ao próprio sistema do usuário, perda de dados, instabilidades, vazamento de credenciais (API Keys CARTO, etc.) decorrentes de uso incompatível com os requisitos técnicos ou de má configuração de ambiente;',
    '• Responsabilidade pelo uso de dados de terceiros (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Prefeitura Cabo, SEINFRA-PE, CONDEPE-FIDEM) em desacordo com os termos de uso de cada fonte original;',
    '• Responsabilidade por decisões urbanísticas, imobiliárias, securitárias ou de gestão pública baseadas unicamente nos outputs do ASI sem validação técnica independente.',
    'O Desenvolvedor não poderá, em nenhuma circunstância, ser responsabilizado por danos diretos, indiretos, incidentais, especiais, exemplares, punitivos ou consequenciais (incluindo lucros cessantes, perda de dados, interrupção de negócio, danos morais, danos à reputação) resultantes do uso ou da impossibilidade de uso do software, mesmo que advertido da possibilidade de tais danos.'
])

# Section 7
add_section(doc, '7. Proibição de Uso Indevido e Ilegal', [
    'É terminantemente proibido o uso do ASI para fins ilícitos, imorais, antiéticos ou que violem qualquer dispositivo da legislação brasileira ou do direito internacional. Mais especificamente:',
    '• Fica proibido o uso para manipulação de dados públicos com fins fraudulentos, para induzir autoridades a erro ou para fundamentar atos administrativos viciados;',
    '• Fica proibido o uso para criação de desinformação, notícias falsas, análises tendenciosas ou relatórios enganosos com dados gerados pelo sistema;',
    '• Fica proibido o uso para fins de vigilância, espionagem, rastreamento de pessoas, geolocalização não autorizada ou coleta de dados pessoais/sensíveis sem consentimento livre, informado e específico (LGPD art. 7º);',
    '• Fica proibido o uso que configure qualquer forma de concorrência desleal (Lei nº 9.279/1996 art. 195), parasitismo, aproveitamento indevido da reputação do software ou passing off;',
    '• Fica proibido o uso para instrumentalização de políticas públicas sem transparência metodológica e validação por comissão técnica multidisciplinar;',
    '• Fica proibido o uso em processos licitatórios, contratos administrativos ou concessões públicas sem divulgação prévia da metodologia, limitações e incertezas do modelo.',
    'O uso indevido será tratado com o máximo rigor legal disponível, incluindo notificação extrajudicial, ação civil de indenização por danos materiais e morais, ação de obrigação de fazer/não fazer (tutela de urgência), representação ao MPF/MPPE, e, quando cabível, representação criminal perante as autoridades competentes (Polícia Federal, Delegacia de Crimes Cibernéticos).'
])

# Section 8
add_section(doc, '8. Estado do Software — Versão 3.3.0 (Estável, Operacional e Auditável)', [
    'O ASI, na versão 3.3.0 ora disponibilizada, encontra-se em estado estável, operacional e auditável. Esta afirmação baseia-se em:',
    '• 59 testes automatizados passando (unitários + integração) via pytest com cobertura >70%;',
    '• CI/CD completo no GitHub Actions (6 jobs: lint, type-check, test, security, build, deploy);',
    '• Validação de schemas Pandera em 100% dos DataFrames de entrada/saída;',
    '• Verificação de integridade SHA256 em todos os assets de dados (data_V3.0-System.zip);',
    '• Health checks expostos em /_health e métricas Prometheus em /metrics;',
    '• Build reproduzível do componente React (Vite + TypeScript) com bundle inlined no Streamlit;',
    '• Documentação técnica completa: README.md, INSTRUCTIONS.md, DTM (docs/academic_context/DTM_doc.md), Instituições (docs/academic_context/institutions.md), Changelog.',
    'Esta versão NÃO É:',
    '• Um produto comercial homologado para venda ou licenciamento em mercado de software;',
    '• Um software de código-fonte aberto para edição irrestrita — embora o código seja visível no repositório, sua edição e redistribuição estão sujeitas às restrições contratuais deste documento (Seção 4.2), além da Apache 2.0;',
    '• Um sistema projetado para uso em produção crítica, emergências climáticas, evacuações, decisões de alto impacto financeiro ou risco de vida sem validação técnica independente, homologação por órgão competente e termo de responsabilidade assinado;',
    '• Um sistema de alerta precoce (Early Warning System) certificado por órgão meteorológico ou de defesa civil oficial;',
    '• Isento de incertezas inerentes a modelos geomorfométricos baseados em DEM de 30m (SRTM), interpolados, com erros verticais conhecidos (±5–10m) e limitações em áreas urbanas densas.',
    'Eventuais bugs, limitações, comportamentos inesperados ou sugestões de melhoria devem ser reportados exclusivamente pelo canal oficial do repositório, por meio de abertura de Issues devidamente documentadas (template: bug_report.yml, feature_request.yml) ou Pull Requests referenciando Issue existente.'
])

# Section 9
add_section(doc, '9. Contribuições, Sugestões e Melhorias', [
    'O Desenvolvedor valoriza a colaboração técnica responsável e a ciência aberta. No entanto, qualquer contribuição, modificação, melhoria ou sugestão ao código-fonte, à documentação, aos dados derivados ou aos assets do ASI deve obrigatoriamente seguir o fluxo de governança a seguir:',
    '1. Abrir uma Issue no repositório oficial, descrevendo detalhadamente a proposta, sua motivação técnica, o impacto esperado, testes realizados e referências bibliográficas (se aplicável);',
    '2. Aguardar análise, feedback e, quando aplicável, autorização prévia e expressa do Desenvolvedor (labels: approved, needs-rfc, wontfix);',
    '3. Submeter as alterações somente após aprovação, por meio de Pull Request devidamente documentado, referenciando a Issue correspondente, com testes passando (CI verde) e descrição clara das mudanças;',
    '4. Aceitar que o Desenvolvedor detém a decisão final sobre inclusão, modificação, rejeição ou solicitação de refatoração de qualquer contribuição, sem necessidade de justificativa detalhada além do feedback técnico;',
    '5. Assinar o CLA (Contributor License Agreement) implícito ao submeter PR: a contribuição passa a ser licenciada sob Apache 2.0 + restrições deste documento, com atribuição de autoria preservada.',
    'Contribuições aceitas e publicadas serão devidamente creditadas no repositório (AUTHORS.md, CHANGELOG, release notes), respeitando a autoria original e o esforço de cada colaborador. Modificações realizadas sem autorização prévia, independentemente da intenção, serão tratadas como violação destes termos (Seção 4.2).'
])

# Section 10
add_section(doc, '10. Uso de Imagem, Publicações e Referências Externas', [
    'O uso da imagem, identidade visual (design tokens: cores #080C10, #00B4D8, #00F5D4, tipografia IBM Plex Mono/Sans), nome, marca, logotipo ou qualquer elemento identificável do ASI em publicações, redes sociais, materiais de marketing, vídeos, artigos, teses, relatórios técnicos ou qualquer outro meio de comunicação deve respeitar as seguintes diretrizes:',
    '• Citações acadêmicas e científicas são livres e incentivadas, desde que acompanhadas dos devidos créditos ao Desenvolvedor e referência ao repositório oficial (DOI/Zenodo se disponível);',
    '• Publicações em redes sociais que demonstrem o uso legítimo do software são permitidas, desde que não impliquem endosso comercial não autorizado, parceria institucional inexistente ou certificação oficial;',
    '• É proibida qualquer publicação que distorça, deturpe, apresente o software de forma enganosa ao público, omita suas limitações (Seção 8) ou sugira capacidades não implementadas;',
    '• É proibida a criação de canais, páginas, perfis, sites espelho, forks públicos não-oficiais ou domínios que se apresentem como representantes oficiais do ASI sem autorização expressa e por escrito do Desenvolvedor;',
    '• É proibido o uso de capturas de tela, vídeos ou demos do ASI em materiais de venda de cursos, treinamentos, consultorias ou produtos terceiros sem autorização contratual.',
    'O descumprimento destas diretrizes poderá acarretar solicitação formal de remoção de conteúdo (DMCA/takedown), notificação às plataformas digitais envolvidas (GitHub, YouTube, LinkedIn, Instagram, TikTok, etc.), além de ação judicial por uso indevido de imagem, marca, concorrência desleal e danos morais/reputacionais.'
])

# Section 11
add_section(doc, '11. Fundamentação Legal — Legislação Brasileira Aplicável', [
    'Este software, seus termos de uso, sua documentação, seus dados derivados e sua identidade visual são protegidos pelo ordenamento jurídico brasileiro, compreendendo, entre outros dispositivos, as seguintes legislações (vigentes e consolidadas):',
    'Lei nº 9.610/1998 — Lei de Direitos Autorais (LDA): Estabelece que obras intelectuais, incluindo programas de computador, suas documentações, interfaces, design visual e bases de dados estruturadas, são protegidas como criações do espírito humano. O ASI, como obra original, encontra-se protegido por esta lei, que assegura ao Desenvolvedor os direitos morais (inalienáveis, irrenunciáveis, perpétuos) e patrimoniais sobre sua criação. Reprodução, distribuição, modificação, adaptação, tradução ou qualquer forma de exploração econômica sem autorização constitui violação passível de indenização civil (arts. 101-110) e responsabilidade criminal (art. 184).',
    'Lei nº 9.609/1998 — Lei do Software (Lei de Proteção de Programas de Computador): Regula especificamente a proteção da propriedade intelectual de programas de computador no Brasil. Determina que o registro e a proteção do software independem de inscrição formal no INPI, sendo automáticos a partir da criação (art. 2º). Uso, cópia, modificação, engenharia reversa não autorizada (exceto interoperabilidade art. 6º), distribuição ou comercialização não autorizados são passíveis de sanções civis (indenização por perdas e danos, lucros cessantes, busca e apreensão) e penais (art. 12-15), incluindo multa e reclusão.',
    'Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais (LGPD): Disciplina o tratamento de dados pessoais no Brasil, garantindo transparência, finalidade legítima, adequação, necessidade, livre acesso, qualidade, segurança, prevenção, não discriminação e prestação de contas (art. 6º). Embora o ASI não colete dados pessoais de forma direta (não há autenticação, cadastro, tracking de usuários, cookies de marketing), qualquer uso do software que envolva processamento de dados de pessoas identificáveis (ex: cruzamento com dados de defesa civil contendo endereços, nomes) deve observar rigorosamente os princípios da LGPD. O usuário é o único responsável (controlador) pelo tratamento de dados pessoais eventualmente realizados por meio do sistema, devendo atender aos direitos dos titulares (art. 18) e notificar a ANPD em caso de incidente (art. 48).',
    'Lei nº 12.965/2014 — Marco Civil da Internet (MCI): Estabelece princípios, garantias, direitos e deveres para o uso da Internet no Brasil. Regula a responsabilidade por danos causados por conteúdo gerado na rede (art. 19 — apenas após ordem judicial), protege a privacidade dos usuários (art. 7-11), neutralidade de rede (art. 9) e estabelece critérios claros de responsabilização. Uso do ASI para fins que violem direitos de terceiros no ambiente digital (difamação, exposição indevida, vazamento) estará sujeito às sanções previstas nesta lei.',
    'Lei nº 8.078/1990 — Código de Defesa do Consumidor (CDC): Embora o ASI seja gratuito (não configurando relação de consumo stricto sensu), situações que envolvam práticas abusivas na distribuição, comercialização não autorizada, publicidade enganosa (art. 37), práticas comerciais abusivas (art. 39) ou indução ao erro do público em relação às características, finalidade, origem, versão ou capacidades do software poderão ser enquadradas nesta lei por analogia e jurisprudência (Súmula 481 STJ).',
    'Lei nº 9.279/1996 — Lei da Propriedade Industrial (LPI): Protege marcas, nomes comerciais, sinais distintivos, indicações geográficas e reprime a concorrência desleal (art. 195). O nome "ASI — Atlas de Suscetibilidade a Inundações", sua identidade visual, logotipo e design tokens constituem ativos de propriedade intelectual do Desenvolvedor, protegidos independentemente de registro no INPI (direito de precedência e uso).',
    'Código Penal Brasileiro — Decreto-Lei nº 2.848/1940 (e alterações): Tipificam como crimes condutas como: violação de direito autoral (art. 184 — reclusão 2 a 4 anos + multa), usurpação de nome ou pseudônimo alheio (art. 185 — detenção 3 meses a 1 ano + multa), concorrência desleal (art. 195 LPI — reclusão 3 meses a 1 ano + multa), estelionato (art. 171 — se houver vantagem ilícita), falsidade ideológica (art. 299 — se houver documento público/particular falso). O uso criminoso ou malicioso do ASI, incluindo plágio, venda não autorizada, distribuição ilegal, engenharia reversa com fim comercial, estará sujeito a inquérito policial, denúncia criminal e pena de reclusão conforme a gravidade do delito.',
    'Lei nº 12.527/2011 — Lei de Acesso à Informação (LAI): Garante o direito de acesso à informação pública. O ASI, ao consumir e processar dados de órgãos públicos (IBGE, APAC, SEPDEC, INMET, Prefeituras), atua em consonância com a LAI, promovendo transparência ativa e reutilização de dados abertos. O usuário deve respeitar as licenças de cada fonte (ver Seção 14 e docs/academic_context/institutions.md).',
    'Decreto nº 10.968/2022 — Estratégia Nacional de Segurança Cibernética (E-Ciber): O ASI implementa boas práticas de segurança: validação de entrada (Pandera), integridade de assets (SHA256), rate limiting em APIs externas, ausência de coleta de dados sensíveis, health checks, observabilidade. O usuário deve manter seu ambiente (Python, dependências, SO, rede) atualizado e seguro.'
])

# Section 12
add_section(doc, '12. Jurisdição e Foro Competente', [
    'Todos os litígios, controvérsias, disputas ou questões decorrentes ou relacionadas a estes Termos de Uso, ao software ASI, aos seus dados derivados, à sua documentação, à sua identidade visual ou à conduta de qualquer usuário serão submetidos à jurisdição exclusiva dos tribunais brasileiros, com foro eleito na comarca de domicílio do Desenvolvedor (Recife/PE), renunciando as partes a qualquer outro foro, por mais privilegiado que seja.',
    'A legislação brasileira é soberana e exclusivamente aplicável, independentemente de qualquer convenção internacional, acordo bilateral, tratado multilateral ou legislação estrangeira que eventualmente pudesse ser invocada pelo usuário com base em sua localidade geográfica, nacionalidade ou sede de pessoa jurídica.'
])

# Section 13
add_section(doc, '13. Aceitação Tácita, Automática e Irrevogável dos Termos', [
    'Ao realizar o download, clonar o repositório, instalar, executar, distribuir, modificar, inspecionar, compilar, empacotar ou interagir de qualquer forma com o software ASI (incluindo execução via launch.bat, streamlit run app.py, Docker, Kubernetes, CI/CD, ou qualquer outro meio), o usuário declara, de maneira tácita, automática e irrevogável, que:',
    '• Leu, compreendeu e concorda integralmente com todos os termos deste documento e com a Licença Apache 2.0;',
    '• Possui os conhecimentos técnicos mínimos exigidos descritos na Cláusula 3;',
    '• Assume plena responsabilidade pelo uso que fará do software, conforme descrito na Cláusula 6;',
    '• Está ciente das proibições expressas neste documento e se compromete a não violá-las;',
    '• Reconhece a jurisdição brasileira como exclusivamente competente para quaisquer disputas;',
    '• Reconhece que os dados de terceiros (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Prefeitura Cabo, SEINFRA-PE, CONDEPE-FIDEM) possuem licenças próprias que devem ser respeitadas;',
    '• Reconhece que o software é fornecido "AS IS" (como está), sem garantias de qualquer natureza (Apache 2.0 Seção 7).',
    'A IGNORÂNCIA DESTES TERMOS NÃO EXIME O USUÁRIO DE RESPONSABILIDADE. ESTE DOCUMENTO ESTÁ PUBLICAMENTE DISPONÍVEL NO REPOSITÓRIO OFICIAL (ASI_Termos_de_Uso_PT.docx) E SUA LEITURA INTEGRAL É OBRIGAÇÃO INCONDICIONAL DO USUÁRIO ANTES DE QUALQUER INTERAÇÃO COM O SOFTWARE.'
])

# Section 14
add_section(doc, '14. Fontes de Dados — Licenças e Atribuições Obrigatórias', [
    'O ASI consome e processa dados das seguintes fontes oficiais. O usuário deve respeitar os termos de uso de cada fonte ao utilizar, redistribuir ou derivar produtos baseados nos outputs do ASI:',
    '',
    '| Fonte | Tipo | Licença / Termos | Atribuição Mínima |',
    '|-------|------|------------------|-------------------|',
    '| IBGE (SIDRA, Malhas, SRTM via IBGE) | Dados censitários, limites administrativos, DEM | Domínio público / Uso livre com atribuição (Lei 9.610 art. 8º) | "Fonte: IBGE" + ano da publicação |',
    '| APAC-PE | Precipitação, hidrologia | Dados abertos governo PE | "Fonte: APAC Pernambuco" |',
    '| SEPDEC-PE | Eventos de inundação, danos | Dados abertos governo PE | "Fonte: Defesa Civil PE — SEPDEC" |',
    '| INMET | Meteorologia de superfície | Domínio público / CC-BY 4.0 | "Fonte: INMET" |',
    '| MapBiomas (Coleção 10, Coleção 2 beta) | Cobertura/uso da terra (LULC) | CC-BY 4.0 | "Fonte: Projeto MapBiomas" + coleção/ano |',
    '| SRTM (NASA/USGS/NGA) | DEM 30m | Domínio público (USGS) | "Fonte: SRTM/NASA/USGS via IBGE" |',
    '| NASA POWER (MERRA-2) | Reanálise agrometeorológica | Domínio público NASA | "Fonte: NASA POWER / MERRA-2" |',
    '| Prefeitura Cabo de Santo Agostinho | Malha bairros oficial, zoneamento | Dados abertos municipais | "Fonte: Prefeitura do Cabo de Santo Agostinho" |',
    '| SEINFRA-PE | Infraestrutura, macrozoneamento | Dados abertos governo PE | "Fonte: SEINFRA-PE" |',
    '| CONDEPE-FIDEM | Planejamento territorial, relatórios | Dados abertos governo PE | "Fonte: CONDEPE-FIDEM" |',
    '| CARTO (Basemaps Positron, Dark Matter, Voyager) | Tiles raster/vector | CC-BY 4.0 + API Key | "© OpenStreetMap contributors © CARTO" + key |',
    '',
    'O documento completo de atribuições institucionais, histórico de fomento e créditos técnicos encontra-se em: docs/academic_context/institutions.md.'
])

# Section 15
add_section(doc, '15. Fomento à Pesquisa — Reconhecimento Obrigatório', [
    'O desenvolvimento do ASI foi viabilizado por bolsas de Iniciação Científica e Tecnológica (IC/IT) e infraestrutura concedidas pelas seguintes agências. Qualquer publicação, tese, relatório ou derivação do ASI deve incluir o reconhecimento ao fomento (padrão CNPq/CAPES/FACEPE):',
    '• FACEPE — Fundação de Amparo à Ciência e Tecnologia do Estado de Pernambuco (PIBIC, PIBITI, BIC-JR, APQ);',
    '• CNPq — Conselho Nacional de Desenvolvimento Científico e Tecnológico (PIBIC, PIBITI, PIC, Bolsa Produtividade);',
    '• CAPES — Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (PROEX, DS, PROSUP, Bolsas Mestrado/Doutorado);',
    '• METRO SUL — Programa de Inovação Metropolitana / Região Metropolitana do Recife;',
    '• GRE — Grupo de Recursos Educacionais / Inovação Acadêmica (infraestrutura, licenças, suporte).',
    'Instituição formadora: FACEP — Faculdade de Ciências Educacionais de Pernambuco.'
])

# Section 16
add_section(doc, '16. Documentos Correlatos e Hierarquia Normativa', [
    'Este documento deve ser lido em conjunto com (ordem de prevalência em caso de conflito):',
    '1. Licença Apache 2.0 (LICENSE) — base legal do código-fonte;',
    '2. Estes Termos de Uso PT (ASI_Termos_de_Uso_PT.docx) — restrições contratuais adicionais;',
    '3. Terms of Use EN (ASI_Terms_of_Use_EN.docx) — versão oficial em inglês (prevalece em disputas internacionais);',
    '4. README.md — visão geral, instalação, uso, arquitetura;',
    '5. INSTRUCTIONS.md — instruções detalhadas de instalação e operação;',
    '6. DTM — Documentação Técnica e Metodológica (docs/academic_context/DTM_doc.md);',
    '7. Instituições e Créditos (docs/academic_context/institutions.md);',
    '8. Changelog (ASI_CHANGELOG_v3.0.pdf, RELEASE_NOTES_v3.1.md);',
    '9. requirements.txt / pyproject.toml — dependências e versões exatas;',
    '10. launch.bat — launcher oficial Windows (validação de ambiente, .venv, build, testes).'
])

# Section 17
add_section(doc, '17. Disposições Finais', [
    '17.1 Se qualquer cláusula destes Termos for declarada nula, inválida ou ineficaz por autoridade competente, as demais permanecerão em pleno vigor e efeito.',
    '17.2 A tolerância do Desenvolvedor quanto a qualquer violação não constitui renúncia ao direito de exigir o cumprimento futuro, nem novação tácita.',
    '17.3 O Desenvolvedor reserva-se o direito de atualizar estes Termos a qualquer momento, mediante publicação de nova versão no repositório oficial com versão incremental (SemVer: MAJOR.MINOR.PATCH). O uso contínuo após publicação implica aceitação da nova versão.',
    '17.4 Este documento é parte integrante e indissociável do software ASI. A ausência deste arquivo em qualquer distribuição caracteriza distribuição irregular e não autorizada.',
    '17.5 Contato para assuntos jurídicos, licenciamento comercial, parcerias institucionais, denúncias de uso indevido ou solicitações de autorização: lucio.lima@facep.edu.br (e-mail institucional FACEP) ou via Issues no repositório oficial com label legal.'
])

# Footer
doc.add_paragraph()
doc.add_paragraph()
footer_items = [
    'ASI — Atlas de Suscetibilidade a Inundações',
    'Termos de Uso, Licenciamento e Responsabilidade — Versão 3.3',
    'Licença Apache 2.0 (código) + CC-BY-4.0 (dados/docs) + Restrições Contratuais Adicionais',
    'Regido pelas Leis da República Federativa do Brasil',
    'Desenvolvedor: Lucio Luiz de Lima',
    'Instituição: FACEP — Faculdade de Ciências Educacionais de Pernambuco',
    'Repositório Oficial: https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Data de publicação desta versão: Setembro 2026'
]
for item in footer_items:
    p = doc.add_paragraph(item)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(100, 100, 100)

doc.save('ASI_Termos_de_Uso_PT.docx')
print('Documento PT salvo com sucesso!')