/**
 * CDSCO INTEL - CONVERSATIONAL REGULATORY SEARCH ENGINE (FRONTEND CONTROLLER)
 * Aesthetic: Perplexity & ChatGPT Dark Theme + Claude Chat Stream
 */

// Clean Vector SVG Icons (Replacing cartoon emojis for professional regulatory grade UI)
const ICONS = {
  shield: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>`,
  pill: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/></svg>`,
  dna: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="M17 6l-2.5-2.5"/><path d="M14 8l-1-1"/><path d="M7 18l2.5 2.5"/><path d="M3.5 14.5l.5.5"/><path d="M20 9.5l.5.5"/><path d="M6.5 12.5l1 1"/><path d="M16.5 10.5l1 1"/><path d="M10 16l-1-1"/></svg>`,
  combo: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31L4.47 19.34A2 2 0 0 0 6.2 22h11.6a2 2 0 0 0 1.73-2.66L14 9.31V2"/></svg>`,
  layers: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`,
  slides: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>`,
  csv: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>`,
  info: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
  plus: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
  search: `<svg class="icon-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
  tag: `<svg class="icon-svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>`,
  bolt: `<svg class="latency-icon" width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
  building: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect><line x1="9" y1="22" x2="9" y2="22.01"></line><line x1="15" y1="22" x2="15" y2="22.01"></line></svg>`,
  alert: `<svg class="icon-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`
};

// Application State
const appState = {
  mode: "home", // "home" | "chat"
  turns: [],
  currentResults: [],
  activeContext: {}, // { therapy_area, year, company, product_category, regulatory_type }
  clientId: getOrCreateClientId(),
  sessionQueries: 0
};

// DOM References - Navigation & Common
const navBrandBtn = document.getElementById("navBrandBtn");
const navMiddleControls = document.getElementById("navMiddleControls");
const compactSearchInput = document.getElementById("compactSearchInput");
const compactSearchBtn = document.getElementById("compactSearchBtn");
const totalRecordsCount = document.getElementById("totalRecordsCount");
const newChatBtn = document.getElementById("newChatBtn");
const toastNotification = document.getElementById("toastNotification");
const toastMessage = document.getElementById("toastMessage");

// DOM References - Home Hero
const homeHeroSection = document.getElementById("homeHeroSection");
const heroSearchInput = document.getElementById("heroSearchInput");
const heroSubmitBtn = document.getElementById("heroSubmitBtn");
const heroClearBtn = document.getElementById("heroClearBtn");
const suggestPillsRow = document.getElementById("suggestPillsRow");
const quickTaLinks = document.getElementById("quickTaLinks");

// DOM References - Conversation Section
const conversationSection = document.getElementById("conversationSection");
const chatContainer = document.getElementById("chatContainer");
const chatThread = document.getElementById("chatThread");
const chatBottomDock = document.getElementById("chatBottomDock");
const chatFollowupChips = document.getElementById("chatFollowupChips");
const bottomChatInput = document.getElementById("bottomChatInput");
const bottomSendBtn = document.getElementById("bottomSendBtn");

// DOM References - Modal
const detailModalBackdrop = document.getElementById("detailModalBackdrop");
const modalCloseBtn = document.getElementById("modalCloseBtn");
const modalDrugName = document.getElementById("modalDrugName");
const modalCompany = document.getElementById("modalCompany");
const modalDate = document.getElementById("modalDate");
const modalTherapyTag = document.getElementById("modalTherapyTag");
const modalCatTag = document.getElementById("modalCatTag");
const modalIndication = document.getElementById("modalIndication");
const modalComposition = document.getElementById("modalComposition");
const modalAddressContainer = document.getElementById("modalAddressContainer");
const modalAddress = document.getElementById("modalAddress");
const modalFormId = document.getElementById("modalFormId");
const modalGovPortalBtn = document.getElementById("modalGovPortalBtn");
let currentModalDrug = null;

// Date Parsing Helper for CDSCO Dates (e.g. "16-MAR-2022")
const MONTH_MAP = {
  JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5,
  JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11
};

function parseCdscoDate(dStr, dIso) {
  if (dIso && /^\d{4}-\d{2}-\d{2}$/.test(String(dIso).trim())) {
    return new Date(String(dIso).trim()).getTime();
  }
  if (!dStr) return 0;
  const s = String(dStr).trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    return new Date(s).getTime();
  }
  const parts = s.split("-");
  if (parts.length === 3) {
    const day = parseInt(parts[0], 10) || 1;
    const mStr = parts[1].toUpperCase();
    const month = MONTH_MAP[mStr] !== undefined ? MONTH_MAP[mStr] : 0;
    const year = parseInt(parts[2], 10) || 2020;
    return new Date(year, month, day).getTime();
  }
  return 0;
}

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
  fetchInitialMetadata();
  fetchDynamicSuggestions();
  setupEvents();
  logTelemetry("page_view");
});

// Telemetry Client ID
function getOrCreateClientId() {
  let cid = localStorage.getItem("cdsco_distinct_id");
  if (!cid) {
    cid = "anon_" + Math.random().toString(36).substring(2, 11) + "_" + Date.now().toString(36);
    localStorage.setItem("cdsco_distinct_id", cid);
  }
  return cid;
}

function logTelemetry(eventName, properties = {}) {
  const payload = {
    event: eventName,
    distinct_id: appState.clientId,
    timestamp: new Date().toISOString(),
    session_queries: appState.sessionQueries,
    properties: properties
  };
  try {
    const logs = JSON.parse(localStorage.getItem("cdsco_telemetry_logs") || "[]");
    logs.push(payload);
    if (logs.length > 200) logs.shift();
    localStorage.setItem("cdsco_telemetry_logs", JSON.stringify(logs));
  } catch (e) {}

  // Forward to backend telemetry database
  try {
    fetch("/api/telemetry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true
    }).catch(() => {});
  } catch (e) {}

  if (window.posthog) {
    window.posthog.capture(eventName, properties);
  }
}

// Fetch Initial Stats
async function fetchInitialMetadata() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();
    if (data.total_approvals && totalRecordsCount) {
      totalRecordsCount.textContent = Number(data.total_approvals).toLocaleString();
    }
  } catch (err) {
    console.error("Failed to load initial stats:", err);
  }
}

// Fetch Dynamic Suggestions
async function fetchDynamicSuggestions() {
  try {
    const res = await fetch("/api/suggestions");
    const data = await res.json();
    if (data.suggestions && suggestPillsRow) {
      suggestPillsRow.innerHTML = data.suggestions.map(s => {
        const iconSvg = ICONS[s.icon] || (s.icon && s.icon.includes('<svg') ? s.icon : ICONS.search);
        return `
          <button class="suggest-pill" data-query="${escapeHtml(s.query)}">
            <span class="pill-icon-svg">${iconSvg}</span>
            <span>${escapeHtml(s.label)}</span>
          </button>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("Failed to load dynamic suggestions:", err);
  }
}

// Event Listeners Setup
function setupEvents() {
  // Hero Search Input
  heroSearchInput.addEventListener("input", () => {
    heroClearBtn.style.display = heroSearchInput.value ? "inline-block" : "none";
  });

  heroClearBtn.addEventListener("click", () => {
    heroSearchInput.value = "";
    heroClearBtn.style.display = "none";
    heroSearchInput.focus();
  });

  heroSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      executeSearch(heroSearchInput.value);
    }
  });

  heroSubmitBtn.addEventListener("click", () => {
    executeSearch(heroSearchInput.value);
  });

  // Suggestion Pills
  suggestPillsRow.addEventListener("click", (e) => {
    const pill = e.target.closest(".suggest-pill");
    if (pill) {
      const q = pill.getAttribute("data-query");
      if (q) executeSearch(q);
    }
  });

  // Guide Chips Auto-Fill (Fill search bar without executing)
  const guideBanner = document.getElementById("queryGuideBanner");
  if (guideBanner) {
    guideBanner.addEventListener("click", (e) => {
      const chip = e.target.closest(".guide-chip");
      if (chip) {
        const q = chip.getAttribute("data-query");
        if (q) {
          heroSearchInput.value = q;
          heroClearBtn.style.display = "inline-block";
          heroSearchInput.focus();
        }
      }
    });
  }

  // Quick Therapy Area Pills
  if (quickTaLinks) {
    quickTaLinks.addEventListener("click", (e) => {
      const pill = e.target.closest(".mini-ta-pill");
      if (pill) {
        const q = pill.getAttribute("data-query");
        if (q) executeSearch(q);
      }
    });
  }

  // Feature Card Clicks
  const cardTA = document.getElementById("cardTherapyAreas");
  if (cardTA) cardTA.addEventListener("click", () => executeSearch("Oncology 2025"));

  const cardZH = document.getElementById("cardZeroHallucination");
  if (cardZH) cardZH.addEventListener("click", () => executeSearch("When was Rituximab approved in India?"));

  const cardSR = document.getElementById("cardSlideReady");
  if (cardSR) cardSR.addEventListener("click", () => executeSearch("Innovator launches in 2024"));

  // Compact Search Bar in Header
  compactSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      executeSearch(compactSearchInput.value);
      compactSearchInput.value = "";
    }
  });

  compactSearchBtn.addEventListener("click", () => {
    executeSearch(compactSearchInput.value);
    compactSearchInput.value = "";
  });

  // Bottom Sticky Chat Input (if present)
  if (bottomChatInput) {
    bottomChatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const val = bottomChatInput.value.trim();
        if (val) {
          executeSearch(val);
          bottomChatInput.value = "";
          bottomChatInput.style.height = "auto";
        }
      }
    });

    bottomChatInput.addEventListener("input", () => {
      bottomChatInput.style.height = "auto";
      bottomChatInput.style.height = Math.min(bottomChatInput.scrollHeight, 120) + "px";
    });
  }

  if (bottomSendBtn && bottomChatInput) {
    bottomSendBtn.addEventListener("click", () => {
      const val = bottomChatInput.value.trim();
      if (val) {
        executeSearch(val);
        bottomChatInput.value = "";
        bottomChatInput.style.height = "auto";
      }
    });
  }



  // Return to Home via Brand Icon
  if (navBrandBtn) navBrandBtn.addEventListener("click", switchToHomeView);

  // New Chat Button
  if (newChatBtn) newChatBtn.addEventListener("click", switchToHomeView);

  // Analytics Dashboard Trigger
  const navAnalyticsBtn = document.getElementById("navAnalyticsBtn");
  if (navAnalyticsBtn) {
    navAnalyticsBtn.addEventListener("click", openAnalyticsModal);
  }

  // Regulatory Guide Modal Triggers
  const openFullGuideLink = document.getElementById("openFullGuideLink");
  if (openFullGuideLink) {
    openFullGuideLink.addEventListener("click", openGuideModal);
  }

  // Analytics Refresh Button
  const analyticsRefreshBtn = document.getElementById("analyticsRefreshBtn");
  if (analyticsRefreshBtn) {
    analyticsRefreshBtn.addEventListener("click", () => fetchAnalytics(true));
  }

  // Modal Close Listeners
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeModal();
    });
  }
  if (detailModalBackdrop) {
    detailModalBackdrop.addEventListener("click", (e) => {
      if (e.target === detailModalBackdrop) closeModal();
    });
  }
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModal();
      closeAnalyticsModal();
      closeGuideModal();
    }
  });

  // Modal Government Verification Action (Option A: Direct redirect to official portal with auto-copied Form ID)
  if (modalGovPortalBtn) {
    modalGovPortalBtn.addEventListener("click", () => {
      if (!currentModalDrug) return;
      const formId = currentModalDrug.form_id ? String(currentModalDrug.form_id) : "";
      const copyVal = formId || (currentModalDrug.clean_molecule || currentModalDrug.drug_name || "").trim();
      
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(copyVal).then(() => {
          showToast(`Copied Form ID #${copyVal} to clipboard! Paste (Ctrl+V) into SUGAM Search.`);
        }).catch(() => {
          showToast(`Form ID: #${copyVal}. Paste into SUGAM Search.`);
        });
      } else {
        showToast(`Form ID: #${copyVal}. Paste into SUGAM Search.`);
      }
      
      window.open("https://cdscoonline.gov.in/CDSCO/cdscoDrugs", "_blank", "noopener,noreferrer");
      logTelemetry("gov_portal_opened", { form_id: formId, drug_name: currentModalDrug.drug_name });
    });
  }
}

// Switch UI Modes
function switchToChatView() {
  appState.mode = "chat";
  homeHeroSection.style.display = "none";
  conversationSection.style.display = "flex";
  navMiddleControls.style.display = "block";
}

function switchToHomeView() {
  appState.mode = "home";
  appState.activeContext = {};
  conversationSection.style.display = "none";
  navMiddleControls.style.display = "none";
  homeHeroSection.style.display = "flex";
  chatThread.innerHTML = "";
  appState.turns = [];
  heroSearchInput.value = "";
  heroClearBtn.style.display = "none";
  if (chatFollowupChips) chatFollowupChips.innerHTML = "";
  heroSearchInput.focus();
}

// Smoothly scroll viewport to conversation turn (leaving breathing room below sticky top nav)
function scrollToActiveTurn(targetEl, offsetTop = 75) {
  if (!targetEl) return;
  requestAnimationFrame(() => {
    setTimeout(() => {
      const rect = targetEl.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const targetY = scrollTop + rect.top - offsetTop;
      window.scrollTo({
        top: Math.max(0, targetY),
        behavior: "smooth"
      });
    }, 30);
  });
}

// Execute Search & Append Conversation Turn
async function executeSearch(query) {
  const cleanQ = query.trim();
  if (!cleanQ) return;

  appState.sessionQueries++;
  switchToChatView();

  // Create Conversation Turn ID
  const turnId = "turn_" + Date.now();

  // Render User Message immediately
  appendUserMessage(cleanQ);

  // Render Assistant Loading Bubble
  const assistantMsgEl = appendAssistantLoading(turnId);

  // Instantly scroll down so the generating space and user query are in prominent view
  scrollToActiveTurn(chatThread._activeTurnEl || assistantMsgEl, 75);

  // Log Telemetry
  logTelemetry("query_executed", { query: cleanQ, turn_count: appState.turns.length + 1 });

  try {
    const params = new URLSearchParams({ 
      q: cleanQ, 
      limit: 2500,
      client_id: appState.clientId 
    });
    const res = await fetch(`/api/search?${params.toString()}`);
    const data = await res.json();

    appState.currentResults = data.results || [];
    
    // Replace loading with final synthesized response
    renderAssistantResponse(assistantMsgEl, cleanQ, data);

    // Keep the conversation turn framed comfortably below top nav once results render
    setTimeout(() => {
      scrollToActiveTurn(chatThread._activeTurnEl || assistantMsgEl, 75);
    }, 80);

  } catch (err) {
    console.error("Search query failed:", err);
    assistantMsgEl.querySelector(".assistant-content").innerHTML = `
      <div class="ai-synthesis-text" style="border-left-color: #ef4444;">
        ${ICONS.alert} Error querying CDSCO regulatory database. Please try again.
      </div>
    `;
  }
}

// Append User Chat Bubble
function appendUserMessage(query) {
  const turnWrapper = document.createElement("div");
  turnWrapper.className = "chat-turn";

  const userRow = document.createElement("div");
  userRow.className = "user-msg-row";
  userRow.innerHTML = `
    <div class="user-msg-bubble">${escapeHtml(query)}</div>
  `;

  turnWrapper.appendChild(userRow);
  chatThread.appendChild(turnWrapper);
  chatThread._activeTurnEl = turnWrapper;
}

// Append Assistant Loading Skeleton
function appendAssistantLoading(turnId) {
  const turnWrapper = chatThread._activeTurnEl || chatThread;

  const assistantBlock = document.createElement("div");
  assistantBlock.className = "assistant-msg-block";
  assistantBlock.id = turnId;

  assistantBlock.innerHTML = `
    <div class="assistant-avatar">${ICONS.shield}</div>
    <div class="assistant-content">
      <div class="assistant-header">
        <span class="assistant-name">CDSCO Intel</span>
        <span class="assistant-tag synthesizing-pulse">Synthesizing</span>
        <span class="assistant-latency">${ICONS.bolt} Querying 5,139 records...</span>
      </div>
      <div class="ai-synthesis-text" style="opacity: 0.85;">
        <div style="margin-bottom: 6px;">Searching official SUGAM regulatory records across 24 clinical therapy areas...</div>
        <div class="skeleton-shimmer-wrap">
          <div class="skeleton-shimmer-line skeleton-w-full"></div>
          <div class="skeleton-shimmer-line skeleton-w-85"></div>
          <div class="skeleton-shimmer-line skeleton-w-65"></div>
        </div>
      </div>
    </div>
  `;

  turnWrapper.appendChild(assistantBlock);
  return assistantBlock;
}



// Group rows that belong to the same Form ID or identical product approval
function groupApprovals(rows) {
  const groups = new Map();
  rows.forEach(r => {
    const fid = r.form_id;
    const key = (fid && fid !== 0) 
      ? `form_${fid}` 
      : `${(r.clean_molecule || r.drug_name).toLowerCase()}_${(r.company_std || r.company).toLowerCase()}_${r.approval_date}_${(r.indication || '').substring(0, 30).toLowerCase()}`;

    if (!groups.has(key)) {
      groups.set(key, {
        ...r,
        presentation_count: 1,
        all_compositions: [r.composition || r.dosage].filter(Boolean),
        all_rows: [r]
      });
    } else {
      const existing = groups.get(key);
      existing.presentation_count++;
      const comp = r.composition || r.dosage;
      if (comp && !existing.all_compositions.includes(comp)) {
        existing.all_compositions.push(comp);
      }
      existing.all_rows.push(r);
    }
  });
  return Array.from(groups.values());
}


// Render Full Assistant Response (AI Summary + Molecule Intel + Artifact Table)
function renderAssistantResponse(blockEl, query, data) {
  const content = blockEl.querySelector(".assistant-content");
  const total = data.total_matches || 0;
  const latency = data.latency_ms || 2.5;
  const results = data.results || [];
  const aiSummary = data.ai_summary || `Found ${total} verified CDSCO approvals.`;
  const hist = data.historical_web_context;
  const intel = data.molecule_intel;

  const formattedSummary = formatMarkdown(aiSummary);

  let html = `
    <div class="assistant-header">
      <span class="assistant-name">CDSCO Intel</span>
      <span class="assistant-tag">Gemini 3.5 Flash-Lite + SUGAM</span>
      <span class="assistant-latency">${ICONS.bolt} ${latency} ms</span>
    </div>

    <div class="ai-synthesis-text">
      ${formattedSummary}
    </div>
  `;

  // 1. Dynamic Molecule Intelligence Banner (if active ingredient detected)
  if (intel && intel.total_filings > 0) {
    const brandsList = (intel.commercial_brands && intel.commercial_brands.length > 0)
      ? intel.commercial_brands.map(b => `<span class="brand-chip">${ICONS.tag} <strong>${escapeHtml(b.brand)}</strong> (${escapeHtml(b.company)})</span>`).join(" ")
      : '<span style="color: var(--text-muted); font-size: 12px;">No commercial trade names on file</span>';

    const monoStat = intel.mono_count > 0
      ? `<span class="stat-pill"><strong style="color: #34d399;">${intel.mono_count}</strong> Monotherapy</span>`
      : '';
    const fdcStat = intel.fdc_count > 0
      ? `<span class="stat-pill"><strong style="color: #fbbf24;">${intel.fdc_count}</strong> Combinations</span>`
      : '';

    html += `
      <div class="molecule-intel-card">
        <div class="intel-header">
          <div class="intel-title-wrap">
            <span class="intel-icon">${ICONS.dna}</span>
            <div>
              <h4 class="intel-title">${escapeHtml(intel.molecule)} <span class="intel-type-tag">${escapeHtml(intel.molecule_type)}</span></h4>
              <span class="intel-sub">Clinical Competitive &amp; Regulatory Profile</span>
            </div>
          </div>
          <div class="intel-stats-summary">
            ${monoStat}
            ${fdcStat}
          </div>
        </div>

        <div class="intel-details-grid">
          <div class="intel-item">
            <span class="item-label">Earliest SUGAM Clearance</span>
            <span class="item-val">${escapeHtml(intel.first_approval_date || "Pre-2018")}</span>
            <span class="item-sublabel">2018–2026 Portal Filing</span>
          </div>
          <div class="intel-item">
            <span class="item-label">Earliest SUGAM Applicant</span>
            <span class="item-val bold">${escapeHtml(intel.earliest_sugam_applicant || intel.first_applicant || "Registered Firm")}</span>
            <span class="item-sublabel">First digitized portal filing</span>
          </div>
          <div class="intel-item">
            <span class="item-label">Total Verified Filings</span>
            <span class="item-val bold">${intel.total_filings} Records</span>
            <span class="item-sublabel">Official CDSCO clearances</span>
          </div>
        </div>

        ${(intel.commercial_brands && intel.commercial_brands.length > 0) ? `
        <div class="intel-brands-section">
          <span class="item-label">Approved Commercial Brands in India:</span>
          <div class="brands-chips-row">${brandsList}</div>
        </div>
        ` : ''}
      </div>
    `;
  }

  // 2b. Real-World Market & Originator Intelligence (Exclusive Dedicated Card for Specific Molecules)
  if (data.market_intelligence && data.market_intelligence.global_innovator) {
    const mi = data.market_intelligence;
    html += `
      <div class="market-intel-card">
        <div class="market-intel-header">
          <div class="market-intel-title-group">
            <span class="market-intel-icon">${ICONS.shield}</span>
            <div>
              <h4 class="market-intel-title">Real-World Market &amp; Originator Intelligence</h4>
              <span class="market-intel-subtitle">AI Web &amp; Clinical Pharma Market Dossier</span>
            </div>
          </div>
          <span class="market-intel-badge">Executive Market Intel</span>
        </div>

        <div class="market-intel-body">
          <div class="market-intel-field highlight-field">
            <span class="field-icon">${ICONS.building}</span>
            <div class="field-content">
              <span class="field-label">Global Innovator &amp; Reference Brand</span>
              <span class="field-value highlight-text">${escapeHtml(mi.global_innovator)}</span>
            </div>
          </div>

          <div class="market-intel-grid">
            <div class="market-intel-field">
              <span class="field-icon">${ICONS.building}</span>
              <div class="field-content">
                <span class="field-label">Real-World Indian Clinical Availability</span>
                <span class="field-value">${escapeHtml(mi.indian_clinical_availability || "")}</span>
              </div>
            </div>

            <div class="market-intel-field">
              <span class="field-icon">${ICONS.shield}</span>
              <div class="field-content">
                <span class="field-label">Domestic Biosimilar / Generic Reality</span>
                <span class="field-value">${escapeHtml(mi.domestic_landscape || "")}</span>
              </div>
            </div>
          </div>

          ${mi.executive_takeaway ? `
          <div class="market-intel-takeaway">
            <span class="takeaway-icon">${ICONS.info}</span>
            <span class="takeaway-text"><strong>Executive Takeaway:</strong> ${escapeHtml(mi.executive_takeaway)}</span>
          </div>
          ` : ''}

          <div class="market-disclaimer-box">
            <div class="disclaimer-header">
              <span class="disclaimer-icon">${ICONS.alert}</span>
              <span>Commercial &amp; Regulatory Intelligence Disclaimer</span>
            </div>
            <p class="disclaimer-text">
              Pre-2018 launch history, global originator lineage, and commercial market availability are synthesized via AI Market &amp; Web Intelligence. Official regulatory clearance dates, Form IDs, and permitted presentations above reflect strictly records digitized on the official CDSCO SUGAM portal (2018–2026).
            </p>
          </div>
        </div>
      </div>
    `;
  }

  // 3. Data Artifact Card (Table with Multi-Filters, Distinct Approvals Toggle & Date Sorting)
  if (results.length > 0) {
    const isAsc = Boolean(data && (data.sort_by === "date_asc" || data.is_historical));
    const distinctList = groupApprovals(results);
    if (isAsc) {
      distinctList.sort((a, b) => parseCdscoDate(a.approval_date, a.approval_date_iso) - parseCdscoDate(b.approval_date, b.approval_date_iso));
    }

    // Compute unique filter values
    const uniqueComps = [...new Set(results.map(r => r.company_std || r.company).filter(Boolean))].sort();
    const uniqueTAs = [...new Set(results.flatMap(r => (r.therapy_areas && r.therapy_areas.length ? r.therapy_areas : (r.therapy_area || 'Other').split(',').map(s => s.trim()))))].filter(Boolean).sort();
    const uniqueYears = [...new Set(results.map(r => r.approval_year).filter(Boolean))].sort((a, b) => b - a);

    const monoCountAll = results.filter(r => r.formulation_type === "Monotherapy").length;
    const combCountAll = results.filter(r => r.formulation_type === "Combination (FDC)").length;
    const monoCountDistinct = distinctList.filter(r => r.formulation_type === "Monotherapy").length;
    const combCountDistinct = distinctList.filter(r => r.formulation_type === "Combination (FDC)").length;
    const hasMonoAndComb = ((monoCountAll > 0 && combCountAll > 0) || (monoCountDistinct > 0 && combCountDistinct > 0));

    const compOptions = uniqueComps.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');
    const taOptions = uniqueTAs.map(t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join('');
    const yearOptions = uniqueYears.map(y => `<option value="${y}">${y}</option>`).join('');

    const showFilters = results.length > 2;

    html += `
      <div class="artifact-card">
        <div class="artifact-toolbar">
          <div class="artifact-title-group">
            <span class="artifact-title">CDSCO Verified Approvals</span>
            <span class="artifact-count-tag"><span class="filter-count">${distinctList.length}</span> Clearances</span>
          </div>

          <div class="view-mode-toggle-wrap">
            <button class="view-toggle-btn active" data-view="distinct" title="Group duplicate strength rows into distinct product clearances">
              Distinct (${distinctList.length})
            </button>
            <button class="view-toggle-btn" data-view="all" title="Show every individual strength row recorded by CDSCO">
              All Filings (${results.length})
            </button>
          </div>

          ${hasMonoAndComb ? `
          <div class="quick-mode-chips">
            <button class="quick-mode-chip active" data-form-filter="">All</button>
            <button class="quick-mode-chip" data-form-filter="Monotherapy">Single (${monoCountDistinct})</button>
            <button class="quick-mode-chip" data-form-filter="Combination (FDC)">Combo (${combCountDistinct})</button>
          </div>
          ` : ''}

          <div class="artifact-actions">
            <button class="artifact-btn copy-turn-table-btn" title="Copy table formatted for PowerPoint & Google Slides">
              ${ICONS.slides} <span>Slides</span>
            </button>
            <button class="artifact-btn export-csv-btn" title="Download spreadsheet for Microsoft Excel">
              ${ICONS.csv} <span>Export to Excel</span>
            </button>
          </div>
        </div>

        ${showFilters ? `
        <div class="table-filter-row">
          <div class="filter-group">
            <label>Company</label>
            <select class="table-filter" data-filter="company_std">
              <option value="">All Companies</option>
              ${compOptions}
            </select>
          </div>
          <div class="filter-group">
            <label>Therapy Area</label>
            <select class="table-filter" data-filter="therapy_area">
              <option value="">All Areas</option>
              ${taOptions}
            </select>
          </div>
          <div class="filter-group">
            <label>Year</label>
            <select class="table-filter" data-filter="approval_year">
              <option value="">All Years</option>
              ${yearOptions}
            </select>
          </div>
          <div class="filter-group">
            <label>Molecule Type</label>
            <select class="table-filter" data-filter="molecule_type">
              <option value="">All Types</option>
              <option value="Biologic">Biologic</option>
              <option value="Small Molecule">Small Molecule</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Regulatory Group</label>
            <select class="table-filter" data-filter="approval_group_code">
              <option value="">All Clearances (Group D)</option>
              <option value="new_molecule">★ Group A: New Molecules (First in India)</option>
              <option value="biosimilar">🧬 Group B: Biosimilars</option>
              <option value="generic">💊 Group C: Generics</option>
            </select>
          </div>
          <button class="filter-reset-btn" title="Reset all filters">↺ Reset</button>
        </div>
        ` : ''}

        <div class="table-dossier-hint">
          <span class="hint-icon">${ICONS.info}</span>
          <span><strong>Tip:</strong> Click anywhere on a drug row to open the complete CDSCO master dossier (Form ID, Full Active Composition, and Manufacturing / Import Site).</span>
        </div>

        <div class="table-wrap">
          <table class="results-table">
            <thead>
              <tr>
                <th style="width: 25%;">Drug &amp; Brand</th>
                <th style="width: 20%;">Applicant Firm</th>
                <th style="width: 13%;">Therapy Area</th>
                <th style="width: 14%;">Molecule Type</th>
                <th style="width: 12%; cursor: pointer;" class="sortable-th sort-date-th" title="Click to sort by date (Newest / Oldest)">
                  Approval Date <span class="sort-indicator">${isAsc ? "▲" : "▼"}</span>
                </th>
                <th style="width: 16%;">Approved Indication</th>
              </tr>
            </thead>
            <tbody>
              ${distinctList.map(r => renderTableRow(r)).join("")}
            </tbody>
          </table>
        </div>

        <div class="turn-action-footer">
          <button class="turn-btn new-search-btn" title="Start a fresh search">${ICONS.plus} New Search</button>
        </div>
      </div>
    `;
  } else {
    html += `
      <div class="artifact-card" style="padding: 28px; text-align: center;">
        <div style="font-size: 24px; margin-bottom: 8px; color: var(--accent-teal);">${ICONS.search}</div>
        <h4 style="font-size: 15px; color: #fff; margin-bottom: 6px;">No exact approvals found in the 2018–2026 registry</h4>
        <p style="font-size: 13px; color: var(--text-dim); max-width: 480px; margin: 0 auto 16px;">
          Try searching by active molecule (e.g. "Semaglutide", "Ustekinumab"), standardized company ("Sun Pharma", "AstraZeneca"), or broad therapy area ("Oncology").
        </p>
        <div class="turn-action-footer" style="justify-content: center; margin-top: 12px; margin-bottom: 18px;">
          <button class="turn-btn new-search-btn">${ICONS.plus} New Search</button>
        </div>
      </div>
    `;
  }

  content.innerHTML = html;

  // Bind row clicks, filter dropdowns, date sorting, and view toggle
  bindArtifactEvents(blockEl, results, data);
}

// Render Single Table Row
function renderTableRow(r) {
  const mncTag = r.is_mnc ? `<span class="mnc-badge">MNC</span>` : "";
  const catClass = r.product_category === "Finished Formulation" ? "formulation" : "bulk";

  // Brand pill
  const brandPill = r.brand_name 
    ? `<span class="brand-name-pill" title="Commercial Trade Name in India">${ICONS.tag} ${escapeHtml(r.brand_name)}</span>` 
    : "";

  // Multi-strength badge if aggregated
  const strengthPill = (r.presentation_count && r.presentation_count > 1)
    ? `<span class="multi-strength-badge" title="Covers ${r.presentation_count} approved dosage strengths / vial sizes in this single Form #${r.form_id || ''} clearance">${ICONS.layers} ${r.presentation_count} Strengths</span>`
    : "";

  // Molecule Type Badge: Biologic vs Small Molecule
  const isBiologic = (r.molecule_type === "Biologic");
  const molBadge = isBiologic 
    ? `<span class="mol-badge biologic" title="Biologic / Large Molecule Clearance">${ICONS.dna} Biologic</span>` 
    : `<span class="mol-badge small-molecule" title="Small Molecule Chemical Entity">${ICONS.pill} Small Molecule</span>`;

  // Formulation Mode Badge: Monotherapy vs Combination (FDC)
  // Only display badge for FDC combos; leave monotherapy clean (no redundant "Single Molecule" text)
  const isFdc = (r.formulation_type === "Combination (FDC)" || r.is_combination);
  const formBadge = isFdc
    ? `<span class="form-badge fdc" title="Fixed-Dose Combination (FDC)">${ICONS.combo} FDC Combo</span>`
    : "";

  const companyDisplay = r.company_std || r.company || "Not specified";

  // Regulatory Taxonomy Lineage Badge: Group A, B, C or Line Extension
  let lineageBadge = "";
  if (r.approval_group_code === "new_molecule" || (r.is_first_in_india && (r.regulatory_type === "Innovator" || !r.regulatory_type))) {
    lineageBadge = `<span class="lineage-badge first-in-india" title="Group A: New Molecule (First CDSCO clearance for this active substance in India)">★ First in India</span>`;
  } else if (r.approval_group_code === "biosimilar" || r.regulatory_type === "Biosimilar") {
    lineageBadge = `<span class="lineage-badge biosimilar" title="Group B: Biosimilar (Follow-on to innovator biologic)">🧬 Biosimilar</span>`;
  } else if (r.approval_group_code === "generic" || r.regulatory_type === "Generic") {
    lineageBadge = `<span class="lineage-badge generic" title="Group C: Generic (Small molecule bioequivalent copy)">💊 Generic</span>`;
  } else if (r.first_approval_year && r.approval_year && r.first_approval_year < r.approval_year) {
    lineageBadge = `<span class="lineage-badge line-extension" title="Line extension, new strength, or new formulation. Active molecule was first approved in India in ${r.first_approval_year} (Earliest clearance: ${escapeHtml(r.first_approval_date || '')})">Line Ext · First: ${r.first_approval_year}</span>`;
  }

  // Concise Approved Indication Text
  let conciseIndication = (r.indication || "").trim();
  if (!conciseIndication || conciseIndication.toUpperCase() === "NA" || conciseIndication.toUpperCase() === "N/A") {
    conciseIndication = '<span style="color: var(--text-muted); font-size: 11.5px;">Clearance on file</span>';
  } else {
    const shortText = conciseIndication.length > 55 ? conciseIndication.substring(0, 52) + "..." : conciseIndication;
    conciseIndication = `<span class="indication-cell-text" title="${escapeHtml(conciseIndication)}">${escapeHtml(shortText)}</span>`;
  }

  return `
    <tr data-drug-id="${r.id}">
      <td>
        <div class="drug-cell">
          <div class="drug-title-row">
            <span class="drug-name-text">${escapeHtml(r.drug_name || "-")}</span>
          </div>
          <div class="drug-badges-row">
            ${brandPill}
            ${strengthPill}
          </div>
          <span class="drug-strength-text">${escapeHtml(r.dosage || r.composition || "").substring(0, 45)}</span>
        </div>
      </td>
      <td>
        <div class="company-cell">
          <span class="company-std-text">${escapeHtml(companyDisplay)}</span>
          ${mncTag}
        </div>
      </td>
      <td>
        <div class="ta-badge-wrap">
          ${((r.therapy_areas && r.therapy_areas.length) ? r.therapy_areas : (r.therapy_area ? r.therapy_area.split(',').map(s => s.trim()).filter(Boolean) : ['Other'])).map(ta => `<span class="ta-badge">${escapeHtml(ta)}</span>`).join("")}
        </div>
      </td>
      <td>
        <div class="mol-cell">
          ${molBadge}
          ${formBadge}
        </div>
      </td>
      <td>
        <div class="date-cell">
          <span class="date-text">${escapeHtml(r.approval_date || "-")}</span>
          ${lineageBadge}
        </div>
      </td>
      <td>
        ${conciseIndication}
      </td>
    </tr>
  `;
}

// Bind Events inside Artifact (Filters, Date Sorting, Copy, CSV, Modal, View Toggle)
function bindArtifactEvents(blockEl, initialResults, data) {
  const isAsc = Boolean(data && (data.sort_by === "date_asc" || data.is_historical));
  const distinctResults = groupApprovals(initialResults);
  if (isAsc) {
    distinctResults.sort((a, b) => parseCdscoDate(a.approval_date, a.approval_date_iso) - parseCdscoDate(b.approval_date, b.approval_date_iso));
  }
  let currentResults = [...distinctResults];
  let sortDirection = isAsc ? "asc" : "desc";
  let activeFormFilter = ""; // Tracks the quick-mode chip selection independently
  let activeViewMode = "distinct"; // Tracks active view mode ("distinct" | "all")

  const monoCountAll = initialResults.filter(r => r.formulation_type === "Monotherapy").length;
  const combCountAll = initialResults.filter(r => r.formulation_type === "Combination (FDC)").length;
  const monoCountDistinct = distinctResults.filter(r => r.formulation_type === "Monotherapy").length;
  const combCountDistinct = distinctResults.filter(r => r.formulation_type === "Combination (FDC)").length;

  const tbody = blockEl.querySelector(".results-table tbody");
  const countTag = blockEl.querySelector(".filter-count");
  const filterSelects = blockEl.querySelectorAll(".table-filter");
  const resetBtn = blockEl.querySelector(".filter-reset-btn");
  const dateTh = blockEl.querySelector(".sort-date-th");
  const sortIndicator = blockEl.querySelector(".sort-indicator");
  const viewToggleBtns = blockEl.querySelectorAll(".view-toggle-btn");

  // Re-bind row click listener
  const attachRowListeners = () => {
    const rows = blockEl.querySelectorAll(".results-table tbody tr");
    rows.forEach(tr => {
      tr.addEventListener("click", () => {
        const drugId = tr.getAttribute("data-drug-id");
        const drug = currentResults.find(d => String(d.id) === String(drugId));
        if (drug) openModal(drug);
      });
    });
  };

  attachRowListeners();

  // View Mode Toggle (Distinct Clearances vs All Strength Rows)
  viewToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const mode = btn.getAttribute("data-view");
      activeViewMode = mode;
      viewToggleBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      if (mode === "all") {
        currentResults = [...initialResults];
      } else {
        currentResults = [...distinctResults];
      }

      // Re-apply sorting if user changed sort direction
      if (sortDirection === "asc") {
        currentResults.sort((a, b) => parseCdscoDate(a.approval_date, a.approval_date_iso) - parseCdscoDate(b.approval_date, b.approval_date_iso));
      } else {
        currentResults.sort((a, b) => parseCdscoDate(b.approval_date, b.approval_date_iso) - parseCdscoDate(a.approval_date, a.approval_date_iso));
      }

      if (tbody) {
        tbody.innerHTML = currentResults.map(r => renderTableRow(r)).join("");
        attachRowListeners();
        applyFilters();
      }
    });
  });

  // Apply Filters Function — reads dropdown selects + activeFormFilter from chips
  const applyFilters = () => {
    const activeFilters = {};
    filterSelects.forEach(sel => {
      const key = sel.getAttribute("data-filter");
      const val = sel.value;
      if (val) activeFilters[key] = val;
    });

    // Helper: checks if a record matches all active dropdown selects (company, TA, year)
    const matchesDropdowns = (r) => {
      if (activeFilters.company_std && (r.company_std || r.company) !== activeFilters.company_std) return false;
      if (activeFilters.therapy_area) {
        const rowTAs = (r.therapy_areas && r.therapy_areas.length)
          ? r.therapy_areas
          : (r.therapy_area || 'Other').split(',').map(s => s.trim());
        if (!rowTAs.includes(activeFilters.therapy_area)) return false;
      }
      if (activeFilters.approval_year && r.approval_year !== parseInt(activeFilters.approval_year)) return false;
      if (activeFilters.molecule_type && (r.molecule_type || 'Small Molecule') !== activeFilters.molecule_type) return false;
      if (activeFilters.approval_group_code) {
        if (activeFilters.approval_group_code === "new_molecule") {
          const isA = (r.approval_group_code === "new_molecule") || (r.is_first_in_india && (r.regulatory_type === "Innovator" || !r.regulatory_type));
          if (!isA) return false;
        } else if (activeFilters.approval_group_code === "biosimilar") {
          const isB = (r.approval_group_code === "biosimilar") || (r.regulatory_type === "Biosimilar");
          if (!isB) return false;
        } else if (activeFilters.approval_group_code === "generic") {
          const isC = (r.approval_group_code === "generic") || (r.regulatory_type === "Generic");
          if (!isC) return false;
        }
      }
      return true;
    };

    // Calculate dynamic counts based on the dropdown-filtered subset
    const filteredDistinct = distinctResults.filter(matchesDropdowns);
    const filteredAll = initialResults.filter(matchesDropdowns);

    // 1. Dynamically update View Toggle Buttons (Distinct and All Filings counts)
    const distinctBtn = blockEl.querySelector('.view-toggle-btn[data-view="distinct"]');
    const allBtn = blockEl.querySelector('.view-toggle-btn[data-view="all"]');
    if (distinctBtn) distinctBtn.textContent = `Distinct (${filteredDistinct.length})`;
    if (allBtn) allBtn.textContent = `All Filings (${filteredAll.length})`;

    // 2. Dynamically update Quick Mode Chips (Single / Combo counts) based on active view mode
    const isAll = (activeViewMode === "all");
    const activeFilteredList = isAll ? filteredAll : filteredDistinct;
    const sCount = activeFilteredList.filter(r => r.formulation_type === "Monotherapy").length;
    const cCount = activeFilteredList.filter(r => r.formulation_type === "Combination (FDC)").length;

    const singleChip = blockEl.querySelector('.quick-mode-chip[data-form-filter="Monotherapy"]');
    const comboChip = blockEl.querySelector('.quick-mode-chip[data-form-filter="Combination (FDC)"]');
    if (singleChip) singleChip.innerHTML = `Single (${sCount})`;
    if (comboChip) comboChip.innerHTML = `Combo (${cCount})`;

    // 3. Filter rows displayed in the active table
    let visibleCount = 0;
    const allRows = tbody.querySelectorAll("tr");
    allRows.forEach(tr => {
      const drugId = tr.getAttribute("data-drug-id");
      const r = currentResults.find(d => String(d.id) === String(drugId));
      if (!r) return;

      let show = matchesDropdowns(r);
      if (show && activeFormFilter && r.formulation_type !== activeFormFilter) {
        show = false;
      }

      tr.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });

    if (countTag) countTag.textContent = visibleCount;
  };

  // Quick Mode Chips (Single Drug vs Combinations) — self-contained, no select dependency
  const quickModeChips = blockEl.querySelectorAll(".quick-mode-chip");
  quickModeChips.forEach(chip => {
    chip.addEventListener("click", () => {
      activeFormFilter = chip.getAttribute("data-form-filter") || "";
      quickModeChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      applyFilters();
    });
  });

  // Date Column Sorting (Ascending / Descending)
  if (dateTh) {
    dateTh.addEventListener("click", () => {
      sortDirection = sortDirection === "desc" ? "asc" : "desc";
      if (sortIndicator) {
        sortIndicator.textContent = sortDirection === "desc" ? "▼" : "▲";
      }

      // Sort currentResults
      currentResults.sort((a, b) => {
        const tA = parseCdscoDate(a.approval_date, a.approval_date_iso);
        const tB = parseCdscoDate(b.approval_date, b.approval_date_iso);
        return sortDirection === "asc" ? tA - tB : tB - tA;
      });

      // Re-render tbody
      if (tbody) {
        tbody.innerHTML = currentResults.map(r => renderTableRow(r)).join("");
        attachRowListeners();
        applyFilters();
      }
    });
  }

  // Filter Dropdowns
  filterSelects.forEach(sel => sel.addEventListener("change", applyFilters));

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      filterSelects.forEach(sel => { sel.value = ''; });
      activeFormFilter = "";
      quickModeChips.forEach(c => {
        if (!c.getAttribute("data-form-filter")) c.classList.add("active");
        else c.classList.remove("active");
      });
      applyFilters();
    });
  }

  // Copy for Slides Button
  const copyBtn = blockEl.querySelector(".copy-turn-table-btn");
  if (copyBtn) {
    copyBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      copyResultsForSlides(currentResults);
    });
  }

  // Regulatory Guide Modal Triggers (Table Toolbar and Glossary Box)
  const guideModalTriggers = blockEl.querySelectorAll(".guide-modal-trigger-btn");
  guideModalTriggers.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openGuideModal();
    });
  });

  // Export CSV Button
  const exportBtn = blockEl.querySelector(".export-csv-btn");
  if (exportBtn) {
    exportBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      exportResultsToCsv(currentResults);
    });
  }

  // Turn Action Buttons (New Search)
  const newSearchBtns = blockEl.querySelectorAll(".new-search-btn");
  newSearchBtns.forEach(btn => btn.addEventListener("click", switchToHomeView));

}

// Copy Table to Clipboard (Rich HTML Table for Slides & PowerPoint + TSV Fallback)
function copyResultsForSlides(results) {
  if (!results || results.length === 0) return;

  const headers = ["Drug Name", "Brand Name", "Applicant Company", "Classification", "Therapy Area", "Product Category", "Approval Date", "Indication"];
  const rows = results.map(r => [
    cleanForTsv(r.drug_name),
    cleanForTsv(r.brand_name || "-"),
    cleanForTsv(r.company_std || r.company),
    cleanForTsv(r.molecule_type || "Small Molecule"),
    cleanForTsv(r.therapy_area || "Other"),
    cleanForTsv(r.product_category || "Finished Formulation"),
    cleanForTsv(r.approval_date || "-"),
    cleanForTsv(r.indication || "Clearance on file")
  ]);

  // 1. Plain Text TSV
  const tsvText = [headers.join("\t"), ...rows.map(row => row.join("\t"))].join("\n");

  // 2. Rich HTML Table (Required by PowerPoint, Google Slides, Word & Excel to paste as a multi-cell table)
  const headerHtml = headers.map(h => `<th style="border: 1px solid #d1d5db; padding: 7px 12px; background-color: #f3f4f6; color: #111827; font-weight: 700; text-align: left;">${escapeHtml(h)}</th>`).join("");
  const rowsHtml = rows.map((row, idx) => {
    const bg = idx % 2 === 0 ? "#ffffff" : "#f9fafb";
    const cells = row.map(c => `<td style="border: 1px solid #e5e7eb; padding: 6px 10px; color: #1f2937; text-align: left; vertical-align: top;">${escapeHtml(c)}</td>`).join("");
    return `<tr style="background-color: ${bg};">${cells}</tr>`;
  }).join("");

  const htmlTable = `<table style="border-collapse: collapse; font-family: Calibri, Arial, sans-serif; font-size: 10.5pt; width: 100%; border: 1px solid #d1d5db;"><thead><tr>${headerHtml}</tr></thead><tbody>${rowsHtml}</tbody></table>`;

  if (navigator.clipboard && window.ClipboardItem) {
    const blobHtml = new Blob([htmlTable], { type: "text/html" });
    const blobText = new Blob([tsvText], { type: "text/plain" });
    const item = new ClipboardItem({
      "text/html": blobHtml,
      "text/plain": blobText
    });

    navigator.clipboard.write([item]).then(() => {
      showToast(`Copied ${results.length} approvals! Ready to paste as formatted table in PowerPoint & Google Slides.`);
      logTelemetry("slides_copied", { row_count: results.length });
    }).catch(err => {
      console.warn("ClipboardItem write failed, falling back to writeText:", err);
      fallbackWriteText(tsvText, results.length);
    });
  } else {
    fallbackWriteText(tsvText, results.length);
  }
}

function fallbackWriteText(tsvText, count) {
  navigator.clipboard.writeText(tsvText).then(() => {
    showToast(`Copied ${count} approvals as TSV table to clipboard.`);
  }).catch(err => {
    console.error("Failed to copy table:", err);
  });
}

// Export CSV for Excel
function exportResultsToCsv(results) {
  if (!results || results.length === 0) return;

  const headers = ["Drug Name", "Brand Name", "Applicant Company", "Molecule Type", "Therapy Structure", "Therapy Area", "Category", "Approval Date", "Indication", "Form ID"];
  const csvRows = results.map(r => [
    csvQuote(r.drug_name),
    csvQuote(r.brand_name || ""),
    csvQuote(r.company_std || r.company),
    csvQuote(r.molecule_type || "Small Molecule"),
    csvQuote(r.formulation_type || "Monotherapy"),
    csvQuote(r.therapy_area),
    csvQuote(r.product_category),
    csvQuote(r.approval_date),
    csvQuote(r.indication),
    csvQuote(r.form_id)
  ]);

  // \uFEFF UTF-8 BOM ensures Excel cleanly renders accented characters, Greek letters (alpha/beta), and symbols
  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [headers.join(","), ...csvRows.map(row => row.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `CDSCO_Approvals_Export_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Exported ${results.length} approvals to Excel (.csv).`);
  logTelemetry("excel_exported", { row_count: results.length });
}

// Modal Details
function openModal(drug) {
  modalDrugName.textContent = drug.drug_name || "Unspecified Drug";
  modalCompany.textContent = `${drug.company_std || drug.company} • ${drug.molecule_type || 'Small Molecule'}`;
  modalDate.textContent = drug.approval_date || "Unknown Date";

  const modalLineage = document.getElementById("modalLineage");
  if (modalLineage) {
    if (drug.approval_group_code === "new_molecule" || (drug.is_first_in_india && (drug.regulatory_type === "Innovator" || !drug.regulatory_type))) {
      modalLineage.innerHTML = `<span class="lineage-badge first-in-india">★ Group A: New Molecule (First in India)</span> <span style="font-size: 11.5px; color: var(--text-dim); margin-left: 4px;">(Innovator NCE/NBE / First Clearance)</span>`;
    } else if (drug.approval_group_code === "biosimilar" || drug.regulatory_type === "Biosimilar") {
      modalLineage.innerHTML = `<span class="lineage-badge biosimilar">🧬 Group B: Biosimilar</span> <span style="font-size: 11.5px; color: var(--text-dim); margin-left: 4px;">(Biologic Follow-on / Similar Biologic)</span>`;
    } else if (drug.approval_group_code === "generic" || drug.regulatory_type === "Generic") {
      modalLineage.innerHTML = `<span class="lineage-badge generic">💊 Group C: Generic</span> <span style="font-size: 11.5px; color: var(--text-dim); margin-left: 4px;">(Small Molecule Bioequivalent Copy)</span>`;
    } else if (drug.first_approval_year && drug.approval_year && drug.first_approval_year < drug.approval_year) {
      modalLineage.innerHTML = `<span class="lineage-badge line-extension">Line Extension</span> <span style="font-size: 11.5px; color: var(--text-dim); margin-left: 4px;">Substance first approved: <strong>${escapeHtml(drug.first_approval_date || '')}</strong> (${drug.first_approval_year})</span>`;
    } else {
      modalLineage.textContent = drug.approval_group_label || drug.regulatory_status || "Standard clearance";
    }
  }
  const modalTas = (drug.therapy_areas && drug.therapy_areas.length)
    ? drug.therapy_areas
    : (drug.therapy_area ? drug.therapy_area.split(',').map(s => s.trim()).filter(Boolean) : ['Other']);
  if (modalTherapyTag) {
    modalTherapyTag.innerHTML = modalTas.map(ta => `<span class="modal-tag">${escapeHtml(ta)}</span>`).join("");
  }
  modalCatTag.textContent = drug.product_category || "Finished Formulation";
  modalIndication.textContent = drug.indication || "Clinical indication details recorded in physical CDSCO master dossier.";
  
  if (drug.all_compositions && drug.all_compositions.length > 1) {
    modalComposition.innerHTML = `
      <div style="margin-bottom: 6px; font-weight: 700; color: var(--accent-teal); display: flex; align-items: center; gap: 6px;">${ICONS.layers} ${drug.all_compositions.length} Approved Formulations / Strengths in this Permission:</div>
      <ul style="padding-left: 18px; margin: 0; display: flex; flex-direction: column; gap: 4px;">
        ${drug.all_compositions.map(c => `<li>${escapeHtml(c)}</li>`).join("")}
      </ul>
    `;
  } else {
    modalComposition.textContent = drug.composition || drug.dosage || "Not recorded";
  }

  // Manufacturing / Import Site Address
  const rawAddr = (drug.manuf_addr || "").trim();
  const isInvalidAddr = !rawAddr || 
    rawAddr.toUpperCase() === "NA" || 
    rawAddr.toUpperCase() === "NOT AVAILABLE" || 
    rawAddr.toUpperCase() === "NONE" || 
    rawAddr.toUpperCase() === "NOT RECORDED" ||
    rawAddr.toLowerCase() === "finished formulation" ||
    rawAddr.toLowerCase() === "bulk drug";

  if (!isInvalidAddr) {
    if (modalAddressContainer) modalAddressContainer.style.display = "block";
    modalAddress.innerHTML = escapeHtml(rawAddr).replace(/&lt;br\s*\/?&gt;/gi, '<br style="margin-bottom: 4px;">');
  } else {
    if (modalAddressContainer) modalAddressContainer.style.display = "none";
  }

  const formIdStr = drug.form_id ? String(drug.form_id) : "54552";
  modalFormId.textContent = `#${formIdStr}`;

  currentModalDrug = drug;

  if (detailModalBackdrop) {
    detailModalBackdrop.style.display = "flex";
  }
  logTelemetry("dossier_opened", { drug_id: drug.id, drug_name: drug.drug_name });
}

function closeModal() {
  if (detailModalBackdrop) {
    detailModalBackdrop.style.display = "none";
  }
}
window.closeModal = closeModal;

// Toast Alert
function showToast(msg) {
  toastMessage.textContent = msg;
  toastNotification.classList.add("show");
  setTimeout(() => {
    toastNotification.classList.remove("show");
  }, 3200);
}

// Utility Helpers
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
  if (!text) return "";
  // Strictly remove any Sample Clearances section
  text = text.replace(/###?\s*Sample\s+Clearances[\s\S]*$/i, "").trim();
  let esc = escapeHtml(text);

  // Bold & Italic inline formatting
  esc = esc.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  esc = esc.replace(/\*(.*?)\*/g, '<em>$1</em>');

  const rawLines = esc.split('\n');
  const output = [];
  let inList = false;
  let listType = 'ul';
  let inTable = false;
  let tableRows = [];

  function closeList() {
    if (inList) {
      output.push(`</${listType}>`);
      inList = false;
    }
  }

  function closeTable() {
    if (inTable) {
      let html = '<div class="markdown-table-wrap"><table class="markdown-table">';
      if (tableRows.length > 0) {
        html += '<thead><tr>' + tableRows[0].map(c => `<th>${c.trim()}</th>`).join('') + '</tr></thead><tbody>';
        for (let i = 1; i < tableRows.length; i++) {
          html += '<tr>' + tableRows[i].map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
        }
        html += '</tbody>';
      }
      html += '</table></div>';
      output.push(html);
      tableRows = [];
      inTable = false;
    }
  }

  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i].trim();
    if (!line) {
      closeList();
      closeTable();
      continue;
    }

    // Horizontal divider
    if (line === '---' || line === '***' || line === '___') {
      closeList();
      closeTable();
      output.push('<hr class="summary-divider">');
      continue;
    }

    // Table rows: pipe-separated
    if (line.startsWith('|') && line.endsWith('|')) {
      closeList();
      if (line.includes('---')) continue; // skip separator row
      const cells = line.split('|').slice(1, -1);
      inTable = true;
      tableRows.push(cells);
      continue;
    } else {
      closeTable();
    }

    // Markdown Headers (#, ##, ###, ####)
    const headerMatch = line.match(/^(#{1,4})\s+(.+)$/);
    if (headerMatch) {
      closeList();
      output.push(`<h4 class="summary-heading">${headerMatch[2]}</h4>`);
      continue;
    }

    // Common executive section titles without leading '#'
    const isSectionTitle = /^(?:[0-9]{4}\s+)?(?:Regulatory Overview|Key Therapeutic Areas|Therapeutic Areas|Sample Verified Filings|Sample Clearances|Leading Manufacturers|Manufacturer Breakdown|Executive Summary|Clinical Overview|Regulatory Summary)\b.*$/i.test(line);
    if (isSectionTitle && line.length < 80 && !line.endsWith('.')) {
      closeList();
      output.push(`<h4 class="summary-heading">${line}</h4>`);
      continue;
    }

    // Blockquote (> ⚠️ ...)
    if (line.startsWith('&gt;') || line.startsWith('>')) {
      closeList();
      const bqText = line.replace(/^(?:&gt;|>)\s*/, '');
      output.push(`<blockquote class="summary-blockquote">${bqText}</blockquote>`);
      continue;
    }

    // Bullet points (•, *, -)
    const bulletMatch = line.match(/^[•\*\-]\s+(.+)$/);
    if (bulletMatch) {
      if (!inList || listType !== 'ul') {
        closeList();
        output.push('<ul class="summary-list">');
        inList = true;
        listType = 'ul';
      }
      output.push(`<li>${bulletMatch[1]}</li>`);
      continue;
    }

    // Numbered lists (1., 2., etc.)
    const numMatch = line.match(/^\d+[\.\)]\s+(.+)$/);
    if (numMatch) {
      if (!inList || listType !== 'ol') {
        closeList();
        output.push('<ol class="summary-list numbered">');
        inList = true;
        listType = 'ol';
      }
      output.push(`<li>${numMatch[1]}</li>`);
      continue;
    }

    // Plain paragraph text
    closeList();
    output.push(`<p class="summary-p">${line}</p>`);
  }

  closeList();
  closeTable();

  return output.join('\n');
}

function cleanForTsv(str) {
  if (!str) return "-";
  return String(str).replace(/[\t\n\r]/g, " ").trim();
}

function csvQuote(str) {
  if (!str) return '""';
  const clean = String(str).replace(/"/g, '""');
  return `"${clean}"`;
}

// ==========================================
// PLATFORM ANALYTICS & KPI PULSE CONTROLLER
// ==========================================

const analyticsModalBackdrop = document.getElementById("analyticsModalBackdrop");
const analyticsHeaderSync = document.getElementById("analyticsHeaderSync");

// KPI Card Elements
const kpiUniqueVisitors = document.getElementById("kpiUniqueVisitors");
const kpiTotalQueries = document.getElementById("kpiTotalQueries");
const kpiAvgQueriesSub = document.getElementById("kpiAvgQueriesSub");
const kpiAvgLatency = document.getElementById("kpiAvgLatency");
const kpiDeliverables = document.getElementById("kpiDeliverables");
const kpiDeliverablesSub = document.getElementById("kpiDeliverablesSub");
const kpiZeroRate = document.getElementById("kpiZeroRate");
const kpiZeroSub = document.getElementById("kpiZeroSub");
const kpiDossierViews = document.getElementById("kpiDossierViews");

// Visual Bars & Tables
const topQueriesList = document.getElementById("topQueriesList");
const topTasAndActionsList = document.getElementById("topTasAndActionsList");
const zeroResultTableBody = document.getElementById("zeroResultTableBody");
const recentQueriesTableBody = document.getElementById("recentQueriesTableBody");

function openAnalyticsModal() {
  if (!analyticsModalBackdrop) return;
  analyticsModalBackdrop.style.display = "flex";
  fetchAnalytics();
  logTelemetry("analytics_opened");
}
window.openAnalyticsModal = openAnalyticsModal;

function closeAnalyticsModal() {
  if (!analyticsModalBackdrop) return;
  analyticsModalBackdrop.style.display = "none";
}
window.closeAnalyticsModal = closeAnalyticsModal;

// Regulatory Classifications Guide Modal Controller
const guideModalBackdrop = document.getElementById("guideModalBackdrop");

function openGuideModal() {
  if (!guideModalBackdrop) return;
  guideModalBackdrop.style.display = "flex";
  document.body.style.overflow = "hidden";
  logTelemetry("guide_opened");
}
window.openGuideModal = openGuideModal;

function closeGuideModal() {
  if (!guideModalBackdrop) return;
  guideModalBackdrop.style.display = "none";
  document.body.style.overflow = "";
}
window.closeGuideModal = closeGuideModal;

async function fetchAnalytics(isManualRefresh = false) {
  try {
    if (analyticsHeaderSync) {
      analyticsHeaderSync.textContent = "Syncing live telemetry...";
    }
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderAnalyticsDashboard(data);
    if (analyticsHeaderSync) {
      const now = new Date();
      analyticsHeaderSync.textContent = `Auditing live user sessions • Synced at ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;
    }
    if (isManualRefresh) {
      showToast("Analytics & KPI metrics refreshed.");
    }
  } catch (err) {
    console.error("Failed to fetch analytics:", err);
    if (analyticsHeaderSync) {
      analyticsHeaderSync.textContent = "Unable to fetch live telemetry.";
    }
  }
}

function renderAnalyticsDashboard(data) {
  if (!data || !data.kpis) return;
  const k = data.kpis;

  // 1. KPI Cards
  if (kpiUniqueVisitors) kpiUniqueVisitors.textContent = Number(k.unique_visitors || 0).toLocaleString();
  if (kpiTotalQueries) kpiTotalQueries.textContent = Number(k.total_queries || 0).toLocaleString();
  if (kpiAvgQueriesSub) kpiAvgQueriesSub.textContent = `${k.avg_queries_per_visitor || 0} avg queries / visitor`;
  if (kpiAvgLatency) kpiAvgLatency.textContent = `${k.avg_latency_ms || 0} ms`;
  if (kpiDeliverables) kpiDeliverables.textContent = Number(k.total_deliverables || 0).toLocaleString();
  if (kpiDeliverablesSub) kpiDeliverablesSub.textContent = `${k.excel_exports || 0} Excel + ${k.slides_copies || 0} Slides`;
  if (kpiZeroRate) kpiZeroRate.textContent = `${k.zero_match_rate || 0}%`;
  if (kpiZeroSub) kpiZeroSub.textContent = `${k.zero_match_count || 0} unmet / out-of-scope`;
  if (kpiDossierViews) kpiDossierViews.textContent = Number(k.dossier_views || 0).toLocaleString();

  // 2. Top Searched Molecules & Queries
  if (topQueriesList && data.top_queries) {
    const maxCount = Math.max(...data.top_queries.map(q => q.count), 1);
    topQueriesList.innerHTML = data.top_queries.map(q => {
      const pct = Math.max(Math.round((q.count / maxCount) * 100), 8);
      return `
        <div class="stat-bar-item">
          <div class="stat-bar-label-row">
            <span class="stat-bar-name">${escapeHtml(q.query)}</span>
            <span class="stat-bar-val">${q.count} searches</span>
          </div>
          <div class="stat-bar-track">
            <div class="stat-bar-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join("");
  }

  // 3. Top Therapy Areas & Action Mix
  if (topTasAndActionsList) {
    const items = [];
    if (data.top_therapy_areas && data.top_therapy_areas.length) {
      const maxTa = Math.max(...data.top_therapy_areas.map(t => t.count), 1);
      data.top_therapy_areas.forEach(t => {
        const pct = Math.max(Math.round((t.count / maxTa) * 100), 8);
        items.push(`
          <div class="stat-bar-item">
            <div class="stat-bar-label-row">
              <span class="stat-bar-name">${escapeHtml(t.therapy_area)}</span>
              <span class="stat-bar-val">${t.count} queries</span>
            </div>
            <div class="stat-bar-track">
              <div class="stat-bar-fill" style="width: ${pct}%; background: linear-gradient(90deg, #20808d, #259ca9);"></div>
            </div>
          </div>
        `);
      });
    }

    // Engagement Mix
    const deliverableMax = Math.max(k.excel_exports || 0, k.slides_copies || 0, k.dossier_views || 0, 1);
    const excelPct = Math.max(Math.round(((k.excel_exports || 0) / deliverableMax) * 100), 8);
    const slidesPct = Math.max(Math.round(((k.slides_copies || 0) / deliverableMax) * 100), 8);
    const dossierPct = Math.max(Math.round(((k.dossier_views || 0) / deliverableMax) * 100), 8);

    items.push(`
      <div class="stat-bar-item" style="margin-top: 8px;">
        <div class="stat-bar-label-row">
          <span class="stat-bar-name">Excel (.csv) Exports</span>
          <span class="stat-bar-val">${k.excel_exports || 0} downloads</span>
        </div>
        <div class="stat-bar-track">
          <div class="stat-bar-fill" style="width: ${excelPct}%; background: linear-gradient(90deg, #10b981, #34d399);"></div>
        </div>
      </div>
      <div class="stat-bar-item">
        <div class="stat-bar-label-row">
          <span class="stat-bar-name">PowerPoint &amp; Slides Tables</span>
          <span class="stat-bar-val">${k.slides_copies || 0} copies</span>
        </div>
        <div class="stat-bar-track">
          <div class="stat-bar-fill" style="width: ${slidesPct}%; background: linear-gradient(90deg, #20808d, #38bdf8);"></div>
        </div>
      </div>
      <div class="stat-bar-item">
        <div class="stat-bar-label-row">
          <span class="stat-bar-name">Master Dossier Form Clicks</span>
          <span class="stat-bar-val">${k.dossier_views || 0} views</span>
        </div>
        <div class="stat-bar-track">
          <div class="stat-bar-fill" style="width: ${dossierPct}%; background: linear-gradient(90deg, #6366f1, #818cf8);"></div>
        </div>
      </div>
    `);

    topTasAndActionsList.innerHTML = items.join("");
  }

  // 4. Unmet User Demand (Zero-Result Queries) Table
  if (zeroResultTableBody && data.zero_result_queries) {
    if (data.zero_result_queries.length === 0) {
      zeroResultTableBody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-dim); padding: 18px;">No zero-result searches logged yet.</td></tr>`;
    } else {
      zeroResultTableBody.innerHTML = data.zero_result_queries.map(zq => {
        const gapCategory = inferProductGapCategory(zq.query);
        return `
          <tr>
            <td><span class="query-cell-text">${escapeHtml(zq.query)}</span></td>
            <td><span class="count-cell-badge">${zq.count} searches</span></td>
            <td><span class="unmet-gap-tag">${escapeHtml(gapCategory)}</span></td>
          </tr>
        `;
      }).join("");
    }
  }

  // 5. Recent Search Activity Feed Table
  if (recentQueriesTableBody && data.recent_queries) {
    if (data.recent_queries.length === 0) {
      recentQueriesTableBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-dim); padding: 18px;">No search queries recorded yet.</td></tr>`;
    } else {
      recentQueriesTableBody.innerHTML = data.recent_queries.map(rq => {
        const timeAgo = formatTimeAgo(rq.timestamp);
        const matchBadge = rq.is_zero_result
          ? `<span class="unmet-gap-tag" style="background: rgba(239, 68, 68, 0.12); color: #f87171; border-color: rgba(239,68,68,0.25);">0 records</span>`
          : `<span class="count-cell-badge" style="color: var(--accent-teal); background: rgba(32, 128, 141, 0.12);">${Number(rq.result_count).toLocaleString()} records</span>`;
        return `
          <tr>
            <td><span class="query-cell-text">${escapeHtml(rq.query)}</span></td>
            <td>${matchBadge}</td>
            <td><span class="latency-mono">${rq.latency_ms} ms</span></td>
            <td><span class="time-ago-text">${escapeHtml(timeAgo)}</span></td>
          </tr>
        `;
      }).join("");
    }
  }
}

function inferProductGapCategory(queryStr) {
  const q = String(queryStr).toLowerCase();
  if (q.includes("trial") || q.includes("phase") || q.includes("recruiting")) return "Clinical Trial Pipeline (GCT Portal)";
  if (q.includes("price") || q.includes("cost") || q.includes("nppa") || q.includes("ceiling")) return "Pricing & NPPA Ceilings";
  if (q.includes("mrna") || q.includes("vaccine")) return "Pre-approval / In Review Pipeline";
  if (q.includes("generic") || q.includes("patent") || q.includes("expiry")) return "Patent & Loss of Exclusivity";
  if (q.includes("2017") || q.includes("2016") || q.includes("pre-2018") || q.includes("historical")) return "Historical Archive (< 2018)";
  return "Unregistered / Scope Expansion";
}

function formatTimeAgo(isoString) {
  if (!isoString) return "-";
  try {
    const diffSec = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diffSec < 60) return "Just now";
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    if (diffSec < 172800) return "Yesterday";
    return `${Math.floor(diffSec / 86400)}d ago`;
  } catch (e) {
    return isoString;
  }
}

