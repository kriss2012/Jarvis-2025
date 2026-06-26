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
      children: [new TextRun({ text: "JARVIS 2025 — Enterprise AI Assistant | PRD v1.0", ...sp(18, false, C.grey) })]
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
        children: [new TextRun({ text: "Enterprise AI Assistant Platform", ...sp(32, false, C.dark) })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 400 },
        children: [new TextRun({ text: "Product Requirements Document — v1.0   |   June 2025", ...sp(22, false, C.grey), italic: true })]
      }),
      divider(),
      ...spacer(1),

      // ── 1. Executive Summary ──
      heading1("1. Executive Summary"),
      body("Jarvis-2025 is an enterprise-grade AI desktop assistant that merges voice-activated command processing, real-time facial biometric authentication, and large language model (LLM) reasoning into a single unified platform. Built on Python + Eel, it exposes a web-native UI consumed locally, enabling rich interactivity without cloud round-trips for core interactions."),
      body("This PRD defines the product scope, feature roadmap, system architecture, and success criteria required to evolve the current open-source prototype into a commercially deployable, multi-tenant, enterprise product branded under Antigravity Inc."),

      ...spacer(1),
      // ── 2. Problem Statement ──
      heading1("2. Problem Statement"),
      body("Enterprises today operate with fragmented toolchains: separate chat interfaces, separate identity management systems, and siloed automation pipelines. Knowledge workers lose an estimated 30–40% of productive time switching contexts or repeating commands across tools."),
      body("Existing AI assistant solutions (Cortana, Alexa for Business, Google Assistant) suffer from:"),
      bullet("Dependency on cloud processing, raising data sovereignty concerns"),
      bullet("Lack of biometric security — simple wake-words can be spoofed"),
      bullet("No deep integration with internal enterprise data sources"),
      bullet("One-size-fits-all personalities with no personalization layer"),
      ...spacer(1),

      // ── 3. Vision ──
      heading1("3. Product Vision & Goals"),
      blueBox([
        'Vision: "An always-on, biometrically-secured, AI-powered enterprise co-pilot that operates',
        'with near-zero latency and integrates natively with every tool in your organization."'
      ]),
      ...spacer(1),
      heading2("3.1 Primary Goals"),
      bullet("G1 — Security First: Replace password-based login with face recognition + voice biometrics"),
      bullet("G2 — Offline Capable: Core reasoning & authentication must function without internet"),
      bullet("G3 — Enterprise Integrations: Slack, Jira, Confluence, Google Workspace, SAP connectors"),
      bullet("G4 — Extensible Skill Engine: Plugin marketplace for domain-specific capabilities"),
      bullet("G5 — Compliance Ready: SOC 2 Type II, ISO 27001, GDPR, HIPAA pathways"),

      ...spacer(1),
      // ── 4. Scope ──
      heading1("4. Scope"),
      heading2("4.1 In Scope — MVP (Q3 2025)"),
      bullet("Face recognition authentication (OpenCV + face_recognition library)"),
      bullet("Hotword detection (PocketSphinx / Snowboy)"),
      bullet("Speech-to-text (Whisper local model)"),
      bullet("LLM chat integration (local Mistral 7B + cloud fallback to Claude API)"),
      bullet("Text-to-speech responses (pyttsx3 + ElevenLabs cloud)"),
      bullet("SQLite user profile & session database"),
      bullet("Eel-based web UI (HTML/CSS/JS frontend)"),
      bullet("GitHub Actions CI/CD pipeline"),

      heading2("4.2 In Scope — Enterprise (Q4 2025 – Q1 2026)"),
      bullet("Multi-user role-based access control (RBAC)"),
      bullet("Enterprise SSO (SAML 2.0, OIDC)"),
      bullet("Plugin/skill SDK with marketplace"),
      bullet("Audit logging & compliance reports"),
      bullet("Admin dashboard (React SPA)"),
      bullet("REST + WebSocket API for third-party integrations"),
      bullet("Docker / Kubernetes deployment manifests"),
      bullet("Antigravity Vibe Coding Engine — AI-assisted code generation within the assistant"),

      heading2("4.3 Out of Scope"),
      bullet("Mobile native apps (Phase 3)"),
      bullet("Custom ASICs for on-device ML acceleration (Research track)"),
      bullet("Blockchain-based credential management (Evaluation only)"),

      ...spacer(1),
      // ── 5. User Personas ──
      heading1("5. User Personas"),
      twoColTable([
        ["Power User (Dev/Engineer)", "Uses Jarvis for code generation, PR reviews, terminal commands via voice"],
        ["Executive", "Uses Jarvis for meeting summaries, email drafts, KPI dashboards"],
        ["IT Admin", "Manages user onboarding, audit logs, plugin approvals"],
        ["Security Officer", "Reviews biometric logs, configures auth policies, runs compliance reports"],
        ["New Employee", "Onboarding guide, policy Q&A, HR bot integration"],
      ], ["Persona", "Primary Use Cases"]),

      ...spacer(1),
      // ── 6. Functional Requirements ──
      heading1("6. Functional Requirements"),
      heading2("6.1 Authentication Module"),
      bullet("FR-A1: System shall detect faces within 500ms of camera activation"),
      bullet("FR-A2: System shall support enrollment of up to 50 faces per deployment"),
      bullet("FR-A3: False acceptance rate (FAR) shall be < 0.1%"),
      bullet("FR-A4: System shall fall back to PIN after 3 failed face attempts"),
      bullet("FR-A5: All biometric data shall be stored encrypted (AES-256) locally"),

      heading2("6.2 Voice Processing Module"),
      bullet("FR-V1: Hotword detection shall run continuously with < 2% CPU overhead"),
      bullet("FR-V2: STT accuracy shall exceed 95% for English in quiet environments"),
      bullet("FR-V3: System shall handle commands up to 60 seconds in length"),
      bullet("FR-V4: TTS response latency shall be < 800ms for < 50 word responses"),

      heading2("6.3 LLM Reasoning Engine"),
      bullet("FR-L1: System shall support pluggable LLM backends (local & cloud)"),
      bullet("FR-L2: Context window shall maintain last 20 conversation turns"),
      bullet("FR-L3: System shall stream tokens to UI for perceived responsiveness"),
      bullet("FR-L4: System shall cite sources when drawing from indexed documents"),

      heading2("6.4 Antigravity Vibe Coding Engine"),
      body("The Vibe Coding Engine is Antigravity's proprietary differentiator — an embedded AI pair-programmer accessible via voice:"),
      bullet("FR-VC1: User can say 'Jarvis, write a Python function to...' and receive streaming code"),
      bullet("FR-VC2: Engine shall execute sandboxed code snippets and return stdout"),
      bullet("FR-VC3: Engine shall integrate with VS Code extension (Phase 2)"),
      bullet("FR-VC4: Engine shall support 20+ programming languages"),

      ...spacer(1),
      // ── 7. Non-Functional Requirements ──
      heading1("7. Non-Functional Requirements"),
      twoColTable([
        ["Performance", "Cold start < 5s; command response < 2s P95"],
        ["Availability", "99.9% uptime for cloud services; offline degraded mode for core features"],
        ["Security", "AES-256 at rest; TLS 1.3 in transit; OWASP Top 10 mitigated"],
        ["Scalability", "Multi-tenant SaaS: 10,000+ concurrent users per cluster"],
        ["Accessibility", "WCAG 2.1 AA for web UI"],
        ["Observability", "OpenTelemetry traces, Prometheus metrics, Loki logs"],
      ], ["NFR Category", "Requirement"]),

      ...spacer(1),
      // ── 8. Success Metrics ──
      heading1("8. Success Metrics & KPIs"),
      bullet("DAU/MAU ratio > 60% (strong retention)"),
      bullet("Authentication success rate > 98% in controlled environments"),
      bullet("NPS > 45 in enterprise pilot programs"),
      bullet("Command completion rate > 92% (intent correctly resolved)"),
      bullet("Time-to-first-command < 30 seconds from cold boot"),
      bullet("Zero critical security incidents in first 12 months post-launch"),

      ...spacer(1),
      // ── 9. Milestones ──
      heading1("9. Roadmap & Milestones"),
      twoColTable([
        ["M1", "Q2 2025", "Open-source prototype stabilization, CI/CD, unit tests > 80% coverage"],
        ["M2", "Q3 2025", "MVP launch: face auth + voice + LLM, beta with 5 design partners"],
        ["M3", "Q4 2025", "Enterprise features: RBAC, SSO, plugin SDK, admin dashboard"],
        ["M4", "Q1 2026", "Antigravity Vibe Coding Engine GA, VS Code extension"],
        ["M5", "Q2 2026", "SOC 2 Type II audit completion, Series A fundraise readiness"],
      ].map(r => [r[0], r[1], r[2]]), ["Milestone", "Target Date", "Deliverable"]),

      ...spacer(1),
      heading1("10. Risks & Mitigations"),
      twoColTable([
        ["Face recognition bias in diverse populations", "High", "Use InsightFace multi-ethnic dataset; third-party bias audit"],
        ["Local LLM hardware requirements limit adoption", "Medium", "Cloud fallback; optimize with GGUF quantization"],
        ["Privacy regulations block biometric use in EU", "High", "Consent-first architecture; GDPR DPA agreements"],
        ["Open-source fork competition", "Low", "Speed to enterprise features; Antigravity brand moat"],
      ], ["Risk", "Likelihood", "Mitigation"]),
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
      children: [new TextRun({ text: "JARVIS 2025 — Technical Architecture Document | v1.0", ...sp(18, false, C.grey) })]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Confidential — Antigravity Inc.", ...sp(18, false, C.grey) })]
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Technical Architecture Document", ...sp(48, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "JARVIS 2025 Enterprise AI Platform   |   v1.0", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Architecture Overview"),
      body("Jarvis-2025 follows a layered, event-driven architecture with a clear separation between the UI shell, the backend orchestration layer, and the AI inference layer. The design is intentionally modular so that any layer can be swapped independently as technology evolves."),
      ...spacer(1),
      blueBox([
        "ARCHITECTURE LAYERS:",
        "  ① Frontend Shell       — Eel + HTML/CSS/JS (Chromium edge renderer)",
        "  ② API Gateway          — FastAPI (replaces direct Eel calls in enterprise tier)",
        "  ③ Orchestration Engine — Python asyncio event loop + plugin broker",
        "  ④ AI Services Layer    — STT | LLM | TTS | Face Recognition | NLU",
        "  ⑤ Data Layer           — SQLite (dev) → PostgreSQL (production) + Redis cache",
        "  ⑥ Infra / DevOps       — Docker, GitHub Actions CI/CD, Prometheus + Grafana",
      ]),
      ...spacer(1),

      heading1("2. Current Repository Structure"),
      heading2("2.1 Top-Level Layout"),
      twoColTable([
        ["main.py", "Eel app bootstrap, face auth flow, UI event wiring"],
        ["run.py", "Entry-point wrapper with env checks"],
        ["setup.py", "Dependency installation helper"],
        ["init_db.py / create_sample_db.py", "SQLite schema creation and seed data"],
        ["diagnostic.py", "System health checks (camera, audio, libs)"],
        ["backend/", "All Python services (auth, commands, features, LLM)"],
        ["frontend/", "HTML + CSS + JS UI files served by Eel"],
        [".github/workflows/", "GitHub Actions CI pipeline"],
        ["jarvis.db", "SQLite database (gitignored in production)"],
      ], ["Path", "Purpose"]),

      ...spacer(1),
      heading2("2.2 Backend Modules"),
      twoColTable([
        ["backend/auth/recoganize.py", "OpenCV face detection + face_recognition embeddings"],
        ["backend/command.py", "Text-to-speech (pyttsx3) command dispatcher"],
        ["backend/feature.py", "Sound effects, startup chimes"],
        ["backend/hotword/", "PocketSphinx continuous listening thread"],
        ["backend/llm/", "HuggingFace / Claude API chat integration"],
        ["backend/skills/", "(Planned) Plugin skill loader"],
      ], ["Module", "Responsibility"]),

      ...spacer(1),
      heading1("3. Target Enterprise Architecture"),
      heading2("3.1 Microservices Decomposition"),
      body("For the enterprise tier, the monolithic Python backend is decomposed into independently deployable services:"),
      bullet("jarvis-auth-service — Biometric + SSO authentication (FastAPI + OpenCV)"),
      bullet("jarvis-voice-service — STT / TTS pipeline (Whisper + ElevenLabs)"),
      bullet("jarvis-llm-service — LLM orchestration with RAG (LangChain + Mistral/Claude)"),
      bullet("jarvis-skills-service — Plugin broker and skill executor (sandboxed subprocess)"),
      bullet("jarvis-ui-service — Eel server (dev) / React SPA + Nginx (production)"),
      bullet("jarvis-admin-service — RBAC, audit logs, user management API"),
      bullet("jarvis-gateway — Kong API Gateway (rate limiting, auth tokens, routing)"),

      ...spacer(1),
      heading2("3.2 Data Architecture"),
      twoColTable([
        ["User Profiles", "PostgreSQL", "User identity, enrollment metadata, preferences"],
        ["Face Embeddings", "Encrypted file store (AES-256)", "Binary feature vectors; never stored in DB"],
        ["Conversation History", "PostgreSQL + Redis TTL", "Last 20 turns in Redis; archived to PG"],
        ["Audit Logs", "PostgreSQL (append-only)", "SOC 2 compliance; 7-year retention"],
        ["Plugin Registry", "PostgreSQL", "Approved plugins, versions, permissions"],
        ["Metrics / Traces", "Prometheus + Jaeger", "OpenTelemetry instrumentation"],
      ], ["Data Domain", "Store", "Notes"]),

      ...spacer(1),
      heading2("3.3 Authentication Architecture"),
      body("Authentication follows a multi-factor pipeline:"),
      bullet("Layer 1 — Face Recognition: OpenCV Haar cascade (fast pre-filter) → face_recognition dlib embedding (128-dim vector) → cosine similarity threshold ≥ 0.6"),
      bullet("Layer 2 — Voice Biometrics (Phase 2): Speaker verification via x-vector model"),
      bullet("Layer 3 — Enterprise SSO: SAML 2.0 / OIDC token exchange for cloud apps"),
      bullet("Session Tokens: JWT (RS256), 1-hour expiry, refresh token rotation"),
      ...spacer(1),

      heading1("4. Antigravity Vibe Coding Engine — Technical Design"),
      blueBox([
        "The Vibe Coding Engine turns natural language into running code inside the assistant.",
        "It combines intent parsing, code generation, sandboxed execution, and streaming output."
      ]),
      ...spacer(1),
      heading2("4.1 Pipeline"),
      bullet("Step 1 — Intent Detection: NLU classifier identifies 'code generation' intent"),
      bullet("Step 2 — Context Extraction: Language, framework, constraints parsed from utterance"),
      bullet("Step 3 — Code Generation: LLM prompt engineering with system prompt for coding assistant"),
      bullet("Step 4 — Static Analysis: AST parse (Python ast module; ESTree for JS) to catch syntax errors"),
      bullet("Step 5 — Sandboxed Execution: Docker --network=none container with 5s timeout, 256MB RAM cap"),
      bullet("Step 6 — Output Streaming: stdout/stderr streamed to UI via WebSocket"),
      bullet("Step 7 — Feedback Loop: User can say 'fix it' or 'add error handling' for iterative refinement"),
      ...spacer(1),

      heading2("4.2 Supported Languages (MVP)"),
      body("Python, JavaScript/Node.js, TypeScript, Bash, SQL, Go, Rust, Java, C#, Ruby, PHP, Swift, Kotlin, Dart, R, MATLAB syntax, HTML/CSS, YAML, JSON, Terraform HCL"),

      ...spacer(1),
      heading1("5. Security Architecture"),
      heading2("5.1 Threat Model"),
      twoColTable([
        ["Spoofed face (photo/video replay)", "Liveness detection (eye blink + head pose variation)"],
        ["Eavesdropping on local Eel websocket", "Bind to 127.0.0.1 only; TLS for enterprise RemoteUI"],
        ["Plugin supply chain attack", "Code signing requirement; sandboxed execution; approval workflow"],
        ["LLM prompt injection via voice", "Input sanitization; system prompt isolation; output validation"],
        ["SQLite file exfiltration", "SQLCipher encryption; encrypted disk volume"],
      ], ["Threat", "Mitigation"]),

      ...spacer(1),
      heading1("6. CI/CD & DevOps"),
      heading2("6.1 Current GitHub Actions Pipeline"),
      bullet("Trigger: Push to main & PRs"),
      bullet("Jobs: lint (flake8 + black) → unit tests (pytest) → build check"),
      bullet("Planned additions: SAST (Bandit), dependency scan (Trivy), Docker build & push"),

      heading2("6.2 Target Deployment (Kubernetes)"),
      bullet("Helm chart per microservice"),
      bullet("Horizontal Pod Autoscaler on voice-service and llm-service"),
      bullet("Secrets via HashiCorp Vault or AWS Secrets Manager"),
      bullet("GitOps with ArgoCD for production deployments"),
      bullet("Canary releases via Argo Rollouts (5% → 25% → 100% over 24h)"),

      ...spacer(1),
      heading1("7. Observability Stack"),
      twoColTable([
        ["Metrics", "Prometheus + Grafana dashboards (latency, error rate, biometric scores)"],
        ["Tracing", "OpenTelemetry → Jaeger (end-to-end command traces)"],
        ["Logging", "Structured JSON logs → Loki → Grafana"],
        ["Alerting", "PagerDuty integration; SLO-based alerts (error budget burn rate)"],
        ["Uptime", "Synthetic monitoring via Blackbox Exporter"],
      ], ["Concern", "Solution"]),

      ...spacer(1),
      heading1("8. Technology Stack Summary"),
      twoColTable([
        ["UI Framework", "Eel 0.16 (dev) / React 18 + Vite (enterprise)"],
        ["Backend Language", "Python 3.11+"],
        ["API Framework", "FastAPI 0.110+"],
        ["Face Recognition", "OpenCV 4.x + face_recognition (dlib)"],
        ["Speech-to-Text", "OpenAI Whisper (local) + Google STT (fallback)"],
        ["Text-to-Speech", "pyttsx3 (offline) + ElevenLabs (cloud)"],
        ["LLM", "Mistral 7B GGUF (local) + Claude claude-sonnet-4-6 API"],
        ["Database", "SQLite (dev) / PostgreSQL 16 (prod)"],
        ["Cache", "Redis 7"],
        ["Container", "Docker + Kubernetes 1.29"],
        ["CI/CD", "GitHub Actions + ArgoCD"],
        ["Monitoring", "Prometheus + Grafana + Jaeger"],
      ], ["Component", "Technology"]),
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
      children: [new TextRun({ text: "Antigravity Vibe Coding Engine — Developer Guide", ...sp(18, false, C.grey) })]
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "ANTIGRAVITY INC.", ...sp(20, true, C.accent) })] }),
      new Paragraph({ spacing: { before: 0, after: 100 }, children: [new TextRun({ text: "Vibe Coding Engine", ...sp(52, true, C.primary) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Developer Guide & Plugin SDK   |   v1.0", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Introduction"),
      body("The Antigravity Vibe Coding Engine (VCE) is the AI-powered development layer embedded within Jarvis-2025. It transforms spoken or typed natural language into production-quality code, executes it safely, and iterates based on conversational feedback. This guide covers the VCE internals, the Plugin SDK, and best practices for building skills that leverage code generation."),
      ...spacer(1),

      heading1("2. Core Concepts"),
      heading2("2.1 What is Vibe Coding?"),
      body("Vibe coding is the practice of describing your intent at a high level — the 'vibe' — and letting an AI model produce the implementation. Unlike traditional autocomplete (Copilot-style), vibe coding:"),
      bullet("Accepts full natural language descriptions, not just code prefixes"),
      bullet("Executes code and shows live results immediately"),
      bullet("Maintains a conversational loop for refinement ('make it faster', 'add unit tests')"),
      bullet("Understands project context (files, imports, running processes) for grounded generation"),
      ...spacer(1),

      heading2("2.2 VCE Session Lifecycle"),
      body("A VCE session progresses through these states:"),
      bullet("IDLE → listening for code-intent trigger phrase"),
      bullet("CAPTURING → collecting full utterance (up to 60s)"),
      bullet("PARSING → extracting language, framework, constraints via NLU"),
      bullet("GENERATING → streaming code tokens from LLM"),
      bullet("VALIDATING → AST parse + linting"),
      bullet("EXECUTING → sandboxed Docker run (optional, user-confirmed)"),
      bullet("REVIEWING → output displayed; waiting for feedback"),
      bullet("ITERATING → new delta prompt sent with prior code as context"),
      ...spacer(1),

      heading1("3. Quick Start — Your First Vibe Coded Command"),
      blueBox([
        'Speak: "Hey Jarvis, write me a Python function that fetches JSON from a URL',
        '        and returns it as a dict, with retry logic and timeout."',
        "",
        "Jarvis will:",
        "  1. Stream a complete Python function to your screen",
        '  2. Say: "Code ready. Want me to run it?"',
        '  3. On confirmation, execute in a sandbox and show the result',
      ]),
      ...spacer(1),

      heading1("4. Plugin SDK"),
      heading2("4.1 Skill Anatomy"),
      body("A VCE plugin is a Python package with a single required entry point. Here is the minimal structure:"),
      ...spacer(1),
      blueBox([
        "my_skill/",
        "  __init__.py          ← registers the skill",
        "  skill.py             ← SkillBase subclass",
        "  manifest.json        ← metadata, permissions, supported intents",
        "  tests/",
        "    test_skill.py      ← pytest unit tests (required for marketplace)",
      ]),
      ...spacer(1),

      heading2("4.2 manifest.json Schema"),
      body("Every skill must provide a manifest.json describing its capabilities and required permissions:"),
      ...spacer(1),
      blueBox([
        "{",
        '  "name": "my-awesome-skill",',
        '  "version": "1.0.0",',
        '  "author": "Your Name <you@company.com>",',
        '  "description": "What this skill does in one sentence.",',
        '  "intents": ["code_generation", "file_read", "web_search"],',
        '  "permissions": ["filesystem:read", "network:outbound"],',
        '  "jarvis_min_version": "1.0.0",',
        '  "sandbox": true,',
        '  "languages": ["python", "javascript"]',
        "}",
      ]),
      ...spacer(1),

      heading2("4.3 SkillBase API Reference"),
      twoColTable([
        ["on_intent(intent, context)", "Called when the skill's registered intent is detected. Return a SkillResponse."],
        ["on_code_generated(code, language)", "Hook invoked after LLM produces code, before execution."],
        ["on_execution_result(stdout, stderr, exit_code)", "Called after sandbox execution completes."],
        ["speak(text)", "Trigger TTS output from the skill."],
        ["display(html)", "Push arbitrary HTML to the Jarvis UI panel."],
        ["store.get(key) / store.set(key, val)", "Persistent key-value store scoped to the skill."],
        ["llm.complete(prompt, system)", "Make an LLM call within the skill's context."],
        ["sandbox.run(code, language, timeout)", "Execute code in the Jarvis sandbox; returns RunResult."],
      ], ["Method / Property", "Description"]),

      ...spacer(1),
      heading1("5. LLM Prompt Engineering for Code"),
      heading2("5.1 System Prompt Template"),
      body("The VCE uses a carefully crafted system prompt to ensure consistent, high-quality code output. Key principles:"),
      bullet("Always specify language and version in the system prompt context"),
      bullet("Include project context (imports already in scope, style guide)"),
      bullet("Request type annotations and docstrings by default"),
      bullet("Instruct the model to flag assumptions explicitly"),
      bullet("Ask for a brief plain-English summary before the code block"),
      ...spacer(1),

      heading2("5.2 Iterative Refinement Prompts"),
      body("When a user says a follow-up command, the VCE constructs a delta prompt:"),
      blueBox([
        "System: You are an expert {language} developer. The user has this existing code: [CODE]",
        "User: {new_instruction}",
        "Assistant: I'll modify the code to {intent}. Here's the updated version:",
      ]),
      ...spacer(1),

      heading1("6. Sandbox Security Model"),
      heading2("6.1 Execution Environment"),
      twoColTable([
        ["Container", "Docker with --network=none, --read-only filesystem"],
        ["CPU", "0.5 CPU max via --cpus=0.5"],
        ["Memory", "256MB via --memory=256m"],
        ["Timeout", "5 seconds (configurable 1–30s by admin)"],
        ["UID", "Non-root user (uid=1000) inside container"],
        ["Allowed syscalls", "Seccomp profile: compute + file I/O only"],
        ["Volume mounts", "None by default; opt-in with explicit permission"],
      ], ["Parameter", "Value"]),
      ...spacer(1),

      heading2("6.2 Permission Model"),
      body("Skills request permissions in manifest.json. Users (or admins in enterprise mode) approve at install time:"),
      bullet("filesystem:read — can read files in /workspace"),
      bullet("filesystem:write — can write to /workspace/output"),
      bullet("network:outbound — sandbox gets internet access (requires admin approval)"),
      bullet("system:shell — can run arbitrary shell commands (high risk; requires 2-person approval)"),
      ...spacer(1),

      heading1("7. Testing Your Skill"),
      heading2("7.1 Local Testing"),
      blueBox([
        "# Install the Jarvis VCE test harness",
        "pip install jarvis-vce-testkit",
        "",
        "# Run your skill in simulation mode",
        "jarvis-test my_skill/ --intent code_generation \\",
        '  --utterance "write a binary search function in Python"',
        "",
        "# Run the full test suite",
        "pytest my_skill/tests/ -v --cov=my_skill",
      ]),
      ...spacer(1),

      heading2("7.2 Marketplace Submission Checklist"),
      bullet("✓ manifest.json complete and valid"),
      bullet("✓ Unit test coverage ≥ 80%"),
      bullet("✓ No hardcoded credentials or API keys"),
      bullet("✓ Sandbox: true unless specific justification provided"),
      bullet("✓ README.md with install instructions and 3+ example commands"),
      bullet("✓ CHANGELOG.md for v1.0.0"),
      bullet("✓ License file (MIT / Apache 2.0 / Commercial)"),
      bullet("✓ Security review passed (automated Bandit scan clean)"),
      ...spacer(1),

      heading1("8. Example Skills"),
      heading2("8.1 Git Companion Skill"),
      body("Allows: 'Jarvis, commit my changes with a meaningful message' — VCE reads git diff, generates a conventional commit message, and runs git commit."),
      heading2("8.2 SQL Query Builder"),
      body("Allows: 'Jarvis, write a query to find all orders above ₹50,000 from last month' — connects to the configured database schema and generates parameterized SQL."),
      heading2("8.3 Infrastructure-as-Code Generator"),
      body("Allows: 'Jarvis, create a Terraform module for an AWS Lambda with API Gateway' — generates complete HCL with variables, outputs, and a README."),
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
      new Paragraph({ spacing: { before: 0, after: 80 }, children: [new TextRun({ text: "Jarvis-2025: The AI Assistant Platform for the Enterprise", ...sp(26, false, C.dark) })] }),
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Confidential — June 2025   |   For Investor and Partner Review", ...sp(20, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Company Overview"),
      body("Antigravity Inc. is a deep-tech AI company building enterprise-grade AI assistant infrastructure. Our flagship product, Jarvis-2025, combines biometric security, edge AI inference, and a proprietary Vibe Coding Engine to deliver a voice-first productivity platform for knowledge workers."),
      ...spacer(1),
      blueBox([
        "Mission: Eliminate the friction between human intent and software action.",
        "Headquarters: [City, Country]",
        "Founded: 2025",
        "Stage: Seed / Pre-Series A",
        "Team: [X] engineers, [Y] advisors",
      ]),
      ...spacer(1),

      heading1("2. Market Opportunity"),
      heading2("2.1 Total Addressable Market"),
      twoColTable([
        ["Global Enterprise AI Software", "$150B by 2027 (IDC)", "25% CAGR"],
        ["Voice AI for Enterprise", "$28B by 2026 (MarketsandMarkets)", "32% CAGR"],
        ["AI-Assisted Developer Tools", "$12B by 2027 (Gartner)", "40% CAGR"],
        ["Biometric Identity Management", "$8B by 2026 (Grand View Research)", "18% CAGR"],
      ], ["Segment", "Market Size", "Growth"]),
      ...spacer(1),

      heading2("2.2 Competitive Positioning"),
      body("Jarvis-2025 occupies a unique intersection of three high-growth markets:"),
      bullet("Security-first AI (vs. ChatGPT Enterprise — no biometric authentication)"),
      bullet("On-device privacy (vs. Alexa for Business — data stays on premises)"),
      bullet("Developer productivity (vs. GitHub Copilot — voice-native, not IDE-only)"),
      ...spacer(1),

      heading1("3. Product & Revenue Model"),
      heading2("3.1 Pricing Tiers"),
      twoColTable([
        ["Community", "Free", "Single user, local models only, no enterprise features"],
        ["Professional", "$49/user/month", "Cloud LLM access, 10 plugins, email support"],
        ["Enterprise", "$149/user/month (min 50 seats)", "SSO, RBAC, audit logs, SLA, dedicated CSM"],
        ["On-Premise", "Custom contract", "Air-gapped deployment, custom models, 24/7 support"],
      ], ["Tier", "Price", "Includes"]),
      ...spacer(1),

      heading2("3.2 Revenue Projections"),
      twoColTable([
        ["Year 1 (2025)", "5 enterprise pilots × $50K ARR each", "$250K ARR"],
        ["Year 2 (2026)", "50 SMB + 10 enterprise accounts", "$3.2M ARR"],
        ["Year 3 (2027)", "200 SMB + 40 enterprise + marketplace", "$15M ARR"],
      ], ["Period", "Driver", "Projected ARR"]),
      ...spacer(1),

      heading1("4. Go-to-Market Strategy"),
      heading2("4.1 Phase 1 — Developer-Led Growth (Q3–Q4 2025)"),
      bullet("Open-source Jarvis Community edition on GitHub (already live)"),
      bullet("Technical content: YouTube demos, DevRel blog posts, conference talks"),
      bullet("Discord community; 1,000 active developers as brand ambassadors"),
      bullet("GitHub Marketplace integration for Vibe Coding skill discovery"),

      heading2("4.2 Phase 2 — Enterprise Sales Motion (Q1–Q2 2026)"),
      bullet("Inside sales team (2 AEs); focus on IT/security-led buying centers"),
      bullet("Partner channel: system integrators (Accenture, Infosys, TCS) for Indian enterprise market"),
      bullet("Proof-of-concept program: 30-day free pilot with success metrics pre-agreed"),
      bullet("Analyst briefings: Gartner, Forrester, IDC for Magic Quadrant positioning"),

      ...spacer(1),
      heading1("5. Team"),
      body("(Placeholder — to be completed with actual team bios)"),
      twoColTable([
        ["CEO / Co-Founder", "Vision, fundraising, enterprise sales", "Ex-[Company], [X] years AI/enterprise SaaS"],
        ["CTO / Co-Founder", "Architecture, engineering leadership", "Ex-[Company], built ML systems at scale"],
        ["Head of Security", "Biometric systems, compliance", "Ex-CISO, ISO 27001 lead auditor"],
        ["Head of Product", "Roadmap, design, customer research", "Ex-[Product Co], shipped 0→1 enterprise products"],
      ], ["Role", "Responsibility", "Background"]),
      ...spacer(1),

      heading1("6. Funding Ask"),
      blueBox([
        "Seeking: $3M Seed Round",
        "Use of funds:",
        "  40% — Engineering (6 senior engineers, 18-month runway)",
        "  25% — Sales & Marketing (2 AEs, content, events)",
        "  20% — Infrastructure & Security (SOC 2 audit, compliance tooling)",
        "  10% — R&D (Vibe Coding Engine, next-gen biometrics)",
        "   5% — Legal & Operations",
      ]),
      ...spacer(1),

      heading1("7. Risk Factors"),
      twoColTable([
        ["LLM API dependency", "Build local model fallback; diversify providers"],
        ["Biometric regulation changes", "GDPR/PDPA compliance architecture; consent-first design"],
        ["Big Tech competition (Microsoft, Google)", "Speed, vertical focus, open-source community moat"],
        ["Talent acquisition in AI", "Remote-first, equity-heavy compensation, open-source reputation"],
        ["Hardware requirements for local inference", "Progressive enhancement; cloud fallback for low-spec machines"],
      ], ["Risk", "Mitigation"]),

      ...spacer(1),
      heading1("8. Appendix — Key Metrics Dashboard"),
      body("To be tracked monthly and shared with investors via a real-time dashboard:"),
      bullet("MRR / ARR growth rate"),
      bullet("Net Revenue Retention (NRR) — target > 120%"),
      bullet("Customer Acquisition Cost (CAC) vs. Lifetime Value (LTV) — target LTV:CAC > 5×"),
      bullet("Time-to-Value (TTV) — from signup to first successful command"),
      bullet("GitHub stars and fork velocity (community health proxy)"),
      bullet("NPS score across tiers"),
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
      new Paragraph({ spacing: { before: 0, after: 400 }, children: [new TextRun({ text: "Jarvis-2025   |   IT Administrator Reference   |   v1.0", ...sp(24, false, C.grey), italic: true })] }),
      divider(),
      ...spacer(1),

      heading1("1. Prerequisites"),
      heading2("1.1 Hardware Requirements"),
      twoColTable([
        ["CPU", "Minimum: Intel i5 (8th gen) / AMD Ryzen 5   |   Recommended: i7/Ryzen 7 or better"],
        ["RAM", "Minimum: 8GB   |   Recommended: 16GB+ (for local LLM)"],
        ["GPU", "Optional: NVIDIA GTX 1060+ for Whisper acceleration (CUDA 11+)"],
        ["Storage", "Minimum: 20GB free   |   Recommended: 50GB SSD for model storage"],
        ["Camera", "720p minimum for face recognition (1080p recommended)"],
        ["Microphone", "USB or headset; omnidirectional far-field array preferred"],
        ["Network", "100Mbps for cloud LLM fallback; offline mode available"],
      ], ["Component", "Specification"]),
      ...spacer(1),

      heading2("1.2 Software Requirements"),
      bullet("OS: Windows 10/11 (64-bit), Ubuntu 20.04+, macOS 12+"),
      bullet("Python: 3.11+ (3.12 recommended)"),
      bullet("Node.js: 18 LTS+ (for UI build tooling)"),
      bullet("Docker Desktop: 4.x+ (for sandboxed code execution)"),
      bullet("Git: 2.40+"),
      ...spacer(1),

      heading1("2. Installation"),
      heading2("2.1 Community / Developer Install"),
      blueBox([
        "# 1. Clone the repository",
        "git clone https://github.com/kriss2012/Jarvis-2025.git",
        "cd Jarvis-2025",
        "",
        "# 2. Create virtual environment",
        "python -m venv envJarvis",
        "# Windows:",
        ".\\envJarvis\\Scripts\\Activate.ps1",
        "# Linux/Mac:",
        "source envJarvis/bin/activate",
        "",
        "# 3. Install dependencies",
        "pip install --upgrade pip",
        "pip install -r requirements.txt",
        "",
        "# 4. Initialize database",
        "python create_sample_db.py",
        "",
        "# 5. Launch",
        "python run.py",
      ]),
      ...spacer(1),

      heading2("2.2 Enterprise Docker Deployment"),
      blueBox([
        "# Pull enterprise image (requires license key)",
        "docker pull registry.antigravity.ai/jarvis-enterprise:latest",
        "",
        "# Configure environment",
        "cp .env.enterprise.example .env",
        "# Edit .env with your SSO, database, and LLM API credentials",
        "",
        "# Start all services",
        "docker-compose -f docker-compose.enterprise.yml up -d",
        "",
        "# Verify health",
        "curl http://localhost:8000/health",
      ]),
      ...spacer(1),

      heading2("2.3 Kubernetes (Helm) Deployment"),
      blueBox([
        "helm repo add antigravity https://charts.antigravity.ai",
        "helm repo update",
        "",
        "helm install jarvis antigravity/jarvis-enterprise \\",
        "  --namespace jarvis \\",
        "  --create-namespace \\",
        "  --set auth.sso.enabled=true \\",
        "  --set auth.sso.provider=okta \\",
        "  --set llm.backend=claude \\",
        "  --set storage.class=standard",
      ]),
      ...spacer(1),

      heading1("3. Configuration Reference"),
      heading2("3.1 Core Environment Variables"),
      twoColTable([
        ["JARVIS_ENV", "development | staging | production"],
        ["JARVIS_SECRET_KEY", "32-byte random secret for JWT signing"],
        ["DATABASE_URL", "postgresql://user:pass@host:5432/jarvis"],
        ["REDIS_URL", "redis://host:6379/0"],
        ["LLM_BACKEND", "local | claude | openai | huggingface"],
        ["ANTHROPIC_API_KEY", "sk-ant-... (for Claude backend)"],
        ["FACE_CONFIDENCE_THRESHOLD", "0.0–1.0, default 0.6"],
        ["SSO_PROVIDER", "okta | azure-ad | google | saml"],
        ["SSO_CLIENT_ID / SSO_CLIENT_SECRET", "OAuth2 credentials from your IdP"],
        ["AUDIT_LOG_RETENTION_DAYS", "Default 2555 (7 years for SOC 2)"],
      ], ["Variable", "Description"]),
      ...spacer(1),

      heading1("4. User Enrollment — Face Recognition"),
      heading2("4.1 Admin Enrollment Process"),
      bullet("Step 1: Admin logs into admin dashboard at http://jarvis-admin:8080"),
      bullet("Step 2: Navigate to Users → Add User → complete profile form"),
      bullet("Step 3: Click 'Enroll Biometrics' — camera activates"),
      bullet("Step 4: User looks straight ahead; system captures 5 frames from different angles"),
      bullet("Step 5: Embeddings computed and stored encrypted; enrollment complete"),
      bullet("Step 6: User receives welcome email with quick-start guide"),
      ...spacer(1),

      heading2("4.2 Bulk Enrollment via CSV"),
      blueBox([
        "# Prepare CSV: name,email,department,photo_path",
        "python manage.py bulk_enroll --csv users.csv --photos ./photos/",
        "",
        "# Photos must be: JPEG/PNG, 200x200px minimum, single face, good lighting",
        "# System will reject photos failing quality checks and log them to enrollment_errors.csv",
      ]),
      ...spacer(1),

      heading1("5. RBAC Configuration"),
      heading2("5.1 Default Roles"),
      twoColTable([
        ["super_admin", "Full system access, can manage all users and settings"],
        ["admin", "Manage users in own department, approve plugins, view audit logs"],
        ["power_user", "All features including Vibe Coding Engine and file access"],
        ["standard_user", "Voice commands, LLM chat, pre-approved skill plugins only"],
        ["read_only", "View-only access to dashboards; no command execution"],
      ], ["Role", "Permissions"]),
      ...spacer(1),

      heading1("6. Troubleshooting"),
      heading2("6.1 Common Issues"),
      twoColTable([
        ["NumPy version conflict", "pip install 'numpy<2.0'"],
        ["PyAudio installation fails (Windows)", "pipwin install pyaudio"],
        ["cv2.face module not found", "pip install opencv-contrib-python"],
        ["Camera not detected", "Ensure camera not in use by another app; check permissions"],
        ["Face not recognized", "Improve lighting; re-enroll with better photos; lower threshold to 0.5"],
        ["High CPU on hotword detection", "Reduce sample_rate in config; use GPU acceleration"],
        ["LLM timeout errors", "Increase LLM_TIMEOUT_SECONDS; switch to smaller local model"],
      ], ["Issue", "Resolution"]),
      ...spacer(1),

      heading1("7. Compliance & Security Checklist"),
      bullet("☐ All biometric data encrypted at rest (AES-256)"),
      bullet("☐ TLS 1.3 enabled for all network communications"),
      bullet("☐ Audit logging enabled and retention policy configured"),
      bullet("☐ Backup and disaster recovery tested (RPO < 1h, RTO < 4h)"),
      bullet("☐ Penetration test conducted before production go-live"),
      bullet("☐ Employee consent forms collected for biometric enrollment"),
      bullet("☐ Data Processing Agreement (DPA) signed with Antigravity Inc."),
      bullet("☐ Incident response plan documented and team trained"),
      bullet("☐ Regular security patches scheduled (monthly)"),
      ...spacer(1),

      heading1("8. Support & SLA"),
      twoColTable([
        ["Community", "GitHub Issues (best effort, no SLA)"],
        ["Professional", "Email support, 48h response time"],
        ["Enterprise", "Slack/Teams dedicated channel, 4h response, 24/7 for P1 incidents"],
        ["On-Premise", "24/7 hotline, 1h P1 SLA, quarterly business reviews"],
      ], ["Tier", "Support Level"]),
      ...spacer(1),
      body("Support portal: support.antigravity.ai   |   Documentation: docs.antigravity.ai   |   Status: status.antigravity.ai", { color: C.grey, italic: true }),
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
