class BadgeGenerator {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadPresets();
    }
    initializeElements() {
        this.form = document.getElementById('badge-form');
        this.urlInput = document.getElementById('url');
        this.labelInput = document.getElementById('label');
        this.colorInput = document.getElementById('color');
        this.colorPicker = document.getElementById('color-picker');
        this.styleSelect = document.getElementById('style');
        this.logoInput = document.getElementById('logo');
        this.generateBtn = document.getElementById('generate-btn');
        this.resultSection = document.getElementById('result-section');
        this.badgePreview = document.getElementById('badge-preview');
        this.badgeUrl = document.getElementById('badge-url');
        this.markdownCode = document.getElementById('markdown-code');
        this.htmlCode = document.getElementById('html-code');
        this.colorOptions = document.querySelectorAll('.color-option');
    }

    bindEvents() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateBadge();
            });
        }

        this.colorOptions.forEach((option) => {
            option.addEventListener('click', () => {
                this.selectColor(option);
            });
        });

        // Copy button events
        document.querySelectorAll('.copy-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                this.copyToClipboard(e.target);
            });
        }); // Real-time preview
        [
            this.urlInput,
            this.labelInput,
            this.colorInput,
            this.styleSelect,
            this.logoInput,
        ].forEach((input) => {
            if (input) {
                input.addEventListener('input', () => {
                    this.updatePreview();
                });
            }
        });

        // Color picker events
        if (this.colorPicker) {
            this.colorPicker.addEventListener('input', (e) => {
                const hex = e.target.value.replace('#', '');
                this.colorInput.value = hex;
                this.updateColorSelection(hex);
                this.updatePreview();
            });
        }

        if (this.colorInput) {
            this.colorInput.addEventListener('input', (e) => {
                const hex = e.target.value.replace('#', '');
                if (hex.length === 6 && /^[0-9A-F]{6}$/i.test(hex)) {
                    this.colorPicker.value = '#' + hex;
                    this.updateColorSelection(hex);
                }
            });
        }
    }

    loadPresets() {
        const colors = [
            { name: 'Blue', value: '3b82f6' },
            { name: 'Purple', value: '8b5cf6' },
            { name: 'Pink', value: 'ec4899' },
            { name: 'Red', value: 'ef4444' },
            { name: 'Orange', value: 'f97316' },
            { name: 'Yellow', value: 'eab308' },
            { name: 'Teal', value: '14b8a6' },
            { name: 'Indigo', value: '6366f1' },
            { name: 'Gray', value: '6b7280' },
            { name: 'Cyan', value: '06b6d4' },
            { name: 'Emerald', value: '10b981' },
        ];

        colors.forEach((color, index) => {
            if (this.colorOptions[index]) {
                this.colorOptions[index].style.backgroundColor = `#${color.value}`;
                this.colorOptions[index].dataset.color = color.value;
                this.colorOptions[index].title = color.name;
            }
        });

        // Set default color
        const defaultColor = '247e62';
        this.colorInput.value = defaultColor;
        this.colorPicker.value = '#' + defaultColor;
        this.updateColorSelection(defaultColor);
    }
    selectColor(option) {
        this.colorOptions.forEach((opt) => opt.classList.remove('selected'));
        option.classList.add('selected');
        const colorValue = option.dataset.color;
        this.colorInput.value = colorValue;
        this.colorPicker.value = '#' + colorValue;
        this.updatePreview();
    }

    updateColorSelection(hex) {
        this.colorOptions.forEach((opt) => opt.classList.remove('selected'));
        // Try to find matching preset color
        const matchingOption = Array.from(this.colorOptions).find(
            (opt) => opt.dataset.color.toLowerCase() === hex.toLowerCase(),
        );
        if (matchingOption) {
            matchingOption.classList.add('selected');
        }
    }

    updatePreview() {
        if (!this.badgePreview) return;
        const url = this.urlInput.value.trim();
        if (!url) return;

        const badgeUrl = this.buildBadgeUrl();
        this.badgePreview.innerHTML = `<img src="${badgeUrl}" alt="Badge Preview" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjIwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMjAiIGZpbGw9IiNjY2MiLz48dGV4dCB4PSI1MCIgeT0iMTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzMzMyI+UHJldmlldyBVbmF2YWlsYWJsZTwvdGV4dD48L3N2Zz4='" />`;
    }

    buildBadgeUrl() {
        const baseUrl = window.location.origin;
        const params = new URLSearchParams({
            url: this.urlInput.value.trim(),
            label: this.labelInput.value.trim() || 'visits',
            color: this.colorInput.value.trim() || '247e62',
            style: this.styleSelect.value || 'flat',
        });

        if (this.logoInput.value.trim()) {
            params.append('logo', this.logoInput.value.trim());
        }

        return `${baseUrl}/badge?${params.toString()}`;
    }

    generateBadge() {
        const url = this.urlInput.value.trim();
        if (!url) {
            this.showToast('Please enter a URL');
            return;
        }

        // Validate URL format
        try {
            new URL(url.startsWith('http') ? url : `https://${url}`);
        } catch {
            this.showToast('Please enter a valid URL');
            return;
        }

        const badgeUrl = this.buildBadgeUrl();
        const label = this.labelInput.value.trim() || 'visits';

        // Update preview
        this.badgePreview.innerHTML = `<img src="${badgeUrl}" alt="Generated Badge" />`;
        this.badgeUrl.textContent = badgeUrl;

        // Generate markdown
        const markdown = `[![${label}](${badgeUrl})](${url})`;
        this.markdownCode.textContent = markdown;

        // Generate HTML
        const html = `<a href="${url}"><img src="${badgeUrl}" alt="${label}" /></a>`;
        this.htmlCode.textContent = html;

        // Show results
        this.resultSection.classList.add('show');
        this.resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    copyToClipboard(button) {
        const codeBlock = button.parentNode.querySelector('code');
        const text = codeBlock.textContent;

        navigator.clipboard
            .writeText(text)
            .then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
                this.showToast('Copied to clipboard!');
            })
            .catch(() => {
                this.showToast('Failed to copy to clipboard');
            });
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }
}

// Initialize the badge generator when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize the generator on the main page
    if (document.getElementById('badge-form')) {
        new BadgeGenerator();
    }

    // Set current year in footer
    const currentYearElement = document.getElementById('currentYear');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
});