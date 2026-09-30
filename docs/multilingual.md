# SwasthyaGrid Copilot — Multilingual Operational Support

## Overview
India's public healthcare infrastructure relies on health workers across linguistically diverse regions. SwasthyaGrid Copilot supports bilingual operations with **English** and **Hindi (हिन्दी)** out of the box, with extensible architecture for regional Indian languages (e.g. Marathi, Odia, Kannada, Bengali).

---

## Dual-Language Generation Pipeline

1. **Input Normalization**:
   - Accepts queries in English or Devanagari Hindi script.
   - Detects linguistic intent and language preference flag (`language: 'en' | 'hi'`).

2. **Language-Agnostic Tool Execution**:
   - Backend deterministic tools execute identically regardless of prompt language, preserving 100% numerical and factual parity.

3. **Grounding Synthesis**:
   - English outputs formatted with professional medical logistics terminology.
   - Hindi outputs formatted in clear, official Devanagari terminology (e.g., *अति-गंभीर अलर्ट*, *स्टॉक कवरेज*, *पुनर्वितरण योजना*, *बेड अधिभोग*).

---

## Example Dual-Language Queries & Outputs

### 1. National Overview
- **English Prompt**: *"Summarize national health resource situation"*
  - **Output**: *"Total Monitored Facilities: 33 across 5 states. Active Critical Early Warnings: 8. Facilities with Immediate Medicine Shortages: 8..."*
- **Hindi Prompt**: *"राष्ट्रीय स्वास्थ्य संसाधनों की स्थिति का सारांश दें"*
  - **Output**: *"राष्ट्रीय स्वास्थ्य संसाधन स्थिति सारांश: कुल पंजीकृत स्वास्थ्य सुविधाएं: 33 (5 राज्यों में). सक्रिय अति-गंभीर अलर्ट: 8. दवा की तात्कालिक कमी वाले केंद्र: 8..."*

### 2. What-If Simulation
- **English Prompt**: *"What happens if we simulate a transfer of 900 units to PHC-BR-PAT-001?"*
  - **Output**: *"[WHAT-IF SIMULATION RESULTS] Baseline: Stock 120 units, Coverage 1.2 days (CRITICAL) -> Simulated Outcome: Stock 1020 units, Runway 10.2 days (LOW). Net Impact: +9.0 days added runway."*
- **Hindi Prompt**: *"यदि हम PHC-BR-PAT-001 को 900 यूनिट ट्रांसफर करें तो क्या होगा?"*
  - **Output**: *"[सिम्युलेशन परिणाम (व्हाट-इफ विश्लेषण)] वर्तमान स्थिति: स्टॉक 120 यूनिट, स्टॉक कवरेज 1.2 दिन (CRITICAL) -> सिम्युलेटेड परिणाम: नया स्टॉक कवरेज: 10.2 दिन (LOW). शुद्ध सुधार: +9.0 दिन की अतिरिक्त सुरक्षा।"*
