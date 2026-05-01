import streamlit as st
import json
import base64
import io
import httpx
from datetime import datetime
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(
    page_title="QuestionLens // Exam Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
.stApp { background: #060608; color: #e0ffe0; }

section[data-testid="stSidebar"] {
    background: #08090d !important;
    border-right: 1px solid #00ff8820;
}
section[data-testid="stSidebar"] * { color: #c0ffc0 !important; }
section[data-testid="stSidebar"] .stTextInput input {
    background: #0d1a0d !important;
    border: 1px solid #00ff4430 !important;
    color: #00ff88 !important;
    border-radius: 4px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

.main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    color: #ffffff;
    letter-spacing: 0.05em;
    line-height: 0.9;
    text-shadow: 0 0 40px #00ff8840;
}
.main-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #00ff88;
    margin-bottom: 2rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.accent { color: #00ff88; }

.stat-card {
    background: #0a0f0a;
    border: 1px solid #00ff8830;
    border-top: 2px solid #00ff88;
    padding: 1.2rem 1rem;
    text-align: center;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px));
}
.stat-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #00ff88;
    line-height: 1;
    text-shadow: 0 0 20px #00ff8860;
}
.stat-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #006633;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.topic-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    color: #00ff88;
    background: #080f08;
    border: 1px solid #00ff8830;
    border-left: 3px solid #00ff88;
    padding: 0.6rem 1rem;
    margin: 1.5rem 0 0.6rem 0;
    letter-spacing: 0.08em;
    text-shadow: 0 0 10px #00ff8840;
}

.question-row {
    background: #080d08;
    border: 1px solid #00ff8815;
    border-left: 2px solid #00ff8840;
    padding: 0.8rem 1rem;
    margin-bottom: 0.4rem;
}
.question-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    color: #a0d0a0;
    line-height: 1.5;
    margin-bottom: 0.4rem;
    font-weight: 500;
}

.badge {
    display: inline-block;
    padding: 1px 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    margin-right: 5px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-high { background: #001a00; color: #00ff44; border: 1px solid #00ff4450; }
.badge-medium { background: #001a10; color: #00ffaa; border: 1px solid #00ffaa40; }
.badge-low { background: #00100a; color: #00cc88; border: 1px solid #00cc8830; }
.badge-count { background: #1a0a00; color: #ff8800; border: 1px solid #ff880050; }
.badge-year { background: #0a0a0a; color: #667766; border: 1px solid #33443330; }

.hot-card {
    background: #080d08;
    border: 1px solid #00ff4430;
    border-top: 1px solid #00ff8860;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    position: relative;
    clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 0 100%);
}
.hot-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #00ff8815;
    position: absolute;
    top: 0.5rem;
    right: 1rem;
    line-height: 1;
}
.hot-question {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    color: #b0e0b0;
    line-height: 1.5;
    margin-bottom: 0.5rem;
    padding-right: 3rem;
    font-weight: 500;
}
.hot-meta { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #336633; }

.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    color: #ffffff;
    margin: 2rem 0 0.8rem 0;
    letter-spacing: 0.06em;
    border-bottom: 1px solid #00ff8820;
    padding-bottom: 0.4rem;
}

.upload-hint {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #00aa55;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
}

div[data-testid="stButton"] button {
    background: #001a00 !important;
    color: #00ff88 !important;
    border: 1px solid #00ff88 !important;
    border-radius: 0 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.12em !important;
    padding: 0.5rem 1.5rem !important;
    width: 100% !important;
    text-shadow: 0 0 10px #00ff8880 !important;
    box-shadow: 0 0 15px #00ff8820 !important;
}
div[data-testid="stButton"] button:hover {
    background: #00ff8815 !important;
    box-shadow: 0 0 25px #00ff8840 !important;
}
div[data-testid="stDownloadButton"] button {
    background: #001408 !important;
    color: #00ff66 !important;
    border: 1px solid #00ff6650 !important;
    border-radius: 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1.2rem !important;
    width: 100% !important;
    letter-spacing: 0.08em !important;
}
.stTextInput input {
    background: #080d08 !important;
    border: 1px solid #00ff8830 !important;
    color: #00ff88 !important;
    border-radius: 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.analyzing-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #00ff88;
    text-align: center;
    padding: 1rem;
    letter-spacing: 0.1em;
}
hr { border-color: #00ff8815 !important; }
</style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """You are an expert academic question analyzer.

Analyze previous year exam questions from provided text.

Step 1: Extract all questions. Normalize wording. Ignore question numbers and marks.
Step 2: Identify repetitions. Group similar questions. Record how many times each appeared and which years.
Step 3: Organize by topic. Classify each question into a relevant subject topic.
Step 4: Return ONLY this JSON structure with no extra text:

{
  "summary": {
    "total_questions_extracted": 0,
    "unique_questions": 0,
    "repeated_questions": 0,
    "topics_found": []
  },
  "topics": [
    {
      "topic_name": "Topic Name",
      "questions": [
        {
          "question": "Question text here",
          "repeat_count": 3,
          "years": ["2021", "2022", "2023"],
          "priority": "High"
        }
      ]
    }
  ],
  "most_repeated": [
    {
      "question": "Question text here",
      "repeat_count": 5,
      "topic": "Topic Name",
      "years": ["2019", "2020", "2021", "2022", "2023"]
    }
  ]
}

Priority: High = 3+ times, Medium = 2 times, Low = 1 time.
most_repeated = top 10 by repeat_count descending.
Return ONLY valid JSON. No preamble, no markdown backticks."""


def call_openrouter(api_key, model, messages, timeout=90):
    import urllib.request
    import urllib.error
    import json as _json
    payload = _json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 4000
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://questionlens.streamlit.app",
            "X-Title": "QuestionLens"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = _json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {error_body}")
    if "choices" not in result:
        raise Exception(f"API Error: {result}")
    return result["choices"][0]["message"]["content"]


def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i+1} ---\n{page_text}"
    return text


def extract_text_from_image(file_bytes, mime_type, api_key):
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    try:
        return call_openrouter(
            api_key,
            "openrouter/free",
            [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    {"type": "text", "text": "Extract all exam questions from this image. List every question you can see, preserving the original wording. Include any year or exam information visible."}
                ]
            }]
        )
    except Exception:
        return call_openrouter(
            api_key,
            "openrouter/free",
            [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                    {"type": "text", "text": "Extract all exam questions from this image. List every question you can see, preserving the original wording. Include any year or exam information visible."}
                ]
            }]
        )


def analyze_questions(all_text, api_key):
    raw = call_openrouter(
        api_key,
        "openrouter/free",
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here are the exam questions to analyze:\n\n{all_text}"}
        ]
    )
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_pdf_report(data, subject_name=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=22,
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=6,
        fontName='Helvetica-Bold', alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#6b6880'), spaceAfter=20, alignment=TA_CENTER)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=13,
        textColor=colors.HexColor('#7c6af7'), spaceBefore=18, spaceAfter=8,
        fontName='Helvetica-Bold')
    topic_style = ParagraphStyle('Top', parent=styles['Heading3'], fontSize=11,
        textColor=colors.HexColor('#1a1a2e'), spaceBefore=14, spaceAfter=6,
        fontName='Helvetica-Bold', leftIndent=8)
    question_style = ParagraphStyle('Q', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#333344'), spaceAfter=4, leftIndent=12, leading=14)
    meta_style = ParagraphStyle('M', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#888899'), spaceAfter=8, leftIndent=12)

    story = []
    story.append(Spacer(1, 0.5*cm))
    title_text = f"QuestionLens Report: {subject_name}" if subject_name else "QuestionLens Analysis Report"
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0f0')))
    story.append(Spacer(1, 0.5*cm))

    summary = data.get("summary", {})
    summary_data = [
        ["Total Questions", "Unique Questions", "Repeated Questions", "Topics Found"],
        [str(summary.get("total_questions_extracted", 0)),
         str(summary.get("unique_questions", 0)),
         str(summary.get("repeated_questions", 0)),
         str(len(summary.get("topics_found", [])))]
    ]
    t = Table(summary_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0eeff')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#fafaff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#7c6af7')),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#1a1a2e')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8), ('FONTSIZE', (0,1), (-1,1), 14),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d8d0f8')),
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.8*cm))

    most_repeated = data.get("most_repeated", [])
    if most_repeated:
        story.append(Paragraph("Most Repeated Questions", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0e0f0')))
        story.append(Spacer(1, 0.2*cm))
        for i, q in enumerate(most_repeated[:10], 1):
            years = q.get("years", [])
            qdata = [[
                Paragraph(f"<b>#{i}</b>", ParagraphStyle('r', fontSize=11,
                    textColor=colors.HexColor('#7c6af7'), fontName='Helvetica-Bold')),
                Paragraph(q.get("question", ""), ParagraphStyle('qt', fontSize=9,
                    textColor=colors.HexColor('#1a1a2e'), leading=14)),
                Paragraph(f"<b>{q.get('repeat_count',1)}x</b><br/>{q.get('topic','')}<br/>{', '.join(years) if years else 'N/A'}",
                    ParagraphStyle('qm', fontSize=8, textColor=colors.HexColor('#6b6880'),
                    leading=12, alignment=TA_CENTER))
            ]]
            qt = Table(qdata, colWidths=[1.2*cm, 12*cm, 2.8*cm])
            qt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf8ff') if i%2==0 else colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (2,0), (2,0), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e8e0f8')),
                ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 8), ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(qt)
            story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.5*cm))
    topics = data.get("topics", [])
    if topics:
        story.append(Paragraph("Questions by Topic", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0e0f0')))
        for topic_data in topics:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(f"▸ {topic_data.get('topic_name','')} ({len(topic_data.get('questions',[]))} questions)", topic_style))
            for q in topic_data.get("questions", []):
                years = q.get("years", [])
                story.append(Paragraph(f"• {q.get('question','')}", question_style))
                story.append(Paragraph(
                    f"Priority: {q.get('priority','Low')}  |  Repeated: {q.get('repeat_count',1)}x  |  Years: {', '.join(years) if years else 'N/A'}",
                    meta_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def priority_badge(priority):
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(priority, "badge-low")
    return f'<span class="badge {cls}">{priority}</span>'


def main():
    with st.sidebar:
        st.markdown('<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#00ff88;letter-spacing:0.1em;text-shadow:0 0 15px #00ff8860;margin-bottom:0;">QUESTIONLENS</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#336633;margin-top:-0.5rem;letter-spacing:0.15em;">// EXAM INTELLIGENCE SYSTEM</p>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#00aa55;letter-spacing:0.15em;">[ API_CONFIG ]</p>', unsafe_allow_html=True)

        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-...",
            value=st.session_state.api_key,
            help="Get your free key from openrouter.ai"
        )
        st.session_state.api_key = api_key

        if api_key:
            st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;color:#00ff88;letter-spacing:0.08em;">▶ KEY_AUTHENTICATED</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#ff4400;letter-spacing:0.06em;">! GET FREE KEY: openrouter.ai</p>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#00aa55;letter-spacing:0.15em;">[ SUBJECT_TAG ]</p>', unsafe_allow_html=True)

        if "subject_name" not in st.session_state:
            st.session_state.subject_name = ""
        subject_name = st.text_input(
            "Subject name",
            placeholder="e.g. Structural Analysis",
            value=st.session_state.subject_name
        )
        st.session_state.subject_name = subject_name

        st.markdown("---")
        st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.62rem;color:#1a3320;line-height:1.8;">// KEY NOT STORED<br/>// SESSION ONLY<br/>// REAL-TIME PROCESSING</p>', unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">QUESTION<span class="accent">LENS</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">// UPLOAD PAPERS → DETECT PATTERNS → DOMINATE EXAMS</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "UPLOAD QUESTION PAPERS [ PDF / PNG / JPG ]",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        names = ", ".join([f.name for f in uploaded_files])
        st.markdown(f'<p class="upload-hint">▶ {len(uploaded_files)} FILE(S) LOADED — {names}</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_btn = st.button("🔍 ANALYZE QUESTIONS", disabled=not (uploaded_files and api_key))
    with col2:
        if not api_key:
            st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;color:#ff4400;padding-top:0.6rem;">! KEY_REQUIRED</p>', unsafe_allow_html=True)

    if analyze_btn and uploaded_files and api_key:
        try:
            progress = st.empty()
            progress.markdown('<p class="analyzing-text">▶ EXTRACTING_QUESTIONS... SCANNING FILES...</p>', unsafe_allow_html=True)

            all_extracted_text = ""
            for file in uploaded_files:
                file_bytes = file.read()
                fname = file.name.lower()
                if fname.endswith(".pdf"):
                    text = extract_text_from_pdf(file_bytes)
                    if not text.strip():
                        text = extract_text_from_image(file_bytes, "application/pdf", api_key)
                else:
                    mime = "image/jpeg" if fname.endswith((".jpg", ".jpeg")) else "image/png"
                    text = extract_text_from_image(file_bytes, mime, api_key)
                all_extracted_text += f"\n\n=== FILE: {file.name} ===\n{text}"

            progress.markdown('<p class="analyzing-text">▶ ANALYZING_PATTERNS... DETECTING REPEATS...</p>', unsafe_allow_html=True)
            result = analyze_questions(all_extracted_text, api_key)
            progress.empty()
            st.session_state["result"] = result
            st.session_state["subject_name_saved"] = subject_name

        except json.JSONDecodeError:
            st.error("Could not parse AI response. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if "result" in st.session_state:
        data = st.session_state["result"]
        subj = st.session_state.get("subject_name_saved", "")
        summary = data.get("summary", {})

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{summary.get("total_questions_extracted",0)}</div><div class="stat-label">Total Extracted</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{summary.get("unique_questions",0)}</div><div class="stat-label">Unique Questions</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{summary.get("repeated_questions",0)}</div><div class="stat-label">Repeated</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(summary.get("topics_found",[]))}</div><div class="stat-label">Topics Found</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">// MOST REPEATED QUESTIONS</div>', unsafe_allow_html=True)
        for i, q in enumerate(data.get("most_repeated", []), 1):
            years_str = " ".join([f'<span class="badge badge-year">{y}</span>' for y in q.get("years", [])])
            st.markdown(f"""
            <div class="hot-card">
                <div class="hot-rank">#{i}</div>
                <div class="hot-question">{q.get("question","")}</div>
                <div class="hot-meta">
                    <span class="badge badge-count">× {q.get("repeat_count",1)} times</span>
                    <span class="badge badge-high">{q.get("topic","")}</span>
                    {years_str}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">// ALL QUESTIONS BY TOPIC</div>', unsafe_allow_html=True)
        for topic_data in data.get("topics", []):
            questions = topic_data.get("questions", [])
            st.markdown(f'<div class="topic-header">{topic_data.get("topic_name","")} <span style="color:#336633;font-size:0.8rem;">({len(questions)} questions)</span></div>', unsafe_allow_html=True)
            for q in questions:
                priority = q.get("priority", "Low")
                years_str = " ".join([f'<span class="badge badge-year">{y}</span>' for y in q.get("years", [])])
                st.markdown(f"""
                <div class="question-row">
                    <div class="question-text">{q.get("question","")}</div>
                    <div>{priority_badge(priority)}<span class="badge badge-count">× {q.get("repeat_count",1)}</span>{years_str}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">// EXPORT REPORT</div>', unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(data, subj)
        filename = f"questionlens_{subj.lower().replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf" if subj else f"questionlens_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        st.download_button(
            label="DOWNLOAD ANALYSIS REPORT [PDF]",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf"
        )


if __name__ == "__main__":
    main()
