// JobMentor AI - Client Application Logic

let currentDoc = null;
let currentSessionId = null;
let currentAtsResult = null;
let currentEmailPackage = null;

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white', 'shadow-md', 'shadow-blue-500/20');
    btn.classList.add('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800/70');
  });

  const activeContent = document.getElementById(tabId);
  const activeBtn = document.getElementById(`btn-${tabId}`);
  if (activeContent) activeContent.classList.remove('hidden');
  if (activeBtn) {
    activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow-md', 'shadow-blue-500/20');
    activeBtn.classList.remove('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800/70');
  }

  if (tabId === 'tab-vault') {
    refreshVaultData();
  }
}

// System Health Check
async function checkSystemHealth() {
  try {
    const res = await fetch('/health');
    const data = await res.json();
    
    // Update Gemini badge
    const geminiBadge = document.getElementById('gemini-status-badge');
    if (geminiBadge) {
      if (data.gemini_configured) {
        geminiBadge.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-blue-950/80 text-blue-300 border border-blue-800/60';
        geminiBadge.innerHTML = `<i data-lucide="cpu" class="w-3.5 h-3.5"></i><span>${data.gemini_model}</span>`;
      } else {
        geminiBadge.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-700';
        geminiBadge.innerHTML = `<i data-lucide="cpu" class="w-3.5 h-3.5"></i><span>Gemini Demo Mode</span>`;
      }
    }

    // Update Firestore badge
    const firestoreBadge = document.getElementById('firestore-status-badge');
    if (firestoreBadge) {
      if (data.firestore_connected) {
        firestoreBadge.className = 'hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-800/60';
        firestoreBadge.innerHTML = `<i data-lucide="database" class="w-3.5 h-3.5"></i><span>Firestore Cloud</span>`;
      } else {
        firestoreBadge.className = 'hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-700';
        firestoreBadge.innerHTML = `<i data-lucide="database" class="w-3.5 h-3.5"></i><span>Firestore Local</span>`;
      }
    }

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.warn("Health check error:", e);
  }
}

// =================================================================
// TAB 1: PDF UPLOAD & CHAT
// =================================================================

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('pdf-file-input');

if (dropZone && fileInput) {
  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500', 'bg-blue-950/20');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500', 'bg-blue-950/20');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500', 'bg-blue-950/20');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    alert("Please select a valid PDF file.");
    return;
  }

  const statusEl = document.getElementById('upload-status');
  statusEl.classList.remove('hidden');
  statusEl.className = 'mt-4 text-xs p-3 rounded-lg bg-blue-950/50 border border-blue-800 text-blue-300 flex items-center space-x-2';
  statusEl.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i><span>Parsing "${file.name}" with PyPDF...</span>`;
  if (window.lucide) lucide.createIcons();

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');

    currentDoc = data.document;

    statusEl.className = 'mt-4 text-xs p-3 rounded-lg bg-emerald-950/50 border border-emerald-800 text-emerald-300 flex items-center space-x-2';
    statusEl.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i><span>Uploaded & Parsed "${currentDoc.filename}"!</span>`;

    // Render metadata card
    const metaCard = document.getElementById('doc-meta-card');
    metaCard.classList.remove('hidden');
    document.getElementById('active-doc-filename').innerText = currentDoc.filename;
    document.getElementById('active-doc-pages').innerText = `${currentDoc.pages} page${currentDoc.pages > 1 ? 's' : ''}`;
    document.getElementById('active-doc-words').innerText = currentDoc.word_count.toLocaleString();
    document.getElementById('active-doc-chars').innerText = currentDoc.total_chars.toLocaleString();
    document.getElementById('active-doc-preview').innerText = currentDoc.text_preview;

    // Post notification to chat
    appendChatMessage('assistant', `I have successfully analyzed **${currentDoc.filename}** (${currentDoc.pages} pages, ${currentDoc.word_count} words). What would you like to explore?`);

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    statusEl.className = 'mt-4 text-xs p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 flex items-center space-x-2';
    statusEl.innerHTML = `<i data-lucide="alert-triangle" class="w-4 h-4"></i><span>${err.message}</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function useAsAtsResume() {
  if (!currentDoc) return;
  const atsResumeArea = document.getElementById('ats-resume-text');
  if (atsResumeArea) {
    atsResumeArea.value = currentDoc.text_preview + "\n\n[Full text loaded from Document ID: " + currentDoc.id + "]";
    switchTab('tab-ats');
  }
}

// Chat Handling
async function handleChatSubmit(e) {
  e.preventDefault();
  const inputEl = document.getElementById('chat-input');
  const question = inputEl.value.trim();
  if (!question) return;

  // Append user message
  appendChatMessage('user', question);
  inputEl.value = '';

  const sendBtn = document.getElementById('chat-send-btn');
  sendBtn.disabled = true;
  sendBtn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i>`;
  if (window.lucide) lucide.createIcons();

  try {
    const payload = {
      question: question,
      document_id: currentDoc ? currentDoc.id : null,
      document_text: !currentDoc ? getSampleResumeText() : null,
      session_id: currentSessionId
    };

    const res = await fetch('/api/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Chat query failed');

    currentSessionId = data.session_id;

    // Render assistant response
    appendChatMessage('assistant', data.answer, data.source_excerpts);

    // Render follow up chips
    if (data.suggested_follow_ups && data.suggested_follow_ups.length > 0) {
      renderFollowUpChips(data.suggested_follow_ups);
    }

  } catch (err) {
    appendChatMessage('assistant', `⚠️ **Error:** ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.innerHTML = `<span>Ask</span><i data-lucide="send" class="w-4 h-4"></i>`;
    if (window.lucide) lucide.createIcons();
  }
}

function appendChatMessage(role, text, excerpts = []) {
  const container = document.getElementById('chat-messages');
  const isUser = role === 'user';

  const wrapper = document.createElement('div');
  wrapper.className = `flex items-start space-x-3 ${isUser ? 'justify-end' : ''}`;

  const iconBg = isUser ? 'bg-blue-600' : 'bg-gradient-to-tr from-blue-600 to-indigo-600';
  const iconName = isUser ? 'user' : 'bot';
  const bubbleBg = isUser ? 'bg-blue-600/90 text-white rounded-2xl rounded-tr-none' : 'bg-slate-900/90 border border-slate-800 rounded-2xl rounded-tl-none text-slate-200';

  const htmlContent = window.marked ? marked.parse(text) : text;

  let excerptsHtml = '';
  if (excerpts && excerpts.length > 0) {
    excerptsHtml = `
      <div class="mt-2 pt-2 border-t border-slate-800 text-[11px] text-slate-400">
        <span class="font-semibold text-slate-300">Cited Excerpt:</span> "${excerpts[0]}"
      </div>
    `;
  }

  wrapper.innerHTML = `
    ${!isUser ? `
      <div class="w-8 h-8 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0 text-white shadow-md">
        <i data-lucide="${iconName}" class="w-4 h-4"></i>
      </div>` : ''}
    <div class="max-w-2xl ${bubbleBg} p-4 text-xs sm:text-sm prose-dark space-y-1 shadow-md">
      ${htmlContent}
      ${excerptsHtml}
    </div>
    ${isUser ? `
      <div class="w-8 h-8 rounded-full ${iconBg} flex items-center justify-center flex-shrink-0 text-white shadow-md">
        <i data-lucide="${iconName}" class="w-4 h-4"></i>
      </div>` : ''}
  `;

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
  if (window.lucide) lucide.createIcons();
}

function renderFollowUpChips(chips) {
  const container = document.getElementById('followup-container');
  const list = document.getElementById('followup-chips');
  list.innerHTML = '';

  chips.forEach(q => {
    const btn = document.createElement('button');
    btn.className = 'text-[11px] px-3 py-1 rounded-full bg-slate-800 hover:bg-blue-900/50 hover:text-blue-200 text-slate-300 border border-slate-700 whitespace-nowrap transition flex-shrink-0';
    btn.innerText = q;
    btn.onclick = () => {
      document.getElementById('chat-input').value = q;
      document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    };
    list.appendChild(btn);
  });

  container.classList.remove('hidden');
}

function clearChat() {
  const container = document.getElementById('chat-messages');
  container.innerHTML = '';
  currentSessionId = null;
  appendChatMessage('assistant', "Chat reset. You can now ask questions about the current or newly uploaded document.");
  document.getElementById('followup-container').classList.add('hidden');
}

// Quick Sample Loaders
function loadSampleResume() {
  const sample = getSampleResumeText();
  currentDoc = {
    id: "sample-senior-cloud-engineer",
    filename: "Alex_Chen_Senior_Cloud_AI_Engineer_Resume.pdf",
    pages: 2,
    word_count: 540,
    total_chars: 3620,
    text_preview: sample.substring(0, 420) + "..."
  };

  const metaCard = document.getElementById('doc-meta-card');
  metaCard.classList.remove('hidden');
  document.getElementById('active-doc-filename').innerText = currentDoc.filename;
  document.getElementById('active-doc-pages').innerText = `${currentDoc.pages} pages`;
  document.getElementById('active-doc-words').innerText = currentDoc.word_count.toLocaleString();
  document.getElementById('active-doc-chars').innerText = currentDoc.total_chars.toLocaleString();
  document.getElementById('active-doc-preview').innerText = currentDoc.text_preview;

  appendChatMessage('assistant', `Loaded sample document: **${currentDoc.filename}**. Try asking questions like *"What is Alex's experience with Google Cloud Run?"*`);
}

function loadSampleResumeIntoAts() {
  document.getElementById('ats-resume-text').value = getSampleResumeText();
}

function loadSampleJobDescription() {
  document.getElementById('ats-job-title').value = "Senior Cloud & AI Solutions Architect";
  document.getElementById('ats-company').value = "NextGen Cloud Platforms";
  document.getElementById('ats-jd-text').value = getSampleJobDescriptionText();
}

// =================================================================
// TAB 2: ATS RESUME MATCHER
// =================================================================

async function runAtsEvaluation() {
  const resumeText = document.getElementById('ats-resume-text').value.trim();
  const jdText = document.getElementById('ats-jd-text').value.trim();
  const jobTitle = document.getElementById('ats-job-title').value.trim() || "Target Role";
  const company = document.getElementById('ats-company').value.trim() || "Target Company";

  if (!resumeText || !jdText) {
    alert("Please provide both candidate resume text and target job description.");
    return;
  }

  const btn = document.getElementById('btn-run-ats');
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i><span>Analyzing with Gemini ATS Engine...</span>`;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch('/api/ats/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jdText,
        job_title: jobTitle,
        company_name: company
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'ATS evaluation failed');

    currentAtsResult = data.evaluation;
    renderAtsResults(currentAtsResult);

  } catch (err) {
    alert("ATS Evaluation Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="zap" class="w-4 h-4"></i><span>Evaluate ATS Compatibility with Gemini</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderAtsResults(evalData) {
  const container = document.getElementById('ats-results-container');
  container.classList.remove('hidden');

  const score = evalData.overall_score || 0;
  document.getElementById('ats-score-number').innerText = `${score}%`;

  // Animate circular gauge (circumference: 2 * pi * 42 ≈ 264)
  const circle = document.getElementById('gauge-circle-elem');
  const offset = 264 - (score / 100) * 264;
  circle.style.strokeDashoffset = offset;

  // Gauge color based on score
  if (score >= 80) {
    circle.setAttribute('stroke', '#34d399'); // Emerald
    document.getElementById('ats-rating-badge').className = 'mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-950/80 text-emerald-300 border border-emerald-700/50';
    document.getElementById('ats-rating-badge').innerText = 'Strong ATS Match';
  } else if (score >= 60) {
    circle.setAttribute('stroke', '#fbbf24'); // Amber
    document.getElementById('ats-rating-badge').className = 'mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-950/80 text-amber-300 border border-amber-700/50';
    document.getElementById('ats-rating-badge').innerText = 'Moderate Match';
  } else {
    circle.setAttribute('stroke', '#f87171'); // Rose
    document.getElementById('ats-rating-badge').className = 'mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-rose-950/80 text-rose-300 border border-rose-700/50';
    document.getElementById('ats-rating-badge').innerText = 'Needs Optimization';
  }

  // Sub-scores
  const sub = evalData.sub_scores || {};
  document.getElementById('score-hard-skills').innerText = `${sub.hard_skills || score}%`;
  document.getElementById('score-soft-skills').innerText = `${sub.soft_skills || 75}%`;
  document.getElementById('score-exp').innerText = `${sub.experience_alignment || score}%`;
  document.getElementById('score-edu').innerText = `${sub.education_and_certifications || 85}%`;

  // Skills Gap Text
  document.getElementById('ats-gap-text').innerText = evalData.skills_gap_analysis || "Good overall alignment.";

  // Matched Keywords Tags
  const matchedContainer = document.getElementById('matching-keywords-tags');
  matchedContainer.innerHTML = '';
  (evalData.matching_keywords || []).forEach(k => {
    const tag = document.createElement('span');
    tag.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium bg-emerald-950/70 text-emerald-300 border border-emerald-800/60';
    tag.innerText = `✓ ${k}`;
    matchedContainer.appendChild(tag);
  });

  // Missing Keywords Tags
  const missingContainer = document.getElementById('missing-keywords-tags');
  missingContainer.innerHTML = '';
  (evalData.missing_critical_keywords || []).forEach(k => {
    const tag = document.createElement('span');
    tag.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium bg-rose-950/70 text-rose-300 border border-rose-800/60';
    tag.innerText = `+ ${k}`;
    missingContainer.appendChild(tag);
  });

  // Bullet Point Rewrites
  const rewritesContainer = document.getElementById('bullet-rewrites-container');
  rewritesContainer.innerHTML = '';
  (evalData.bullet_point_rewrites || []).forEach(item => {
    const card = document.createElement('div');
    card.className = 'p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2';
    card.innerHTML = `
      <div class="text-xs">
        <span class="text-slate-400 uppercase font-semibold text-[10px] block">Original Bullet:</span>
        <p class="text-slate-400 line-through italic mt-0.5">${item.original}</p>
      </div>
      <div class="text-xs pt-1 border-t border-slate-800/60">
        <span class="text-purple-400 uppercase font-bold text-[10px] block">Optimized (Google XYZ Formula):</span>
        <p class="text-slate-100 font-medium mt-0.5">${item.improved}</p>
      </div>
      <div class="text-[11px] text-slate-500 italic mt-1">
        💡 <strong>Rationale:</strong> ${item.reason}
      </div>
    `;
    rewritesContainer.appendChild(card);
  });

  // Quick Wins Checklist
  const quickWinsList = document.getElementById('quick-wins-list');
  quickWinsList.innerHTML = '';
  (evalData.quick_wins || []).forEach(win => {
    const li = document.createElement('li');
    li.className = 'flex items-start space-x-2';
    li.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0"></i><span>${win}</span>`;
    quickWinsList.appendChild(li);
  });

  if (window.lucide) lucide.createIcons();

  // Scroll to results
  container.scrollIntoView({ behavior: 'smooth' });
}

// =================================================================
// TAB 3: COLD EMAIL STUDIO
// =================================================================

async function generateColdEmailPackage() {
  const resumeText = document.getElementById('ats-resume-text').value.trim() || getSampleResumeText();
  const jdText = document.getElementById('ats-jd-text').value.trim() || getSampleJobDescriptionText();
  const recruiter = document.getElementById('email-recruiter-name').value.trim();
  const company = document.getElementById('email-company-name').value.trim();
  const tone = document.getElementById('email-tone').value;

  const btn = document.getElementById('btn-gen-email');
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i><span>Synthesizing Outreach Package...</span>`;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch('/api/email/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jdText,
        recruiter_name: recruiter,
        company_name: company,
        tone: tone
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Email generation failed');

    currentEmailPackage = data.email_package;
    renderColdEmailPackage(currentEmailPackage);

  } catch (err) {
    alert("Email Generation Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Generate Cold Email Package</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function renderColdEmailPackage(pkg) {
  // Render Subject Lines
  const subjContainer = document.getElementById('subject-lines-list');
  subjContainer.innerHTML = '';
  
  (pkg.subject_lines || []).forEach((subj, idx) => {
    const item = document.createElement('div');
    item.className = 'p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-purple-500/50 cursor-pointer flex items-center justify-between transition group';
    item.innerHTML = `
      <div class="flex items-center space-x-2 text-xs text-slate-200">
        <input type="radio" name="selected-subj" id="subj-${idx}" ${idx === 0 ? 'checked' : ''} class="text-purple-600 focus:ring-purple-500" />
        <label for="subj-${idx}" class="cursor-pointer">${subj}</label>
      </div>
      <button onclick="navigator.clipboard.writeText('${subj.replace(/'/g, "\\'")}')" class="text-[11px] text-slate-500 group-hover:text-purple-400 flex items-center space-x-1">
        <i data-lucide="copy" class="w-3 h-3"></i>
        <span>Copy</span>
      </button>
    `;
    subjContainer.appendChild(item);
  });

  // Render Body
  document.getElementById('email-body-text').value = pkg.email_body || '';

  // Render LinkedIn note
  document.getElementById('linkedin-note-text').innerText = pkg.linkedin_note || 'No note generated.';

  // Render Follow Up
  document.getElementById('follow-up-email-text').innerText = pkg.follow_up_email || 'No follow up generated.';

  if (window.lucide) lucide.createIcons();
}

function getSelectedSubject() {
  const radios = document.querySelectorAll('input[name="selected-subj"]');
  for (let r of radios) {
    if (r.checked) {
      const label = r.parentElement.querySelector('label');
      return label ? label.innerText : '';
    }
  }
  return "Inquiry regarding open role";
}

function copyEmailToClipboard() {
  const body = document.getElementById('email-body-text').value;
  if (!body) return;
  navigator.clipboard.writeText(body).then(() => {
    const textEl = document.getElementById('copy-btn-text');
    textEl.innerText = "Copied!";
    setTimeout(() => { textEl.innerText = "Copy Email"; }, 2000);
  });
}

function copyLinkedInNote() {
  const note = document.getElementById('linkedin-note-text').innerText;
  navigator.clipboard.writeText(note);
  alert("LinkedIn note copied to clipboard!");
}

function copyFollowUpEmail() {
  const followUp = document.getElementById('follow-up-email-text').innerText;
  navigator.clipboard.writeText(followUp);
  alert("Follow-up email copied to clipboard!");
}

function launchEmailClient() {
  const subject = encodeURIComponent(getSelectedSubject());
  const body = encodeURIComponent(document.getElementById('email-body-text').value);
  window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
}

async function saveEmailToFirestore() {
  const recruiter = document.getElementById('email-recruiter-name').value.trim();
  const company = document.getElementById('email-company-name').value.trim();
  const subject = getSelectedSubject();
  const body = document.getElementById('email-body-text').value;
  const tone = document.getElementById('email-tone').value;
  const note = document.getElementById('linkedin-note-text').innerText;

  try {
    const res = await fetch('/api/email/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recruiter_name: recruiter,
        company_name: company,
        subject: subject,
        body: body,
        tone: tone,
        linkedin_note: note
      })
    });

    const data = await res.json();
    if (data.success) {
      alert("Email saved to Google Cloud Firestore successfully!");
    }
  } catch (e) {
    alert("Error saving to Firestore: " + e.message);
  }
}

// =================================================================
// TAB 4: FIRESTORE CLOUD VAULT
// =================================================================

async function refreshVaultData() {
  try {
    // 1. Documents
    const docRes = await fetch('/api/documents/');
    const docData = await docRes.json();
    const docsContainer = document.getElementById('vault-docs-list');
    docsContainer.innerHTML = '';
    
    if (docData.documents && docData.documents.length > 0) {
      docData.documents.forEach(d => {
        const item = document.createElement('div');
        item.className = 'p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1';
        item.innerHTML = `
          <div class="font-bold text-slate-200 truncate">${d.filename}</div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>${d.pages} pages • ${d.word_count} words</span>
            <span class="font-mono text-[10px] text-blue-400">${d.created_at ? d.created_at.substring(0, 10) : ''}</span>
          </div>
        `;
        docsContainer.appendChild(item);
      });
    } else {
      docsContainer.innerHTML = `<div class="text-xs text-slate-500 italic p-3">No documents in vault yet.</div>`;
    }

    // 2. ATS Audits
    const atsRes = await fetch('/api/ats/audits');
    const atsData = await atsRes.json();
    const auditsContainer = document.getElementById('vault-audits-list');
    auditsContainer.innerHTML = '';

    if (atsData.audits && atsData.audits.length > 0) {
      atsData.audits.forEach(a => {
        const score = a.overall_score || 0;
        const color = score >= 80 ? 'text-emerald-400' : (score >= 60 ? 'text-amber-400' : 'text-rose-400');
        const item = document.createElement('div');
        item.className = 'p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1';
        item.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-200 truncate">${a.job_title || 'Role'}</span>
            <span class="font-extrabold ${color}">${score}%</span>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>${a.company_name || 'Company'}</span>
            <span class="text-[10px] text-slate-500">${a.rating || 'Audit'}</span>
          </div>
        `;
        auditsContainer.appendChild(item);
      });
    } else {
      auditsContainer.innerHTML = `<div class="text-xs text-slate-500 italic p-3">No ATS audits evaluated yet.</div>`;
    }

    // 3. Saved Emails
    const emailRes = await fetch('/api/email/saved');
    const emailData = await emailRes.json();
    const emailsContainer = document.getElementById('vault-emails-list');
    emailsContainer.innerHTML = '';

    if (emailData.saved_emails && emailData.saved_emails.length > 0) {
      emailData.saved_emails.forEach(em => {
        const item = document.createElement('div');
        item.className = 'p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1';
        item.innerHTML = `
          <div class="font-bold text-slate-200 truncate">${em.subject}</div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>To: ${em.recruiter_name} (${em.company_name})</span>
            <span class="text-[10px] text-purple-400">${em.tone}</span>
          </div>
        `;
        emailsContainer.appendChild(item);
      });
    } else {
      emailsContainer.innerHTML = `<div class="text-xs text-slate-500 italic p-3">No outreach emails saved yet.</div>`;
    }

  } catch (err) {
    console.error("Failed to load vault data:", err);
  }
}

// Sample Text Helpers
function getSampleResumeText() {
  return `ALEX CHEN
San Francisco, CA | alex.chen@example.com | linkedin.com/in/alexchen-cloud | github.com/alexchen-dev

PROFESSIONAL SUMMARY
Results-driven Cloud & AI Engineer with 4+ years of experience designing, containerizing, and orchestrating distributed systems on Google Cloud Platform. Specialist in asynchronous Python backends (FastAPI), Google Cloud Run microservices, Google Gemini LLM integrations, and NoSQL databases (Firestore). Passionate about building resilient, low-latency AI-driven enterprise applications.

CORE TECHNICAL SKILLS
- Cloud & Infrastructure: Google Cloud Platform (Cloud Run, Cloud Build, Artifact Registry, Cloud Functions), Docker, Kubernetes, Linux, Terraform
- AI & LLM Systems: Google Gemini 2.5 / 1.5 Flash, Multimodal Document AI, LangChain, RAG Pipelines, Prompt Engineering
- Programming & Frameworks: Python 3.11, FastAPI, REST APIs, TypeScript, Node.js, HTML5, Tailwind CSS
- Databases & Storage: Google Cloud Firestore, Firebase Auth, PostgreSQL, Redis, Google Cloud Storage
- CI/CD & DevOps: GitHub Actions, Cloud Build, Docker Compose, Git, Unit Testing (pytest)

PROFESSIONAL EXPERIENCE

Senior Cloud Software Engineer | Apex Solutions Inc. (2022 - Present)
- Architected and deployed serverless microservices on Google Cloud Run serving 120,000+ daily active users with 99.98% uptime.
- Integrated Google Gemini Flash multimodal API into candidate screening platform, reducing document parsing turnaround from 8 minutes to 1.4 seconds.
- Designed Firestore data schemas and security rules ensuring strict tenant isolation across 15,000+ customer records.
- Automated end-to-end CI/CD deployments using Google Cloud Build, reducing software release cycles by 45%.

Cloud Application Developer | DataVanguard Systems (2020 - 2022)
- Built asynchronous RESTful APIs using Python FastAPI and PostgreSQL, handling 2,000 requests/sec during peak traffic.
- Containerized legacy monolithic services with Docker, migrating 12 core services to Google Cloud serverless architecture and cutting monthly cloud compute spend by 28%.
- Collaborated with product and security teams to implement OAuth2 and JWT token authentication.

EDUCATION & CERTIFICATIONS
- B.S. in Computer Science | University of California, Berkeley (2016 - 2020)
- Google Cloud Certified: Professional Cloud Developer
- Google Cloud Certified: Associate Cloud Engineer`;
}

function getSampleJobDescriptionText() {
  return `NextGen Cloud Platforms is hiring a Senior Cloud & AI Solutions Architect to spearhead our next-generation document intelligence suite.

About The Role:
We are looking for an experienced cloud engineer who thrives at the intersection of serverless cloud computing and modern Large Language Models (LLMs). In this role, you will build scalable, production-grade microservices on Google Cloud Run and Vertex AI / Gemini to empower enterprise document workflows.

Key Responsibilities:
- Design, build, and maintain containerized microservices deployed on Google Cloud Run.
- Integrate Google Gemini models for multimodal document extraction, intelligent Q&A, and real-time inference.
- Architect real-time, highly available database layers using Google Cloud Firestore and Firebase.
- Drive CI/CD automation and container orchestration with Docker and Cloud Build.
- Optimize API performance, ensuring sub-second response times and high availability.

Minimum Qualifications:
- 3+ years of professional experience building cloud-native backend services with Python (FastAPI or Flask).
- Hands-on experience deploying containerized workloads to Google Cloud Run or Kubernetes.
- Demonstrated experience integrating LLM APIs (Google Gemini, OpenAI, or Anthropic) into production features.
- Strong proficiency with NoSQL databases, specifically Google Cloud Firestore or Firebase.
- Solid understanding of Docker, container optimization, and modern CI/CD pipelines.

Preferred Qualifications:
- Google Cloud certification (Professional Cloud Architect or Professional Cloud Developer).
- Familiarity with ATS algorithms, resume parsing, or natural language document synthesis.`;
}
