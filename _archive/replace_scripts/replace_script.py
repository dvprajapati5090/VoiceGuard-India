import re

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Results HTML
old_results_pattern = re.compile(r'<div class="results" id="results" style="display: none;[^>]+>.*?</div>\s*</section>', re.DOTALL)

new_results = """<div class="results" id="results" style="display: none; background: rgba(255, 255, 255, 0.04); border-radius: 24px; padding: 32px; border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <div>
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.5);">Analysis Status</h4>
            <div id="status-text" style="font-size: 1.25rem; font-weight: 500; margin-top: 4px;">Uploading...</div>
        </div>
        <div style="text-align: right;">
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255,255,255,0.5);">Final Verdict</h4>
            <div id="final-verdict" class="verdict" style="font-size: 1.5rem; margin-top: 4px;">PENDING</div>
        </div>
    </div>

    <div class="progress-bar" id="progress-container" style="background: rgba(255,255,255,0.1); border-radius: 8px; height: 8px; overflow: hidden; margin-bottom: 24px;">
        <div class="progress-fill" id="progress-fill" style="background: var(--blue); height: 100%; width: 0%; transition: width 0.3s ease;"></div>
    </div>

    <div id="analysis-details" style="display: none; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px;">
        <div style="margin-bottom: 24px; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);">
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--blue); margin-bottom: 12px;">Primary Indicator</h4>
            <p id="explainability-reason" style="font-size: 1.1rem; color: #ffffff; line-height: 1.6; font-weight: 300;"></p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: rgba(255,255,255,0.8);">
                    <span>LCNN Risk</span>
                    <span id="lcnn-val" style="font-weight: 700;">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="lcnn-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: rgba(255,255,255,0.8);">
                    <span>Wav2Vec2 Risk</span>
                    <span id="w2v2-val" style="font-weight: 700;">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="w2v2-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 12px; color: rgba(255,255,255,0.8);">
                    <span>Prosody Risk</span>
                    <span id="prosody-val" style="font-weight: 700;">0%</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="prosody-bar" style="height: 100%; width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                </div>
            </div>
        </div>
    </div>
</div>
</section>"""

html = old_results_pattern.sub(new_results, html)

# Replace JS logic
old_js_pattern = re.compile(r'analyzeBtn\.addEventListener\(\'click\', async \(\) => \{.*?\n        \}\);', re.DOTALL)

new_js = """analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const resultsBox = document.getElementById('results');
    const statusText = document.getElementById('status-text');
    const progressFill = document.getElementById('progress-fill');
    const finalVerdict = document.getElementById('final-verdict');
    
    resultsBox.style.display = 'block';
    resultsBox.style.borderColor = "rgba(255, 255, 255, 0.05)";
    document.getElementById('analysis-details').style.display = 'none';
    document.getElementById('progress-container').style.display = 'block';
    statusText.innerText = 'Uploading and analyzing audio...';
    progressFill.style.width = '10%';
    finalVerdict.innerText = 'PENDING';
    finalVerdict.className = 'verdict';
    finalVerdict.style.color = '#ffffff';

    try {
        const langSelect = document.getElementById('lang-select');
        const lang = langSelect ? langSelect.value : "hi";
        const formData = new FormData();
        formData.append('file', selectedFile);

        let p = 10;
        const progressInterval = setInterval(() => {
            p += (90 - p) * 0.05;
            progressFill.style.width = p + '%';
        }, 150);

        const response = await fetch(`http://localhost:8000/api/detect?language=${lang}`, {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';

        if (!response.ok) {
            const errTxt = await response.text();
            throw new Error(`API Error: ${response.status} - ${errTxt}`);
        }

        const data = await response.json();
        
        setTimeout(() => {
            document.getElementById('progress-container').style.display = 'none';
            document.getElementById('analysis-details').style.display = 'block';
            
            statusText.innerText = 'Analysis Complete';
            
            if (data.is_deepfake) {
                finalVerdict.innerHTML = `<span style="color: #EF4444;">AI CLONE</span> <span style="font-size:1rem; opacity:0.8;">(${data.confidence_score}%)</span>`;
                resultsBox.style.borderColor = "rgba(239, 68, 68, 0.3)";
            } else {
                finalVerdict.innerHTML = `<span style="color: #10B981;">HUMAN</span> <span style="font-size:1rem; opacity:0.8;">(${100 - data.confidence_score}%)</span>`;
                resultsBox.style.borderColor = "rgba(16, 185, 129, 0.3)";
            }

            document.getElementById('explainability-reason').innerText = data.explainability.reason;

            const lcnn = data.explainability.stage_breakdown.lcnn_risk;
            const w2v2 = data.explainability.stage_breakdown.w2v2_risk;
            const pros = data.explainability.stage_breakdown.prosody_risk;

            document.getElementById('lcnn-val').innerText = lcnn + '%';
            document.getElementById('lcnn-bar').style.width = lcnn + '%';
            document.getElementById('lcnn-bar').style.background = lcnn > 50 ? '#EF4444' : '#3B82F6';

            document.getElementById('w2v2-val').innerText = w2v2 + '%';
            document.getElementById('w2v2-bar').style.width = w2v2 + '%';
            document.getElementById('w2v2-bar').style.background = w2v2 > 50 ? '#EF4444' : '#6366F1';

            document.getElementById('prosody-val').innerText = pros + '%';
            document.getElementById('prosody-bar').style.width = pros + '%';
            document.getElementById('prosody-bar').style.background = pros > 50 ? '#EF4444' : '#A855F7';

        }, 400);

    } catch (err) {
        statusText.innerText = 'Error: ' + err.message;
        progressFill.style.background = '#EF4444';
    }
});"""

html = old_js_pattern.sub(new_js, html)

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully replaced.")
