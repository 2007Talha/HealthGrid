# SwasthyaGrid Copilot — Voice & Speech Architecture

## Overview
Field medical officers and on-duty PHC pharmacists often operate in hands-busy environments (clinics, cold-storage facilities, emergency disaster zones). The SwasthyaGrid voice pipeline enables seamless audio-in, audio-out operational intelligence.

---

## Technical Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Officer as Medical Officer / Operator
    participant Client as Web / Mobile Client
    participant API as POST /api/v1/copilot/voice
    participant STT as Google Cloud Speech-to-Text
    participant Copilot as Copilot Reasoner & Tools
    participant TTS as Google Cloud Text-to-Speech

    Officer->>Client: Speaks ("Which facilities are at critical risk today?")
    Client->>API: Audio Stream (Base64 WAV / WebM)
    API->>STT: Recognize Speech (English / Hindi Indian Accents)
    STT-->>API: Transcribed Text Prompt
    API->>Copilot: Execute process_query(transcription)
    Copilot-->>API: Grounded Operational Response + Tool Evidence
    API->>TTS: Synthesize Audio (Standard Neural Voice en-IN / hi-IN)
    TTS-->>API: Audio Synthesis Buffer
    API-->>Client: Transcribed Text + Audio Payload + Tool Calls
    Client->>Officer: Plays Voice Summary & Renders UI Cards
```

---

## Low-Latency Design
- **Sampling**: 16kHz linear PCM / Opus encoding for high accuracy over cellular 4G/5G connections.
- **Language Models**: Configured for Indian English (`en-IN`) and Hindi (`hi-IN`) accents and regional healthcare terminology (e.g. "Paracetamol", "Amoxicillin", "PHC Bakhtiyarpur", "District Hospital").
- **Voice Response Available**: All API responses provide `audio_response_available: true` flags for immediate playback in the UI.
