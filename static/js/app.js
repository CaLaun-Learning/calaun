/**
 * Modern JavaScript for Calc Tutor
 * ES6+ modules, no jQuery dependency
 */

// Chat functionality
class ChatBot {
    constructor(containerSelector, apiUrl, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) return;
        
        this.apiUrl = apiUrl;
        this.chatLog = this.container.querySelector('.chat-log');
        this.input = this.container.querySelector('.chat-input input');
        this.sendBtn = this.container.querySelector('.chat-input button');
        
        // LLM mode options
        this.useLLM = options.useLLM || false;
        this.stepsSelector = options.stepsSelector || '#resultsContainer';
        this.conversationHistory = [];
        
        this.init();
    }
    
    init() {
        this.sendBtn?.addEventListener('click', () => this.send());
        this.input?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.send();
        });
    }
    
    addMessage(text, isUser = false) {
        const msg = document.createElement('div');
        msg.className = `chat-message chat-message--${isUser ? 'user' : 'bot'}`;
        
        // For bot messages, render potential LaTeX
        if (!isUser && window.MathJax) {
            msg.innerHTML = text;
            MathJax.typesetPromise([msg]).catch(err => console.log('MathJax error:', err));
        } else {
            msg.textContent = text;
        }
        
        this.chatLog?.appendChild(msg);
        this.chatLog?.scrollTo(0, this.chatLog.scrollHeight);
        
        // Track conversation history for LLM mode
        if (this.useLLM) {
            this.conversationHistory.push({
                role: isUser ? 'user' : 'assistant',
                content: text
            });
            // Keep only last 10 messages
            if (this.conversationHistory.length > 10) {
                this.conversationHistory = this.conversationHistory.slice(-10);
            }
        }
    }
    
    getStepsContext() {
        const stepsContainer = document.querySelector(this.stepsSelector);
        return stepsContainer ? stepsContainer.innerHTML : '';
    }
    
    async send() {
        const text = this.input?.value.trim();
        if (!text) return;
        
        this.addMessage(text, true);
        this.input.value = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-message chat-message--bot chat-message--typing';
        typingIndicator.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
        this.chatLog?.appendChild(typingIndicator);
        this.chatLog?.scrollTo(0, this.chatLog.scrollHeight);
        
        try {
            // Build request body
            const body = { text };
            
            if (this.useLLM) {
                body.steps = this.getStepsContext();
                body.history = this.conversationHistory.slice(0, -1); // Exclude current message
            }
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (!response.ok) throw new Error('Network error');
            
            const data = await response.json();
            const responseText = Array.isArray(data.text) ? data.text[0] : data.text;
            this.addMessage(responseText || 'Sorry, I didn\'t understand that.');
        } catch (err) {
            typingIndicator.remove();
            console.error('Chat error:', err);
            this.addMessage('Sorry, something went wrong. Please try again.');
        }
    }
}

// Modal functionality (kept for legacy/mobile support)
class Modal {
    constructor(modalSelector, triggerSelector) {
        this.modal = document.querySelector(modalSelector);
        this.triggers = document.querySelectorAll(triggerSelector);
        this.closeBtn = this.modal?.querySelector('.modal__close');
        
        this.init();
    }
    
    init() {
        this.triggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
            });
        });
        
        this.closeBtn?.addEventListener('click', () => this.close());
        
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.close();
        });
    }
    
    open() {
        this.modal?.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.modal?.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Chat Sidebar functionality
class ChatSidebar {
    constructor(sidebarSelector, triggerSelector) {
        this.sidebar = document.querySelector(sidebarSelector);
        this.triggers = document.querySelectorAll(triggerSelector);
        
        if (!this.sidebar) return;
        
        this.init();
    }
    
    init() {
        this.triggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar.classList.contains('open')) {
                this.close();
            }
        });
    }
    
    toggle() {
        if (this.sidebar.classList.contains('open')) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.sidebar.classList.add('open');
        // Focus the input when opening
        const input = this.sidebar.querySelector('.chat-input input');
        if (input) {
            setTimeout(() => input.focus(), 300);
        }
    }
    
    close() {
        this.sidebar.classList.remove('open');
    }
}

// Collapsible steps - click on step to toggle math visibility
class Collapsible {
    constructor(selector = '.step.collapsible') {
        this.selector = selector;
        this.allExpanded = false;
        this.initCollapsibles(document.querySelectorAll(selector));
        this.initToggleAllButton();
    }
    
    initCollapsibles(elements) {
        elements.forEach(el => {
            // Skip if already initialized
            if (el.dataset.initialized) return;
            el.dataset.initialized = 'true';
            
            // Make the whole step clickable
            el.style.cursor = 'pointer';
            
            el.addEventListener('click', (e) => {
                // Don't toggle if clicking on a link or nested step
                if (e.target.closest('a') || (e.target.closest('.step') !== el)) {
                    return;
                }
                e.preventDefault();
                e.stopPropagation();
                el.classList.toggle('open');
            });
        });
    }
    
    initToggleAllButton() {
        const btn = document.getElementById('toggleAllSteps');
        if (!btn) return;
        
        btn.addEventListener('click', () => {
            this.allExpanded = !this.allExpanded;
            const steps = document.querySelectorAll(this.selector);
            
            steps.forEach(step => {
                if (this.allExpanded) {
                    step.classList.add('open');
                } else {
                    step.classList.remove('open');
                }
            });
            
            btn.textContent = this.allExpanded ? 'Hide all steps' : 'Show all steps';
            
            // Re-render MathJax for newly visible content
            if (this.allExpanded && window.MathJax?.typesetPromise) {
                MathJax.typesetPromise();
            }
        });
    }
}

// Card loader (for async card content)
class CardLoader {
    constructor() {
        this.loadCards();
    }
    
    async loadCards() {
        const cards = document.querySelectorAll('[data-card-name]');
        
        for (const card of cards) {
            const cardName = card.dataset.cardName;
            const variable = card.dataset.variable || '';
            const expr = card.dataset.expr || '';
            const params = card.dataset.parameters;
            
            if (!cardName) continue;
            
            try {
                // Build URL with query parameters (matching old card.js behavior)
                const searchParams = new URLSearchParams({
                    variable: variable,
                    expression: expr
                });
                
                // Add any additional parameters
                if (params) {
                    try {
                        const extraParams = JSON.parse(params);
                        Object.entries(extraParams).forEach(([k, v]) => {
                            searchParams.append(k, v);
                        });
                    } catch (e) {
                        console.warn('Failed to parse card parameters:', e);
                    }
                }
                
                const url = `/card/${cardName}?${searchParams.toString()}`;
                const response = await fetch(url);
                
                if (!response.ok) throw new Error('Failed to load card');
                
                const data = await response.json();
                const loader = card.querySelector('.loader');
                if (loader) loader.remove();
                
                if (data.output) {
                    const output = document.createElement('div');
                    output.innerHTML = data.output;
                    card.appendChild(output);
                    
                    // Initialize collapsible steps in the new content
                    output.querySelectorAll('.step.collapsible').forEach(el => {
                        if (el.dataset.initialized) return;
                        el.dataset.initialized = 'true';
                        el.style.cursor = 'pointer';
                        
                        el.addEventListener('click', (e) => {
                            if (e.target.closest('a') || (e.target.closest('.step') !== el)) {
                                return;
                            }
                            e.preventDefault();
                            e.stopPropagation();
                            el.classList.toggle('open');
                        });
                    });
                } else if (data.error) {
                    const error = document.createElement('div');
                    error.className = 'card__error-message';
                    error.textContent = data.error;
                    card.appendChild(error);
                }
                
                // Re-render MathJax
                if (window.MathJax?.typesetPromise) {
                    await MathJax.typesetPromise([card]);
                }
            } catch (err) {
                console.error('Card load error:', err);
                const loader = card.querySelector('.loader');
                if (loader) {
                    loader.textContent = 'Error loading content';
                    loader.className = 'error';
                }
            }
        }
    }
}

// MathJax compatibility for old script tags
function convertLegacyMath() {
    // Convert old script[type="math/tex"] to modern format
    document.querySelectorAll('script[type="math/tex"]').forEach(script => {
        const isDisplay = script.type.includes('mode=display');
        const math = script.textContent;
        const span = document.createElement('span');
        span.innerHTML = isDisplay ? `\\[${math}\\]` : `\\(${math}\\)`;
        script.replaceWith(span);
    });
    
    // Trigger MathJax rendering
    if (window.MathJax?.typesetPromise) {
        MathJax.typesetPromise();
    }
}

// Tab switching functionality
class TabSwitcher {
    constructor(tabSelector = '.tab', panelSelector = '.examples-panel') {
        this.tabs = document.querySelectorAll(tabSelector);
        this.panels = document.querySelectorAll(panelSelector);
        
        if (this.tabs.length === 0) return;
        
        this.init();
    }
    
    init() {
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.tab;
                
                // Update active tab
                this.tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update active panel
                this.panels.forEach(panel => {
                    panel.classList.remove('active');
                    if (panel.id === target) {
                        panel.classList.add('active');
                    }
                });
            });
        });
    }
}

// Back to top button
class BackToTop {
    constructor(selector = '.back-to-top') {
        this.button = document.querySelector(selector);
        if (!this.button) return;
        
        this.init();
    }
    
    init() {
        // Show/hide based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                this.button.classList.add('visible');
            } else {
                this.button.classList.remove('visible');
            }
        });
        
        // Smooth scroll to top
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize chat sidebar (new style)
    const chatSidebar = new ChatSidebar('#chatSidebar', '[data-chat-trigger]');
    
    // Use URL from template or fall back to default
    const chatBotUrl = window.CHATBOT_URL || '/api/chatbot/';
    const useLLM = window.USE_LLM_CHATBOT || false;
    
    // Initialize chatbot with sidebar container
    const chatBot = new ChatBot('#chatSidebar', chatBotUrl, {
        useLLM: useLLM,
        stepsSelector: '#resultsContainer'
    });
    
    // Initialize collapsibles
    const collapsible = new Collapsible();
    
    // Initialize card loader
    new CardLoader();
    
    // Convert legacy math notation
    convertLegacyMath();
    
    // Initialize tabs
    new TabSwitcher();
    
    // Initialize back to top button
    new BackToTop();
    
    // Re-initialize collapsibles after a short delay to catch any late-rendered content
    setTimeout(() => {
        collapsible.initCollapsibles(document.querySelectorAll('.step.collapsible'));
    }, 500);
});
