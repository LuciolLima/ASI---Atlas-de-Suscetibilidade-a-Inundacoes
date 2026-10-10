from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading('ASI \u2014 Flood Susceptibility Atlas', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('SIGWeb \u2014 Version 3.3.0')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0, 180, 216)

doc.add_paragraph()

# Header
header = doc.add_heading('TERMS OF USE, LICENSING AND LIABILITY', level=1)
header.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Official Document \u2014 Read this document in full before installing, running or distributing this software.')
run.bold = True
run.font.size = Pt(11)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Document Version: 3.3 | Effective: as of the date of publication in the official repository')
run.font.size = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Developed and governed under the laws of the Federative Republic of Brazil')
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
add_section(doc, '1. Software and Developer Identification', [
    'This document constitutes the Terms of Use, Licensing and Liability Agreement for the software known as ASI \u2014 Flood Susceptibility Atlas, developed and maintained by its creator, Lucio Luiz de Lima, hereinafter referred to simply as the Developer. ASI is a Web-based Geographic Information System (SIGWeb) of an educational, scientific and technical nature, built on a modular architecture of geospatial data engineering pipeline, focused on interactive visualization, geospatial statistical analysis and communication of hydrological susceptibility indices derived from topographic, geomorphometric and meteorological parameters.',
    'This software was conceived, designed and developed entirely in Brazil and is therefore governed, interpreted and protected exclusively by the laws of the Federative Republic of Brazil, regardless of the user\u2019s geographic location, the device on which the software is installed, or the territory from which it is accessed or executed. Brazilian jurisdiction is sovereign and incontestable with respect to this product, without any territorial exception whatsoever.',
    'The official project repository, which serves as the sole legitimate channel for distribution, updates, technical documentation and communication between the Developer and users, is available at:',
    'https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Any distribution of the software carried out outside this official repository shall be considered unauthorized and potentially irregular, being the exclusive responsibility of whoever promoted it.'
])

# Section 2
add_section(doc, '2. Nature, Purpose and Scope of the Software', [
    'ASI is software of a strictly technical, academic, educational and applied research nature. Its primary function is high-performance interactive cartographic visualization (WebGL 60fps via Deck.gl + MapLibre), statistical and geostatistical analysis of geospatial data related to the Topographic Wetness Index (TWI), applied to the identification of flood susceptibility zones, territorial planning to support decision-making, and multi-source correlation of hydrological, demographic, socioeconomic and historical event data.',
    'The system integrates, at runtime, the following technical capabilities:',
    '\u2022 TWI calculation and classification from DEM (SRTM 30m) via DuckDB + Polars + GeoParquet pipeline (sub-ms queries);',
    '\u2022 WebGL map rendering with custom React component (AsiMap) + Folium/Leaflet fallback;',
    '\u2022 Loop-free spatial cross-filtering via state machine (SelectionState + EventOrigin + debounce);',
    '\u2022 Geostatistical dashboards (Plotly) with IRA ranking by neighborhood, historical precipitation series (APAC/INMET/NASA POWER), TWI \u00d7 Civil Defense correlation;',
    '\u2022 Point-click diagnosis with 500m buffer, risk heatmap, hydrography, official territorial mesh;',
    '\u2022 Full observability: OpenTelemetry (traces/metrics), Prometheus/Grafana, Loki, Tempo, Pyroscope;',
    '\u2022 WCAG 2.1 AA compliance, reduced motion, high contrast, design tokens + atomic components.',
    'THIS SYSTEM WAS NOT DEVELOPED, IS NOT CERTIFIED AND MUST NOT BE USED FOR ANY OF THE FOLLOWING PURPOSES:',
    '\u2022 Manipulation, modification or editing of geospatial data for purposes not covered by these terms;',
    '\u2022 Use in emergency alert, evacuation or civil defense systems without independent technical validation by a qualified professional registered with CREA/CAU;',
    '\u2022 Replacement of geotechnical surveys, risk analyses or environmental impact studies issued by legally qualified professionals;',
    '\u2022 Commercial, governmental or institutional applications without prior, express and documented authorization from the Developer;',
    '\u2022 Military purposes, surveillance, tracking, monitoring of persons or any use posing a risk to third-party privacy;',
    '\u2022 Decision-making in life-risk situations, climate emergencies or disaster management without independent validation;',
    '\u2022 Reverse engineering for commercial replication or competitive purposes.',
    'WARNING: The use of the software outside the purposes described above is the exclusive responsibility of the user, completely exempting the Developer from any civil, criminal or administrative liability arising therefrom.'
])

# Section 3
add_section(doc, '3. Minimum Technical Requirements and User Awareness', [
    'This software is intended for a specific technical audience. By installing, running, accessing or distributing ASI, the user irrevocably declares and warrants that they possess technical knowledge equivalent to or exceeding the following:',
    '\u2022 Intermediate to advanced level in geospatial data analysis, with command of tools and languages such as Python 3.12+, Pandas 2.x, Polars, DuckDB, PyArrow, GeoPandas and related libraries;',
    '\u2022 Fundamentals of modern web system development, with understanding of client-server architectures, reactive frameworks (Streamlit 1.35+), WebSockets, WebGL, WebAssembly;',
    '\u2022 Solid knowledge of data engineering, including ETL/ELT pipelines, transformation and loading of geospatial databases (GeoParquet, Shapefile, GeoJSON), schema validation (Pandera);',
    '\u2022 Knowledge in computer science or computer engineering sufficient to understand the logical flow, modular structure (src/api, src/core, src/processing, src/sigweb, src/analysis) and cross-filtering state machine;',
    '\u2022 Ability to interpret geospatial data, geographic coordinates, cartographic projections (UTM SIRGAS 2000 EPSG:31985 \u2194 WGS84 EPSG:4326), geomorphometric indices (TWI, slope, flow accumulation) and spatial statistics;',
    '\u2022 Notions of observability (OpenTelemetry, Prometheus, Grafana, Loki, Tempo) and CI/CD (GitHub Actions) for production environments.',
    'FORMAL NOTICE: If the user does not possess the technical knowledge described above, they are expressly prohibited from installing, running, modifying, distributing or attempting to use this software in any way other than strict execution according to the official documented instructions (launch.bat, INSTRUCTIONS.md, README.md). Failure to comply with this clause constitutes misuse and subjects the offender to the penalties set out in this document and applicable Brazilian law.'
])

# Section 4
add_section(doc, '4. Licensing and Intellectual Property', [
    'ASI is distributed under the Apache License 2.0 (source code), the full terms of which are available at: https://www.apache.org/licenses/LICENSE-2.0 and in the LICENSE file at the repository root. Derived data and documentation are under CC-BY-4.0, respecting the licenses of the original sources.',
    'Although the Apache 2.0 License permits use, reproduction, distribution and creation of derivative works, this document imposes additional contractual restrictions automatically accepted by the user upon any interaction with the software (download, clone, execution, distribution), as detailed below. These restrictions are compatible with Apache 2.0 Section 4(d) and Section 9.',
    '4.1 What is permitted',
    '\u2022 Running the software for educational, research, personal analysis and non-critical territorial planning purposes, in accordance with official instructions;',
    '\u2022 Sharing the software free of charge, provided it is done through the official repository or with a direct link to it, without altering its content;',
    '\u2022 Citing the software in academic papers, technical reports, theses, dissertations and scientific publications, with appropriate credit to the Developer and reference to the official repository (suggested format: "Lima, L.L. (2026). ASI \u2014 Flood Susceptibility Atlas v3.3. https://github.com/LuciolLima/ASI");',
    '\u2022 Suggesting improvements and contributions exclusively through official repository channels (Issues, Pull Requests or direct contact via institutional email);',
    '\u2022 Using code snippets in own projects, provided that copyright notices, license and original attribution are maintained (per Apache 2.0 Section 4).',
    '4.2 What is expressly prohibited',
    '\u2022 Selling, sublicensing, charging for or attributing any monetary value to the software or products derived from it, even if modified;',
    '\u2022 Removing, altering or concealing credits, copyright notices, the license or any identification of the original Developer;',
    '\u2022 Distributing modified versions of the software without prior, express and documented authorization from the Developer;',
    '\u2022 Publishing the software or excerpts thereof on third-party platforms as if they were the author\u2019s own work (software plagiarism);',
    '\u2022 Using the name, brand, image, visual identity (design tokens, logo, color palette) or identity of the software or the Developer for commercial purposes without authorization;',
    '\u2022 Incorporating ASI (in whole or in part) into SaaS products, paid platforms, commercial consultancies or services generating direct or indirect revenue without prior contractual authorization;',
    '\u2022 Removing or disabling telemetry mechanisms, health checks, observability or integrity validation (SHA256 checksums);',
    '\u2022 Reverse engineering the React/TypeScript component (AsiMap) for extraction of proprietary WebGL rendering logic.',
    'Failure to comply with the above prohibitions constitutes intellectual property infringement and may result in civil and criminal liability under Brazilian Law No. 9,610/1998 (Copyright Law), Law No. 9,609/1998 (Software Law) and other applicable legal provisions.'
])

# Section 5
add_section(doc, '5. Free of Charge \u2014 Prohibition of Commercialization', [
    'ASI is, in its entirety, a free and open-source product. Its distribution at no cost is a deliberate and irrevocable decision by the Developer, grounded in the principles of democratization of technical knowledge, Open Science, computational reproducibility and commitment to flood risk mitigation in vulnerable territories.',
    'Therefore, it is expressly prohibited, under any circumstance, hypothesis or justification:',
    '\u2022 Charging any fee for access, installation, use, support, training, customization or distribution of the software, even partially;',
    '\u2022 Including the software or parts thereof in paid products, subscriptions, commercial packages or third-party services without prior, express and written authorization;',
    '\u2022 Using the software as a hook, attraction or differentiator in business models generating direct or indirect revenue for the user or third parties (including unauthorized "freemium", "open core" or "dual licensing" models).',
    'Unauthorized commercialization of this software, even when disguised as a \u2018service\u2019, \u2018consultancy\u2019, \u2018support\u2019, \u2018implementation\u2019, \u2018training\u2019 or \u2018customization\u2019, constitutes a serious contractual violation and may constitute crimes under the Brazilian Penal Code (arts. 184, 185, 195), Law No. 9,610/1998, Law No. 9,609/1998 and consumer protection legislation (Law No. 8,078/1990 \u2014 CDC).'
])

# Section 6
add_section(doc, '6. Transfer and Assumption of Liability by the User', [
    'From the moment the user downloads, clones the repository, runs the software or interacts with any component of ASI (including external APIs consumed by the system), they automatically and irrevocably assume full responsibility for the use they make of the system, the data they process, the conclusions they draw and all consequences, direct or indirect, that may result from such use.',
    'This assumption of liability includes, but is not limited to:',
    '\u2022 Liability for damages caused to third parties as a result of misinterpretation, improper use or undue extrapolation of information generated by the system;',
    '\u2022 Liability for alterations, modifications, tampering or disabling of validations in the source code, processed data or validation schemas (Pandera);',
    '\u2022 Liability for privacy breaches, data security violations, LGPD (Law No. 13,709/2018) or infringement of third-party rights carried out with the aid of the software;',
    '\u2022 Liability for damage to the user\u2019s own system, data loss, instabilities, credential leaks (CARTO API keys, etc.) resulting from use incompatible with technical requirements or misconfiguration of the environment;',
    '\u2022 Liability for the use of third-party data (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Cabo City Hall, SEINFRA-PE, CONDEPE-FIDEM) in disagreement with the terms of use of each original source;',
    '\u2022 Liability for urbanistic, real estate, insurance or public management decisions based solely on ASI outputs without independent technical validation.',
    'The Developer cannot, under any circumstances, be held liable for direct, indirect, incidental, special, exemplary, punitive or consequential damages (including lost profits, data loss, business interruption, moral damages, reputational damages) resulting from the use or inability to use the software, even if advised of the possibility of such damages.'
])

# Section 7
add_section(doc, '7. Prohibition of Improper and Illegal Use', [
    'The use of ASI for illicit, immoral, unethical purposes or any purpose violating any provision of Brazilian law or international law is strictly prohibited. More specifically:',
    '\u2022 It is prohibited to use the system for manipulation of public data for fraudulent purposes, to mislead authorities or to substantiate flawed administrative acts;',
    '\u2022 It is prohibited to use the system for the creation of disinformation, fake news, biased analyses or misleading reports with data generated by the system;',
    '\u2022 It is prohibited to use the system for surveillance, espionage, tracking of persons, unauthorized geolocation or collection of personal/sensitive data without free, informed and specific consent (LGPD art. 7);',
    '\u2022 It is prohibited to use the system in any manner constituting unfair competition (Law No. 9,279/1996 art. 195), parasitism, undue exploitation of the software\u2019s reputation or passing off;',
    '\u2022 It is prohibited to use the system for instrumentalization of public policies without methodological transparency and validation by a multidisciplinary technical committee;',
    '\u2022 It is prohibited to use the system in bidding processes, administrative contracts or public concessions without prior disclosure of methodology, limitations and model uncertainties.',
    'Improper use will be met with the maximum legal rigour available, including extrajudicial notification, civil action for material and moral damages, injunction (urgent relief), representation to MPF/MPPE, and, where applicable, criminal complaint before competent authorities (Federal Police, Cybercrime Division).'
])

# Section 8
add_section(doc, '8. Software State \u2014 Version 3.3.0 (Stable, Operational and Auditable)', [
    'ASI, in version 3.3.0 now made available, is in a stable, operational and auditable state. This statement is based on:',
    '\u2022 59 automated tests passing (unit + integration) via pytest with coverage >70%;',
    '\u2022 Complete CI/CD on GitHub Actions (6 jobs: lint, type-check, test, security, build, deploy);',
    '\u2022 Pandera schema validation on 100% of input/output DataFrames;',
    '\u2022 SHA256 integrity verification on all data assets (data_V3.0-System.zip);',
    '\u2022 Health checks exposed at /_health and Prometheus metrics at /metrics;',
    '\u2022 Reproducible React component build (Vite + TypeScript) with bundle inlined in Streamlit;',
    '\u2022 Complete technical documentation: README.md, INSTRUCTIONS.md, DTM (docs/academic_context/DTM_doc.md), Institutions (docs/academic_context/institutions.md), Changelog.',
    'This version IS NOT:',
    '\u2022 A commercial product certified for sale or licensing in the software market;',
    '\u2022 Open-source software for unrestricted editing \u2014 although the code is visible in the repository, its editing and redistribution are subject to the contractual restrictions of this document (Section 4.2), in addition to Apache 2.0;',
    '\u2022 A system designed for use in critical production, climate emergencies, evacuations, high-impact financial decisions or life-risk situations without independent technical validation, certification by a competent body and signed liability waiver;',
    '\u2022 An Early Warning System certified by an official meteorological or civil defense agency;',
    '\u2022 Exempt from uncertainties inherent to geomorphometric models based on 30m DEM (SRTM), interpolated, with known vertical errors (\u00b15\u201310m) and limitations in dense urban areas.',
    'Any bugs, limitations, unexpected behavior or improvement suggestions must be reported exclusively through the official repository channel by opening properly documented Issues (template: bug_report.yml, feature_request.yml) or Pull Requests referencing an existing Issue.'
])

# Section 9
add_section(doc, '9. Contributions, Suggestions and Improvements', [
    'The Developer values responsible technical collaboration and Open Science. However, any contribution, modification, improvement or suggestion to the source code, documentation, derived data or ASI assets must mandatorily follow the governance workflow below:',
    '1. Open an Issue in the official repository, describing in detail the proposal, its technical motivation, expected impact, tests performed and bibliographic references (if applicable);',
    '2. Await analysis, feedback and, where applicable, prior express authorization from the Developer (labels: approved, needs-rfc, wontfix);',
    '3. Submit changes only after approval, via a properly documented Pull Request referencing the corresponding Issue, with passing tests (green CI) and clear description of changes;',
    '4. Accept that the Developer retains the final decision on inclusion, modification, rejection or request for refactoring of any contribution, without obligation to provide detailed justification beyond technical feedback;',
    '5. Sign the implicit CLA (Contributor License Agreement) upon submitting PR: the contribution becomes licensed under Apache 2.0 + restrictions of this document, with authorship attribution preserved.',
    'Accepted and published contributions will be duly credited in the repository (AUTHORS.md, CHANGELOG, release notes), respecting original authorship and the effort of each collaborator. Modifications made without prior authorization, regardless of intent, will be treated as a violation of these terms (Section 4.2).'
])

# Section 10
add_section(doc, '10. Use of Image, Publications and External References', [
    'The use of the image, visual identity (design tokens: colors #080C10, #00B4D8, #00F5D4, typography IBM Plex Mono/Sans), name, brand, logo or any identifiable element of ASI in publications, social media, marketing materials, videos, articles, theses, technical reports or any other medium must comply with the following guidelines:',
    '\u2022 Academic and scientific citations are free and encouraged, provided they are accompanied by appropriate credit to the Developer and reference to the official repository (DOI/Zenodo if available);',
    '\u2022 Social media publications demonstrating legitimate use of the software are permitted, provided they do not imply unauthorized commercial endorsement, non-existent institutional partnership or official certification;',
    '\u2022 Any publication that distorts, misrepresents, presents the software in a misleading manner to the public, omits its limitations (Section 8) or suggests unimplemented capabilities is prohibited;',
    '\u2022 The creation of channels, pages, profiles, mirror sites, unofficial public forks or domains presenting themselves as official representatives of ASI without express written authorization from the Developer is prohibited;',
    '\u2022 The use of screenshots, videos or demos of ASI in sales materials for courses, training, consultancies or third-party products without contractual authorization is prohibited.',
    'Failure to comply with these guidelines may result in a formal content removal request (DMCA/takedown), notification to the digital platforms involved (GitHub, YouTube, LinkedIn, Instagram, TikTok, etc.), and legal action for improper use of image, brand, unfair competition and moral/reputational damages.'
])

# Section 11
add_section(doc, '11. Legal Basis \u2014 Applicable Brazilian Legislation', [
    'This software, its terms of use, its documentation, its derived data and its visual identity are protected by the Brazilian legal system, including, among other provisions, the following legislation (current and consolidated):',
    'Law No. 9,610/1998 \u2014 Brazilian Copyright Law (LDA): Establishes that intellectual works, including computer programs, their documentation, interfaces, visual design and structured databases, are protected as creations of the human mind. ASI, as an original work, is protected by this law, which guarantees the Developer both moral rights (inalienable, unwaivable, perpetual) and economic rights over the creation. Reproduction, distribution, modification, adaptation, translation or any form of economic exploitation without authorization constitutes a violation subject to civil indemnification (arts. 101-110) and criminal liability (art. 184).',
    'Law No. 9,609/1998 \u2014 Software Law (Computer Program Protection Law): Specifically governs the protection of intellectual property in computer programs in Brazil. It establishes that registration and protection of software do not depend on formal registration with INPI, being automatic from the moment of creation (art. 2). Unauthorized use, copying, modification, reverse engineering (except interoperability art. 6), distribution or commercialization are subject to civil sanctions (damages, lost profits, search and seizure) and criminal penalties (arts. 12-15), including fines and imprisonment.',
    'Law No. 13,709/2018 \u2014 General Personal Data Protection Law (LGPD): Regulates the processing of personal data in Brazil, ensuring transparency, legitimate purpose, adequacy, necessity, free access, quality, security, prevention, non-discrimination and accountability (art. 6). Although ASI does not directly collect personal data (no authentication, registration, user tracking, marketing cookies), any use of the software involving processing of identifiable persons\u2019 data (e.g., cross-referencing with civil defense data containing addresses, names) must strictly comply with LGPD principles. The user is the sole responsible party (controller) for any personal data processing eventually carried out through the system, and must comply with data subjects\u2019 rights (art. 18) and notify ANPD in case of incident (art. 48).',
    'Law No. 12,965/2014 \u2014 Brazilian Internet Civil Framework (MCI): Establishes principles, guarantees, rights and duties for Internet use in Brazil. Regulates liability for damages caused by online content (art. 19 \u2014 only after court order), protects user privacy (arts. 7-11), net neutrality (art. 9) and establishes clear accountability criteria. Use of ASI for purposes violating third-party rights in the digital environment (defamation, undue exposure, leaks) shall be subject to sanctions under this law.',
    'Law No. 8,078/1990 \u2014 Consumer Defense Code (CDC): Although ASI is free of charge (not configuring a strict consumer relationship), situations involving abusive distribution practices, unauthorized commercialization, misleading advertising (art. 37), abusive commercial practices (art. 39) or misleading the public regarding the software\u2019s characteristics, purpose, origin, version or capabilities may fall under this law by analogy and jurisprudence (STJ S\u00famula 481).',
    'Law No. 9,279/1996 \u2014 Industrial Property Law (LPI): Protects trademarks, trade names, distinctive signs, geographical indications and represses unfair competition (art. 195). The name "ASI \u2014 Flood Susceptibility Atlas", its visual identity, logo and design tokens constitute the Developer\u2019s intellectual property assets, protected regardless of INPI registration (precedence and use rights).',
    'Brazilian Penal Code \u2014 Decree-Law No. 2,848/1940 (and amendments): Classifies as crimes conducts such as: copyright infringement (art. 184 \u2014 imprisonment 2 to 4 years + fine), usurpation of another\u2019s name or pseudonym (art. 185 \u2014 detention 3 months to 1 year + fine), unfair competition (art. 195 LPI \u2014 imprisonment 3 months to 1 year + fine), fraud (art. 171 \u2014 if illicit advantage obtained), ideological falsehood (art. 299 \u2014 if false public/private document). Criminal or malicious use of ASI, including plagiarism, unauthorized sale, illegal distribution, reverse engineering for commercial purposes, shall be subject to police inquiry, criminal prosecution and imprisonment according to the severity of the offence.',
    'Law No. 12,527/2011 \u2014 Access to Information Law (LAI): Guarantees the right of access to public information. ASI, by consuming and processing data from public agencies (IBGE, APAC, SEPDEC, INMET, City Halls), acts in consonance with LAI, promoting active transparency and open data reuse. The user must respect the licenses of each source (see Section 14 and docs/academic_context/institutions.md).',
    'Decree No. 10,968/2022 \u2014 National Cybersecurity Strategy (E-Ciber): ASI implements security best practices: input validation (Pandera), asset integrity (SHA256), rate limiting on external APIs, no sensitive data collection, health checks, observability. The user must keep their environment (Python, dependencies, OS, network) updated and secure.'
])

# Section 12
add_section(doc, '12. Jurisdiction and Competent Forum', [
    'All disputes, controversies, disputes or matters arising from or related to these Terms of Use, the ASI software, its derived data, its documentation, its visual identity or the conduct of any user shall be submitted to the exclusive jurisdiction of Brazilian courts, with the elected forum being the jurisdiction of the Developer\u2019s domicile (Recife/PE), the parties waiving any other forum, however privileged it may be.',
    'Brazilian law is sovereign and exclusively applicable, regardless of any international convention, bilateral agreement, multilateral treaty or foreign legislation that the user might invoke based on their geographic location, nationality or legal entity headquarters.'
])

# Section 13
add_section(doc, '13. Tacit, Automatic and Irrevocable Acceptance of the Terms', [
    'By downloading, cloning the repository, installing, running, distributing, modifying, inspecting, compiling, packaging or interacting in any way with the ASI software (including execution via launch.bat, streamlit run app.py, Docker, Kubernetes, CI/CD, or any other means), the user tacitly, automatically and irrevocably declares that:',
    '\u2022 They have read, understood and fully agree to all terms of this document and the Apache 2.0 License;',
    '\u2022 They possess the minimum technical knowledge required as described in Clause 3;',
    '\u2022 They assume full responsibility for their use of the software, as described in Clause 6;',
    '\u2022 They are aware of the prohibitions set out in this document and commit to not violating them;',
    '\u2022 They recognize Brazilian jurisdiction as exclusively competent for any disputes;',
    '\u2022 They recognize that third-party data (IBGE, APAC, SEPDEC, INMET, MapBiomas, NASA, Cabo City Hall, SEINFRA-PE, CONDEPE-FIDEM) have their own licenses that must be respected;',
    '\u2022 They recognize that the software is provided "AS IS" (as is), without warranties of any kind (Apache 2.0 Section 7).',
    'IGNORANCE OF THESE TERMS DOES NOT EXEMPT THE USER FROM LIABILITY. THIS DOCUMENT IS PUBLICLY AVAILABLE IN THE OFFICIAL REPOSITORY (ASI_Termos_de_Uso_PT.docx) AND ITS FULL READING IS AN UNCONDITIONAL OBLIGATION OF THE USER BEFORE ANY INTERACTION WITH THE SOFTWARE.'
])

# Section 14
add_section(doc, '14. Data Sources \u2014 Licenses and Mandatory Attributions', [
    'ASI consumes and processes data from the following official sources. The user must respect the terms of use of each source when using, redistributing or deriving products based on ASI outputs:',
    '',
    '| Source | Type | License / Terms | Minimum Attribution |',
    '|--------|------|-----------------|---------------------|',
    '| IBGE (SIDRA, Meshes, SRTM via IBGE) | Census data, administrative boundaries, DEM | Public domain / Free use with attribution (Law 9.610 art. 8) | "Source: IBGE" + publication year |',
    '| APAC-PE | Precipitation, hydrology | Open data Pernambuco State | "Source: APAC Pernambuco" |',
    '| SEPDEC-PE | Flood events, damages | Open data Pernambuco State | "Source: Civil Defense PE \u2014 SEPDEC" |',
    '| INMET | Surface meteorology | Public domain / CC-BY 4.0 | "Source: INMET" |',
    '| MapBiomas (Collection 10, Collection 2 beta) | Land cover/use (LULC) | CC-BY 4.0 | "Source: MapBiomas Project" + collection/year |',
    '| SRTM (NASA/USGS/NGA) | DEM 30m | Public domain (USGS) | "Source: SRTM/NASA/USGS via IBGE" |',
    '| NASA POWER (MERRA-2) | Agrometeorological reanalysis | Public domain NASA | "Source: NASA POWER / MERRA-2" |',
    '| Cabo de Santo Agostinho City Hall | Official neighborhood mesh, zoning | Municipal open data | "Source: Cabo de Santo Agostinho City Hall" |',
    '| SEINFRA-PE | Infrastructure, macrozoning | Open data Pernambuco State | "Source: SEINFRA-PE" |',
    '| CONDEPE-FIDEM | Territorial planning, reports | Open data Pernambuco State | "Source: CONDEPE-FIDEM" |',
    '| CARTO (Basemaps Positron, Dark Matter, Voyager) | Raster/vector tiles | CC-BY 4.0 + API Key | "\u00a9 OpenStreetMap contributors \u00a9 CARTO" + key |',
    '',
    'The complete document of institutional attributions, funding history and technical credits is available at: docs/academic_context/institutions.md.'
])

# Section 15
add_section(doc, '15. Research Funding \u2014 Mandatory Acknowledgement', [
    'The development of ASI was enabled by Scientific and Technological Initiation scholarships (IC/IT) and infrastructure granted by the following agencies. Any publication, thesis, report or derivation of ASI must include acknowledgement to the funding (CNPq/CAPES/FACEPE standard):',
    '\u2022 FACEPE \u2014 Foundation for Science and Technology Support of the State of Pernambuco (PIBIC, PIBITI, BIC-JR, APQ);',
    '\u2022 CNPq \u2014 National Council for Scientific and Technological Development (PIBIC, PIBITI, PIC, Productivity Fellowship);',
    '\u2022 CAPES \u2014 Coordination for the Improvement of Higher Education Personnel (PROEX, DS, PROSUP, Master\u2019s/Doctoral Fellowships);',
    '\u2022 METRO SUL \u2014 Metropolitan Innovation Program / Recife Metropolitan Region;',
    '\u2022 GRE \u2014 Educational Resources Group / Academic Innovation (infrastructure, licenses, support).',
    'Home institution: FACEP \u2014 Faculdade de Ci\u00eancias Educacionais de Pernambuco.'
])

# Section 16
add_section(doc, '16. Correlated Documents and Normative Hierarchy', [
    'This document must be read in conjunction with (order of precedence in case of conflict):',
    '1. Apache 2.0 License (LICENSE) \u2014 legal basis for source code;',
    '2. These Terms of Use PT (ASI_Termos_de_Uso_PT.docx) \u2014 additional contractual restrictions;',
    '3. Terms of Use EN (ASI_Terms_of_Use_EN.docx) \u2014 official English version (prevails in international disputes);',
    '4. README.md \u2014 overview, installation, usage, architecture;',
    '5. INSTRUCTIONS.md \u2014 detailed installation and operation instructions;',
    '6. DTM \u2014 Technical and Methodological Documentation (docs/academic_context/DTM_doc.md);',
    '7. Institutions and Credits (docs/academic_context/institutions.md);',
    '8. Changelog (ASI_CHANGELOG_v3.0.pdf, RELEASE_NOTES_v3.1.md);',
    '9. requirements.txt / pyproject.toml \u2014 dependencies and exact versions;',
    '10. launch.bat \u2014 official Windows launcher (environment validation, .venv, build, tests).'
])

# Section 17
add_section(doc, '17. Final Provisions', [
    '17.1 If any clause of these Terms is declared null, invalid or ineffective by a competent authority, the remaining clauses shall remain in full force and effect.',
    '17.2 The Developer\u2019s tolerance regarding any violation does not constitute waiver of the right to demand future compliance, nor tacit novation.',
    '17.3 The Developer reserves the right to update these Terms at any time, by publishing a new version in the official repository with incremental versioning (SemVer: MAJOR.MINOR.PATCH). Continued use after publication implies acceptance of the new version.',
    '17.4 This document is an integral and inseparable part of the ASI software. The absence of this file in any distribution characterizes irregular and unauthorized distribution.',
    '17.5 Contact for legal matters, commercial licensing, institutional partnerships, misuse reports or authorization requests: lucio.lima@facep.edu.br (FACEP institutional email) or via Issues in the official repository with label legal.'
])

# Footer
doc.add_paragraph()
doc.add_paragraph()
footer_items = [
    'ASI \u2014 Flood Susceptibility Atlas',
    'Terms of Use, Licensing and Liability \u2014 Version 3.3',
    'Apache 2.0 License (code) + CC-BY-4.0 (data/docs) + Additional Contractual Restrictions',
    'Governed by the Laws of the Federative Republic of Brazil',
    'Developer: Lucio Luiz de Lima',
    'Institution: FACEP \u2014 Faculdade de Ci\u00eancias Educacionais de Pernambuco',
    'Official Repository: https://github.com/LuciolLima/ASI---Atlas-de-Suscetibilidade-a-Inundacoes',
    'Publication date of this version: September 2026'
]
for item in footer_items:
    p = doc.add_paragraph(item)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(100, 100, 100)

doc.save('ASI_Terms_of_Use_EN.docx')
print('Documento EN salvo com sucesso!')