const summaryText = document.getElementById('summaryText');
const charCount = document.getElementById('charCount');
const lengthRatio = document.getElementById('lengthRatio');
const formatType = document.getElementById('formatType');
const summarizeBtn = document.getElementById('summarizeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const errorMsg = document.getElementById('errorMsg');
const summaryResult = document.getElementById('summaryResult');
const originalWords = document.getElementById('originalWords');
const summaryWords = document.getElementById('summaryWords');
const compressionRatio = document.getElementById('compressionRatio');
const copyBtn = document.getElementById('copyBtn');

summaryText.addEventListener('input', () => {
    charCount.textContent = summaryText.value.length;
});

summarizeBtn.addEventListener('click', async () => {
    const text = summaryText.value.trim();
    
    if (!text) {
        showError('Please enter text to summarize');
        return;
    }
    
    if (text.length < 100) {
        showError('Text must be at least 100 characters for meaningful summarization');
        return;
    }
    
    hideError();
    results.classList.remove('show');
    loading.style.display = 'block';
    summarizeBtn.disabled = true;
    
    try {
        const response = await fetch('YOUR_CLOUD_FUNCTION_URL/summarizeText', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                ratio: parseFloat(lengthRatio.value),
                format: formatType.value
            })
        });
        
        if (!response.ok) throw new Error('Summarization failed');
        
        const data = await response.json();
        displayResults(data);
        saveToFirestore(text, data);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to generate summary. Please try again.');
    } finally {
        loading.style.display = 'none';
        summarizeBtn.disabled = false;
    }
});

function displayResults(data) {
    summaryResult.textContent = data.summary;
    originalWords.textContent = data.originalWords;
    summaryWords.textContent = data.summaryWords;
    compressionRatio.textContent = Math.round(data.compressionRatio * 100) + '%';
    results.classList.add('show');
}

function saveToFirestore(text, result) {
    if (typeof firebase !== 'undefined' && firebase.firestore) {
        db.collection('results').add({
            type: 'summary',
            input: text.substring(0, 500),
            output: result,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        }).catch(console.error);
    }
}

copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(summaryResult.textContent).then(() => {
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyBtn.textContent = 'Copy Summary';
            copyBtn.classList.remove('copied');
        }, 2000);
    });
});

function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.add('show');
}

function hideError() {
    errorMsg.classList.remove('show');
}