/**
 * Modern JavaScript for Calc Tutor
 * ES6+ modules, no jQuery dependency
 */

// Chat functionality
class ChatBot {
    constructor(containerSelector, apiUrl) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) return;
        
        this.apiUrl = apiUrl;
        this.chatLog = this.container.querySelector('.chat-log');
        this.input = this.container.querySelector('.chat-input input');
        this.sendBtn = this.container.querySelector('.chat-input button');
        
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
        msg.textContent = text;
        this.chatLog?.appendChild(msg);
        this.chatLog?.scrollTo(0, this.chatLog.scrollHeight);
    }
    
    async send() {
        const text = this.input?.value.trim();
        if (!text) return;
        
        this.addMessage(text, true);
        this.input.value = '';
        
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            if (!response.ok) throw new Error('Network error');
            
            const data = await response.json();
            this.addMessage(data.text || 'Sorry, I didn\'t understand that.');
        } catch (err) {
            console.error('Chat error:', err);
            this.addMessage('Sorry, something went wrong. Please try again.');
        }
    }
}

// Modal functionality
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

// Collapsible sections
class Collapsible {
    constructor(selector = '.collapsible') {
        this.initCollapsibles(document.querySelectorAll(selector));
    }
    
    initCollapsibles(elements) {
        elements.forEach(el => {
            // Find the h2 that is a direct child of this collapsible
            const header = el.querySelector(':scope > h2');
            if (!header) return;
            
            // Skip if already initialized
            if (header.dataset.initialized) return;
            header.dataset.initialized = 'true';
            
            // Make sure the header is clickable
            header.style.cursor = 'pointer';
            
            header.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                el.classList.toggle('open');
                const text = header.textContent.trim();
                if (el.classList.contains('open')) {
                    header.textContent = text.replace('Show', 'Hide');
                } else {
                    header.textContent = text.replace('Hide', 'Show');
                }
            });
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
                    
                    // Initialize collapsibles in the new content
                    output.querySelectorAll('.collapsible').forEach(el => {
                        const header = el.querySelector(':scope > h2');
                        if (!header || header.dataset.initialized) return;
                        header.dataset.initialized = 'true';
                        header.style.cursor = 'pointer';
                        
                        header.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            el.classList.toggle('open');
                            const text = header.textContent.trim();
                            if (el.classList.contains('open')) {
                                header.textContent = text.replace('Show', 'Hide');
                            } else {
                                header.textContent = text.replace('Hide', 'Show');
                            }
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

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const chatModal = new Modal('#chatModal', '[data-chat-trigger]');
    // Use URL from template or fall back to default
    const chatBotUrl = window.CHATBOT_URL || '/api/chatbot/';
    const chatBot = new ChatBot('#chatModal', chatBotUrl);
    
    // Initialize collapsibles
    const collapsible = new Collapsible();
    
    // Initialize card loader
    new CardLoader();
    
    // Convert legacy math notation
    convertLegacyMath();
    
    // Re-initialize collapsibles after a short delay to catch any late-rendered content
    setTimeout(() => {
        collapsible.initCollapsibles(document.querySelectorAll('.collapsible'));
    }, 500);
});
