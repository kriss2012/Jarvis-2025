const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  VerticalAlign, PageNumber, PageBreak, LevelFormat, ShadingType,
  ExternalHyperlink, TableOfContents
} = require('docx');
const fs = require('fs');
const path = require('path');

// Target directory for the documents
const outputDir = path.join(__dirname, '..', 'jarvis-docs');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// ─── Color palette ───────────────────────────────────────────────────────────
const C = {
  primary:   "1A2D5A",   // deep navy
  accent:    "00B4D8",   // antigravity cyan
  dark:      "0D1B2A",   // near-black
  light:     "E8F4FD",   // pale blue
  white:     "FFFFFF",
  grey:      "6B7280",
  lightgrey: "F3F4F6",
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
const sp = (sz, bold, color, italic) => ({
  size: sz || 22, bold: !!bold,
  color: color || "000000", font: "Arial", italic: !!italic
});

const heading1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 400, after: 200 },
  children: [new TextRun({ text, ...sp(36, true, C.primary) })]
});

const heading2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 320, after: 160 },
  children: [new TextRun({ text, ...sp(28, true, C.primary) })]
});

const heading3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  spacing: { before: 200, after: 100 },
  children: [new TextRun({ text, ...sp(24, true, C.dark) })]
});

const body = (text, options = {}) => new Paragraph({
  spacing: { before: 80, after: 80 },
  children: [new TextRun({ text, ...sp(22, false, options.color || "1F2937"), italic: options.italic })],
  indent: options.indent ? { left: 720 } : undefined
});

const bullet = (text, ref = "bullets") => new Paragraph({
  numbering: { reference: ref, level: 0 },
  spacing: { before: 60, after: 60 },
  children: [new TextRun({ text, ...sp(22, false, "1F2937") })]
});

const divider = () => new Paragraph({
  spacing: { before: 200, after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.accent } },
  children: []
});

const spacer = (n = 1) => Array(n).fill(new Paragraph({ children: [new TextRun("")] }));

const blueBox = (lines) => {
  const children = lines.map(l => new Paragraph({
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text: l, ...sp(21, false, C.white) })]
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [new TableRow({ children: [new TableCell({
      shading: { type: ShadingType.SOLID, color: C.primary },
      margins: { top: 200, bottom: 200, left: 300, right: 300 },
      children
    })] })]
  });
};

const twoColTable = (rows, header) => {
  const makeRow = (cells, isHeader) => new TableRow({
    tableHeader: isHeader,
    children: cells.map((c, i) => new TableCell({
      shading: isHeader
        ? { type: ShadingType.SOLID, color: C.primary }
        : (i === 0 ? { type: ShadingType.SOLID, color: C.lightgrey } : undefined),
      margins: { top: 100, bottom: 100, left: 150, right: 150 },
      children: [new Paragraph({
        children: [new TextRun({ text: c, ...sp(21, isHeader, isHeader ? C.white : "1F2937") })]
      })]
    }))
  });
  const headerRow = makeRow(header, true);
  const dataRows = rows.map(r => makeRow(r, false));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...dataRows]
  });
};

// ─── NUMBERING CONFIG (shared) ───────────────────────────────────────────────
const numbering = {
  config: [
    {
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    },
    {
      reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }
  ]
};

// ─── STYLES ──────────────────────────────────────────────────────────────────
const styles = {
  default: { document: { run: { font: "Arial", size: 22 } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 36, bold: true, font: "Arial", color: C.primary },
      paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 28, bold: true, font: "Arial", color: C.primary },
      paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 24, bold: true, font: "Arial", color: C.dark },
      paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } }
  ]
};

const pageProps = {
  size: { width: 12240, height: 15840 },
  margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
};

// ════════════════════════════════════════════════════════════════════════════
// DOC 1 — PRODUCT REQUIREMENTS DOCUMENT
// ════════════════════════════════════════════════════════════════════════════
async function makePRD() {
  const sections = [{
    properties: { page: pageProps },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "JARVIS 2025 — Enterprise AI Assistant | PRD v1.2", ...sp(18, false, C.grey) })]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Confidential — Antigravity Inc.  |  Page ", ...sp(18, false, C.grey) }), new TextRun({ children: [PageNumber.CURRENT], ...sp(18, false, C.grey) })]
    })] }) },
    children: [
      new Paragraph({
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 200 },
        children: [new TextRun({ text: "JARVIS 2025", ...sp(56, true, C.primary) })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Enterprise AI Assistant Platform (Core Architecture Specs)", ...sp(32, false, C.dark) })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 400 },
        children: [new TextRun({ text: "Product Requirements Document — v1.2   |   June 2026", ...sp(22, false, C.grey), italic: true })]
      }),
      divider(),
      ...spacer(1),

      // ── 1. Executive Summary ──
      body("Jarvis-2025 is an enterprise-grade AI desktop assistant that merges voice-activated command processing, real-time facial biometric authentication, and hybrid large language model (LLM) reasoning into a single unified platform. Built on Python + Eel, it exposes a web-native UI consumed locally, enabling rich interactivity without cloud round-trips for core interactions."),
      body("This PRD defines the product scope, feature roadmap, system architecture, and success criteria required to evolve the current open-source prototype into a commercially deployable, multi-tenant, enterprise product branded under Antigravity Inc. In this version 1.2, the product is grounded strictly in our actual implementation: OpenCV LBPH Face Recognition, pvporcupine wake-word triggers, local pyttsx3 speech synthesis, pyautogui WhatsApp protocol automation, and a hybrid online/offline NLU engine (HuggingFace online cookies + local Ollama Gemma-4-E4B heretic GGUF model fallback)."),,

      ...spacer(1),
      // ── 2. Problem Statement ──
      heading1("2. Problem Statement"),
      body("Enterprises today operate with fragmented toolchains: separate chat interfaces, separate identity management systems, and siloed automation pipelines. Knowledge workers lose an estimated 30–40% of productive time switching contexts or repeating commands across tools."),
      body("Existing AI assistant solutions suffer from:"),
      bullet("Dependency on massive cloud processing, raising data sovereignty concerns"),
      bullet("Lack of biometric security — simple wake-words can be spoofed in open offices"),
      bullet("No deep integration with local desktop applications or system operations"),
      bullet("Rigid voice recognition with zero tolerance for regional accents or language switching (e.g. Hindi, Marathi)"),
      ...spacer(1),

      // ── 3. Vision ──
      heading1("3. Product Vision & Goals"),
      blueBox([
        'Vision: "An always-on, biometrically-secured, multilingual AI-powered enterprise co-pilot that operates',
        'with near-zero latency, understands intent variations, and integrates natively with corporate tools."'
      ]),
      ...spacer(1),
      heading2("3.1 Primary Goals"),
      bullet("G1 — Security First: Replace password-based login with OpenCV LBPH face recognition"),
      bullet("G2 — Edge-First: Core reasoning, database lookups, and UI render must function with local processes"),
      bullet("G3 — System Automation: Launch local applications and URLs stored in a SQL database dynamically"),
      bullet("G4 — Social & Communications: Trigger hands-free messaging and calls via WhatsApp desktop protocol URL handlers"),
      bullet("G5 — Native Multilingualism: Support on-the-fly language switching and localized speech processing (English, Hindi, Marathi) with custom conversational tone"),

      ...spacer(1),
      // ── 4. Scope ──
      heading1("4. Scope"),
      heading2("4.1 In Scope — MVP (Current Production Release)"),
      bullet("Face recognition authentication (OpenCV Haar Cascade + LBPHFaceRecognizer loading trainer.yml)"),
      bullet("Hotword detection (Porcupine - pvporcupine listening for 'jarvis' and 'alexa' to trigger pyautogui Win+J event)"),
      bullet("Speech-to-text (SpeechRecognition library using Google Web Speech API with language codes: en-US, hi-IN, mr-IN)"),
      bullet("Fuzzy intent matching & command processing via CommandProcessor with SequenceMatcher similarity ratios"),
      bullet("Context tracker that retains recent command states for follow-up dialogs"),
      bullet("Jarvis Movie-like Personality with witty, professional, and time-aware verbal greetings"),
      bullet("AI Chat reasoning via a hybrid engine: tries online hugchat connection with cookie.json session; falls back to local offline Ollama port 11434 using gemma-heretic-local (Gemma-4-E4B GGUF) from G:\\Shared\\models"),
      bullet("Text-to-speech responses (pyttsx3 with Windows SAPI5 voice driver set at 174 WPM)"),
      bullet("SQLite database (jarvis.db with tables: sys_command, web_command, contacts)"),
      bullet("Eel-based web UI frontend served on localhost:8000 using edge web renderer mode"),,

      heading2("4.2 In Scope — Enterprise (Q4 2026 Roadmap)"),
      bullet("Multi-user role-based access control (RBAC) backed by enterprise DB schemas"),
      bullet("Enterprise SSO integrations (OIDC, SAML 2.0)"),
      bullet("Centralized biometric database replacing the local trainer.yml files"),
      bullet("Audit logging & compliance reports for SOC 2 security validation"),
      bullet("Antigravity Vibe Coding Engine — AI-assisted code generation within the assistant"),

      heading2("4.3 Out of Scope"),
      bullet("Mobile native apps (Phase 3)"),
      bullet("Custom ASICs for on-device ML acceleration (Research track)"),

      ...spacer(1),
      // ── 5. User Personas ──
      heading1("5. User Personas"),
      twoColTable([
        ["Power User (krishna)", "Uses Jarvis for app launching, WhatsApp hands-free messages, and Google searches in preferred language"],
        ["Executive", "Uses Jarvis for fast queries, status checks, and voice-queries in regional Hindi or Marathi dialects"],
        ["IT Admin", "Manages database command registers (sys_command, web_command), updates cookie.json, and reviews logs"],
        ["Security Officer", "Ensures biometric databases (trainer.yml) and session keys are secured using AES-256 local partitions"],
      ], ["Persona", "Primary Use Cases"]),

      ...spacer(1),
      // ── 6. Functional Requirements ──
      heading1("6. Functional Requirements"),
      heading2("6.1 Authentication Module"),
      bullet("FR-A1: System shall detect faces using cv2.CascadeClassifier with haarcascade_frontalface_default.xml"),
      bullet("FR-A2: System shall match faces against trained features using LBPHFaceRecognizer with trainer.yml model"),
      bullet("FR-A3: Biometric match scoring shall yield a distance indicator where < 100 is treated as a successful validation"),
      bullet("FR-A4: System shall shut down camera resources immediately after successful recognition or exit command (ESC)"),

      heading2("6.2 Voice Processing & Language Module"),
      bullet("FR-V1: Hotword detection shall run in a separate background process using pvporcupine listening for keywords"),
      bullet("FR-V2: Upon hotword match, system shall invoke pyautogui key downs to press Win+J, focusing the main UI shell"),
      bullet("FR-V3: STT processing shall support English, Hindi, and Marathi utilizing recognize_google with corresponding locales (en-US, hi-IN, mr-IN)"),
      bullet("FR-V4: User language preferences shall be saved automatically to language_config.json and persist across boots"),

      heading2("6.3 LLM Reasoning & NLU Engine"),
      bullet("FR-L1: AI Chat capability shall operate in a hybrid online/offline model. The system shall prioritize HuggingFace (hugchat) online responses but automatically route to local offline Ollama inference using gemma-heretic-local if cookies are missing, expired, or internet connection is down."),
      bullet("FR-L2: If falling back to local Ollama, the system shall check if the server is active on port 11434, and if not, boot G:\\Shared\\bin\\ollama-windows.exe in the background with local cache pointing to G:\\Shared\\models\\ollama_data."),
      bullet("FR-L3: The system shall verify if the model gemma-heretic-local is registered in Ollama. If missing, it shall automatically compile/create the model using G:\\Shared\\models\\Modelfile before executing the user query."),
      bullet("FR-L4: System shall use CommandProcessor sequence matcher similarity ratios (threshold: 0.5) to route intents"),
      bullet("FR-L5: System shall parse parameters (entities) by removing stop words ('open', 'play', 'send', 'call')"),
      bullet("FR-L6: Conversation tracking shall maintain last command and last entity keys within a local context dictionary"),
      
      heading2("6.4 Dynamic Persona System"),
      bullet("FR-P1: The system shall support voice/text commands to switch active personas between 'Jarvis' and 'Friday'."),
      bullet("FR-P2: Activating the 'Friday' persona shall set the default reasoning priority to Online Cloud layers, falling back to Local Offline core if offline."),
      bullet("FR-P3: Activating the 'Jarvis' persona shall set the default reasoning priority to Local Offline core, falling back to Online Cloud layers if offline core fails."),
      bullet("FR-P4: Assistant address formats ('Sir' for Jarvis, 'Boss' for Friday), verbal greeting templates, and local GGUF system instructions shall adjust dynamically according to the active persona."),

      heading2("6.4 Integration & Execution Adapter"),
      bullet("FR-I1: Application launching shall scan the SQLite database (jarvis.db) tables sys_command and web_command to map commands to local executables or web browser URLs."),
      bullet("FR-I2: WhatsApp integrations shall support messaging, calling, and video calling via URL schemes (whatsapp://) and simulated tab sequences."),
      bullet("FR-I3: YouTube playbacks shall execute search terms extracted from user queries via pywhatkit.playonyt"),

      ...spacer(1),
      // ── 7. Non-Functional Requirements ──
      heading1("7. Non-Functional Requirements"),
      twoColTable([
        ["Performance", "Edge authentication < 2s; local command processing < 100ms; speech rate optimized to 174 WPM"],
        ["Availability", "99.9% uptime for cloud services; offline local application execution without active internet connection"],
        ["Security", "Local data protection; cookie.json and trainer.yml stored on secured workspace volumes; seccomp profiles for execution"],
        ["Compatibility", "Runs on standard Windows 10/11 platforms with Edge chromium HTML renderer support"],
      ], ["NFR Category", "Requirement"]),

      ...spacer(1),
      // ── 8. Success Metrics ──
      heading1("8. Success Metrics & KPIs"),
      bullet("Biometric authentication success rate > 98% in typical desktop lighting environments"),
      bullet("NLU intent routing accuracy > 92% utilizing fuzzy SequenceMatcher processing"),
      bullet("Zero database corruption incidents across SQLite deployments"),
      bullet("Hotword CPU overhead kept below 3% using pvporcupine engine"),

      ...spacer(1),
      // ── 9. Milestones ──
      heading1("9. Roadmap & Milestones"),
      twoColTable([
        ["M1", "June 2026", "Stabilization of version 1.2: OpenCV LBPH, pvporcupine, hugchat fallback, and SQLite registers"],
        ["M2", "Q3 2026", "Enterprise migration: transition to central PostgreSQL, deployment of RBAC schemas"],
        ["M3", "Q4 2026", "Vibe Coding Engine: sandboxed compilation and script runner integration"],
      ].map(r => [r[0], r[1], r[2]]), ["Milestone", "Target Date", "Deliverable"]),
    ]
  }];

  const doc = new Document({ styles, numbering, sections });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outputDir, "01_PRD_Jarvis2025.docx"), buffer);
  console.log("✓ PRD written");
}

// ════════════════════════════════════════════════════════════════════════════
// DOC 2 — TECHNICAL ARCHITECTURE DOCUMENT
// ════════════════════════════════════════════════════════════════════════════
async function makeTAD() {
  const sections = [{
    properties: { page: pageProps },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "JARVIS 2025 — Technical Architecture Document | v1.2", ...sp(18, false, C.grey) })]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Confidential — Antigravity Inc.", ...sp(18, false, C.grey) })]
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Technical Architecture Document", ...sp(48, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "JARVIS 2025 Enterprise AI Platform   |   v1.2", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Architecture Overview"),
      body("Jarvis-2025 follows a layered, event-driven architecture with a clear separation between the UI shell, the backend orchestration layer, and the AI inference layer. The design is intentionally modular so that any layer can be swapped independently as technology evolves."),
      ...spacer(1),
      blueBox([
        "ARCHITECTURE LAYERS:",
        "  ① Frontend Shell       — Eel (HTML/CSS/JS) rendered via Microsoft Edge Chromium engine",
        "  ② Background Process  — Hotword Listener (pvporcupine) simulating pyautogui keystrokes",
        "  ③ Main UI Process     — Eel server executing main.py startup and authentication",
        "  ④ Orchestration Engine — Python asyncio event loop + localized CommandProcessor",
        "  ⑤ AI & Automation     — OpenCV LBPH recognizer | hugchat HF client & local Ollama (hybrid) | pyttsx3 SAPI5 | pyautogui",
        "  ⑥ Data Store           — SQLite (jarvis.db) and local JSON configurations",
      ]),,
      ...spacer(1),

      heading1("2. Repository Structure & Module Map"),
      heading2("2.1 Core Repository Layout"),
      twoColTable([
        ["main.py", "Bootstrap script; initializes Eel UI shell and triggers Face Authentication"],
        ["run.py", "System entry point; spawns main process and hotword listener process using multiprocessing"],
        ["setup.py", "Automatic dependency configuration script (installs opencv, pyaudio, hugchat, etc.)"],
        ["init_db.py", "SQLite database initialization script; creates tables and loads seed data"],
        ["diagnostic.py", "Hardware validator; verifies camera feeds, audio devices, and package installations"],
        ["backend/", "All Python core logical handlers and services"],
        ["frontend/", "Eel web UI components (HTML, CSS, JS, sound effects)"],
        ["jarvis.db", "SQLite database containing command registries and contacts"],
      ], ["Path", "Purpose"]),

      ...spacer(1),
      heading2("2.2 Backend Modules"),
      twoColTable([
        ["backend/auth/recoganize.py", "Face detection using Haar cascade, verification using LBPHFaceRecognizer"],
        ["backend/command.py", "Core execution coordinator; handles speak(), takecommand() and processCommand() loops"],
        ["backend/language_manager.py", "Language config manager; tracks language switches (en, hi, mr) and maps codes"],
        ["backend/intelligent_processor.py", "Fuzzy command processor; checks intents using sequence match ratios"],
        ["backend/jarvis_personality.py", "Jarvis personality simulator; generates movie-style responses in correct locales"],
        ["backend/feature.py", "Features including play_assistant_sound, hotword, openCommand, whatsApp, and hybrid online/offline chatBot"],
        ["backend/cookie.json", "Session cookie storage for HuggingFace (hugchat client access)"],
        ["backend/language_config.json", "Saved language code configuration"],
        ["backend/persona_config.json", "Saved active assistant persona configuration (Jarvis vs Friday)"],
      ], ["Module", "Responsibility"]),

      ...spacer(1),
      heading1("3. Detailed Module Subsystems"),
      heading2("3.1 Biometric Authentication (OpenCV LBPH)"),
      body("The Face Recognition subsystem is written using OpenCV. The architecture is as follows:"),
      bullet("Detector: Haar Cascade Classifier (haarcascade_frontalface_default.xml) detects facial bounds."),
      bullet("Recognizer: LBPHFaceRecognizer loads trained facial features from trainer.yml."),
      bullet("Prediction: predict() returns (label_id, distance). A distance < 100 denotes a valid match."),
      bullet("Metadata: Names are mapped to label indices in a local index database (label 2 maps to 'krishna')."),
      ...spacer(1),

      heading2("3.2 Voice & NLU Subsystem"),
      bullet("Hotword: pvporcupine.create(keywords=['jarvis', 'alexa']) streams microphone samples at 16kHz. On detection, pyautogui presses Win+J keybind."),
      bullet("Speech-to-Text: SpeechRecognition listens through PyAudio source, invoking r.recognize_google with current language code (en-US, hi-IN, mr-IN)."),
      bullet("Fuzzy Intent: SequenceMatcher compares queries to keyword lists. If match ratio > 0.5, intent type is recognized. If query contains a keyword (e.g. 'open' in query), default paths are assigned."),
      bullet("Context Tracker: Retains last_command and last_entity variables to resolve follow-ups."),
      bullet("Persona Router: Parses 'persona' commands to swap names and save state in backend/persona_config.json, dynamically adjusting SAPI5 synthesis prefix greetings and address formats (Sir vs Boss)."),
      bullet("Text-to-Speech: pyttsx3 SAPI5 driver plays voice output locally at 174 WPM, concurrently updating UI DisplayMessage panels."),,

      ...spacer(1),
      heading2("3.3 Automation & Integrations"),
      bullet("App Launcher: Queries sys_command (local paths) and web_command (URLs) in SQLite. Runs os.startfile() or webbrowser.open() on match. Falls back to cmd.exe 'start' commands."),
      bullet("WhatsApp Protocol: Extracts number from contacts table. Formats whatsapp://send?phone=... URL, launches it via cmd, and automates tab-selections via pyautogui to trigger send."),
      bullet("YouTube Player: Uses pywhatkit.playonyt to search term and launch browser player directly."),
      bullet("AI Chatbot: Tries online hugchat connection with cookie.json session; falls back to local Ollama on port 11434. Automatically starts G:\\Shared\\bin\\ollama-windows.exe using local models cache at G:\\Shared\\models\\ollama_data and creates the gemma-heretic-local model from Modelfile if not present."),,

      ...spacer(1),
      heading1("4. Database Schema (SQLite)"),
      body("The database jarvis.db contains the following tables:"),
      twoColTable([
        ["sys_command", "id (INTEGER PK AUTOINCREMENT), name (VARCHAR UNIQUE), path (VARCHAR)"],
        ["web_command", "id (INTEGER PK AUTOINCREMENT), name (VARCHAR UNIQUE), url (VARCHAR)"],
        ["contacts", "id (INTEGER PK AUTOINCREMENT), name (VARCHAR UNIQUE), phone (VARCHAR), email (VARCHAR)"],
      ], ["Table Name", "Columns"]),

      ...spacer(1),
      heading1("5. Security Threats & Mitigations"),
      twoColTable([
        ["Biometric bypass (unknown faces)", "Liveness detection integration (planned); strict distance filter < 100"],
        ["Cookie hijacking", "HuggingFace cookies stored in local cookie.json with read-only file privileges"],
        ["Microphone eavesdropping", "Edge processing; pvporcupine processes audio frames locally in memory; no streaming to external servers"],
        ["SQL Injection", "Database queries parameterized using SQLite placeholder markers (?)"],
      ], ["Threat", "Mitigation"]),
    ]
  }];

  const doc = new Document({ styles, numbering, sections });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outputDir, "02_Technical_Architecture.docx"), buffer);
  console.log("✓ Architecture doc written");
}

// ════════════════════════════════════════════════════════════════════════════
// DOC 3 — VIBE CODING DEVELOPER GUIDE
// ════════════════════════════════════════════════════════════════════════════
async function makeVibeCodingGuide() {
  const sections = [{
    properties: { page: pageProps },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "Jarvis-2025 — Vibe Coding Developer Guide", ...sp(18, false, C.grey) })]
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Vibe Coding Engine", ...sp(52, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Developer Guide & Skill Extensions   |   v1.2", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Introduction"),
      body("The Antigravity Vibe Coding Engine (VCE) is the AI-powered development layer embedded within Jarvis-2025. It transforms spoken or typed natural language into product extensions. This guide covers how developers can register skills, add system shortcuts, extend database command records, and interact with the NLU parsing classes."),
      ...spacer(1),

      heading1("2. Registering Database Commands"),
      body("Jarvis launches applications and websites by checking SQLite registries in jarvis.db. Developers can add features by adding database records:"),
      heading2("2.1 Adding a Local System Application"),
      blueBox([
        "import sqlite3",
        "conn = sqlite3.connect('jarvis.db')",
        "cursor = conn.cursor()",
        "",
        "# Register local text editor",
        "cursor.execute(",
        "  'INSERT INTO sys_command (name, path) VALUES (?, ?)',",
        "  ('sublime', 'C:\\\\Program Files\\\\Sublime Text\\\\sublime_text.exe')",
        ")",
        "conn.commit()",
        "conn.close()",
      ]),
      ...spacer(1),

      heading2("2.2 Adding a Web Application Link"),
      blueBox([
        "conn = sqlite3.connect('jarvis.db')",
        "cursor = conn.cursor()",
        "",
        "# Register internal corporate dashboard",
        "cursor.execute(",
        "  'INSERT INTO web_command (name, url) VALUES (?, ?)',",
        "  ('dashboard', 'https://internal.antigravity.ai/dash')",
        ")",
        "conn.commit()",
        "conn.close()",
      ]),
      ...spacer(1),

      heading1("3. Developing Core Intent Extensions"),
      body("To add a new voice intent to the CommandProcessor, developers must modify command patterns in backend/intelligent_processor.py:"),
      blueBox([
        "# Inside CommandProcessor.load_command_patterns():",
        "return {",
        "    'open_app': { ... },",
        "    'weather': {",
        "        'en': ['weather', 'temperature', 'climate', 'forecast'],",
        "        'hi': ['मौसम', 'तापमान', 'जलवायु'],",
        "        'mr': ['हवामान', 'तापमान', 'हवामानाचा']",
        "    },",
        "    # Add your custom intent here:",
        "    'deploy_code': {",
        "        'en': ['deploy', 'publish', 'push code'],",
        "        'hi': ['डेप्लॉय करो', 'पब्लिश करो'],",
        "        'mr': ['डेप्लॉय करा', 'पब्लिश करा']",
        "    }",
        "}",
      ]),
      ...spacer(1),
      body("Then, add the execution block inside backend/command.py's processCommand(query) handler:"),
      blueBox([
        "elif command_type == 'deploy_code':",
        "    speak('Initiating code deployment sequence, sir.')",
        "    # Call deployment automation logic here...",
      ]),

      ...spacer(1),
      heading1("4. Biometric Training and Onboarding"),
      body("To onboard a new user into the OpenCV LBPH recognizer, developers must capture sample frames and run the training scripts:"),
      bullet("Step 1: Save JPEG face frames into backend/auth/dataSet/ under naming conventions (e.g. User.2.1.jpg for Krishna)."),
      bullet("Step 2: Initialize Haar Cascades to crop coordinates around the face box."),
      bullet("Step 3: Train the model: recognizer.train(faces, np.array(ids)) and save the output matrix to backend/auth/trainer/trainer.yml."),
      bullet("Step 4: Update the names array in backend/auth/recoganize.py: names = ['', '', 'krishna', 'new_user']."),
    ]
  }];

  const doc = new Document({ styles, numbering, sections });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outputDir, "03_VibeCoding_Developer_Guide.docx"), buffer);
  console.log("✓ Vibe Coding guide written");
}

// ════════════════════════════════════════════════════════════════════════════
// DOC 4 — ENTERPRISE PITCH / BUSINESS PLAN
// ════════════════════════════════════════════════════════════════════════════
async function makeBusinessPlan() {
  const sections = [{
    properties: { page: pageProps },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(22, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Enterprise Business Plan", ...sp(48, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 80 }, children: [new TextRun({ text: "Jarvis-2025: Grounded Local AI Security Platform", ...sp(26, false, C.dark) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Confidential — June 2026   |   For Investor and Partner Review", ...sp(20, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Company Overview"),
      body("Antigravity Inc. is a deep-tech AI company building enterprise-grade AI assistant infrastructure. Our flagship product, Jarvis-2025, combines local biometric security (OpenCV face recognition), edge UI execution (Eel), multilingual voice capabilities, and AI reasoning adapters to deliver an air-gapped, privacy-compliant workflow assistant for corporate environments."),
      ...spacer(1),
      blueBox([
        "Mission: Eliminate enterprise context-switching through local biometrics and local voice automation.",
        "Founded: 2025",
        "Stage: Seed",
      ]),
      ...spacer(1),

      heading1("2. Market Opportunity"),
      heading2("2.1 Competitive Moat"),
      body("Unlike general cloud assistants (Siri, ChatGPT Enterprise), Jarvis-2025 runs core desktop automation locally. It interfaces with local applications, retrieves configuration scripts from an embedded SQLite base, and utilizes local SAPI5 voices. This provides an absolute privacy barrier for defense, healthcare, and finance sectors."),
      ...spacer(1),

      heading1("3. Revenue Model"),
      twoColTable([
        ["Developer License", "Free", "Access to open-source base, local SQLite, basic English triggers"],
        ["Enterprise Seat", "$99/user/month", "SSO integration, centralized trainer.yml biometrics management, SLA"],
        ["On-Premise Defense", "Custom Contract", "Fully air-gapped models, customized vocabulary dictionary mapping, custom languages"],
      ], ["Tier", "Price", "Features"]),
      ...spacer(1),

      heading1("4. Go-to-Market Strategy"),
      bullet("Provide the open-source community edition on GitHub to capture early adopters."),
      bullet("Target system integrators deploying automation setups in India and APAC, highlighting native English, Hindi, and Marathi command features."),
      bullet("Offer plug-and-play local installation bundles that bypass typical cloud approval cycles."),
    ]
  }];

  const doc = new Document({ styles, numbering, sections });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outputDir, "04_Business_Plan.docx"), buffer);
  console.log("✓ Business plan written");
}

// ════════════════════════════════════════════════════════════════════════════
// DOC 5 — ENTERPRISE ONBOARDING & DEPLOYMENT GUIDE
// ════════════════════════════════════════════════════════════════════════════
async function makeOnboardingGuide() {
  const sections = [{
    properties: { page: pageProps },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Enterprise Deployment Guide", ...sp(48, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Jarvis-2025   |   IT Administrator Reference   |   v1.2", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Prerequisites"),
      heading2("1.1 Hardware Specifications"),
      twoColTable([
        ["Camera", "720p or 1080p webcam supporting cv2.VideoCapture(0) with direct show frames"],
        ["Microphone", "Standard microphone; audio streams set at 16kHz for pvporcupine"],
        ["RAM", "16GB minimum; 32GB recommended (for local 5.34GB Gemma-4-E4B heretic GGUF model execution)"],
        ["OS", "Windows 10/11 (fully supports pyttsx3 SAPI5 driver)"],
      ], ["Component", "Specification"]),,
      ...spacer(1),

      heading2("1.2 Software Dependencies"),
      bullet("Python: Version 3.11+ (ensure python.exe is in PATH)"),
      bullet("C++ Build Tools: Required for compiling PyAudio (pyaudio wheel)"),
      bullet("SQLite3: Installed by default with Python distribution"),
      ...spacer(1),

      heading1("2. Installation Steps"),
      blueBox([
        "# 1. Clone repository and navigate to folder",
        "git clone https://github.com/kriss2012/Jarvis-2025.git",
        "cd Jarvis-2025",
        "",
        "# 2. Set up virtual environment",
        "python -m venv envJarvis",
        ".\\envJarvis\\Scripts\\Activate.ps1",
        "",
        "# 3. Run setup command (installs requirements.txt dependencies)",
        "python setup.py",
        "",
        "# 4. Initialize SQLite tables",
        "python init_db.py",
        "",
        "# 5. Perform diagnostics to verify hardware compatibility",
        "python diagnostic.py",
        "",
        "# 6. Launch the dual-process application",
        "python run.py",
      ]),
      ...spacer(1),

      heading1("3. Configuration Management"),
      heading2("3.1 HuggingFace Session Cookies (cookie.json)"),
      body("General AI Chat (hugchat agent) requires valid browser cookies from HuggingFace. Format backend/cookie.json:"),
      blueBox([
        "[",
        '  {"name": "token_name", "value": "token_value"},',
        '  {"name": "another_cookie", "value": "another_value"}',
        "]",
      ]),
      body("To obtain these cookies, log into huggingface.co, open browser DevTools, inspect the cookies panel in the Network tab, and save the exported values to cookie.json."),
      ...spacer(1),

      heading2("3.2 Language Configuration (language_config.json)"),
      body("Located at backend/language_config.json. Configures active speech locale:"),
      blueBox([
        "{",
        '  "language": "en"',
        "}",
      ]),
      body("Supported values: 'en' (English), 'hi' (Hindi), 'mr' (Marathi). Updated automatically when users issue commands like 'change language to Hindi'."),
      ...spacer(1),
      heading2("3.3 Local Offline Model Configuration (Ollama)"),
      body("The hybrid chatbot fallback connects to a local Ollama instance configured with the offline Gemma-4-E4B-it heretic model:"),
      bullet("Model Name: gemma-heretic-local"),
      bullet("Binary Path: G:\\Shared\\bin\\ollama-windows.exe"),
      bullet("Model Path: G:\\Shared\\models\\gemma-4-E4B-it-ultra-uncensored-heretic-Q4_K_M.gguf"),
      bullet("Modelfile: G:\\Shared\\models\\Modelfile (defines temperature 0.7, top_p 0.9, and the uncensored system instructions)"),
      bullet("Environment Variables: OLLAMA_MODELS set to G:\\Shared\\models\\ollama_data ensures that all model caches run entirely from the G:\\ volume, conserving local disk space."),
      ...spacer(1),
      
      heading2("3.4 Persona Configuration (persona_config.json)"),
      body("Located at backend/persona_config.json. Tracks active assistant identity and reasoning priority:"),
      blueBox([
        "{",
        '  "persona": "Jarvis"',
        "}"
      ]),
      body("Supported values: 'Jarvis' (Offline priority, address 'Sir'), 'Friday' (Online priority, address 'Boss'). Updated dynamically when user issues commands like 'activate Friday' or 'switch to Jarvis'."),
      ...spacer(1),

      ...spacer(1),
      heading1("4. Troubleshooting"),
      twoColTable([
        ["cv2.face module not found", "Install opencv-contrib-python which embeds the face recognizers: pip install opencv-contrib-python"],
        ["No cookies configured / HuggingChat error", "Verify backend/cookie.json contains active, unexpired session cookies. Fallback to local Ollama should trigger automatically if cookies are invalid."],
        ["Ollama failed to start / offline model unavailable", "Ensure G:\\ drive is mounted, check write permissions on G:\\Shared\\models\\ollama_data, and verify G:\\Shared\\bin\\ollama-windows.exe execution permissions."],
        ["PyAudio compilation errors on Windows", "Install precompiled wheel: pip install pipwin followed by pipwin install pyaudio"],
        ["pvporcupine key error", "Ensure Porcupine access key is configured or default pre-trained local model is active"],
        ["Numpy version warnings", "Ensure numpy is pinned to version < 2.0 (e.g. numpy>=1.25.0,<2.0)"],
      ], ["Issue", "Resolution"]),,
      ...spacer(1),
      body("Support portal: support.antigravity.ai   |   Documentation: docs.antigravity.ai", { color: C.grey, italic: true }),
    ]
  }];

  const doc = new Document({ styles, numbering, sections });
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(path.join(outputDir, "05_Enterprise_Deployment_Guide.docx"), buffer);
  console.log("✓ Deployment guide written");
}

// ════════════════════════════════════════════════════════════════════════════
// MAIN
// ════════════════════════════════════════════════════════════════════════════
(async () => {
  console.log("Generating Jarvis-2025 enterprise documentation suite...\n");
  try {
    await makePRD();
    await makeTAD();
    await makeVibeCodingGuide();
    await makeBusinessPlan();
    await makeOnboardingGuide();
    console.log("\n✅ All 5 documents generated successfully.");
  } catch (err) {
    console.error("Error generating documents:", err);
    process.exit(1);
  }
})();
