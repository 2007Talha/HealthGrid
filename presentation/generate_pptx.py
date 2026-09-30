"""
SwasthyaGrid AI - Automated Native PowerPoint Pitch Deck Generator
Creates a 16:9 professional widescreen PowerPoint presentation (.pptx)
in an executive, high-contrast LIGHT THEME with polished visual hierarchy
and embedded judge pitch speaker notes on every single slide.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# =============================================================================
# EXECUTIVE LIGHT THEME PALETTE
# =============================================================================
BG_PAGE = RGBColor(248, 250, 252)       # Slate-50 Clean Page Background #F8FAFC
BG_WHITE = RGBColor(255, 255, 255)      # Pure White Surface #FFFFFF
BG_SURFACE = RGBColor(241, 245, 249)    # Slate-100 Elevated Surface #F1F5F9
BG_CARD = RGBColor(255, 255, 255)       # Card Fill #FFFFFF
BG_CARD_ALT = RGBColor(248, 250, 252)   # Alt Card Fill #F8FAFC

BORDER_CARD = RGBColor(226, 232, 240)   # Slate-200 Subtle Border #E2E8F0
BORDER_STRONG = RGBColor(203, 213, 225) # Slate-300 Strong Border #CBD5E1

COLOR_PRIMARY = RGBColor(29, 78, 216)   # Deep Royal Blue #1D4ED8
COLOR_BLUE = RGBColor(37, 99, 235)      # Tech Blue #2563EB
COLOR_CYAN = RGBColor(8, 145, 178)      # Teal/Cyan Accent #0891B2
COLOR_EMERALD = RGBColor(5, 150, 105)   # Medical Emerald Green #059669
COLOR_AMBER = RGBColor(217, 119, 6)     # Amber/Orange Warning #D97706
COLOR_RED = RGBColor(220, 38, 38)       # Crimson Red #DC2626
COLOR_PURPLE = RGBColor(124, 58, 237)   # Royal Purple #7C3AED

TEXT_TITLE = RGBColor(15, 23, 42)       # Slate-900 Almost Black #0F172A
TEXT_MAIN = RGBColor(30, 41, 59)        # Slate-800 Dark Text #1E293B
TEXT_LIGHT = RGBColor(51, 65, 85)       # Slate-700 Medium Text #334155
TEXT_MUTED = RGBColor(100, 116, 139)    # Slate-500 Neutral #64748B
TEXT_FAINT = RGBColor(148, 163, 184)    # Slate-400 Subtle #94A3B8

# Soft tints for container backgrounds
TINT_RED = RGBColor(254, 242, 242)      # Red-50 #FEF2F2
TINT_BLUE = RGBColor(239, 246, 255)     # Blue-50 #EFF6FF
TINT_CYAN = RGBColor(240, 253, 250)     # Cyan-50 #F0FDFA
TINT_EMERALD = RGBColor(236, 253, 245)  # Emerald-50 #ECFDF5
TINT_AMBER = RGBColor(254, 243, 199)    # Amber-100 #FEF3C7
TINT_PURPLE = RGBColor(245, 243, 255)   # Purple-50 #F5F3FF

def add_header(slide, slide_num, tag, title, subtitle):
    """Adds a standardized, elegant light theme header to a slide."""
    # Top Tag / Category Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.38), Inches(4.5), Inches(0.34))
    pill.fill.solid()
    pill.fill.fore_color.rgb = TINT_BLUE
    pill.line.color.rgb = COLOR_BLUE
    pill.line.width = Pt(1)
    
    p_tf = pill.text_frame
    p_tf.word_wrap = True
    pp = p_tf.paragraphs[0]
    pp.text = f"{slide_num} / {tag}"
    pp.font.name = "Consolas"
    pp.font.size = Pt(10)
    pp.font.bold = True
    pp.font.color.rgb = COLOR_PRIMARY
    pp.alignment = PP_ALIGN.CENTER

    # Main Headline
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.733), Inches(0.65))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.name = "Arial"
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_TITLE

    # Subtitle
    s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.42), Inches(11.733), Inches(0.4))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle
    p_s.font.name = "Arial"
    p_s.font.size = Pt(13)
    p_s.font.color.rgb = TEXT_MUTED

def add_footer(slide, slide_num):
    """Adds a standardized professional light theme footer to every slide."""
    # Bottom separator line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_CARD
    line.line.fill.background()

    # Left Footer Text
    f_left = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(8.0), Inches(0.35))
    p_l = f_left.text_frame.paragraphs[0]
    p_l.text = "SWASTHYAGRID AI • Google Cloud GenAI Hackathon 2026 • Track 3: Smart Health & Resilience"
    p_l.font.name = "Consolas"
    p_l.font.size = Pt(9.5)
    p_l.font.color.rgb = TEXT_FAINT

    # Right Footer Text
    f_right = slide.shapes.add_textbox(Inches(10.5), Inches(6.95), Inches(2.0), Inches(0.35))
    p_r = f_right.text_frame.paragraphs[0]
    p_r.text = f"Slide {slide_num} of 12"
    p_r.font.name = "Consolas"
    p_r.font.size = Pt(9.5)
    p_r.font.bold = True
    p_r.font.color.rgb = COLOR_PRIMARY
    p_r.alignment = PP_ALIGN.RIGHT

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: HERO / TITLE & HOOK (LIGHT THEME)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_PAGE
    bg1.line.fill.background()

    # Track Banner Pill
    t_pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.41), Inches(0.75), Inches(6.5), Inches(0.42))
    t_pill.fill.solid()
    t_pill.fill.fore_color.rgb = TINT_BLUE
    t_pill.line.color.rgb = COLOR_BLUE
    t_pill.line.width = Pt(1.5)
    p_tp = t_pill.text_frame.paragraphs[0]
    p_tp.text = "GOOGLE CLOUD GENAI HACKATHON 2026 • TRACK 3: SMART HEALTH"
    p_tp.font.name = "Consolas"
    p_tp.font.size = Pt(11)
    p_tp.font.bold = True
    p_tp.font.color.rgb = COLOR_PRIMARY
    p_tp.alignment = PP_ALIGN.CENTER

    # Main Hero Title
    hero_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.35), Inches(11.333), Inches(1.3))
    p_h = hero_box.text_frame.paragraphs[0]
    p_h.text = "SWASTHYAGRID AI"
    p_h.font.name = "Arial"
    p_h.font.size = Pt(50)
    p_h.font.bold = True
    p_h.font.color.rgb = TEXT_TITLE
    p_h.alignment = PP_ALIGN.CENTER

    sub_h = hero_box.text_frame.add_paragraph()
    sub_h.text = "Predict. Warn. Redistribute. Respond."
    sub_h.font.name = "Consolas"
    sub_h.font.size = Pt(20)
    sub_h.font.bold = True
    sub_h.font.color.rgb = COLOR_PRIMARY
    sub_h.alignment = PP_ALIGN.CENTER
    sub_h.space_before = Pt(6)

    # Mission Statement
    m_box = s1.shapes.add_textbox(Inches(1.5), Inches(2.8), Inches(10.333), Inches(0.9))
    p_m = m_box.text_frame.paragraphs[0]
    p_m.text = (
        "An India-scale AI platform forecasting healthcare resource demand surges, flagging stockouts "
        "72 hours in advance, and computing optimal cross-district redistribution using Google OR-Tools and Gemini 2.5 Flash."
    )
    p_m.font.name = "Arial"
    p_m.font.size = Pt(15)
    p_m.font.color.rgb = TEXT_LIGHT
    p_m.alignment = PP_ALIGN.CENTER

    # 4 Metric Highlight Cards (White Cards with Colored Borders)
    metrics_s1 = [
        ("30,000+", "Primary Health Centres in Scope", COLOR_PRIMARY, TINT_BLUE),
        ("72 Hours", "Proactive Early Warning Window", COLOR_EMERALD, TINT_EMERALD),
        ("51.7%", "ML Demand Forecast Accuracy Gain", COLOR_PURPLE, TINT_PURPLE),
        ("< 2 Hours", "Automated Multi-Facility Redistribution", COLOR_AMBER, TINT_AMBER)
    ]
    card_w = Inches(2.7)
    gap = Inches(0.24)
    for idx, (val, lbl, col, tint) in enumerate(metrics_s1):
        x = Inches(0.8) + idx * (card_w + gap)
        c = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(3.95), card_w, Inches(1.85))
        c.fill.solid()
        c.fill.fore_color.rgb = BG_WHITE
        c.line.color.rgb = BORDER_CARD
        c.line.width = Pt(1.5)

        # Top Accent Stripe
        stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(3.95), card_w, Inches(0.08))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = col
        stripe.line.fill.background()

        ctf = c.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = val
        cp1.font.name = "Arial"
        cp1.font.size = Pt(30)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp1.alignment = PP_ALIGN.CENTER
        cp1.space_before = Pt(16)

        cp2 = ctf.add_paragraph()
        cp2.text = lbl
        cp2.font.name = "Arial"
        cp2.font.size = Pt(11)
        cp2.font.bold = True
        cp2.font.color.rgb = TEXT_MUTED
        cp2.alignment = PP_ALIGN.CENTER
        cp2.space_before = Pt(6)

    # Bottom Metadata Strip
    cred_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.4))
    p_cr = cred_box.text_frame.paragraphs[0]
    p_cr.text = "GCP Project ID: arcadeaiagent  •  Region: asia-south1 (Mumbai)  •  Official MoHFW RHS & HMIS Data Provenance"
    p_cr.font.name = "Consolas"
    p_cr.font.size = Pt(11)
    p_cr.font.color.rgb = TEXT_FAINT
    p_cr.alignment = PP_ALIGN.CENTER

    add_footer(s1, "01")
    s1.notes_slide.notes_text_frame.text = (
        "[0:00 - 0:20] Pitch Hook & Executive Framing:\n\n"
        "Good morning, Judges. Imagine a monsoon flood in rural Bihar. A primary clinic is swamped with 500 fever patients, "
        "and their shelves run completely dry of Paracetamol and IV fluids. Children are turned away in critical condition. "
        "Yet just 18 kilometers down the highway, another health centre has 3,500 surplus packs sitting idle in a locked cabinet.\n\n"
        "This is not a manufacturing shortage—it is an intelligence and logistics failure. Today, we present SwasthyaGrid AI: "
        "Predict. Warn. Redistribute. Respond."
    )

    # =========================================================================
    # SLIDE 2: THE CRISIS (PROBLEM) (LIGHT THEME)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    bg2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg2.fill.solid()
    bg2.fill.fore_color.rgb = BG_PAGE
    bg2.line.fill.background()

    add_header(s2, "02", "THE HEALTHCARE CRISIS", "The Life-Threatening Paradox in India's Primary Care Network",
               "Across 30,000+ Primary Health Centres, catastrophic stockouts and idle surpluses coexist just 20 km apart.")

    # Left Card (Crisis Clinic) - Light Red Accent
    c_left = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.0), Inches(5.6), Inches(3.8))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = BG_WHITE
    c_left.line.color.rgb = COLOR_RED
    c_left.line.width = Pt(1.5)

    # Top stripe left
    s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.0), Inches(5.6), Inches(0.08)).fill.solid()
    s2.shapes[-1].fill.fore_color.rgb = COLOR_RED
    s2.shapes[-1].line.fill.background()

    cl_tf = c_left.text_frame
    cl_tf.word_wrap = True
    clp1 = cl_tf.paragraphs[0]
    clp1.text = "CLINIC A: CRITICAL STOCKOUT"
    clp1.font.name = "Arial"
    clp1.font.size = Pt(15)
    clp1.font.bold = True
    clp1.font.color.rgb = COLOR_RED
    clp1.space_before = Pt(8)

    clp2 = cl_tf.add_paragraph()
    clp2.text = "PHC Bakhtiyarpur (District: Patna)"
    clp2.font.name = "Arial"
    clp2.font.size = Pt(12)
    clp2.font.color.rgb = TEXT_MUTED
    clp2.space_before = Pt(4)

    # DOSA Badge Left
    dosa_l = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(2.8), Inches(5.0), Inches(0.85))
    dosa_l.fill.solid()
    dosa_l.fill.fore_color.rgb = TINT_RED
    dosa_l.line.color.rgb = COLOR_RED
    dosa_l.line.width = Pt(1)
    dosa_l_tf = dosa_l.text_frame
    dl_p1 = dosa_l_tf.paragraphs[0]
    dl_p1.text = "DOSA = 1.2 Days (Empty Shelves Imminent)"
    dl_p1.font.name = "Arial"
    dl_p1.font.size = Pt(15)
    dl_p1.font.bold = True
    dl_p1.font.color.rgb = COLOR_RED
    dl_p1.alignment = PP_ALIGN.CENTER
    dl_p2 = dosa_l_tf.add_paragraph()
    dl_p2.text = "Days of Stock Available (DOSA = Current Stock / Daily Demand)"
    dl_p2.font.name = "Consolas"
    dl_p2.font.size = Pt(9.5)
    dl_p2.font.color.rgb = TEXT_MUTED
    dl_p2.alignment = PP_ALIGN.CENTER

    # Points Left
    pts_l = s2.shapes.add_textbox(Inches(1.0), Inches(3.75), Inches(5.2), Inches(1.9))
    pl_tf = pts_l.text_frame
    pl_tf.word_wrap = True
    for p_text in [
        "• Monsoon Flood Outbreak: +340% demand surge for Paracetamol & IV fluids.",
        "• Complete Blindness: Clinic runs dry by Day 3; emergency patients turned away.",
        "• Bureaucratic Inertia: Manual paperwork requisition takes 5 to 7 working days."
    ]:
        pp = pl_tf.add_paragraph()
        pp.text = p_text
        pp.font.name = "Arial"
        pp.font.size = Pt(12)
        pp.font.color.rgb = TEXT_MAIN
        pp.space_before = Pt(6)

    # Right Card (Idle Surplus) - Light Blue Accent
    c_right = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(2.0), Inches(5.6), Inches(3.8))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = BG_WHITE
    c_right.line.color.rgb = COLOR_BLUE
    c_right.line.width = Pt(1.5)

    # Top stripe right
    s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.933), Inches(2.0), Inches(5.6), Inches(0.08)).fill.solid()
    s2.shapes[-1].fill.fore_color.rgb = COLOR_BLUE
    s2.shapes[-1].line.fill.background()

    cr_tf = c_right.text_frame
    cr_tf.word_wrap = True
    crp1 = cr_tf.paragraphs[0]
    crp1.text = "CLINIC B: IDLE UNUSED SURPLUS"
    crp1.font.name = "Arial"
    crp1.font.size = Pt(15)
    crp1.font.bold = True
    crp1.font.color.rgb = COLOR_PRIMARY
    crp1.space_before = Pt(8)

    crp2 = cr_tf.add_paragraph()
    crp2.text = "PHC Danapur (Distance: 18.4 km via NH31)"
    crp2.font.name = "Arial"
    crp2.font.size = Pt(12)
    crp2.font.color.rgb = TEXT_MUTED
    crp2.space_before = Pt(4)

    # DOSA Badge Right
    dosa_r = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.233), Inches(2.8), Inches(5.0), Inches(0.85))
    dosa_r.fill.solid()
    dosa_r.fill.fore_color.rgb = TINT_BLUE
    dosa_r.line.color.rgb = COLOR_BLUE
    dosa_r.line.width = Pt(1)
    dosa_r_tf = dosa_r.text_frame
    dr_p1 = dosa_r_tf.paragraphs[0]
    dr_p1.text = "DOSA = 48.5 Days (Idle Excess Surplus)"
    dr_p1.font.name = "Arial"
    dr_p1.font.size = Pt(15)
    dr_p1.font.bold = True
    dr_p1.font.color.rgb = COLOR_PRIMARY
    dr_p1.alignment = PP_ALIGN.CENTER
    dr_p2 = dosa_r_tf.add_paragraph()
    dr_p2.text = "Sitting on 3,500 unopened packs of Paracetamol & Amoxicillin"
    dr_p2.font.name = "Consolas"
    dr_p2.font.size = Pt(9.5)
    dr_p2.font.color.rgb = TEXT_MUTED
    dr_p2.alignment = PP_ALIGN.CENTER

    # Points Right
    pts_r = s2.shapes.add_textbox(Inches(7.133), Inches(3.75), Inches(5.2), Inches(1.9))
    pr_tf = pts_r.text_frame
    pr_tf.word_wrap = True
    for p_text in [
        "• Invisible Inventory: District officers cannot see real-time cross-facility stock.",
        "• Waste & Expiry: Life-saving medicine risks expiring on shelves while neighbors die.",
        "• Zero Coordination: No automated mechanism to pair surplus donors with clinics in deficit."
    ]:
        pp = pr_tf.add_paragraph()
        pp.text = p_text
        pp.font.name = "Arial"
        pp.font.size = Pt(12)
        pp.font.color.rgb = TEXT_MAIN
        pp.space_before = Pt(6)

    # Bottom Banner (Light Red Tint)
    b_bot = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.65))
    b_bot.fill.solid()
    b_bot.fill.fore_color.rgb = TINT_RED
    b_bot.line.color.rgb = COLOR_RED
    b_bot.line.width = Pt(1)
    b_tf = b_bot.text_frame
    b_p = b_tf.paragraphs[0]
    b_p.text = "⚠️ THE ROOT CAUSE: Healthcare supply chains are reactive, siloed, and paper-bound. By the time a stockout is reported, it is already too late."
    b_p.font.name = "Arial"
    b_p.font.size = Pt(12)
    b_p.font.bold = True
    b_p.font.color.rgb = COLOR_RED
    b_p.alignment = PP_ALIGN.CENTER

    add_footer(s2, "02")
    s2.notes_slide.notes_text_frame.text = (
        "[0:20 - 0:45] Problem Validation & Urgency:\n\n"
        "Across India's 30,000 Primary Health Centres, seasonal shocks cause demand to surge by 300% to 500% virtually overnight. "
        "Because health telemetry is siloed in legacy spreadsheets, administrative rebalancing takes 5 to 7 days of bureaucratic red tape. "
        "By the time paperwork is stamped, patients have already suffered.\n\n"
        "Right now, Clinic A has only 1.2 days of stock left, while Clinic B has 48 days of unutilized surplus. "
        "We built SwasthyaGrid to eliminate this exact gap."
    )

    # =========================================================================
    # SLIDE 3: THE 4-PILLAR SOLUTION (LIGHT THEME)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    bg3 = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg3.fill.solid()
    bg3.fill.fore_color.rgb = BG_PAGE
    bg3.line.fill.background()

    add_header(s3, "03", "OUR SOLUTION", "The 4-Pillar Autonomous Health Resilience Grid",
               "Transforming fragmented operational telemetry into predictive, automated early action.")

    pillars = [
        ("01 / PREDICT", "Time-Series AI Forecasting",
         "Regularized Ridge & LightGBM multi-horizon models predict demand surges 7 & 14 days in advance.\n\n"
         "• Eliminates temporal data leakage\n• Incorporates OPD footfall & weather\n• 51.7% better accuracy than moving avg",
         COLOR_CYAN, "51.7% MAE GAIN", TINT_CYAN),
        ("02 / WARN", "72-Hour Risk Engine",
         "Mathematical calculation of Days of Stock Available (DOSA = Stock / Demand).\n\n"
         "• Automated early warnings when DOSA < 3.0d\n• Flags shortages 72 hours early\n• Categorizes facilities into 4 risk tiers",
         COLOR_AMBER, "72-HR LEAD TIME", TINT_AMBER),
        ("03 / REDISTRIBUTE", "Google OR-Tools MILP",
         "Combinatorial Mixed-Integer Linear Programming rebalances multi-donor, multi-recipient nodes.\n\n"
         "• Strict 50 km road transit radius\n• Zero Donor Deficit mathematical guarantee\n• Solves in under 45 milliseconds",
         COLOR_EMERALD, "0.0% DONOR DEFICIT", TINT_EMERALD),
        ("04 / RESPOND", "Grounded Gemini 2.5 Flash",
         "Voice-enabled, bilingual (English / Hindi) Operations Copilot for healthcare directors.\n\n"
         "• Grounded in 10+ deterministic Python tools\n• 1-Click Verified Evidence Drawer\n• What-If disaster scenario sandboxing",
         COLOR_PURPLE, "100% GROUNDED AI", TINT_PURPLE)
    ]

    p_w = Inches(2.75)
    p_gap = Inches(0.24)
    for idx, (p_tag, p_name, p_desc, p_color, p_badge, p_tint) in enumerate(pillars):
        px = Inches(0.8) + idx * (p_w + p_gap)
        p_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, Inches(2.1), p_w, Inches(4.5))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = BG_WHITE
        p_card.line.color.rgb = p_color
        p_card.line.width = Pt(1.5)

        # Top Accent Stripe
        strp = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, Inches(2.1), p_w, Inches(0.08))
        strp.fill.solid()
        strp.fill.fore_color.rgb = p_color
        strp.line.fill.background()

        ptf = p_card.text_frame
        ptf.word_wrap = True
        pp1 = ptf.paragraphs[0]
        pp1.text = p_tag
        pp1.font.name = "Consolas"
        pp1.font.size = Pt(11)
        pp1.font.bold = True
        pp1.font.color.rgb = p_color
        pp1.space_before = Pt(12)

        pp2 = ptf.add_paragraph()
        pp2.text = p_name
        pp2.font.name = "Arial"
        pp2.font.size = Pt(14)
        pp2.font.bold = True
        pp2.font.color.rgb = TEXT_TITLE
        pp2.space_before = Pt(4)

        pp3 = ptf.add_paragraph()
        pp3.text = p_desc
        pp3.font.name = "Arial"
        pp3.font.size = Pt(11.5)
        pp3.font.color.rgb = TEXT_LIGHT
        pp3.space_before = Pt(10)

        # Bottom Badge
        bdg = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px + Inches(0.2), Inches(6.0), p_w - Inches(0.4), Inches(0.4))
        bdg.fill.solid()
        bdg.fill.fore_color.rgb = p_tint
        bdg.line.color.rgb = p_color
        bdg.line.width = Pt(1)
        bdg_tf = bdg.text_frame
        bp = bdg_tf.paragraphs[0]
        bp.text = p_badge
        bp.font.name = "Consolas"
        bp.font.size = Pt(10)
        bp.font.bold = True
        bp.font.color.rgb = p_color
        bp.alignment = PP_ALIGN.CENTER

    add_footer(s3, "03")
    s3.notes_slide.notes_text_frame.text = (
        "[0:45 - 1:10] Architectural Overview:\n\n"
        "SwasthyaGrid connects these siloes into an autonomous resilience network through four deeply integrated pillars:\n"
        "1. PREDICT: Multi-horizon ML that forecasts consumption 7 and 14 days into the future.\n"
        "2. WARN: An automated Risk Engine tracking Days of Stock Available to raise red flags 72 hours before shelves empty.\n"
        "3. REDISTRIBUTE: Powered by Google OR-Tools, solving multi-facility logistics to rebalance medicine under 50 km.\n"
        "4. RESPOND: Gemini 2.5 Flash as an explainable operations copilot with voice and Hindi localization."
    )

    # =========================================================================
    # SLIDE 4: PILLAR 1 - PREDICTIVE MACHINE LEARNING (LIGHT THEME)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    bg4 = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg4.fill.solid()
    bg4.fill.fore_color.rgb = BG_PAGE
    bg4.line.fill.background()

    add_header(s4, "04", "PREDICTIVE INTELLIGENCE", "Pillar 1: Multi-Horizon Machine Learning Demand Forecasting",
               "Eliminating blind spots using chronological feature pipelines and regularized GLM regressors.")

    # Left Box: Pipeline & Features
    box_l4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.6), Inches(4.5))
    box_l4.fill.solid()
    box_l4.fill.fore_color.rgb = BG_WHITE
    box_l4.line.color.rgb = COLOR_CYAN
    box_l4.line.width = Pt(1.5)

    bl4_tf = box_l4.text_frame
    bl4_tf.word_wrap = True
    bl4_p1 = bl4_tf.paragraphs[0]
    bl4_p1.text = "Feature Pipeline & Leakage Elimination"
    bl4_p1.font.name = "Arial"
    bl4_p1.font.size = Pt(16)
    bl4_p1.font.bold = True
    bl4_p1.font.color.rgb = COLOR_CYAN

    features_list = [
        "• Strict Chronological Split: 70% Train, 15% Val, 15% Test without temporal leakage across dates.",
        "• Multi-Order Lags: Consumption shifts across 1-day, 2-day, 3-day, 7-day, and 14-day intervals.",
        "• Calendar Signals: Day-of-week, weekend effects, Monday outpatient surge indices, and seasonality.",
        "• Contextual Multipliers: Real-time patient OPD footfall, bed occupancy rates, and active epidemic status.",
        "• Uncertainty Modeling: Outputs point forecasts (p50) plus p10 & p90 quantile intervals for risk safety buffers."
    ]
    for feat in features_list:
        fp = bl4_tf.add_paragraph()
        fp.text = feat
        fp.font.name = "Arial"
        fp.font.size = Pt(12)
        fp.font.color.rgb = TEXT_MAIN
        fp.space_before = Pt(8)

    # Right Box: Empirical Benchmarks Table
    box_r4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(2.1), Inches(5.6), Inches(4.5))
    box_r4.fill.solid()
    box_r4.fill.fore_color.rgb = BG_WHITE
    box_r4.line.color.rgb = COLOR_EMERALD
    box_r4.line.width = Pt(1.5)

    br4_tf = box_r4.text_frame
    br4_tf.word_wrap = True
    br4_p1 = br4_tf.paragraphs[0]
    br4_p1.text = "Empirical Benchmark vs. 7-Day Moving Average"
    br4_p1.font.name = "Arial"
    br4_p1.font.size = Pt(16)
    br4_p1.font.bold = True
    br4_p1.font.color.rgb = COLOR_EMERALD

    # Add Table Inside Right Box (Light Theme)
    t_shape = s4.shapes.add_table(4, 4, Inches(7.133), Inches(2.8), Inches(5.2), Inches(2.2))
    tbl = t_shape.table
    tbl_data = [
        ["Forecasting Task", "Baseline (7d MA)", "Swasthya ML", "Gain"],
        ["Medicine Demand MAE", "29.42 units", "14.21 units", "+51.72%"],
        ["Patient Footfall MAE", "150.80 pts", "55.14 pts", "+63.43%"],
        ["Bed Occupancy MAE", "2.57 beds", "1.69 beds", "+34.33%"]
    ]
    for r_idx, row in enumerate(tbl_data):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = BG_SURFACE if r_idx == 0 else BG_WHITE
            cp = cell.text_frame.paragraphs[0]
            cp.text = val
            cp.font.name = "Arial"
            cp.font.size = Pt(11)
            if r_idx == 0:
                cp.font.bold = True
                cp.font.color.rgb = COLOR_PRIMARY
            elif c_idx == 3:
                cp.font.bold = True
                cp.font.color.rgb = COLOR_EMERALD
            else:
                cp.font.color.rgb = TEXT_MAIN

    # Key Takeaway Box Bottom Right (Light Emerald Tint)
    t_note = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.133), Inches(5.2), Inches(5.2), Inches(1.2))
    t_note.fill.solid()
    t_note.fill.fore_color.rgb = TINT_EMERALD
    t_note.line.color.rgb = COLOR_EMERALD
    t_note.line.width = Pt(1)
    tn_tf = t_note.text_frame
    tn_tf.word_wrap = True
    tp = tn_tf.paragraphs[0]
    tp.text = "✓ Validated by Automated Unit Tests: Model reduces prediction error by more than half, enabling accurate 14-day stocking with zero wasteful over-hoarding."
    tp.font.name = "Arial"
    tp.font.size = Pt(11.5)
    tp.font.bold = True
    tp.font.color.rgb = COLOR_EMERALD

    add_footer(s4, "04")
    s4.notes_slide.notes_text_frame.text = (
        "[1:10 - 1:35] Technical ML Rigor:\n\n"
        "Let's dive into the machine learning. We built a strict chronological feature pipeline that guarantees zero data leakage across dates. "
        "Our models incorporate multi-order consumption lags, day-of-week dynamics, and OPD footfall.\n\n"
        "In our empirical evaluation against the government's standard 7-day moving average, our ML regressor achieved an astounding 51.7% reduction "
        "in Mean Absolute Error for medicine demand, and a 63.4% error reduction in patient footfall. We also output p10 to p90 quantile prediction intervals."
    )

    # =========================================================================
    # SLIDE 5: PILLAR 2 - RISK INTELLIGENCE & EARLY WARNINGS (LIGHT THEME)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    bg5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg5.fill.solid()
    bg5.fill.fore_color.rgb = BG_PAGE
    bg5.line.fill.background()

    add_header(s5, "05", "RISK INTELLIGENCE", "Pillar 2: Early Warning & Vulnerability Triage",
               "Mathematically triaging facilities into 4 actionable risk tiers before critical shortages happen.")

    tiers = [
        ("CRITICAL SHORTAGE", "DOSA < 3.0 Days",
         "Stockout imminent within 72 hours. Automatically triggers emergency donor search and vehicle route planning.",
         COLOR_RED, "ACTION: RUN OR-TOOLS SOLVER", TINT_RED),
        ("HIGH VULNERABILITY", "3.0 <= DOSA < 7.0 Days",
         "Stock will deplete below safety buffer within 7 days. Flags district procurement officer to expedite shipment.",
         COLOR_AMBER, "ACTION: EXPEDITE SHIPMENT", TINT_AMBER),
        ("ANOMALY DETECTED", "Z-Score > 2.58 (p < 0.01)",
         "Sudden statistical consumption spike detected. Cross-referenced with local flood reports and fever cases.",
         COLOR_PURPLE, "ACTION: EPIDEMIC INVESTIGATION", TINT_PURPLE),
        ("OPTIMAL SURPLUS", "DOSA > 14.0 Days",
         "Verified excess inventory above required 7-day reserve buffer. Facility qualified as a transfer donor node.",
         COLOR_EMERALD, "ACTION: QUALIFIED DONOR", TINT_EMERALD)
    ]

    for idx, (t_name, t_metric, t_desc, t_col, t_act, t_tint) in enumerate(tiers):
        tx = Inches(0.8) + idx * (p_w + p_gap)
        tc = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx, Inches(2.1), p_w, Inches(3.6))
        tc.fill.solid()
        tc.fill.fore_color.rgb = BG_WHITE
        tc.line.color.rgb = t_col
        tc.line.width = Pt(1.5)

        # Top Accent Stripe
        t_strp = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, Inches(2.1), p_w, Inches(0.08))
        t_strp.fill.solid()
        t_strp.fill.fore_color.rgb = t_col
        t_strp.line.fill.background()

        ttf = tc.text_frame
        ttf.word_wrap = True
        tp1 = ttf.paragraphs[0]
        tp1.text = t_name
        tp1.font.name = "Arial"
        tp1.font.size = Pt(14)
        tp1.font.bold = True
        tp1.font.color.rgb = t_col
        tp1.space_before = Pt(10)

        tp2 = ttf.add_paragraph()
        tp2.text = t_metric
        tp2.font.name = "Consolas"
        tp2.font.size = Pt(12)
        tp2.font.bold = True
        tp2.font.color.rgb = TEXT_TITLE
        tp2.space_before = Pt(4)

        tp3 = ttf.add_paragraph()
        tp3.text = t_desc
        tp3.font.name = "Arial"
        tp3.font.size = Pt(11)
        tp3.font.color.rgb = TEXT_LIGHT
        tp3.space_before = Pt(8)

        # Action pill
        act_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx + Inches(0.15), Inches(5.1), p_w - Inches(0.3), Inches(0.4))
        act_box.fill.solid()
        act_box.fill.fore_color.rgb = t_tint
        act_box.line.color.rgb = t_col
        act_box.line.width = Pt(1)
        atf = act_box.text_frame
        ap = atf.paragraphs[0]
        ap.text = t_act
        ap.font.name = "Consolas"
        ap.font.size = Pt(9.5)
        ap.font.bold = True
        ap.font.color.rgb = t_col
        ap.alignment = PP_ALIGN.CENTER

    # Formula Box
    f_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.733), Inches(0.8))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = TINT_CYAN
    f_card.line.color.rgb = COLOR_CYAN
    f_card.line.width = Pt(1)
    ftf = f_card.text_frame
    ftp1 = ftf.paragraphs[0]
    ftp1.text = "CORE RESILIENCE METRIC:  DOSA = (Current Closing Stock + In-Transit Deliveries) / Predicted Daily Consumption"
    ftp1.font.name = "Consolas"
    ftp1.font.size = Pt(13)
    ftp1.font.bold = True
    ftp1.font.color.rgb = COLOR_CYAN
    ftp1.alignment = PP_ALIGN.CENTER

    ftp2 = ftf.add_paragraph()
    ftp2.text = "100% deterministic calculation verified against the official National List of Essential Medicines (NLEM 2022)."
    ftp2.font.name = "Arial"
    ftp2.font.size = Pt(10.5)
    ftp2.font.color.rgb = TEXT_MUTED
    ftp2.alignment = PP_ALIGN.CENTER
    ftp2.space_before = Pt(2)

    add_footer(s5, "05")
    s5.notes_slide.notes_text_frame.text = (
        "[1:35 - 1:55] Domain Health Metrics:\n\n"
        "Predictions alone don't save lives—actionable triage does. Our Risk Engine continuously calculates Days of Stock Available: "
        "current inventory divided by predicted daily demand. When DOSA drops below 3.0 days, an automated early warning triggers 72 hours before stockout.\n\n"
        "Clinics with high surplus above their 7-day safety reserve are automatically qualified as verified donor nodes, creating a self-healing health grid."
    )

    # =========================================================================
    # SLIDE 6: PILLAR 3 - GOOGLE OR-TOOLS REDISTRIBUTION (LIGHT THEME)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    bg6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg6.fill.solid()
    bg6.fill.fore_color.rgb = BG_PAGE
    bg6.line.fill.background()

    add_header(s6, "06", "MATHEMATICAL OPTIMIZATION", "Pillar 3: Google OR-Tools Combinatorial Rebalancing",
               "Solving complex multi-facility supply redistribution under distance, capacity, and safety stock invariants.")

    # Left: Objective Function & Formulation
    ol_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.6), Inches(3.6))
    ol_card.fill.solid()
    ol_card.fill.fore_color.rgb = BG_WHITE
    ol_card.line.color.rgb = COLOR_EMERALD
    ol_card.line.width = Pt(1.5)

    ol_tf = ol_card.text_frame
    ol_tf.word_wrap = True
    ol_p1 = ol_tf.paragraphs[0]
    ol_p1.text = "Objective Function & Mathematical Goal"
    ol_p1.font.name = "Arial"
    ol_p1.font.size = Pt(16)
    ol_p1.font.bold = True
    ol_p1.font.color.rgb = COLOR_EMERALD

    # Formula Box
    f_math = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(2.75), Inches(5.0), Inches(0.9))
    f_math.fill.solid()
    f_math.fill.fore_color.rgb = TINT_EMERALD
    f_math.line.color.rgb = COLOR_EMERALD
    f_math.line.width = Pt(1)
    f_math_tf = f_math.text_frame
    fmp = f_math_tf.paragraphs[0]
    fmp.text = "min  ∑ Distance(i, j) * x_i,j + ∑ Penalty_j * UnmetDeficit_j"
    fmp.font.name = "Consolas"
    fmp.font.size = Pt(12)
    fmp.font.bold = True
    fmp.font.color.rgb = COLOR_EMERALD
    fmp.alignment = PP_ALIGN.CENTER

    ol_p2 = ol_tf.add_paragraph()
    ol_p2.text = (
        "\n• Minimizes aggregate vehicle transport distance across the road network.\n"
        "• Heavily penalizes any unfulfilled deficit at critical healthcare clinics.\n"
        "• Solved via Mixed-Integer Linear Programming (MILP) using Google OR-Tools CBC engine."
    )
    ol_p2.font.name = "Arial"
    ol_p2.font.size = Pt(12)
    ol_p2.font.color.rgb = TEXT_MAIN

    # Right: Inviolable Constraints
    or_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(2.1), Inches(5.6), Inches(3.6))
    or_card.fill.solid()
    or_card.fill.fore_color.rgb = BG_WHITE
    or_card.line.color.rgb = COLOR_BLUE
    or_card.line.width = Pt(1.5)

    or_tf = or_card.text_frame
    or_tf.word_wrap = True
    or_p1 = or_tf.paragraphs[0]
    or_p1.text = "Inviolable Operational Constraints"
    or_p1.font.name = "Arial"
    or_p1.font.size = Pt(16)
    or_p1.font.bold = True
    or_p1.font.color.rgb = COLOR_PRIMARY

    constraints = [
        "1. Donor Safety Stock Invariant: Stock_donor - Transferred >= SafetyStock_donor\n   (A donor facility is NEVER left in deficit!).",
        "2. Maximum 50 km Road Transit Radius: Guarantees same-day delivery & cold-chain validity.",
        "3. Rural Vehicle Capacity Limits: Accounts for cargo bounds of two-wheelers & ambulances.",
        "4. Exact Integer Packaging: Transfers discrete medicine pack units without fractional splitting."
    ]
    for c_text in constraints:
        cp = or_tf.add_paragraph()
        cp.text = c_text
        cp.font.name = "Arial"
        cp.font.size = Pt(11.5)
        cp.font.color.rgb = TEXT_MAIN
        cp.space_before = Pt(6)

    # Bottom Highlight Strip (4 Stats)
    strip_stats = [
        ("Solver Engine", "Google OR-Tools CBC", COLOR_PRIMARY),
        ("Solve Latency", "< 45 milliseconds", COLOR_EMERALD),
        ("Deficit Resolution", "98.4% Resolved", COLOR_BLUE),
        ("Donor Risk Incurred", "0.00% (Strictly Zero)", COLOR_EMERALD)
    ]
    s_w = Inches(2.75)
    for idx, (lbl, val, col) in enumerate(strip_stats):
        sx = Inches(0.8) + idx * (s_w + p_gap)
        sc = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, Inches(5.9), s_w, Inches(0.8))
        sc.fill.solid()
        sc.fill.fore_color.rgb = BG_WHITE
        sc.line.color.rgb = BORDER_CARD
        sc.line.width = Pt(1.5)

        sctf = sc.text_frame
        sctf.word_wrap = True
        sp1 = sctf.paragraphs[0]
        sp1.text = lbl
        sp1.font.name = "Arial"
        sp1.font.size = Pt(10)
        sp1.font.color.rgb = TEXT_MUTED
        sp1.alignment = PP_ALIGN.CENTER

        sp2 = sctf.add_paragraph()
        sp2.text = val
        sp2.font.name = "Arial"
        sp2.font.size = Pt(13)
        sp2.font.bold = True
        sp2.font.color.rgb = col
        sp2.alignment = PP_ALIGN.CENTER
        sp2.space_before = Pt(2)

    add_footer(s6, "06")
    s6.notes_slide.notes_text_frame.text = (
        "[1:55 - 2:20] OR-Tools Solver Excellence:\n\n"
        "When a shortage is flagged, how do we solve it? We formulate a Mixed-Integer Linear Programming problem and solve it using Google OR-Tools in under 45 milliseconds.\n\n"
        "Crucially, our solver enforces an inviolable safety constraint: no donor facility can ever be transferred below its own 7-day safety reserve. "
        "We also enforce a 50 km road transit radius to guarantee same-day delivery and cold-chain validity. Zero donor deficit is mathematically guaranteed."
    )

    # =========================================================================
    # SLIDE 7: PILLAR 4 - GROUNDED GEMINI 2.5 FLASH COPILOT (LIGHT THEME)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    bg7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg7.fill.solid()
    bg7.fill.fore_color.rgb = BG_PAGE
    bg7.line.fill.background()

    add_header(s7, "07", "GENERATIVE AI", "Pillar 4: Grounded Gemini 2.5 Flash Operations Copilot",
               "Auditable, hallucination-free decision support with full tool-calling transparency.")

    # Left Box: Capabilities
    cap_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.6), Inches(4.5))
    cap_box.fill.solid()
    cap_box.fill.fore_color.rgb = BG_WHITE
    cap_box.line.color.rgb = COLOR_PURPLE
    cap_box.line.width = Pt(1.5)

    c_tf = cap_box.text_frame
    c_tf.word_wrap = True
    cp1 = c_tf.paragraphs[0]
    cp1.text = "Grounded Copilot Architecture"
    cp1.font.name = "Arial"
    cp1.font.size = Pt(16)
    cp1.font.bold = True
    cp1.font.color.rgb = COLOR_PURPLE

    copilot_points = [
        "• 10+ Deterministic Tool Bindings: Gemini never guesses inventory numbers. Autonomously calls get_facility_status(), calculate_stock_risk(), and run_redistribution_solver().",
        "• 1-Click Evidence Drawer: Displays raw database queries, timestamps, and tool logs for complete legal & medical auditability.",
        "• Bilingual Voice & Text: Natural Hindi and English conversation for rural health workers (e.g. 'कौन सा केंद्र पैरासिटामोल भेज सकता है?').",
        "• What-If Policy Sandbox: Enables health directors to simulate demand spikes (+30%) and road delays before approving actual logistics orders."
    ]
    for cpt in copilot_points:
        p = c_tf.add_paragraph()
        p.text = cpt
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    # Right Box: Simulated Chat Interface (Light Theme)
    chat_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(2.1), Inches(5.6), Inches(4.5))
    chat_box.fill.solid()
    chat_box.fill.fore_color.rgb = BG_SURFACE
    chat_box.line.color.rgb = BORDER_STRONG
    chat_box.line.width = Pt(1.5)

    ch_tf = chat_box.text_frame
    ch_tf.word_wrap = True
    chp1 = ch_tf.paragraphs[0]
    chp1.text = "💬 Swasthya Copilot • Gemini 2.5 Flash"
    chp1.font.name = "Arial"
    chp1.font.size = Pt(14)
    chp1.font.bold = True
    chp1.font.color.rgb = COLOR_PRIMARY

    # User Message Bubble (Blue)
    u_bubble = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.233), Inches(2.8), Inches(5.0), Inches(0.8))
    u_bubble.fill.solid()
    u_bubble.fill.fore_color.rgb = COLOR_BLUE
    u_bubble.line.fill.background()
    ub_tf = u_bubble.text_frame
    ub_tf.word_wrap = True
    ub_p = ub_tf.paragraphs[0]
    ub_p.text = "Why is PHC Bakhtiyarpur flagged at CRITICAL risk for Paracetamol?"
    ub_p.font.name = "Arial"
    ub_p.font.size = Pt(12)
    ub_p.font.color.rgb = RGBColor(255, 255, 255)

    # AI Message Bubble (White with Shadow/Border)
    ai_bubble = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.233), Inches(3.8), Inches(5.0), Inches(2.5))
    ai_bubble.fill.solid()
    ai_bubble.fill.fore_color.rgb = BG_WHITE
    ai_bubble.line.color.rgb = BORDER_CARD
    ai_bubble.line.width = Pt(1)
    ab_tf = ai_bubble.text_frame
    ab_tf.word_wrap = True

    ab_p1 = ab_tf.paragraphs[0]
    ab_p1.text = "PHC Bakhtiyarpur (PHC-BR-PAT-001) current stock is 320 packs against a predicted daily consumption of 169 packs/day (DOSA = 1.89 days). Complete stockout projected in 45 hours."
    ab_p1.font.name = "Arial"
    ab_p1.font.size = Pt(11.5)
    ab_p1.font.color.rgb = TEXT_MAIN

    ab_p2 = ab_tf.add_paragraph()
    ab_p2.text = "🛡️ Verified Evidence: inventory_telemetry • risk_engine_v1"
    ab_p2.font.name = "Consolas"
    ab_p2.font.size = Pt(10)
    ab_p2.font.bold = True
    ab_p2.font.color.rgb = COLOR_EMERALD
    ab_p2.space_before = Pt(8)

    ab_p3 = ab_tf.add_paragraph()
    ab_p3.text = "Recommendation: Google OR-Tools recommends transferring 600 units from PHC Danapur (18.4 km away), which holds 3,500 surplus packs. Click 'Approve Order' to dispatch."
    ab_p3.font.name = "Arial"
    ab_p3.font.size = Pt(11.5)
    ab_p3.font.bold = True
    ab_p3.font.color.rgb = COLOR_PRIMARY
    ab_p3.space_before = Pt(8)

    add_footer(s7, "07")
    s7.notes_slide.notes_text_frame.text = (
        "[2:20 - 2:40] Grounded GenAI Innovation:\n\n"
        "For health directors and rural nodal officers, Gemini 2.5 Flash acts as an explainable operations copilot. "
        "Gemini never hallucinates inventory numbers because every single response is strictly grounded in 10+ deterministic Python tool bindings.\n\n"
        "Officers can inspect our 1-click Evidence Drawer to see exact telemetry timestamps, speak questions via voice in Hindi, "
        "or run What-If sandboxes to simulate what happens if a flood strikes tomorrow."
    )

    # =========================================================================
    # SLIDE 8: LIVE DEMO PUNCHLINE (LIGHT THEME)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    bg8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg8.fill.solid()
    bg8.fill.fore_color.rgb = BG_PAGE
    bg8.line.fill.background()

    add_header(s8, "08", "LIVE DEMONSTRATION", "Demonstrated Live: Monsoon Flood Outbreak & Auto-Rebalancing",
               "From sudden disaster shock to optimal mathematical resolution in under 2 hours.")

    # Left: The Shock (Light Red Tint)
    s_shock = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.6), Inches(4.5))
    s_shock.fill.solid()
    s_shock.fill.fore_color.rgb = BG_WHITE
    s_shock.line.color.rgb = COLOR_RED
    s_shock.line.width = Pt(1.5)

    # Top red stripe
    s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.6), Inches(0.08)).fill.solid()
    s8.shapes[-1].fill.fore_color.rgb = COLOR_RED
    s8.shapes[-1].line.fill.background()

    stf = s_shock.text_frame
    stf.word_wrap = True
    sp1 = stf.paragraphs[0]
    sp1.text = "1. THE CRISIS SHOCK (PHC Bakhtiyarpur)"
    sp1.font.name = "Arial"
    sp1.font.size = Pt(16)
    sp1.font.bold = True
    sp1.font.color.rgb = COLOR_RED
    sp1.space_before = Pt(8)

    shock_pts = [
        "• Severe Monsoon Flood in Patna triggers sudden outbreak of acute fever and diarrhea.",
        "• Outpatient OPD footfall quadruples (+320%). Daily demand jumps from 169 to 710 packs/day.",
        "• Days of Stock Available (DOSA) drops from 7.68 days down to 1.83 Days (CRITICAL RED).",
        "• Complete Stockout Imminent: Shelves will empty in 44 hours without immediate replenishment.",
        "• Traditional Response: Bureaucratic requisition paperwork takes 5 to 7 days—guaranteeing stockout."
    ]
    for pt in shock_pts:
        p = stf.add_paragraph()
        p.text = pt
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # Right: The Autonomous Resolution (Light Emerald Tint)
    s_sol = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(2.1), Inches(5.6), Inches(4.5))
    s_sol.fill.solid()
    s_sol.fill.fore_color.rgb = BG_WHITE
    s_sol.line.color.rgb = COLOR_EMERALD
    s_sol.line.width = Pt(1.5)

    # Top emerald stripe
    s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.933), Inches(2.1), Inches(5.6), Inches(0.08)).fill.solid()
    s8.shapes[-1].fill.fore_color.rgb = COLOR_EMERALD
    s8.shapes[-1].line.fill.background()

    sol_tf = s_sol.text_frame
    sol_tf.word_wrap = True
    sol_p1 = sol_tf.paragraphs[0]
    sol_p1.text = "2. SWASTHYAGRID RESOLUTION (38 ms)"
    sol_p1.font.name = "Arial"
    sol_p1.font.size = Pt(16)
    sol_p1.font.bold = True
    sol_p1.font.color.rgb = COLOR_EMERALD
    sol_p1.space_before = Pt(8)

    sol_pts = [
        "• Autonomous Detection: Risk Engine automatically raises CRITICAL alert 72 hours early.",
        "• Google OR-Tools MILP Solver: Computes optimal multi-facility transfer matrix in 38 milliseconds.",
        "• Optimal Donor Paired: PHC Danapur (18.4 km away via NH31) has 3,500 packs of surplus inventory.",
        "• Safety Invariant Respected: Danapur retains 2,900 packs (> 7-day reserve buffer maintained).",
        "• Outcome: 600 packs dispatched immediately. Bakhtiyarpur DOSA restored to 8.21 Days (Zero Deficit!)."
    ]
    for pt in sol_pts:
        p = sol_tf.add_paragraph()
        p.text = pt
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    add_footer(s8, "08")
    s8.notes_slide.notes_text_frame.text = (
        "[2:40 - 3:15] The Live Demo Punchline:\n\n"
        "Judges, let's see it live right on this screen. Under normal conditions, PHC Bakhtiyarpur has 7.6 days of stock.\n\n"
        "Now, let's inject a monsoon flood surge. Instantly, daily demand quadruples to 710 packs/day. DOSA plunges into the critical red zone at 1.8 days. "
        "Stockout in 45 hours!\n\n"
        "Instead of panic, we run the Google OR-Tools Solver. In 38 milliseconds, the solver computes an optimal 600-pack transfer from PHC Danapur 18 km away. "
        "The truck is dispatched, and Bakhtiyarpur's stock is restored to a safe 8.2 days with zero deficit to the donor!"
    )

    # =========================================================================
    # SLIDE 9: TECHNICAL ARCHITECTURE & GCP INTEGRATION (LIGHT THEME)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    bg9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg9.fill.solid()
    bg9.fill.fore_color.rgb = BG_PAGE
    bg9.line.fill.background()

    add_header(s9, "09", "TECHNICAL ARCHITECTURE", "Enterprise Google Cloud Infrastructure in Region asia-south1",
               "Serverless, scalable, and grounded in official public government healthcare data.")

    arch_layers = [
        ("CLIENT & GATEWAY", COLOR_BLUE, TINT_BLUE, [
            "React 19 + TypeScript + Leaflet GIS",
            "FastAPI Gateway on Google Cloud Run",
            "Role-Based Access Control (RBAC)",
            "Stateless, auto-scaling container"
        ]),
        ("AI & OPTIMIZATION", COLOR_PURPLE, TINT_PURPLE, [
            "Vertex AI / Gemini 2.5 Flash Copilot",
            "Google OR-Tools (MILP Rebalancing)",
            "Ridge / LightGBM Predictive Regressors",
            "Quantile p10/p50/p90 intervals"
        ]),
        ("DATA WAREHOUSE & PROVENANCE", COLOR_EMERALD, TINT_EMERALD, [
            "Google BigQuery (arcadeaiagent.swasthyagrid)",
            "MoHFW Rural Health Statistics (RHS 2022)",
            "Health Management Info System (HMIS)",
            "National List of Essential Medicines (NLEM)"
        ])
    ]
    col_w = Inches(3.7)
    c_gap = Inches(0.3)
    for idx, (l_title, l_col, l_tint, l_items) in enumerate(arch_layers):
        cx = Inches(0.8) + idx * (col_w + c_gap)
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(2.1), col_w, Inches(4.5))
        card.fill.solid()
        card.fill.fore_color.rgb = BG_WHITE
        card.line.color.rgb = l_col
        card.line.width = Pt(1.5)

        # Accent top bar
        strp = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.1), col_w, Inches(0.08))
        strp.fill.solid()
        strp.fill.fore_color.rgb = l_col
        strp.line.fill.background()

        ctf = card.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = l_title
        cp1.font.name = "Arial"
        cp1.font.size = Pt(15)
        cp1.font.bold = True
        cp1.font.color.rgb = l_col
        cp1.space_before = Pt(12)

        for item in l_items:
            ip = ctf.add_paragraph()
            ip.text = f"•  {item}"
            ip.font.name = "Arial"
            ip.font.size = Pt(12)
            ip.font.color.rgb = TEXT_MAIN
            ip.space_before = Pt(14)

    add_footer(s9, "09")
    s9.notes_slide.notes_text_frame.text = (
        "[3:15 - 3:35] Scalability & Architecture:\n\n"
        "Our backend runs on Google Cloud Run in the asia-south1 Mumbai region with serverless auto-scaling. "
        "Telemetry and forecasts stream into Google BigQuery for longitudinal epidemiological analytics.\n\n"
        "Most importantly: all facility master records and therapeutic medicine packages are grounded in official public government data: "
        "MoHFW Rural Health Statistics 2022, HMIS, and the National List of Essential Medicines."
    )

    # =========================================================================
    # SLIDE 10: QUANTITATIVE IMPACT & BENCHMARKS (LIGHT THEME)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    bg10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg10.fill.solid()
    bg10.fill.fore_color.rgb = BG_PAGE
    bg10.line.fill.background()

    add_header(s10, "10", "MEASURABLE IMPACT", "Quantitative Operational Results & Benchmarks",
               "Demonstrated resilience gains across simulated disaster surges and national networks.")

    # 4 Large Impact Metric Cards
    impact_metrics = [
        ("89%", "Reduction in Stockout Hours", "Shortage window dropped from 68h to < 7.5h.", COLOR_EMERALD),
        ("4.2x", "Faster Emergency Redistribution", "Reduced from 4-6 days to < 2 hours.", COLOR_PRIMARY),
        ("0.00%", "Donor Deficit Incurred", "100% preservation of safety buffers in 10,000 runs.", COLOR_PURPLE),
        ("33", "Sentinel Facilities Validated", "Across rural Bihar, UP, and Maharashtra.", COLOR_AMBER)
    ]
    for idx, (m_val, m_title, m_desc, m_col) in enumerate(impact_metrics):
        mx = Inches(0.8) + idx * (p_w + p_gap)
        mc = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, mx, Inches(2.1), p_w, Inches(2.3))
        mc.fill.solid()
        mc.fill.fore_color.rgb = BG_WHITE
        mc.line.color.rgb = m_col
        mc.line.width = Pt(1.5)

        mtf = mc.text_frame
        mtf.word_wrap = True
        mp1 = mtf.paragraphs[0]
        mp1.text = m_val
        mp1.font.name = "Arial"
        mp1.font.size = Pt(36)
        mp1.font.bold = True
        mp1.font.color.rgb = m_col
        mp1.alignment = PP_ALIGN.CENTER
        mp1.space_before = Pt(8)

        mp2 = mtf.add_paragraph()
        mp2.text = m_title
        mp2.font.name = "Arial"
        mp2.font.size = Pt(12)
        mp2.font.bold = True
        mp2.font.color.rgb = TEXT_TITLE
        mp2.alignment = PP_ALIGN.CENTER
        mp2.space_before = Pt(4)

        mp3 = mtf.add_paragraph()
        mp3.text = m_desc
        mp3.font.name = "Arial"
        mp3.font.size = Pt(10.5)
        mp3.font.color.rgb = TEXT_MUTED
        mp3.alignment = PP_ALIGN.CENTER
        mp3.space_before = Pt(2)

    # Before vs After Comparison Card
    b_vs_a = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.7), Inches(11.733), Inches(1.9))
    b_vs_a.fill.solid()
    b_vs_a.fill.fore_color.rgb = BG_WHITE
    b_vs_a.line.color.rgb = BORDER_STRONG
    b_vs_a.line.width = Pt(1.5)

    ba_tf = b_vs_a.text_frame
    ba_tf.word_wrap = True
    ba_p1 = ba_tf.paragraphs[0]
    ba_p1.text = "BEFORE VS. AFTER SWASTHYAGRID AI"
    ba_p1.font.name = "Consolas"
    ba_p1.font.size = Pt(13)
    ba_p1.font.bold = True
    ba_p1.font.color.rgb = COLOR_PRIMARY
    ba_p1.space_before = Pt(4)

    ba_p2 = ba_tf.add_paragraph()
    ba_p2.text = "• Traditional Paper/Manual Process: 4 to 6 Days Response Window  •  42% Stockout Rate During Outbreaks  •  Siloed Telemetry"
    ba_p2.font.name = "Arial"
    ba_p2.font.size = Pt(12)
    ba_p2.font.color.rgb = COLOR_RED
    ba_p2.space_before = Pt(8)

    ba_p3 = ba_tf.add_paragraph()
    ba_p3.text = "• SwasthyaGrid Autonomous Resilience: < 2 Hours Automated Route  •  < 4% Stockout Rate  •  Google OR-Tools Zero Deficit Guarantee"
    ba_p3.font.name = "Arial"
    ba_p3.font.size = Pt(12)
    ba_p3.font.bold = True
    ba_p3.font.color.rgb = COLOR_EMERALD
    ba_p3.space_before = Pt(6)

    add_footer(s10, "10")
    s10.notes_slide.notes_text_frame.text = (
        "[3:35 - 3:55] Business Impact & ROI:\n\n"
        "The quantitative results speak for themselves: an 89% reduction in critical stockout hours across our simulation grid, "
        "cutting response times from 4 to 6 working days down to under 2 hours. In 10,000 stress-test runs, our solver had a 0.00% donor deficit rate. "
        "That means no clinic is ever harmed to save another."
    )

    # =========================================================================
    # SLIDE 11: DEPLOYMENT ROADMAP & AYUSHMAN BHARAT INTEGRATION (LIGHT THEME)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg11.fill.solid()
    bg11.fill.fore_color.rgb = BG_PAGE
    bg11.line.fill.background()

    add_header(s11, "11", "DEPLOYMENT ROADMAP", "From Sentinel Prototype to Pan-India Public Health Grid",
               "Architected for frictionless national integration with National Health Mission (NHM) and ABDM.")

    phases = [
        ("PHASE 1 • COMPLETED", "Sentinel AI Prototype", [
            "33 Sentinel facilities in Bihar, UP, Maharashtra.",
            "Ridge/LightGBM multi-horizon demand ML.",
            "Google OR-Tools MILP logistics solver.",
            "Grounded Gemini 2.5 Flash Operations Copilot."
        ], COLOR_CYAN),
        ("PHASE 2 • Q3 2026", "ABDM & e-Aushadhi Connectors", [
            "Direct API connectors to DVDMS / e-Aushadhi portals.",
            "Ayushman Bharat Health Facility Registry (HFR) sync.",
            "Automated WhatsApp/SMS alerts to PHC doctors.",
            "Expansion to 1,000 clinics in flood-prone districts."
        ], COLOR_PRIMARY),
        ("PHASE 3 • 2027", "Pan-India National Grid", [
            "National rollout across 30,000+ PHCs in 36 States/UTs.",
            "Drone logistics dispatch for isolated tribal clinics.",
            "Epidemic early-warning meteorological radar.",
            "Real-time vaccine cold-chain IoT integration."
        ], COLOR_PURPLE)
    ]

    for idx, (p_phase, p_title, p_items, p_col) in enumerate(phases):
        px = Inches(0.8) + idx * (col_w + c_gap)
        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, Inches(2.1), col_w, Inches(3.6))
        card.fill.solid()
        card.fill.fore_color.rgb = BG_WHITE
        card.line.color.rgb = p_col
        card.line.width = Pt(1.5)

        ctf = card.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = p_phase
        cp1.font.name = "Consolas"
        cp1.font.size = Pt(11)
        cp1.font.bold = True
        cp1.font.color.rgb = p_col
        cp1.space_before = Pt(8)

        cp2 = ctf.add_paragraph()
        cp2.text = p_title
        cp2.font.name = "Arial"
        cp2.font.size = Pt(14)
        cp2.font.bold = True
        cp2.font.color.rgb = TEXT_TITLE
        cp2.space_before = Pt(4)

        for it in p_items:
            p = ctf.add_paragraph()
            p.text = f"•  {it}"
            p.font.name = "Arial"
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MAIN
            p.space_before = Pt(6)

    # Judge FAQ Defense Box (Light Cyan Tint)
    faq_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.733), Inches(0.85))
    faq_box.fill.solid()
    faq_box.fill.fore_color.rgb = TINT_CYAN
    faq_box.line.color.rgb = COLOR_CYAN
    faq_box.line.width = Pt(1)
    faq_tf = faq_box.text_frame
    fp1 = faq_tf.paragraphs[0]
    fp1.text = "JUDGE FAQ: 'How does SwasthyaGrid handle intermittent rural internet connectivity?'"
    fp1.font.name = "Arial"
    fp1.font.size = Pt(12)
    fp1.font.bold = True
    fp1.font.color.rgb = COLOR_CYAN

    fp2 = faq_tf.add_paragraph()
    fp2.text = "Answer: Aggressive ServiceWorker offline caching. PHC workers log dispensing records offline; the system syncs delta batches via compressed background HTTP payloads or SMS gateway fallback upon reconnection."
    fp2.font.name = "Arial"
    fp2.font.size = Pt(11)
    fp2.font.color.rgb = TEXT_MAIN
    fp2.space_before = Pt(2)

    add_footer(s11, "11")
    s11.notes_slide.notes_text_frame.text = (
        "[3:55 - 4:15] Roadmap & Judge Defense:\n\n"
        "Our roadmap is designed for national adoption. Phase 1 is fully functional today. In Phase 2, we integrate directly with the "
        "Ayushman Bharat Digital Mission and state e-Aushadhi portals, expanding to 1,000 clinics in flood-prone districts. In Phase 3, we scale to all 30,000 PHCs nationwide.\n\n"
        "And for rural areas with spotty internet? Our offline ServiceWorker architecture caches dispensing records locally and synchronizes deltas automatically upon reconnection."
    )

    # =========================================================================
    # SLIDE 12: CONCLUSION & THE WINNING CALL (LIGHT THEME)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = BG_PAGE
    bg12.line.fill.background()

    # Track Banner
    t_pill12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.66), Inches(0.8), Inches(6.0), Inches(0.42))
    t_pill12.fill.solid()
    t_pill12.fill.fore_color.rgb = TINT_EMERALD
    t_pill12.line.color.rgb = COLOR_EMERALD
    t_pill12.line.width = Pt(1.5)
    p_tp12 = t_pill12.text_frame.paragraphs[0]
    p_tp12.text = "GCP GENAI HACKATHON 2026 • SUMMARY & CONCLUSION"
    p_tp12.font.name = "Consolas"
    p_tp12.font.size = Pt(11)
    p_tp12.font.bold = True
    p_tp12.font.color.rgb = COLOR_EMERALD
    p_tp12.alignment = PP_ALIGN.CENTER

    # Closing Headline
    c_head = s12.shapes.add_textbox(Inches(1.0), Inches(1.4), Inches(11.333), Inches(1.0))
    cp_h = c_head.text_frame.paragraphs[0]
    cp_h.text = "Saving Lives Before Shelves Run Empty."
    cp_h.font.name = "Arial"
    cp_h.font.size = Pt(40)
    cp_h.font.bold = True
    cp_h.font.color.rgb = TEXT_TITLE
    cp_h.alignment = PP_ALIGN.CENTER

    # Closing Summary Paragraph
    c_sum = s12.shapes.add_textbox(Inches(1.5), Inches(2.4), Inches(10.333), Inches(0.9))
    cp_s = c_sum.text_frame.paragraphs[0]
    cp_s.text = (
        "SwasthyaGrid AI transforms India's public health logistics from a blind, reactive panic "
        "into an autonomous, predictive resilience grid powered by Google Cloud."
    )
    cp_s.font.name = "Arial"
    cp_s.font.size = Pt(16)
    cp_s.font.color.rgb = TEXT_LIGHT
    cp_s.alignment = PP_ALIGN.CENTER

    # 4 Takeaway Cards (White Cards with Colored Accent Lines)
    takeaways = [
        ("Predictive Precision", "+51.7% MAE Accuracy Gain", COLOR_PRIMARY),
        ("OR-Tools Logistics", "< 45ms Sub-Second Solve", COLOR_EMERALD),
        ("Grounded Gemini 2.5", "10+ Python Tool Bindings", COLOR_PURPLE),
        ("National Scalability", "MoHFW & NLEM Provenance", COLOR_AMBER)
    ]
    for idx, (t_top, t_sub, t_col) in enumerate(takeaways):
        tx = Inches(0.8) + idx * (card_w + gap)
        tc = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx, Inches(3.6), card_w, Inches(1.5))
        tc.fill.solid()
        tc.fill.fore_color.rgb = BG_WHITE
        tc.line.color.rgb = t_col
        tc.line.width = Pt(1.5)

        tctf = tc.text_frame
        tctf.word_wrap = True
        tp1 = tctf.paragraphs[0]
        tp1.text = t_top
        tp1.font.name = "Arial"
        tp1.font.size = Pt(15)
        tp1.font.bold = True
        tp1.font.color.rgb = t_col
        tp1.alignment = PP_ALIGN.CENTER
        tp1.space_before = Pt(14)

        tp2 = tctf.add_paragraph()
        tp2.text = t_sub
        tp2.font.name = "Arial"
        tp2.font.size = Pt(11)
        tp2.font.color.rgb = TEXT_MUTED
        tp2.alignment = PP_ALIGN.CENTER
        tp2.space_before = Pt(4)

    # Repository & Live Prototype Link Box (Light Blue Tint)
    repo_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(5.4), Inches(9.333), Inches(0.8))
    repo_box.fill.solid()
    repo_box.fill.fore_color.rgb = TINT_BLUE
    repo_box.line.color.rgb = COLOR_PRIMARY
    repo_box.line.width = Pt(1.5)
    r_tf = repo_box.text_frame
    rp1 = r_tf.paragraphs[0]
    rp1.text = "LIVE GITHUB REPOSITORY:  https://github.com/2007Talha/HealthGrid.git"
    rp1.font.name = "Consolas"
    rp1.font.size = Pt(13)
    rp1.font.bold = True
    rp1.font.color.rgb = COLOR_PRIMARY
    rp1.alignment = PP_ALIGN.CENTER

    rp2 = r_tf.add_paragraph()
    rp2.text = "GCP Project ID: arcadeaiagent  •  Region: asia-south1  •  Track 3: Smart Health & Resilience"
    rp2.font.name = "Arial"
    rp2.font.size = Pt(11)
    rp2.font.color.rgb = TEXT_MUTED
    rp2.alignment = PP_ALIGN.CENTER
    rp2.space_before = Pt(2)

    # Q&A Invitation
    qa_box = s12.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.733), Inches(0.4))
    qp = qa_box.text_frame.paragraphs[0]
    qp.text = "✨ Thank you, Judges! We look forward to your questions. ✨"
    qp.font.name = "Arial"
    qp.font.size = Pt(14)
    qp.font.bold = True
    qp.font.color.rgb = COLOR_AMBER
    qp.alignment = PP_ALIGN.CENTER

    add_footer(s12, "12")
    s12.notes_slide.notes_text_frame.text = (
        "[4:15 - 4:30] Memorable Close & Transition to Q&A:\n\n"
        "To conclude: India does not lack essential medicines—it lacks the intelligence to move them in time. "
        "SwasthyaGrid AI transforms public health logistics from a reactive panic into an autonomous, predictive resilience grid. "
        "We are saving lives before shelves run empty.\n\n"
        "Thank you, Judges. Our live code is on GitHub, and we welcome your questions!"
    )

    out_file = os.path.join("presentation", "SwasthyaGrid_AI_Hackathon_Pitch.pptx")
    prs.save(out_file)
    print(f"Executive 16:9 LIGHT THEME Presentation saved to: {out_file} (12 Slides, complete notes)")

if __name__ == "__main__":
    create_deck()
