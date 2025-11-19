// Get DOM elements
const detectText = document.getElementById('detectText');
const charCount = document.getElementById('charCount');
const detectBtn = document.getElementById('detectBtn');
const fileUpload = document.getElementById('fileUpload');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const errorMsg = document.getElementById('errorMsg');
const confidenceValue = document.getElementById('confidenceValue');
const verdict = document.getElementById('verdict');
const confidenceFill = document.getElementById('confidenceFill');
const analysisDetails = document.getElementById('analysisDetails');
const copyBtn = document.getElementById('copyBtn');

// Character counter
detectText.addEventListener('input', () => {
    const count = detectText.value.length;
    charCount.textContent = count;
});

// File upload handler
fileUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/plain') {
        const reader = new FileReader();
        reader.onload = (event) => {
            detectText.value = event.target.result;
            charCount.textContent = detectText.value.length;
        };
        reader.readAsText(file);
    } else {
        showError('Please upload a .txt file');
    }
});

// Detect button handler
detectBtn.addEventListener('click', async () => {
    const text = detectText.value.trim();
    
    // Validation
    if (!text) {
        showError('Please enter some text to analyze');
        return;
    }
    
    if (text.length < 50) {
        showError('Text must be at least 50 characters long');
        return;
    }
    
    // Hide error and results
    hideError();
    results.classList.remove('show');
    
    // Show loading
    loading.style.display = 'block';
    detectBtn.disabled = true;
    
    try {
        // Call Firebase Cloud Function
        const response = await fetch('YOUR_CLOUD_FUNCTION_URL/detectAIText', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze text');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
        // Save to Firestore
        saveToFirestore(text, data);
        
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred while analyzing the text. Please try again.');
    } finally {
        loading.style.display = 'none';
        detectBtn.disabled = false;
    }
});

// Display results function
function displayResults(data) {
    const confidence = Math.round(data.confidence);
    const isAI = data.isAI;
    
    // Update confidence value
    confidenceValue.textContent = confidence + '%';
    
    // Update verdict
    verdict.textContent = isAI ? '🤖 AI Generated' : '👤 Human Written';
    verdict.style.color = isAI ? '#ef4444' : '#4ade80';
    
    // Update confidence bar
    confidenceFill.style.width = confidence + '%';
    confidenceFill.textContent = confidence + '%';
    
    // Color the bar based on confidence
    if (confidence < 30) {
        confidenceFill.style.background = '#4ade80'; // Green
    } else if (confidence < 70) {
        confidenceFill.style.background = '#fbbf24'; // Yellow
    } else {
        confidenceFill.style.background = '#ef4444'; // Red
    }
    
    // Update analysis details
    let details = `Detection Confidence: ${confidence}%\n\n`;
    details += `Verdict: ${isAI ? 'This text appears to be AI-generated' : 'This text appears to be human-written'}\n\n`;
    
    if (data.perplexity) {
        details += `Perplexity Score: ${data.perplexity.toFixed(2)}\n`;
    }
    
    if (data.burstiness) {
        details += `Burstiness Score: ${data.burstiness.toFixed(2)}\n`;
    }
    
    details += `\nNote: This is a probabilistic analysis and may not be 100% accurate.`;
    
    analysisDetails.textContent = details;
    
    // Show results
    results.classList.add('show');
}

// Save to Firestore
function saveToFirestore(text, result) {
    if (typeof firebase !== 'undefined' && firebase.firestore) {
        const db = firebase.firestore();
        db.collection('results').add({
            type: 'detection',
            input: text.substring(0, 500), // Store first 500 chars
            output: result,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        }).catch(error => {
            console.error('Error saving to Firestore:', error);
        });
    }
}

// Copy results button
copyBtn.addEventListener('click', () => {
    const resultText = `AI Detection Results\n\n${analysisDetails.textContent}`;
    navigator.clipboard.writeText(resultText).then(() => {
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyBtn.textContent = 'Copy Results';
            copyBtn.classList.remove('copied');
        }, 2000);
    });
});

// Error handling functions
function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.add('show');
}

function hideError() {
    errorMsg.classList.remove('show');
}