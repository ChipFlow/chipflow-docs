/**
 * ChipFlow Documentation AI Chat Widget
 *
 * A floating chat widget that allows users to ask questions about
 * ChipFlow documentation using an AI-powered backend.
 */
(function() {
  'use strict';

  // Configuration - update this when deploying the backend
  const CONFIG = {
    apiUrl: 'https://chipflow-docs-chat-ixzgvx6kya-uc.a.run.app/api/chat',
    supportUrl: 'https://chipflow-docs-chat-ixzgvx6kya-uc.a.run.app/api/request-support',
    projectName: 'ChipFlow',
    placeholder: 'Ask about ChipFlow docs...',
    welcomeMessage: 'Hi! I can help answer questions about ChipFlow documentation. What would you like to know?'
  };

  // Don't initialize if already loaded
  if (window.chipflowChatLoaded) return;
  window.chipflowChatLoaded = true;

  // Create styles
  const styles = document.createElement('style');
  styles.textContent = `
    #cf-chat-btn {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      padding: 14px 20px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 28px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      font-family: system-ui, -apple-system, sans-serif;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    #cf-chat-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    }
    #cf-chat-btn svg {
      width: 18px;
      height: 18px;
    }
    #cf-chat-modal {
      display: none;
      position: fixed;
      bottom: 90px;
      right: 24px;
      width: 400px;
      max-width: calc(100vw - 48px);
      height: 520px;
      max-height: calc(100vh - 120px);
      background: var(--color-background-primary, #ffffff);
      border-radius: 16px;
      box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
      z-index: 9999;
      flex-direction: column;
      overflow: hidden;
      font-family: system-ui, -apple-system, sans-serif;
    }
    #cf-chat-modal.open {
      display: flex;
    }
    .cf-chat-header {
      padding: 16px 20px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .cf-chat-header h3 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
    }
    .cf-chat-close {
      background: rgba(255,255,255,0.2);
      border: none;
      color: white;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
    }
    .cf-chat-close:hover {
      background: rgba(255,255,255,0.3);
    }
    .cf-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .cf-msg {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 14px;
      line-height: 1.5;
      word-wrap: break-word;
    }
    .cf-msg-user {
      align-self: flex-end;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      border-bottom-right-radius: 4px;
    }
    .cf-msg-assistant {
      align-self: flex-start;
      background: var(--color-background-secondary, #f3f4f6);
      color: var(--color-foreground-primary, #1f2937);
      border-bottom-left-radius: 4px;
    }
    .cf-msg-assistant a {
      color: #6366f1;
    }
    .cf-msg-error {
      background: #fef2f2;
      color: #991b1b;
    }
    .cf-msg-loading {
      display: flex;
      gap: 4px;
      padding: 12px 16px;
    }
    .cf-msg-loading span {
      width: 8px;
      height: 8px;
      background: #9ca3af;
      border-radius: 50%;
      animation: cf-bounce 1.4s infinite ease-in-out both;
    }
    .cf-msg-loading span:nth-child(1) { animation-delay: -0.32s; }
    .cf-msg-loading span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes cf-bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
    .cf-chat-input-area {
      padding: 12px 16px;
      border-top: 1px solid var(--color-background-border, #e5e7eb);
      display: flex;
      gap: 8px;
    }
    .cf-chat-input {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid var(--color-background-border, #d1d5db);
      border-radius: 8px;
      font-size: 14px;
      outline: none;
      background: var(--color-background-primary, #ffffff);
      color: var(--color-foreground-primary, #1f2937);
    }
    .cf-chat-input:focus {
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    .cf-chat-send {
      padding: 10px 16px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: opacity 0.2s;
    }
    .cf-chat-send:hover {
      opacity: 0.9;
    }
    .cf-chat-send:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .cf-powered-by {
      padding: 8px 16px;
      text-align: center;
      font-size: 11px;
      color: var(--color-foreground-muted, #6b7280);
      border-top: 1px solid var(--color-background-border, #e5e7eb);
    }
    .cf-powered-by a {
      color: #6366f1;
      text-decoration: none;
    }
    .cf-support-btn {
      display: block;
      width: 100%;
      padding: 8px 12px;
      margin-top: 8px;
      background: transparent;
      border: 1px solid #6366f1;
      color: #6366f1;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      transition: all 0.2s;
    }
    .cf-support-btn:hover {
      background: rgba(99, 102, 241, 0.1);
    }
    .cf-support-form {
      display: none;
      padding: 16px;
      flex-direction: column;
      gap: 12px;
    }
    .cf-support-form.open {
      display: flex;
    }
    .cf-support-form label {
      font-size: 12px;
      font-weight: 500;
      color: var(--color-foreground-primary, #374151);
    }
    .cf-support-form input,
    .cf-support-form textarea {
      padding: 8px 12px;
      border: 1px solid var(--color-background-border, #d1d5db);
      border-radius: 6px;
      font-size: 13px;
      background: var(--color-background-primary, #ffffff);
      color: var(--color-foreground-primary, #1f2937);
    }
    .cf-support-form input:focus,
    .cf-support-form textarea:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
    }
    .cf-support-form textarea {
      min-height: 80px;
      resize: vertical;
    }
    .cf-support-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
    }
    .cf-support-cancel {
      padding: 8px 16px;
      background: transparent;
      border: 1px solid var(--color-background-border, #d1d5db);
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      color: var(--color-foreground-primary, #374151);
    }
    .cf-support-submit {
      padding: 8px 16px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
    }
    .cf-support-submit:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .cf-support-success {
      color: #059669;
      font-size: 13px;
      text-align: center;
      padding: 12px;
    }
  `;
  document.head.appendChild(styles);

  // Create chat button
  const chatBtn = document.createElement('button');
  chatBtn.id = 'cf-chat-btn';
  chatBtn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    Ask AI
  `;

  // Create chat modal
  const chatModal = document.createElement('div');
  chatModal.id = 'cf-chat-modal';
  chatModal.innerHTML = `
    <div class="cf-chat-header">
      <h3>${CONFIG.projectName} Docs AI</h3>
      <button class="cf-chat-close" aria-label="Close chat">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"></path>
        </svg>
      </button>
    </div>
    <div class="cf-chat-messages" id="cf-chat-messages"></div>
    <div class="cf-support-form" id="cf-support-form">
      <label>Your Email</label>
      <input type="email" id="cf-support-email" placeholder="you@example.com" required>
      <label>Subject</label>
      <input type="text" id="cf-support-subject" placeholder="Brief description of your issue">
      <label>Message</label>
      <textarea id="cf-support-message" placeholder="Please describe what you need help with..."></textarea>
      <div class="cf-support-actions">
        <button class="cf-support-cancel" id="cf-support-cancel">Cancel</button>
        <button class="cf-support-submit" id="cf-support-submit">Send to Support</button>
      </div>
    </div>
    <div class="cf-chat-input-area" id="cf-chat-input-area">
      <input type="text" class="cf-chat-input" id="cf-chat-input" placeholder="${CONFIG.placeholder}">
      <button class="cf-chat-send" id="cf-chat-send">Send</button>
    </div>
    <div class="cf-powered-by">
      <button class="cf-support-btn" id="cf-support-btn">Contact Support</button>
    </div>
  `;

  document.body.appendChild(chatBtn);
  document.body.appendChild(chatModal);

  // Get elements
  const messagesContainer = document.getElementById('cf-chat-messages');
  const inputField = document.getElementById('cf-chat-input');
  const inputArea = document.getElementById('cf-chat-input-area');
  const sendBtn = document.getElementById('cf-chat-send');
  const closeBtn = chatModal.querySelector('.cf-chat-close');
  const supportBtn = document.getElementById('cf-support-btn');
  const supportForm = document.getElementById('cf-support-form');
  const supportEmail = document.getElementById('cf-support-email');
  const supportSubject = document.getElementById('cf-support-subject');
  const supportMessage = document.getElementById('cf-support-message');
  const supportCancel = document.getElementById('cf-support-cancel');
  const supportSubmit = document.getElementById('cf-support-submit');

  // State
  let isOpen = false;
  let isLoading = false;
  let isSupportFormOpen = false;
  let conversationHistory = [];

  // Add welcome message
  function addWelcomeMessage() {
    if (messagesContainer.children.length === 0) {
      addMessage(CONFIG.welcomeMessage, 'assistant');
    }
  }

  // Track event to Google Analytics
  function trackChatEvent(eventName, params = {}) {
    if (typeof gtag === 'function') {
      gtag('event', eventName, { ...params, source: 'docs' });
    }
  }

  // Toggle chat
  function toggleChat() {
    isOpen = !isOpen;
    chatModal.classList.toggle('open', isOpen);
    if (isOpen) {
      addWelcomeMessage();
      inputField.focus();
      trackChatEvent('ai_chat_opened', { page: window.location.pathname });
    } else {
      // Close support form when closing chat
      if (isSupportFormOpen) {
        toggleSupportForm(false);
      }
    }
  }

  // Add message to chat
  function addMessage(text, role, isError = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `cf-msg cf-msg-${role}${isError ? ' cf-msg-error' : ''}`;

    // Simple markdown-like formatting for links
    const formattedText = text.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    );
    msgDiv.innerHTML = formattedText;

    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return msgDiv;
  }

  // Add loading indicator
  function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'cf-msg cf-msg-assistant cf-msg-loading';
    loadingDiv.id = 'cf-loading';
    loadingDiv.innerHTML = '<span></span><span></span><span></span>';
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Remove loading indicator
  function removeLoading() {
    const loading = document.getElementById('cf-loading');
    if (loading) loading.remove();
  }

  // Send message
  async function sendMessage() {
    const question = inputField.value.trim();
    if (!question || isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;
    inputField.value = '';

    addMessage(question, 'user');
    addLoading();

    // Track question
    trackChatEvent('ai_chat_question', {
      question_length: question.length,
      question_preview: question.substring(0, 100),
      page: window.location.pathname
    });

    try {
      const response = await fetch(CONFIG.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          conversation_history: conversationHistory,
          page: window.location.pathname
        })
      });

      removeLoading();

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      addMessage(data.answer, 'assistant');

      // Track successful response
      trackChatEvent('ai_chat_response', {
        response_length: data.answer.length,
        page: window.location.pathname
      });

      // Update conversation history
      conversationHistory.push(
        { role: 'user', content: question },
        { role: 'assistant', content: data.answer }
      );

      // Keep history manageable
      if (conversationHistory.length > 10) {
        conversationHistory = conversationHistory.slice(-10);
      }

    } catch (error) {
      removeLoading();
      console.error('Chat error:', error);
      addMessage(
        'Sorry, I encountered an error. Please try again later.',
        'assistant',
        true
      );

      // Track error
      trackChatEvent('ai_chat_error', {
        error_message: error.message || 'Unknown error',
        page: window.location.pathname
      });
    } finally {
      isLoading = false;
      sendBtn.disabled = false;
      inputField.focus();
    }
  }

  // Toggle support form
  function toggleSupportForm(show) {
    isSupportFormOpen = show;
    supportForm.classList.toggle('open', show);
    inputArea.style.display = show ? 'none' : 'flex';
    messagesContainer.style.display = show ? 'none' : 'flex';
    if (show) {
      supportEmail.focus();
    } else {
      inputField.focus();
    }
  }

  // Submit support request
  async function submitSupportRequest() {
    const email = supportEmail.value.trim();
    const subject = supportSubject.value.trim() || 'Support request from docs chat';
    const message = supportMessage.value.trim();

    if (!email || !message) {
      alert('Please provide your email and message.');
      return;
    }

    supportSubmit.disabled = true;
    supportSubmit.textContent = 'Sending...';

    try {
      const response = await fetch(CONFIG.supportUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          subject,
          message,
          conversation_history: conversationHistory,
          page: window.location.pathname
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Show success message
      toggleSupportForm(false);
      addMessage(data.message, 'assistant');

      // Clear form
      supportEmail.value = '';
      supportSubject.value = '';
      supportMessage.value = '';

      trackChatEvent('support_request_sent', { page: window.location.pathname });

    } catch (error) {
      console.error('Support request error:', error);
      alert('Failed to send support request. Please try again or email support@chipflow.io directly.');
      trackChatEvent('support_request_error', { error: error.message });
    } finally {
      supportSubmit.disabled = false;
      supportSubmit.textContent = 'Send to Support';
    }
  }

  // Event listeners
  chatBtn.addEventListener('click', toggleChat);
  closeBtn.addEventListener('click', toggleChat);
  sendBtn.addEventListener('click', sendMessage);
  supportBtn.addEventListener('click', () => toggleSupportForm(true));
  supportCancel.addEventListener('click', () => toggleSupportForm(false));
  supportSubmit.addEventListener('click', submitSupportRequest);
  inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Close on escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      toggleChat();
    }
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (isOpen && !chatModal.contains(e.target) && !chatBtn.contains(e.target)) {
      toggleChat();
    }
  });

})();
