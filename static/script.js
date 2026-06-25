document.addEventListener('DOMContentLoaded', function() {
    const topicInput = document.getElementById('topic');
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const articleContent = document.getElementById('articleContent');
    const copyBtn = document.getElementById('copyBtn');

    // Input validation
    topicInput.addEventListener('input', function() {
        const value = this.value.trim();
        if (value.length >= 3 && value.length <= 100) {
            this.style.borderColor = '#4caf50';
            generateBtn.disabled = false;
        } else {
            this.style.borderColor = '#e0e0e0';
            generateBtn.disabled = true;
        }
    });

    // Generate article
    generateBtn.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        
        if (!topic || topic.length < 3) {
            showError('Please enter a topic with at least 3 characters');
            return;
        }

        // Show loading, hide previous results
        loading.classList.remove('hidden');
        result.classList.add('hidden');
        error.classList.add('hidden');
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic: topic })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                displayArticle(data.article);
            } else {
                showError(data.error || 'Failed to generate article');
            }
        } catch (err) {
            showError('Network error. Please check your connection and try again.');
            console.error('Error:', err);
        } finally {
            loading.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Article';
        }
    });

    // Display article
    function displayArticle(markdown) {
        // Simple markdown to HTML conversion (you can use a library for better rendering)
        let html = markdown
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/\n/g, '<br>');
        
        // Wrap lists
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        
        articleContent.innerHTML = html;
        result.classList.remove('hidden');
    }

    // Show error
    function showError(message) {
        error.textContent = message;
        error.classList.remove('hidden');
        setTimeout(() => {
            error.classList.add('hidden');
        }, 8000);
    }

    // Copy to clipboard
    copyBtn.addEventListener('click', function() {
        const text = articleContent.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = this.textContent;
            this.textContent = '✅ Copied!';
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        }).catch(() => {
            // Fallback method
            const range = document.createRange();
            range.selectNode(articleContent);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand('copy');
            const originalText = this.textContent;
            this.textContent = '✅ Copied!';
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        });
    });

    // Enter key support
    topicInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !generateBtn.disabled) {
            generateBtn.click();
        }
    });

    // Initial validation
    generateBtn.disabled = true;
});