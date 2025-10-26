/**
 * CareBridge Voiceover System
 * Provides text-to-speech functionality and accessibility controls
 */

class VoiceoverSystem {
    constructor() {
        this.isPlaying = false;
        this.currentAudio = null;
        this.autoReadEnabled = localStorage.getItem('autoReadEnabled') === 'true';
        this.speechRate = parseFloat(localStorage.getItem('speechRate') || '1.0');
        this.volume = parseFloat(localStorage.getItem('volume') || '1.0');
        
        // --- DICTATION PROPERTIES ---
        this.isDictating = false;
        this.speechRecognition = null;
        this.initSpeechRecognition();
        // ----------------------------
        
        this.init();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.speechRecognition = new SpeechRecognition();
            this.speechRecognition.interimResults = false;
            this.speechRecognition.continuous = false; // Dictation should stop after a complete phrase
            this.speechRecognition.lang = 'en-US';
            
            this.speechRecognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                
                this.insertDictationText(transcript);
            };
            
            this.speechRecognition.onend = () => {
                this.stopDictation(false); // Update state, but don't explicitly call stop() again
            };

            this.speechRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopDictation(false);
                this.announceToScreenReader('Dictation failed or was cancelled');
            };

            console.log('✅ Speech Recognition initialized');
        } else {
            console.warn('⚠️ Web Speech API (SpeechRecognition) not supported in this browser.');
        }
    }
    
    init() {
        this.createControlPanel();
        this.attachEventListeners();
        this.makeContentReadable();
        
        // Auto-read page content if enabled
        if (this.autoReadEnabled) {
            setTimeout(() => this.readPageContent(), 1000);
        }
        
        // Add keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        this.makeInputsDictationReady();

        console.log('✅ Voiceover system initialized');
    }
    
    createControlPanel() {
        // Create floating control panel
        const panel = document.createElement('div');
        panel.id = 'voiceover-control-panel';
        panel.className = 'voiceover-panel';
        panel.setAttribute('role', 'region');
        panel.setAttribute('aria-label', 'Voice controls');
        
        panel.innerHTML = `
            <div class="voiceover-header">
                <h3>🔊 Voice Controls</h3>
                <button id="voiceover-minimize" class="btn-icon" aria-label="Minimize voice controls">−</button>
            </div>
            <div class="voiceover-body">
                <div class="control-group">
                    <button id="read-page" class="btn-voice" aria-label="Read entire page aloud">
                        <span class="icon">📖</span> Read Page
                    </button>
                    <button id="stop-reading" class="btn-voice" aria-label="Stop reading" disabled>
                        <span class="icon">⏹</span> Stop
                    </button>
                </div>

                ${this.speechRecognition ? `
                    <div class="control-group">
                        <button id="start-dictation" class="btn-dictation" aria-label="Start voice dictation for form inputs">
                            <span class="icon">🎤</span> Voice Dictation
                        </button>
                    </div>
                ` : `<p class="unsupported-feature">⚠️ Dictation not supported</p>`}
                <div class="control-group">
                    <label for="speech-rate">
                        Speed: <span id="rate-value">${this.speechRate.toFixed(1)}x</span>
                    </label>
                    <input type="range" id="speech-rate" min="0.5" max="2.0" step="0.1" 
                           value="${this.speechRate}" aria-label="Speech speed control">
                </div>
                
                <div class="control-group">
                    <label for="volume-control">
                        Volume: <span id="volume-value">${Math.round(this.volume * 100)}%</span>
                    </label>
                    <input type="range" id="volume-control" min="0" max="1" step="0.1" 
                           value="${this.volume}" aria-label="Volume control">
                </div>
                
                <div class="control-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="auto-read" ${this.autoReadEnabled ? 'checked' : ''}>
                        <span>Auto-read new pages</span>
                    </label>
                </div>
                
                <div class="keyboard-shortcuts">
                    <small>Keyboard shortcuts:</small>
                    <ul>
                        <li><kbd>Ctrl+Shift+R</kbd> - Read page</li>
                        <li><kbd>Ctrl+Shift+S</kbd> - Stop reading</li>
                        <li><kbd>Ctrl+Shift+D</kbd> - Toggle Dictation</li>
                        <li><kbd>Ctrl+Shift+H</kbd> - Toggle panel</li>
                    </ul>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
    }
    
    attachEventListeners() {
        // Read page button
        document.getElementById('read-page')?.addEventListener('click', () => {
            this.readPageContent();
        });
        
        // Stop button
        document.getElementById('stop-reading')?.addEventListener('click', () => {
            this.stopReading();
        });
        
        // --- DICTATION FOCUS FIX AND LISTENER ---
        const dictationBtn = document.getElementById('start-dictation');
        if (dictationBtn) {
            // FIX: Prevent the button from stealing focus from the input field on click/mousedown
            dictationBtn.addEventListener('mousedown', (e) => {
                e.preventDefault(); 
            });
            
            // Toggle dictation on click
            dictationBtn.addEventListener('click', () => {
                this.toggleDictation();
            });
        }
        // ----------------------------------------

        // Speech rate control
        document.getElementById('speech-rate')?.addEventListener('input', (e) => {
            this.speechRate = parseFloat(e.target.value);
            document.getElementById('rate-value').textContent = this.speechRate.toFixed(1) + 'x';
            localStorage.setItem('speechRate', this.speechRate);
            
            if (this.currentAudio) {
                this.currentAudio.playbackRate = this.speechRate;
            }
        });
        
        // Volume control
        document.getElementById('volume-control')?.addEventListener('input', (e) => {
            this.volume = parseFloat(e.target.value);
            document.getElementById('volume-value').textContent = Math.round(this.volume * 100) + '%';
            localStorage.setItem('volume', this.volume);
            
            if (this.currentAudio) {
                this.currentAudio.volume = this.volume;
            }
        });
        
        // Auto-read toggle
        document.getElementById('auto-read')?.addEventListener('change', (e) => {
            this.autoReadEnabled = e.target.checked;
            localStorage.setItem('autoReadEnabled', this.autoReadEnabled);
        });
        
        // Minimize button
        document.getElementById('voiceover-minimize')?.addEventListener('click', () => {
            this.togglePanel();
        });
        
        // Add click-to-read functionality for readable elements
        document.querySelectorAll('.voice-readable').forEach(element => {
            element.addEventListener('click', (e) => {
                if (e.shiftKey) {
                    this.readElement(element);
                    e.preventDefault();
                }
            });
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Shift+R: Read page
            if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                e.preventDefault();
                this.readPageContent();
            }
            
            // Ctrl+Shift+S: Stop reading
            if (e.ctrlKey && e.shiftKey && e.key === 'S') {
                e.preventDefault();
                this.stopReading();
            }

            // Ctrl+Shift+D: Toggle Dictation
            if (e.ctrlKey && e.shiftKey && e.key === 'D' && this.speechRecognition) {
                e.preventDefault();
                this.toggleDictation();
            }
            
            // Ctrl+Shift+H: Toggle panel
            if (e.ctrlKey && e.shiftKey && e.key === 'H') {
                e.preventDefault();
                this.togglePanel();
            }
        });
    }
    
    makeContentReadable() {
        // Add voice-readable class to main content elements
        const selectors = ['h1', 'h2', 'h3', 'p', '.cta-button', 'label', 'main'];
        
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                if (!element.classList.contains('voiceover-panel')) {
                    element.classList.add('voice-readable');
                    element.setAttribute('tabindex', '0');
                    element.title = 'Shift+Click to read aloud';
                }
            });
        });
    }

    makeInputsDictationReady() {
        // Apply dictation-ready class to standard input fields for form dictation
        document.querySelectorAll('input[type="text"], input[type="tel"], input[type="email"], textarea').forEach(element => {
            element.classList.add('dictation-ready');
            element.setAttribute('aria-label', `${element.previousElementSibling?.textContent || element.placeholder || 'Input field'}. Use Ctrl+Shift+D to dictate.`);
        });
    }

    toggleDictation() {
        if (!this.speechRecognition) return;

        this.stopReading(); // Stop reading before starting dictation

        if (this.isDictating) {
            this.stopDictation(true);
        } else {
            this.startDictation();
        }
    }

    startDictation() {
        if (!this.speechRecognition) return;

        const focusedElement = document.activeElement;
        // Check if the currently focused element is a dictation-ready input
        if (focusedElement && focusedElement.classList.contains('dictation-ready')) {
            try {
                this.speechRecognition.start();
                this.isDictating = true;
                this.updateDictationState();
                this.updateButtons();
                this.announceToScreenReader('Dictation started. Speak now.');
            } catch (e) {
                console.error('Error starting speech recognition:', e);
                // The error is often: "Speech recognition already started"
                // No need to set isDictating=false here, as onend/onerror will handle it
            }
        } else {
            this.announceToScreenReader('Please focus on a form input field (text area, text, phone, or email) to start dictation.');
        }
    }

    stopDictation(explicitStop = true) {
        if (!this.speechRecognition) return;

        if (explicitStop) {
            this.speechRecognition.stop();
        }
        this.isDictating = false;
        this.updateDictationState();
        this.updateButtons();
        this.announceToScreenReader('Dictation stopped.');
    }

    insertDictationText(text) {
        const focusedElement = document.activeElement;
        if (focusedElement && focusedElement.classList.contains('dictation-ready')) {
            // Append the dictated text to the current value
            const separator = focusedElement.value ? ' ' : '';
            focusedElement.value += separator + text.trim();
            
            // Dispatch input event to trigger any frameworks that rely on it (like React)
            focusedElement.dispatchEvent(new Event('input', { bubbles: true }));
            this.announceToScreenReader(`Dictated text: ${text.trim()}`);
        } else {
            this.announceToScreenReader('Dictated text received, but no input field was focused.');
        }
    }

    updateDictationState() {
        const dictationBtn = document.getElementById('start-dictation');
        if (dictationBtn) {
            if (this.isDictating) {
                dictationBtn.classList.add('active');
                dictationBtn.innerHTML = '<span class="icon">🛑</span> Stop Dictation';
                dictationBtn.setAttribute('aria-label', 'Stop voice dictation');
                document.body.classList.add('is-dictating');
            } else {
                dictationBtn.classList.remove('active');
                dictationBtn.innerHTML = '<span class="icon">🎤</span> Voice Dictation';
                dictationBtn.setAttribute('aria-label', 'Start voice dictation for form inputs');
                document.body.classList.remove('is-dictating');
            }
        }
    }

    async readPageContent() {
        const main = document.querySelector('main');
        if (!main) return;
        
        this.stopReading(); // Stop any current reading
        
        // Extract readable text
        const text = this.extractReadableText(main);
        
        if (!text) {
            this.announceToScreenReader('No content to read');
            return;
        }
        
        this.announceToScreenReader('Reading page content');
        await this.speak(text);
    }
    
    async readElement(element) {
        const text = this.extractReadableText(element);
        if (text) {
            this.stopReading();
            await this.speak(text);
        }
    }
    
    extractReadableText(element) {
        // Clone element to manipulate
        const clone = element.cloneNode(true);
        
        // Remove script, style, and voiceover panel
        clone.querySelectorAll('script, style, .voiceover-panel, nav, .dictation-indicator').forEach(el => el.remove());
        
        // Get text content
        let text = clone.textContent || '';
        
        // Clean up text
        text = text.replace(/\s+/g, ' ').trim();
        
        return text;
    }
    
    async speak(text) {
        if (!text || this.isPlaying) return;
        
        this.isPlaying = true;
        this.updateButtons();
        
        try {
            // Try ElevenLabs API first
            const audio = await this.fetchAudio(text);
            
            if (audio) {
                await this.playAudio(audio);
            } else {
                // Fallback to browser speech synthesis
                this.useBrowserSpeech(text);
            }
        } catch (error) {
            console.error('Error in speech:', error);
            this.useBrowserSpeech(text);
        }
    }
    
    async fetchAudio(text) {
        try {
            const response = await fetch('/api/text-to-speech', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                return URL.createObjectURL(blob);
            }
            
            // Check for fallback instruction from server
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const errorBody = await response.json();
                if (errorBody.fallback === "browser") {
                    console.warn("Server requested browser fallback for TTS.");
                    return null;
                }
            }
            
            return null;
        } catch (error) {
            console.error('Error fetching audio:', error);
            return null;
        }
    }
    
    playAudio(audioUrl) {
        return new Promise((resolve, reject) => {
            this.currentAudio = new Audio(audioUrl);
            this.currentAudio.playbackRate = this.speechRate;
            this.currentAudio.volume = this.volume;
            
            this.currentAudio.onended = () => {
                this.isPlaying = false;
                this.updateButtons();
                URL.revokeObjectURL(audioUrl);
                resolve();
            };
            
            this.currentAudio.onerror = () => {
                this.isPlaying = false;
                this.updateButtons();
                reject(new Error('Audio playback failed'));
            };
            
            this.currentAudio.play().catch(reject);
        });
    }
    
    useBrowserSpeech(text) {
        if (!window.speechSynthesis) {
            console.error('Speech synthesis not supported');
            this.isPlaying = false;
            this.updateButtons();
            return;
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.speechRate;
        utterance.volume = this.volume;
        
        utterance.onend = () => {
            this.isPlaying = false;
            this.updateButtons();
        };
        
        utterance.onerror = () => {
            this.isPlaying = false;
            this.updateButtons();
        };
        
        window.speechSynthesis.speak(utterance);
    }
    
    stopReading() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        
        // Stop dictation if running
        if (this.isDictating) {
            this.stopDictation(true);
        }
        
        this.isPlaying = false;
        this.updateButtons();
        this.announceToScreenReader('Stopped reading');
    }
    
    updateButtons() {
        const readBtn = document.getElementById('read-page');
        const stopBtn = document.getElementById('stop-reading');
        const dictationBtn = document.getElementById('start-dictation');
        
        const isActionActive = this.isPlaying || this.isDictating; 

        if (readBtn && stopBtn) {
            readBtn.disabled = isActionActive; 
            stopBtn.disabled = !isActionActive; 
        }

        // Disable dictation button when reading
        if (dictationBtn) {
            dictationBtn.disabled = this.isPlaying;
        }
    }
    
    togglePanel() {
        const panel = document.getElementById('voiceover-control-panel');
        if (panel) {
            panel.classList.toggle('minimized');
            const minimizeBtn = document.getElementById('voiceover-minimize');
            minimizeBtn.textContent = panel.classList.contains('minimized') ? '+' : '−';
            minimizeBtn.setAttribute('aria-label', 
                panel.classList.contains('minimized') ? 'Maximize voice controls' : 'Minimize voice controls'
            );
        }
    }
    
    announceToScreenReader(message) {
        // Create or update ARIA live region for screen reader announcements
        let liveRegion = document.getElementById('voiceover-announcements');
        
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'voiceover-announcements';
            liveRegion.className = 'sr-only';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            document.body.appendChild(liveRegion);
        }
        
        liveRegion.textContent = message;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.voiceoverSystem = new VoiceoverSystem();
    });
} else {
    window.voiceoverSystem = new VoiceoverSystem();
}