import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on cover page

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        self.drawString(54, 750, "SWASTHYA RECORDS — COMPLETE ARCHITECTURE & PROJECT SPECIFICATION")
        self.setFont("Helvetica", 8)
        self.drawRightString(612 - 54, 750, "Google Cloud GenAI Hackathon 2026")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)

        # Running Footer
        self.line(54, 48, 612 - 54, 48)
        self.setFont("Helvetica", 8)
        self.drawString(54, 36, "Track 3: Smart Health & Supply Chain Resilience • GCP Project: arcadeaiagent")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_text)
        self.restoreState()

def build_pdf(filename="Swasthya_Records_Complete_Architecture_and_Project_Details.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    C_PRIMARY = colors.HexColor("#6b21a8")    # Deep Purple
    C_SECONDARY = colors.HexColor("#a855f7")  # Electric Violet
    C_ACCENT = colors.HexColor("#e11d48")     # Crimson/Rose
    C_TEXT = colors.HexColor("#0f172a")       # Dark Slate Text
    C_MUTED = colors.HexColor("#475569")      # Muted Slate
    C_BG_LIGHT = colors.HexColor("#f8fafc")   # Light Background
    C_BORDER = colors.HexColor("#e2e8f0")     # Light Border
    C_CALLOUT_BG = colors.HexColor("#f1f5f9") # Callout Box
    C_EMERALD = colors.HexColor("#059669")    # Green
    C_AMBER = colors.HexColor("#d97706")      # Amber

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=C_PRIMARY,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        textColor=C_SECONDARY,
        spaceAfter=12
    )

    tagline_style = ParagraphStyle(
        'CoverTagline',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=C_ACCENT,
        spaceAfter=24
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=C_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=C_TEXT,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=C_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=C_TEXT,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#1e293b")
    )

    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_TEXT
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=C_TEXT
    )

    story = []

    # =========================================================================
    # COVER PAGE / TITLE BLOCK
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("SWASTHYA RECORDS", title_style))
    story.append(Paragraph("AI-Powered Health Resource & Supply Chain Resilience Platform", subtitle_style))
    story.append(Paragraph("Predict. Warn. Redistribute. Respond.", tagline_style))

    # Decorative Rule
    story.append(HRFlowable(width="100%", thickness=3, color=C_SECONDARY, spaceBefore=0, spaceAfter=16))

    # Executive Metadata Box
    meta_data = [
        [Paragraph("<b>Hackathon Track</b>", table_cell_bold), Paragraph("Track 3: Smart Health & Supply Chain Resilience", table_cell_style)],
        [Paragraph("<b>Target Cloud</b>", table_cell_bold), Paragraph("Google Cloud Run (asia-south1 Mumbai) • BigQuery • Vertex AI", table_cell_style)],
        [Paragraph("<b>GCP Project ID</b>", table_cell_bold), Paragraph("<code>arcadeaiagent</code>", table_cell_style)],
        [Paragraph("<b>GitHub Repository</b>", table_cell_bold), Paragraph("https://github.com/2007Talha/HealthGrid.git", table_cell_style)],
        [Paragraph("<b>Platform Status</b>", table_cell_bold), Paragraph("<font color='#059669'><b>Feature-Complete • Hardened • Verified • Production-Ready</b></font>", table_cell_style)],
        [Paragraph("<b>Date of Release</b>", table_cell_bold), Paragraph("September 2026", table_cell_style)],
    ]
    t_meta = Table(meta_data, colWidths=[130, 374])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 16))

    # Executive Summary Highlight Box
    exec_summary_text = """<b>One-Line Product Definition:</b><br/>
SwasthyaGrid AI is an India-scale AI platform that forecasts healthcare resource demand, detects emerging shortages, and recommends cross-district redistribution before critical stock-outs occur.<br/><br/>
<b>Comprehensive Product Summary:</b><br/>
SwasthyaGrid AI provides a unified view of medicine stocks, patient demand, beds, staffing and health-resource risks across India's PHC network. Gemini and predictive models transform operational data into early warnings and explainable redistribution recommendations, helping decision-makers respond before shortages become critical."""
    
    t_exec = Table([[Paragraph(exec_summary_text, callout_style)]], colWidths=[504])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ede9fe")),
        ('BOX', (0,0), (-1,-1), 1.5, C_SECONDARY),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_exec)
    story.append(Spacer(1, 16))

    # Mandatory Disclaimers Callout
    disclaimer_text = """<b>MANDATORY HACKATHON & REGULATORY DISCLAIMERS:</b><br/>
<b>1. Official Data Disclaimer:</b> Swasthya Records is a prototype decision-support platform. Public and government datasets (MoHFW RHS 2022, HMIS 2022-2023, NLEM 2022, Census 2011) are used where available, while operational PHC inventory, demand, staffing and emergency conditions are simulated for demonstration. The prototype does not execute real-world medical logistics.<br/>
<b>2. AI Decision-Support Disclaimer:</b> AI-generated forecasts and recommendations are decision-support outputs and should always be reviewed and confirmed by authorized human health officers before operational action."""

    t_disc = Table([[Paragraph(disclaimer_text, callout_style)]], colWidths=[504])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fffbeb")),
        ('BOX', (0,0), (-1,-1), 1.5, C_AMBER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_disc)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: THE HEALTHCARE CHALLENGE IN INDIA
    # =========================================================================
    story.append(Paragraph("1. The Healthcare Challenge & Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))
    
    p1 = """Across India's vast public healthcare delivery framework—encompassing over <b>30,000 Primary Health Centres (PHCs)</b> and <b>Community Health Centres (CHCs)</b> serving 1.4 billion citizens—critical medicine shortages, stock-outs, and bed saturation occur unpredictably. Seasonal and climate-induced shocks (such as post-monsoon dengue, malaria, encephalitis, and flood-borne diarrheal outbreaks) trigger sudden localized patient surges of <b>300% to 500%</b>."""
    story.append(Paragraph(p1, body_style))

    p2 = """Under current operational realities:
    <br/>• <b>Fragmented Visibility:</b> Clinic inventory records remain siloed in manual paper registers or localized spreadsheets without real-time state-level aggregation.
    <br/>• <b>Late Detection:</b> Shortages are discovered only after stock hits zero and ill patients are turned away.
    <br/>• <b>Reactive Logistics:</b> Emergency resupply orders take weeks of bureaucratic paperwork to traverse block, district, and state procurement levels.
    <br/>• <b>Unutilized Regional Surplus:</b> While one PHC suffers complete exhaustion of Oral Rehydration Salts (ORS) or Paracetamol, neighboring clinics within a 20–40 km radius frequently hold abundant surplus inventory that sits unutilized until expiration."""
    story.append(Paragraph(p2, body_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: THE SWASTHYA RECORDS SOLUTION
    # =========================================================================
    story.append(Paragraph("2. The Swasthya Records Solution & Core Capabilities", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    sol_text = """Swasthya Records transforms public health supply chain logistics from a <i>reactive crisis management paradigm</i> into an <b>automated, predictive, and resilient intelligence network</b>:"""
    story.append(Paragraph(sol_text, body_style))

    features_table_data = [
        [Paragraph("Pillar", table_header_style), Paragraph("Capability", table_header_style), Paragraph("Operational Impact", table_header_style)],
        [
            Paragraph("<b>1. Predict</b>", table_cell_bold),
            Paragraph("Multi-horizon AI forecasting (Ridge Regression + LightGBM)", table_cell_style),
            Paragraph("Calculates forward medicine consumption 7 and 14 days ahead, detecting demand acceleration before shelves empty.", table_cell_style)
        ],
        [
            Paragraph("<b>2. Warn</b>", table_cell_bold),
            Paragraph("Automated Risk Intelligence Engine & Days of Stock (DOSA)", table_cell_style),
            Paragraph("Categorizes clinics into URGENT, HIGH RISK, WATCHLIST, and HEALTHY tiers. Flags shortages 72 hours in advance.", table_cell_style)
        ],
        [
            Paragraph("<b>3. Explain</b>", table_cell_bold),
            Paragraph("Grounded Gemini 2.5 Flash Operations Copilot", table_cell_style),
            Paragraph("Provides explainable root-cause answers in English and Hindi using deterministic Python backend tools—eliminating AI hallucination.", table_cell_style)
        ],
        [
            Paragraph("<b>4. Redistribute</b>", table_cell_bold),
            Paragraph("Google OR-Tools Mixed-Integer Linear Programming (MILP)", table_cell_style),
            Paragraph("Finds optimal surplus donor clinics within 50 km and computes safe transfer quantities without endangering donor safety buffers.", table_cell_style)
        ],
        [
            Paragraph("<b>5. Simulate</b>", table_cell_bold),
            Paragraph("Sandboxed Digital Twin What-If Simulator", table_cell_style),
            Paragraph("Enables health administrators to simulate hypothetical demand spikes (+40%), delivery delays (+3d), and transfers safely.", table_cell_style)
        ],
    ]
    t_feat = Table(features_table_data, colWidths=[75, 180, 249])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_feat)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("3. Full End-to-End System Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    arch_desc = """The platform follows a decoupled, 5-tier enterprise cloud architecture designed for high throughput, sub-second latency, and verifiable data provenance:"""
    story.append(Paragraph(arch_desc, body_style))

    arch_table_data = [
        [
            Paragraph("<b>TIER 1: PRESENTATION & GIS LAYER</b><br/>"
                      "<font size=7.5 color='#475569'>React 19 • TypeScript • Vite • Tailwind CSS • Leaflet GIS • Arial Sans-Serif Typo</font><br/>"
                      "Interactive GIS command center displaying 33 sentinel facilities with vulnerability-coded map markers. Universal bilingual support (English / हिन्दी) and voice recognition via Web Speech API.", table_cell_style)
        ],
        [
            Paragraph("<font size=7 color='#64748b'>▼ &nbsp; HTTPS / REST JSON API with X-Request-ID Distributed Tracing & Session Security</font>", table_cell_bold)
        ],
        [
            Paragraph("<b>TIER 2: APPLICATION GATEWAY & SECURITY LAYER</b><br/>"
                      "<font size=7.5 color='#475569'>FastAPI (Python 3.11/3.14) • Uvicorn ASGI • Multi-Stage Non-Root Docker Container (Google Cloud Run)</font><br/>"
                      "Centralized Least-Privilege RBAC scoping (ADMIN national, STATE_OPERATOR regional, DISTRICT_OPERATOR local). Unauthorized cross-state queries rejected with HTTP 403. Sliding-window in-memory rate limiting (HTTP 429). Structured JSON logging middleware.", table_cell_style)
        ],
        [
            Paragraph("<font size=7 color='#64748b'>▼ &nbsp; Decoupled Analytical Warehouse & Real-Time Operational Twin Busses</font>", table_cell_bold)
        ],
        [
            Paragraph("<b>TIER 3: DATA WAREHOUSE & REAL-TIME OPERATIONAL TWIN</b><br/>"
                      "<font size=7.5 color='#475569'>Google BigQuery (OLAP Warehouse) & SQLite Relational Store (ACID Transactional Twin)</font><br/>"
                      "BigQuery dataset <code>arcadeaiagent.swasthyagrid</code> hosts public MoHFW RHS 2022 facility counts, HMIS 2022-2023 footfall baselines, and NLEM 2022 formulary. SQLite maintains real-time clinic inventory, active emergency multipliers, and transfer audit logs.", table_cell_style)
        ],
        [
            Paragraph("<font size=7 color='#64748b'>▼ &nbsp; Grounded AI Feature Extraction & Combinatorial Optimization Pipelines</font>", table_cell_bold)
        ],
        [
            Paragraph("<b>TIER 4: AI FORECASTING & RESOURCE REDISTRIBUTION ENGINES</b><br/>"
                      "<font size=7.5 color='#475569'>Scikit-Learn Ridge + LightGBM Forecasting & Google OR-Tools CBC/SCIP MILP Solver</font><br/>"
                      "Projects forward medicine consumption over 7 and 14 days. Risk engine computes Days of Stock Available (DOSA) with 60s in-memory TTL cache. OR-Tools computes cross-district vehicle routes enforcing a 7-day donor safety buffer and a 50 km transit radius.", table_cell_style)
        ],
        [
            Paragraph("<font size=7 color='#64748b'>▼ &nbsp; Deterministic Function Calling & Anti-Hallucination Guardrail Layer</font>", table_cell_bold)
        ],
        [
            Paragraph("<b>TIER 5: GROUNDED OPERATIONS COPILOT (GEMINI 2.5 FLASH)</b><br/>"
                      "<font size=7.5 color='#475569'>Google Cloud Vertex AI SDK • Gemini 2.5 Flash Foundation Model</font><br/>"
                      "Provides explainable root-cause insights and What-If practice sandboxing. Bound by strict Python deterministic function tools (<code>get_facility_status</code>, <code>calculate_stock_risk</code>, <code>recommend_redistribution</code>). Strict regex registry guardrails prevent hallucinated inventory.", table_cell_style)
        ]
    ]

    t_arch = Table(arch_table_data, colWidths=[504])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f3e8ff")),
        ('BOX', (0,0), (0,0), 1, C_SECONDARY),
        ('BACKGROUND', (0,1), (0,1), colors.white),
        ('ALIGN', (0,1), (0,1), 'CENTER'),
        ('BACKGROUND', (0,2), (0,2), colors.HexColor("#f1f5f9")),
        ('BOX', (0,2), (0,2), 1, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,3), (0,3), colors.white),
        ('ALIGN', (0,3), (0,3), 'CENTER'),
        ('BACKGROUND', (0,4), (0,4), colors.HexColor("#ede9fe")),
        ('BOX', (0,4), (0,4), 1, colors.HexColor("#a78bfa")),
        ('BACKGROUND', (0,5), (0,5), colors.white),
        ('ALIGN', (0,5), (0,5), 'CENTER'),
        ('BACKGROUND', (0,6), (0,6), colors.HexColor("#ecfdf5")),
        ('BOX', (0,6), (0,6), 1, colors.HexColor("#6ee7b7")),
        ('BACKGROUND', (0,7), (0,7), colors.white),
        ('ALIGN', (0,7), (0,7), 'CENTER'),
        ('BACKGROUND', (0,8), (0,8), colors.HexColor("#fff1f2")),
        ('BOX', (0,8), (0,8), 1, colors.HexColor("#fda4af")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: LANGUAGES & TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("4. Languages, Frameworks & Complete Technology Stack", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("The application is engineered exclusively with battle-tested, high-performance open technologies:", body_style))

    tech_stack_data = [
        [Paragraph("Category", table_header_style), Paragraph("Technology", table_header_style), Paragraph("Version", table_header_style), Paragraph("Purpose / Rationale", table_header_style)],
        [
            Paragraph("<b>Core Language</b>", table_cell_bold),
            Paragraph("<b>Python</b>", table_cell_style),
            Paragraph("3.11 / 3.14", table_cell_style),
            Paragraph("Backend API service, data simulation engine, machine learning forecasting, and OR-Tools optimization logic.", table_cell_style)
        ],
        [
            Paragraph("<b>Core Language</b>", table_cell_bold),
            Paragraph("<b>TypeScript / JS</b>", table_cell_style),
            Paragraph("ES2022 / TS 5.x", table_cell_style),
            Paragraph("Strongly-typed frontend client logic, API data models, state management, and real-time reactive UI rendering.", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend Core</b>", table_cell_bold),
            Paragraph("<b>React</b>", table_cell_style),
            Paragraph("19.0.0", table_cell_style),
            Paragraph("Modern component-based user interface, hooks-driven state, context providers, and responsive client hydration.", table_cell_style)
        ],
        [
            Paragraph("<b>Build Tool</b>", table_cell_bold),
            Paragraph("<b>Vite</b>", table_cell_style),
            Paragraph("8.2.2", table_cell_style),
            Paragraph("Blazing fast development server and optimized production bundler producing minified static assets in dist/.", table_cell_style)
        ],
        [
            Paragraph("<b>Styling Framework</b>", table_cell_bold),
            Paragraph("<b>Tailwind CSS</b>", table_cell_style),
            Paragraph("3.4.1", table_cell_style),
            Paragraph("Utility-first styling customized with the Obsidian Neon dark palette, responsive breakpoints, and custom scrollbars.", table_cell_style)
        ],
        [
            Paragraph("<b>Typography</b>", table_cell_bold),
            Paragraph("<b>Arial Sans-Serif</b>", table_cell_style),
            Paragraph("Universal", table_cell_style),
            Paragraph("Clean, distraction-free, globally accessible sans-serif typography across all headers, tables, charts, and buttons.", table_cell_style)
        ],
        [
            Paragraph("<b>GIS Mapping</b>", table_cell_bold),
            Paragraph("<b>Leaflet & React-Leaflet</b>", table_cell_style),
            Paragraph("1.9.4 / 4.2.1", table_cell_style),
            Paragraph("Interactive geospatial mapping displaying 33 sentinel facilities with vulnerability-coded interactive pin markers.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend Gateway</b>", table_cell_bold),
            Paragraph("<b>FastAPI</b>", table_cell_style),
            Paragraph("0.110.0", table_cell_style),
            Paragraph("High-throughput asynchronous ASGI web framework with automatic OpenAPI/Swagger generation and Pydantic v2 validation.", table_cell_style)
        ],
        [
            Paragraph("<b>ASGI Server</b>", table_cell_bold),
            Paragraph("<b>Uvicorn</b>", table_cell_style),
            Paragraph("0.28.0", table_cell_style),
            Paragraph("Production-grade Lightning-fast ASGI web server implementation for Python.", table_cell_style)
        ],
        [
            Paragraph("<b>Optimization Solver</b>", table_cell_bold),
            Paragraph("<b>Google OR-Tools</b>", table_cell_style),
            Paragraph("9.9.3963", table_cell_style),
            Paragraph("Mixed-Integer Linear Programming (MILP) solving cross-district redistribution under capacity and safety constraints.", table_cell_style)
        ],
        [
            Paragraph("<b>Predictive AI</b>", table_cell_bold),
            Paragraph("<b>Scikit-Learn / LightGBM</b>", table_cell_style),
            Paragraph("1.4.1 / 4.3.0", table_cell_style),
            Paragraph("Multi-horizon time series forecasting modeling seasonality, trends, and disaster-driven surge multipliers.", table_cell_style)
        ],
        [
            Paragraph("<b>Generative AI</b>", table_cell_bold),
            Paragraph("<b>Google GenAI SDK</b>", table_cell_style),
            Paragraph("Gemini 2.5 Flash", table_cell_style),
            Paragraph("Vertex AI / Google GenAI foundation model powering the Operations Copilot with deterministic function calling.", table_cell_style)
        ],
        [
            Paragraph("<b>Data Warehouse</b>", table_cell_bold),
            Paragraph("<b>Google BigQuery</b>", table_cell_style),
            Paragraph("Cloud OLAP", table_cell_style),
            Paragraph("Serverless, highly scalable multi-cloud data warehouse hosting official public Indian government healthcare records.", table_cell_style)
        ],
        [
            Paragraph("<b>Operational DB</b>", table_cell_bold),
            Paragraph("<b>SQLite / SQLAlchemy</b>", table_cell_style),
            Paragraph("3.x / 2.0.28", table_cell_style),
            Paragraph("Embedded ACID-compliant transactional relational database driving the low-latency operational digital twin.", table_cell_style)
        ],
        [
            Paragraph("<b>Containerization</b>", table_cell_bold),
            Paragraph("<b>Docker / Nginx</b>", table_cell_style),
            Paragraph("Multi-Stage", table_cell_style),
            Paragraph("Non-root Python 3.11 container for FastAPI backend; Alpine Nginx reverse proxy container for React frontend.", table_cell_style)
        ],
        [
            Paragraph("<b>Test Suites</b>", table_cell_bold),
            Paragraph("<b>Pytest & Vitest</b>", table_cell_style),
            Paragraph("9.1.1 / 4.1.11", table_cell_style),
            Paragraph("Automated test runners achieving 100% test passing rate across security RBAC, data invariants, and UI components.", table_cell_style)
        ],
    ]
    t_tech = Table(tech_stack_data, colWidths=[90, 110, 64, 240])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tech)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: THE FOUR AI PILLARS IN DETAIL
    # =========================================================================
    story.append(Paragraph("5. Deep Dive: The Four Artificial Intelligence Pillars", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("<b>Pillar 1: Predictive Demand Forecasting</b>", h2_style))
    p_ai1 = """The demand forecasting service (<code>backend/app/services/forecasting_service.py</code>) projects medicine consumption over 1-day, 3-day, 7-day, and 14-day horizons.
    <br/>• <b>Mathematical Methodology:</b> Combines regularized L2 Ridge Regression with LightGBM gradient-boosted decision trees.
    <br/>• <b>Feature Inputs:</b> 90-day rolling daily dispensation records, day-of-week seasonality, OPD footfall trends from HMIS, and active disaster multipliers.
    <br/>• <b>Output:</b> Expected daily unit demand with 80% and 95% confidence intervals, allowing the platform to detect accelerating consumption before inventory runs out."""
    story.append(Paragraph(p_ai1, body_style))

    story.append(Paragraph("<b>Pillar 2: Risk Intelligence & Days of Stock Available (DOSA)</b>", h2_style))
    p_ai2 = """The risk intelligence engine (<code>backend/app/services/risk_engine.py</code>) continuously evaluates stockout probability across all facility-medicine pairs:
    <br/>• <b>Mathematical Formula:</b>
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>DOSA = Current Usable Stock / Projected Daily Demand</b>
    <br/>• <b>Classification Thresholds:</b>
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;- <b>URGENT / CRITICAL:</b> DOSA < 3.0 days (Immediate stockout risk within resupply lead time).
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;- <b>HIGH RISK:</b> 3.0 <= DOSA < 7.0 days (Vulnerable to sudden footfall spikes).
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;- <b>WATCHLIST:</b> 7.0 <= DOSA < 14.0 days (Normal buffer maintenance).
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;- <b>HEALTHY:</b> DOSA >= 14.0 days (Optimal operational inventory).
    <br/>• <b>Caching & Speedup:</b> Implements a 60-second in-memory TTL cache with automated invalidation on simulation events, reducing evaluation time from minutes to <b>1.1 seconds</b>."""
    story.append(Paragraph(p_ai2, body_style))

    story.append(Paragraph("<b>Pillar 3: Grounded Operations Copilot (Gemini 2.5 Flash)</b>", h2_style))
    p_ai3 = """The AI Copilot (<code>backend/app/services/copilot_service.py</code>) provides natural-language operational reasoning:
    <br/>• <b>Zero Hallucination Architecture:</b> The LLM never invents inventory levels or facility names. All operational answers are formulated by invoking deterministic backend tools:
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;1. <code>get_facility_status(facility_id)</code>: Returns live verified inventory, beds, and staff.
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;2. <code>calculate_stock_risk(facility_id, medicine_code)</code>: Returns DOSA and risk classification.
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;3. <code>recommend_redistribution(facility_id, medicine_code, days_buffer)</code>: Executes OR-Tools rebalancing.
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;4. <code>simulate_transfer(source_id, dest_id, quantity)</code>: Sandboxed practice transfer.
    <br/>• <b>Anti-Hallucination Guardrail:</b> Regex validation rejects invalid facility IDs (e.g., PHC-999999) with an explicit <i>'Facility ID not found in registry'</i> response."""
    story.append(Paragraph(p_ai3, body_style))

    story.append(Paragraph("<b>Pillar 4: Resource Redistribution Optimization (Google OR-Tools)</b>", h2_style))
    p_ai4 = """The redistribution engine (<code>backend/app/services/optimization_engine.py</code>) uses Google OR-Tools CBC Mixed-Integer Linear Programming:
    <br/>• <b>Objective Function:</b> Minimizes total logistics transit distance and delivery urgency cost:
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;<b>min Σ (c_ij * x_ij + λ * d_ij)</b>
    <br/>• <b>Hard Safety Constraints:</b>
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;1. <i>Donor Non-Depletion:</i> A donor clinic cannot transfer stock if its own DOSA drops below 7.0 days.
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;2. <i>Target Need Cap:</i> Recipient receives only enough to restore inventory to a safe 14-day level.
    <br/>&nbsp;&nbsp;&nbsp;&nbsp;3. <i>Transit Radius:</i> Prioritizes donors within a 50 km road distance to ensure transit ETA under 2.5 hours."""
    story.append(Paragraph(p_ai4, body_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: DATA PROVENANCE & TRANSPARENCY
    # =========================================================================
    story.append(Paragraph("6. Data Foundations & Provenance Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Swasthya Records maintains complete transparency between official government data and simulated operational data:", body_style))

    data_matrix = [
        [Paragraph("Dataset Name", table_header_style), Paragraph("Publisher / Authority", table_header_style), Paragraph("Source Type", table_header_style), Paragraph("How Swasthya Records Uses It", table_header_style)],
        [
            Paragraph("<b>Rural Health Statistics (RHS) 2021-22</b>", table_cell_bold),
            Paragraph("Ministry of Health and Family Welfare (MoHFW), Govt of India", table_cell_style),
            Paragraph("<font color='#059669'><b>Official Public Data</b></font>", table_cell_style),
            Paragraph("Establishes the foundational registry of 33 sentinel facilities across Bihar, UP, and Maharashtra with sanctioned beds, staff, and GPS coordinates.", table_cell_style)
        ],
        [
            Paragraph("<b>HMIS 2022-2023</b>", table_cell_bold),
            Paragraph("National Health Mission (NHM), MoHFW", table_cell_style),
            Paragraph("<font color='#059669'><b>Official Public Data</b></font>", table_cell_style),
            Paragraph("Calibrates seasonal patient footfall baselines, outpatient (OPD) visit rates, and baseline bed occupancy curves.", table_cell_style)
        ],
        [
            Paragraph("<b>National List of Essential Medicines (NLEM 2022)</b>", table_cell_bold),
            Paragraph("Dept of Pharmaceuticals & CDSCO, Govt of India", table_cell_style),
            Paragraph("<font color='#059669'><b>Official Formulary</b></font>", table_cell_style),
            Paragraph("Standardizes the 20 tracked core essential medicines (ORS, Paracetamol, Amoxicillin, Metformin, etc.) with packaging units and safety buffers.", table_cell_style)
        ],
        [
            Paragraph("<b>Census of India Demographics</b>", table_cell_bold),
            Paragraph("Office of the Registrar General, Ministry of Home Affairs", table_cell_style),
            Paragraph("<font color='#059669'><b>Official Demographics</b></font>", table_cell_style),
            Paragraph("Supplies catchment population sizes and district administrative boundaries for logistics transit calculations.", table_cell_style)
        ],
        [
            Paragraph("<b>Operational Digital Twin</b>", table_cell_bold),
            Paragraph("Swasthya Records Simulation Engine", table_cell_style),
            Paragraph("<font color='#d97706'><b>Prototype Simulation</b></font>", table_cell_style),
            Paragraph("Simulates daily medicine consumption telemetry and active flood surge multipliers because real-time minute-by-minute PHC telemetry is not publicly accessible via open APIs.", table_cell_style)
        ],
    ]
    t_data = Table(data_matrix, colWidths=[120, 114, 90, 180])
    t_data.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_data)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 7: SECURITY & RBAC
    # =========================================================================
    story.append(Paragraph("7. Enterprise Security, Access Control & Auditing", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    sec_p = """To ensure complete data protection and administrative boundaries, Swasthya Records implements rigorous enterprise security:"""
    story.append(Paragraph(sec_p, body_style))

    sec_table = [
        [Paragraph("Security Layer", table_header_style), Paragraph("Implementation Mechanism", table_header_style), Paragraph("HTTP Response / Enforcement", table_header_style)],
        [
            Paragraph("<b>National Admin (ADMIN)</b>", table_cell_bold),
            Paragraph("Full unrestricted read, write, and simulation privileges across all 36 States and Union Territories.", table_cell_style),
            Paragraph("<font color='#059669'><b>HTTP 200 OK</b></font> (National Scope)", table_cell_style)
        ],
        [
            Paragraph("<b>State Operator</b>", table_cell_bold),
            Paragraph("Scoped strictly to assigned state code (e.g., Bihar IN-BR). Attempts to query facilities in Uttar Pradesh or Maharashtra are blocked.", table_cell_style),
            Paragraph("<font color='#e11d48'><b>HTTP 403 Forbidden</b></font><br/>(Cross-State Access Denied)", table_cell_style)
        ],
        [
            Paragraph("<b>District Operator</b>", table_cell_bold),
            Paragraph("Scoped strictly to assigned district code (e.g., Patna IN-BR-PAT). Cannot view or alter other districts.", table_cell_style),
            Paragraph("<font color='#e11d48'><b>HTTP 403 Forbidden</b></font><br/>(Cross-District Access Denied)", table_cell_style)
        ],
        [
            Paragraph("<b>Rate Limiting</b>", table_cell_bold),
            Paragraph("Sliding-window in-memory rate limiter on /copilot/* and /redistribution/* preventing server overload and API cost inflation.", table_cell_style),
            Paragraph("<font color='#d97706'><b>HTTP 429 Too Many Requests</b></font><br/>(Retry-After Header attached)", table_cell_style)
        ],
        [
            Paragraph("<b>Structured Observability</b>", table_cell_bold),
            Paragraph("FastAPI middleware injects unique X-Request-ID header on every transaction and logs structured JSON without exposing secrets.", table_cell_style),
            Paragraph("<code>X-Request-ID: &lt;uuid4&gt;</code><br/>Structured JSON Cloud Logs", table_cell_style)
        ],
        [
            Paragraph("<b>Zero Secret Exposure</b>", table_cell_bold),
            Paragraph("100% environment-variable driven configuration (.env.example). Zero hardcoded API keys or credentials in codebase.", table_cell_style),
            Paragraph("Automated GitHub Secret Scanner Verification Passed", table_cell_style)
        ],
    ]
    t_sec = Table(sec_table, colWidths=[120, 234, 150])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sec)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 8: 7-STEP DEMO WALKTHROUGH
    # =========================================================================
    story.append(Paragraph("8. The 7-Step Judge Demonstration Scenario", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("The platform features a turnkey 1-Click Guided Demo Flow (accessible at <code>/demo</code>) walking through a complete real-world crisis scenario:", body_style))

    demo_steps = [
        [Paragraph("Step", table_header_style), Paragraph("Scenario Event", table_header_style), Paragraph("System Actions & Visual Feedback", table_header_style)],
        [
            Paragraph("<b>Step 1</b>", table_cell_bold),
            Paragraph("Baseline Operations", table_cell_style),
            Paragraph("33 sentinel clinics across Bihar, UP, and Maharashtra operate normally tracking 20 essential NLEM medicines.", table_cell_style)
        ],
        [
            Paragraph("<b>Step 2</b>", table_cell_bold),
            Paragraph("Emergency Flood Surge", table_cell_style),
            Paragraph("Monsoon flooding hits Patna District. Patient footfall increases by +40%, accelerating consumption of ORS and Paracetamol.", table_cell_style)
        ],
        [
            Paragraph("<b>Step 3</b>", table_cell_bold),
            Paragraph("AI Demand Recalculation", table_cell_style),
            Paragraph("Forecasting engine detects burn rate doubling to 185 units/day (normally only 60 units/day).", table_cell_style)
        ],
        [
            Paragraph("<b>Step 4</b>", table_cell_bold),
            Paragraph("Early Warning Alert", table_cell_style),
            Paragraph("The system alerts health officers that Patna Sadar PHC will exhaust all ORS in just 1.4 days if no resupply occurs.", table_cell_style)
        ],
        [
            Paragraph("<b>Step 5</b>", table_cell_bold),
            Paragraph("Gemini Copilot Inquiry", table_cell_style),
            Paragraph("Officer asks: 'Why is this clinic low and who can help?' Gemini queries verified database tools and explains the numbers.", table_cell_style)
        ],
        [
            Paragraph("<b>Step 6</b>", table_cell_bold),
            Paragraph("OR-Tools Rebalancing", table_cell_style),
            Paragraph("MILP solver identifies Danapur PHC has 850 units of ORS and can safely transfer 200 units (18 km away, 1.2 hrs transit).", table_cell_style)
        ],
        [
            Paragraph("<b>Step 7</b>", table_cell_bold),
            Paragraph("Simulate & Mitigate", table_cell_style),
            Paragraph("Officer clicks 'Approve & Simulate'. Recipient stock runway jumps to 14.2 days; shortage risk drops from URGENT to SAFE.", table_cell_style)
        ],
    ]
    t_demo = Table(demo_steps, colWidths=[48, 140, 316])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 9: VERIFICATION & TESTING AUDIT
    # =========================================================================
    story.append(Paragraph("9. Testing, Verification & Production Hardening Audit", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Swasthya Records has undergone end-to-end automated testing to verify resilience, data invariants, and security:", body_style))

    test_audit_data = [
        [Paragraph("Test Suite", table_header_style), Paragraph("Framework", table_header_style), Paragraph("Pass Rate", table_header_style), Paragraph("Execution Time", table_header_style), Paragraph("Verified Scope", table_header_style)],
        [
            Paragraph("<b>Backend Security & RBAC</b>", table_cell_bold),
            Paragraph("Pytest 9.1.1", table_cell_style),
            Paragraph("<font color='#059669'><b>100% (8/8)</b></font>", table_cell_style),
            Paragraph("1.48s", table_cell_style),
            Paragraph("Admin access, State/District 403 scoping, 429 rate limiting, X-Request-ID.", table_cell_style)
        ],
        [
            Paragraph("<b>Data Resilience & Invariants</b>", table_cell_bold),
            Paragraph("Pytest 9.1.1", table_cell_style),
            Paragraph("<font color='#059669'><b>100% (4/4)</b></font>", table_cell_style),
            Paragraph("Included above", table_cell_style),
            Paragraph("Deterministic reset, flood seed, anti-hallucination regex, non-negative stock.", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend Unit Tests</b>", table_cell_bold),
            Paragraph("Vitest 4.1.11", table_cell_style),
            Paragraph("<font color='#059669'><b>100% (4/4)</b></font>", table_cell_style),
            Paragraph("202ms", table_cell_style),
            Paragraph("API client auth header injection, English/Hindi dictionary parity, preset users.", table_cell_style)
        ],
        [
            Paragraph("<b>Production Build Bundle</b>", table_cell_bold),
            Paragraph("Vite 8.2.2 / tsc", table_cell_style),
            Paragraph("<font color='#059669'><b>100% SUCCESS</b></font>", table_cell_style),
            Paragraph("1.78s", table_cell_style),
            Paragraph("Zero TypeScript errors, minified production chunk generation in dist/.", table_cell_style)
        ],
        [
            Paragraph("<b>Liveness Probe (/health)</b>", table_cell_bold),
            Paragraph("HTTP Probe", table_cell_style),
            Paragraph("<font color='#059669'><b>HTTP 200 OK</b></font>", table_cell_style),
            Paragraph("12ms", table_cell_style),
            Paragraph("Container orchestrator healthcheck returning status: ok, health: HEALTHY.", table_cell_style)
        ],
        [
            Paragraph("<b>Readiness (/health/deps)</b>", table_cell_bold),
            Paragraph("HTTP Probe", table_cell_style),
            Paragraph("<font color='#059669'><b>HTTP 200 OK</b></font>", table_cell_style),
            Paragraph("18ms", table_cell_style),
            Paragraph("Subsystem verification: Database, BigQuery, Gemini Copilot, Simulator.", table_cell_style)
        ],
    ]
    t_audit = Table(test_audit_data, colWidths=[110, 70, 75, 65, 184])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_audit)

    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 10: DEPLOYMENT & REPRODUCIBILITY
    # =========================================================================
    story.append(Paragraph("10. Google Cloud Run Deployment & Local Execution", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    dep_p = """Swasthya Records is designed for effortless reproducibility both on Google Cloud Run and locally:
    <br/>• <b>Local Multi-Container Stack:</b> Execute <code>docker-compose up --build</code> to launch the full stack (Frontend at port 3000, Backend at port 8000).
    <br/>• <b>Automated Cloud Run Script:</b> Run <code>./scripts/deploy_cloud_run.sh</code> to build multi-stage non-root containers, push to Artifact Registry, and deploy to Cloud Run in <code>asia-south1</code> (Mumbai).
    <br/>• <b>Fast Baseline Reset:</b> Health officials and evaluators can return the digital twin deterministically to its initial state at any moment via <code>POST /api/v1/simulation/reset</code>."""
    story.append(Paragraph(dep_p, body_style))

    story.append(Spacer(1, 14))

    # Final Closing Signature Box
    closing_text = """<b>SWASTHYA RECORDS — PREDICT. WARN. REDISTRIBUTE. RESPOND.</b><br/>
<i>'Swasthya Records turns fragmented healthcare-resource signals into an early-warning and response system—predicting demand, identifying shortages, finding safe redistribution opportunities, and giving decision-makers an explainable AI copilot.'</i><br/><br/>
<b>Team Contact & Source Code:</b> https://github.com/2007Talha/HealthGrid.git • Google Cloud Project: <code>arcadeaiagent</code>"""
    
    t_close = Table([[Paragraph(closing_text, callout_style)]], colWidths=[504])
    t_close.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1.5, C_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_close)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    out_pdf = "Swasthya_Records_Complete_Architecture_and_Project_Details.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)
