import re

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add WaveSurfer scripts before the closing </head>
if "wavesurfer.js" not in html:
    html = html.replace("</head>", "    <script src=\"https://unpkg.com/wavesurfer.js@7\"></script>\n    <script src=\"https://unpkg.com/wavesurfer.js@7/dist/plugins/regions.min.js\"></script>\n</head>")

# 2. Replace the native audio player with waveform container
old_audio = r'<!-- Audio Player -->\s*<div style="margin-bottom: 24px;">\s*<h4[^>]*>Audio Preview</h4>\s*<audio id="audio-preview"[^>]*></audio>\s*</div>'
new_audio = """<!-- Audio Player -->
    <div style="margin-bottom: 24px; display: none;" id="audio-player-container">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <h4 style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--headline-muted);">Audio Waveform</h4>
            <button id="play-pause-btn" type="button" style="background: var(--blue); color: #fff; border: none; border-radius: 20px; padding: 6px 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: background 0.3s;">Play</button>
        </div>
        <div id="waveform" style="width: 100%; background: rgba(0,0,0,0.03); border-radius: 8px; border: 1px solid rgba(0,0,0,0.05); overflow: hidden;"></div>
    </div>"""

html = re.sub(old_audio, new_audio, html, flags=re.DOTALL)

# 3. Update the handleFileSelect JS to initialize/load WaveSurfer
old_handle_file = r'// Set up audio preview.*?if \(audioPreview\) \{.*?audioPreview\.src = URL\.createObjectURL\(selectedFile\);.*?\}'
new_handle_file = """// Set up audio preview
            document.getElementById('audio-player-container').style.display = 'block';
            if (!window.wavesurfer) {
                window.wavesurfer = WaveSurfer.create({
                    container: '#waveform',
                    waveColor: '#a1a1aa',
                    progressColor: '#3B82F6',
                    cursorColor: '#1d4ed8',
                    barWidth: 2,
                    barGap: 1,
                    barRadius: 2,
                    height: 60,
                    normalize: true,
                });
                
                window.wsRegions = window.wavesurfer.registerPlugin(WaveSurfer.Regions.create());
                
                document.getElementById('play-pause-btn').addEventListener('click', () => {
                    window.wavesurfer.playPause();
                });
                
                window.wavesurfer.on('play', () => {
                    document.getElementById('play-pause-btn').innerText = 'Pause';
                });
                window.wavesurfer.on('pause', () => {
                    document.getElementById('play-pause-btn').innerText = 'Play';
                });
            }
            window.wavesurfer.load(URL.createObjectURL(selectedFile));
            if (window.wsRegions) window.wsRegions.clearRegions();"""

html = re.sub(old_handle_file, new_handle_file, html, flags=re.DOTALL)

# 4. Fix colors in the fetch response processing
# We'll replace the timeout block inside the click handler to apply #EF4444 and fix percentage color
old_timeout = re.compile(r'setTimeout\(\(\) => \{.*?if \(data\.is_deepfake\).*?\}, 400\);', re.DOTALL)

new_timeout = """setTimeout(() => {
            document.getElementById('progress-container').style.display = 'none';
            document.getElementById('analysis-details').style.display = 'block';
            
            statusText.innerText = 'Analysis Complete';
            
            if (data.is_deepfake) {
                finalVerdict.innerHTML = `<span style="color: #EF4444;">AI CLONE</span> <span style="font-size:1rem; color: var(--text); font-weight: 700; opacity: 0.9;">(${data.confidence_score}%)</span>`;
                resultsBox.style.borderColor = "rgba(239, 68, 68, 0.3)";
            } else {
                finalVerdict.innerHTML = `<span style="color: var(--brand-green);">AUTHENTIC HUMAN</span> <span style="font-size:1rem; color: var(--text); font-weight: 700; opacity: 0.9;">(${100 - data.confidence_score}%)</span>`;
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
            document.getElementById('w2v2-bar').style.background = w2v2 > 50 ? '#EF4444' : '#3B82F6';

            document.getElementById('prosody-val').innerText = pros + '%';
            document.getElementById('prosody-bar').style.width = pros + '%';
            document.getElementById('prosody-bar').style.background = pros > 50 ? '#EF4444' : '#3B82F6';
            
            // Add red regions to waveform if it's a deepfake
            if (data.is_deepfake && data.explainability.highlight_segments && window.wsRegions) {
                data.explainability.highlight_segments.forEach(seg => {
                    window.wsRegions.addRegion({
                        start: seg.start,
                        end: seg.end,
                        color: 'rgba(239, 68, 68, 0.3)',
                        drag: false,
                        resize: false
                    });
                });
            }

        }, 400);"""

html = old_timeout.sub(new_timeout, html)

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated waveform and colors")
