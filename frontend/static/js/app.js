/**
 * Frontend application logic for AI Chatbot Assistant
 * Connects to Flask REST API: /api/chat, /api/history/:id, /api/sessions, /api/health
 */

const API_BASE = '/api';
const LS_SESSION_KEY = 'ai_chatbot_current_session_id';

const els = {
  messagesContainer: document.getElementById('messagesContainer'),
  messageInput: document.getElementById('messageInput'),
  sendBtn: document.getElementById('sendBtn'),
  clearChatBtn: document.getElementById('clearChatBtn'),
  newChatBtn: document.getElementById('newChatBtn'),
  typingIndicator: document.getElementById('typingIndicator'),
  sidebar: document.getElementById('sidebar'),
  sessionList: document.getElementById('sessionList'),
  emptyState: document.getElementById('emptyState'),
  sidebarToggle: document.getElementById('sidebarToggle'),
  sidebarClose: document.getElementById('sidebarClose'),
  sidebarBackdrop: document.getElementById('sidebarBackdrop'),
  micBtn: document.getElementById('micBtn'),
};

let currentSessionId = localStorage.getItem(LS_SESSION_KEY) || '';
let isProcessing = false;
let recognition = null;
let voiceUnsupported = false;

const FAQ_MATCHES = [
  { keywords: ['pricing', 'plan', 'cost', 'quote'], title: 'Pricing', body: 'We offer starter, growth, and enterprise plans. Want me to compare them?' },
  { keywords: ['hours', 'support', 'available', 'office'], title: 'Support Hours', body: 'Support is available Monday–Friday, 9am–6pm EST.' },
  { keywords: ['contact', 'email', 'phone', 'reach'], title: 'Contact', body: 'You can reach us at support@example.com or through the contact form.' },
  { keywords: ['help', 'how', 'get started'], title: 'Getting Started', body: 'Start by typing a question here. I can help with setup, FAQs, or general guidance.' },
];

function formatTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

function appendMessage(role, content, timestamp) {
  if (els.emptyState) {
    els.emptyState.style.display = 'none';
  }

  const row = document.createElement('div');
  row.className = `message-row ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';

  const text = document.createElement('div');
  text.textContent = content;

  const meta = document.createElement('div');
  meta.className = 'message-meta';
  meta.textContent = timestamp ? formatTime(timestamp) : '';

  bubble.appendChild(text);
  if (meta.textContent) bubble.appendChild(meta);
  row.appendChild(bubble);
  els.messagesContainer.appendChild(row);

  els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
}

function showTyping(show) {
  els.typingIndicator.classList.toggle('active', show);
}

function setProcessing(state) {
  isProcessing = state;
  els.sendBtn.disabled = state;
  els.messageInput.disabled = state;
  showTyping(state);
}

function appendFaqMatches(matches) {
  if (!matches.length) return;
  const row = document.createElement('div');
  row.className = 'message-row assistant';
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble faq-match';

  const title = document.createElement('div');
  title.className = 'faq-title';
  title.textContent = 'Matched FAQs';

  const list = document.createElement('div');
  list.className = 'faq-list';
  for (const m of matches) {
    const item = document.createElement('div');
    item.className = 'faq-item';
    item.innerHTML = `<strong>${m.title}</strong><div>${m.body}</div>`;
    list.appendChild(item);
  }

  bubble.appendChild(title);
  bubble.appendChild(list);
  row.appendChild(bubble);
  els.messagesContainer.appendChild(row);
  els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
}

function matchesFaqs(text) {
  const normalized = text.toLowerCase();
  const matched = [];
  for (const entry of FAQ_MATCHES) {
    if (entry.keywords.some((kw) => normalized.includes(kw.toLowerCase()))) {
      matched.push(entry);
    }
  }
  return matched;
}

async function sendMessage() {
  const text = els.messageInput.value.trim();
  if (!text || isProcessing) return;

  els.messageInput.value = '';
  els.messageInput.style.height = 'auto';

  appendMessage('user', text, new Date().toISOString());
  const matched = matchesFaqs(text);

  if (matched.length) {
    appendFaqMatches(matched);
  }

  setProcessing(true);

  try {
    const payload = { message: text };
    if (currentSessionId) payload.session_id = currentSessionId;
    if (matched.length) payload.faq_matches = matched.map((m) => m.title + ': ' + m.body);

    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || `HTTP ${response.status}`);
    }

    currentSessionId = data.session_id || currentSessionId;
    localStorage.setItem(LS_SESSION_KEY, currentSessionId);

    appendMessage('assistant', data.response, new Date().toISOString());
    await loadSessions();
    highlightActiveSession();
  } catch (error) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = error.message || 'Something went wrong.';
    els.messagesContainer.appendChild(toast);

    console.error('Chat error:', error);
  } finally {
    setProcessing(false);
    els.messageInput.focus();
  }
}

async function loadHistory(sessionId) {
  currentSessionId = sessionId;
  localStorage.setItem(LS_SESSION_KEY, sessionId);
  els.messagesContainer.innerHTML = '';

  try {
    const response = await fetch(`${API_BASE}/history/${encodeURIComponent(sessionId)}`);
    if (!response.ok) return;

    const data = await response.json();
    if (!data.success || !data.messages?.length) {
      els.emptyState.style.display = 'block';
      return;
    }

    els.emptyState.style.display = 'none';
    for (const msg of data.messages) {
      appendMessage(msg.role, msg.content, msg.timestamp);
    }
  } catch (error) {
    console.error('Failed to load history:', error);
  } finally {
    highlightActiveSession();
  }
}

async function loadSessions() {
  try {
    const response = await fetch(`${API_BASE}/sessions`);
    const data = await response.json();

    els.sessionList.innerHTML = '';

    const sessions = data.sessions || [];
    if (!sessions.length) {
      els.sessionList.innerHTML = '<div style="padding:16px;color:#6b7280;font-size:13px">No sessions yet.</div>';
      return;
    }

    for (const s of sessions) {
      const item = document.createElement('div');
      item.className = 'session-item';
      if (s.id === currentSessionId) item.classList.add('active');
      item.dataset.sessionId = s.id;
      item.innerHTML = `
        <div class="session-title">Chat ${s.id.slice(0, 8)}...</div>
        <div class="session-meta">${new Date(s.updated_at).toLocaleString()}</div>
      `;
      item.addEventListener('click', () => {
        loadHistory(s.id);
        closeSidebar();
      });
      els.sessionList.appendChild(item);
    }
  } catch (error) {
    console.error('Failed to load sessions:', error);
  }
}

function highlightActiveSession() {
  els.sessionList.querySelectorAll('.session-item').forEach((item) => {
    item.classList.toggle('active', item.dataset.sessionId === currentSessionId);
  });
}

function openSidebar() {
  els.sidebar.classList.add('open');
  els.sidebarBackdrop.classList.add('open');
}

function closeSidebar() {
  els.sidebar.classList.remove('open');
  els.sidebarBackdrop.classList.remove('open');
}

function setMicState(state) {
  if (!els.micBtn) return;
  els.micBtn.classList.remove('mic-listen', 'mic-error');
  if (state) els.micBtn.classList.add(state);
}

function startDictation() {
  try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (recognition && isProcessing) return;

    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setMicState('mic-listen');
    };

    recognition.onresult = (event) => {
      const result = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join('');
      els.messageInput.value = result;
      els.messageInput.style.height = 'auto';
      els.messageInput.style.height = Math.min(els.messageInput.scrollHeight, 180) + 'px';

      if (event.results[0].isFinal) {
        sendMessage();
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setMicState('mic-error');
    };

    recognition.onend = () => {
      setMicState('');
    };

    recognition.start();
  } catch (error) {
    console.error('Voice input error:', error);
    setMicState('mic-error');
  }
}

function init() {
  els.sendBtn.addEventListener('click', sendMessage);
  els.messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  els.newChatBtn.addEventListener('click', () => {
    currentSessionId = '';
    localStorage.removeItem(LS_SESSION_KEY);
    els.messagesContainer.innerHTML = '';
    els.messagesContainer.appendChild(els.emptyState);
    els.emptyState.style.display = 'block';
    loadSessions();
  });

  els.clearChatBtn.addEventListener('click', async () => {
    if (!currentSessionId) return;
    if (!confirm('Clear this chat history?')) return;

    await fetch(`${API_BASE}/history/${encodeURIComponent(currentSessionId)}`, { method: 'DELETE' });
    currentSessionId = '';
    localStorage.removeItem(LS_SESSION_KEY);
    els.messagesContainer.innerHTML = '';
    els.messagesContainer.appendChild(els.emptyState);
    els.emptyState.style.display = 'block';
    loadSessions();
  });

  if (els.sidebarToggle) {
    els.sidebarToggle.addEventListener('click', openSidebar);
  }
  if (els.sidebarClose) {
    els.sidebarClose.addEventListener('click', closeSidebar);
  }
  if (els.sidebarBackdrop) {
    els.sidebarBackdrop.addEventListener('click', closeSidebar);
  }

  if (els.micBtn) {
    els.micBtn.disabled = false;
    els.micBtn.title = 'Voice Input';
    els.micBtn.addEventListener('click', () => {
      if (!recognition) startDictation();
      else if (isProcessing) return;
      else recognition.start();
    });
  }

  loadSessions();
  highlightActiveSession();

  if (currentSessionId) {
    loadHistory(currentSessionId);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
