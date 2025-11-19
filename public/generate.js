const promptText = document.getElementById('promptText');
const toneSelect = document.getElementById('toneSelect');
const lengthSelect = document.getElementById('lengthSelect');
const tempSlider = document.getElementById('tempSlider');
const tempValue = document.getElementById('tempValue');
const generateBtn = document.getElementById('generateBtn');
const regenerateBtn = document.getElementById('regenerateBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const errorMsg = document.getElementById('errorMsg');
const generatedText = document.getElementById('generatedText');
const wordCount = document.getElementById('wordCount');
const tokensUsed = document.getElementById('tokensUsed');
const copyBtn = document.getElementById('copyBtn');

tempSlider.addEventListener('input', () => {
    tempValue.textContent = tempSlider.value;
});

async function performGeneration() {
    const prompt = promptText.value.trim();
    
    if (!prompt) {
        showError('Please enter a prompt');
        return;
    }
    
    if (prompt.length < 10) {
        showError('Prompt must be at least 10 characters');
        return;
    }
    
    hideError();
    results.classList.remove('show');
    loading.style.display = 'block';
    generateBtn.disabled = true;
    regenerateBtn.disabled = true;
    
    try {
        const response = await fetch('YOUR_CLOUD_FUNCTION_URL/generateText', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                tone: toneSelect.value,
                maxLength: parseInt(lengthSelect.value),
                temperature: parseFloat(tempSlider.value)
            })
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        const data = await response.json();
        displayResults(data);
        saveToFirestore(prompt, data);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to generate text. Please try again.');
    } finally {
        loading.style.display = 'none';
        generateBtn.disabled = false;
        regenerateBtn.disabled = false;
    }
}

generateBtn.addEventListener('click', performGeneration);
regenerateBtn.addEventListener('click', performGeneration);

function displayResults(data) {
    generatedText.textContent = data.generatedText;
    wordCount.textContent = data.wordCount;
    tokensUsed.textContent = data.tokensUsed;
    results.classList.add('show');
}

function saveToFirestore(prompt, result) {
    if (typeof firebase !== 'undefined' && firebase.firestore) {
        db.collection('results').add({
            type: 'generation',
            input: prompt,
            output: result,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        }).catch(console.error);
    }
}

copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(generatedText.textContent).then(() => {
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyBtn.textContent = 'Copy Text';
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