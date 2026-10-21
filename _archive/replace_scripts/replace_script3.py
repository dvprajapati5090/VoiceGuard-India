import re

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the results-box entirely with the updated theme colors and audio player
pattern = re.compile(r'<div class="results-box" id="results" style="display: none;.*?</div>\s*</div>\s*</div>\s*</section>', re.DOTALL)

new_results = """<div class="results-box" id="results" style="display: none; background: var(--glass-light); backdrop-filter: blur(var(--glass-blur)); -webkit-backdrop-filter: blur(var(--glass-blur)); border-radius: 24px; padding: 32px; border: 1px solid rgba(255, 255, 255, 0.4); margin-top: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <div>
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--headline-muted);">Analysis Status</h4>
            <div id="status-text" style="font-size: 1.25rem; font-weight: 600; margin-top: 4px; color: var(--text);">Uploading...</div>
        </div>
        <div style="text-align: right;">
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--headline-muted);">Final Verdict</h4>
            <div id="final-verdict" class="verdict" style="font-size: 1.5rem; margin-top: 4px; font-weight: 700;">PENDING</div>
        </div>
    </div>

    <!-- Audio Player -->
    <div style="margin-bottom: 24px;">
        <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--headline-muted); margin-bottom: 8px;">Audio Preview</h4>
        <audio id="audio-preview" controls style="width: 100%; height: 40px; border-radius: 8px; outline: none;"></audio>
    </div>

    <div class="progress-bar" id="progress-container" style="background: rgba(0,0,0,0.1); border-radius: 8px; height: 8px; overflow: hidden; margin-bottom: 24px;">
        <div class="progress-fill" id="progress-fill" style="background: var(--blue); height: 100%; width: 0%; transition: width 0.3s ease;"></div>
    </div>

    <div id="analysis-details" style="display: none; border-top: 1px solid rgba(0,0,0,0.1); padding-top: 24px;">
        <div style="margin-bottom: 24px; background: rgba(0,0,0,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05);">
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--blue-dark); margin-bottom: 12px; font-weight: 700;">Primary Indicator</h4>
            <p id="explainability-reason" style="font-size: 1.1rem; color: var(--text); line-height: 1.6; font-weight: 500;"></p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
            <div style="background: rgba(255,255,255,0.4); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: var(--muted); font-weight: 600;">
                    <span>LCNN Risk</span>
                    <span id="lcnn-val" style="font-weight: 800; color: var(--text);">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="lcnn-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.4); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: var(--muted); font-weight: 600;">
                    <span>Wav2Vec2 Risk</span>
                    <span id="w2v2-val" style="font-weight: 800; color: var(--text);">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="w2v2-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.4); padding: 20px; border-radius: 16px; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: var(--muted); font-weight: 600;">
                    <span>Prosody Risk</span>
                    <span id="prosody-val" style="font-weight: 800; color: var(--text);">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="prosody-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
        </div>
    </div>
</div>
</section>"""

html, count = pattern.subn(new_results, html)
print(f"Replaced HTML: {count} matches")

# Also inject audio preview URL creation in JS
# Find handleFileSelect() function and update it
js_pattern = re.compile(r'function handleFileSelect\(\) \{.*?\n        \}', re.DOTALL)
new_js = """function handleFileSelect() {
        if (fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
            document.querySelector('#drop-zone h3').innerText = selectedFile.name;
            analyzeBtn.disabled = false;
            analyzeBtn.style.opacity = '1';
            analyzeBtn.style.cursor = 'pointer';
            
            // Set up audio preview
            const audioPreview = document.getElementById('audio-preview');
            if (audioPreview) {
                audioPreview.src = URL.createObjectURL(selectedFile);
            }
        }
    }"""
html, js_count = js_pattern.subn(new_js, html)
print(f"Replaced handleFileSelect JS: {js_count} matches")

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
