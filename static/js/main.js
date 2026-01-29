/**
 * Biblioteca Pessoal - Main JavaScript
 * Utility functions and global behaviors
 */

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success'
        ? '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        : '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';

    toast.innerHTML = `
        <span style="color: ${type === 'success' ? 'var(--accent-primary)' : '#C45C5C'}">${icon}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);


// ============================================
// API Helpers
// ============================================

async function apiGet(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro na requisição');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('Erro ao carregar dados', 'error');
        throw error;
    }
}

async function apiPost(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro na requisição');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('Erro ao salvar dados', 'error');
        throw error;
    }
}

async function apiPut(url, data) {
    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Erro na requisição');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('Erro ao atualizar dados', 'error');
        throw error;
    }
}

async function apiDelete(url) {
    try {
        const response = await fetch(url, { method: 'DELETE' });
        if (!response.ok) throw new Error('Erro na requisição');
        return true;
    } catch (error) {
        console.error('API Error:', error);
        showToast('Erro ao excluir dados', 'error');
        throw error;
    }
}


// ============================================
// Date Helpers
// ============================================

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}

function formatDateFull(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

function getToday() {
    return new Date().toISOString().split('T')[0];
}


// ============================================
// Number Helpers
// ============================================

function formatMoney(value) {
    if (!value) return 'R$ 0,00';
    return value.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function formatNumber(value) {
    if (!value) return '0';
    return value.toLocaleString('pt-BR');
}


// ============================================
// Book Status Helpers
// ============================================

function getStatusLabel(status) {
    const labels = {
        'read': 'Lido',
        'reading': 'Lendo',
        'want_to_read': 'Quero ler'
    };
    return labels[status] || status;
}

function getStatusEmoji(status) {
    const emojis = {
        'read': '✅',
        'reading': '📖',
        'want_to_read': '⭐'
    };
    return emojis[status] || '📚';
}

function getPriorityLabel(priority) {
    const labels = {
        'high': 'Quero muito',
        'normal': 'Normal',
        'low': 'Sem pressa'
    };
    return labels[priority] || priority;
}

function getPriorityEmoji(priority) {
    const emojis = {
        'high': '🔥',
        'normal': '🙂',
        'low': '💤'
    };
    return emojis[priority] || '🙂';
}


// ============================================
// Theme Management
// ============================================

function initTheme() {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('darkMode', !isDark);
}


// ============================================
// Export Data
// ============================================

async function exportData() {
    try {
        showToast('Preparando exportação...', 'success');

        const response = await fetch('/api/export');
        const data = await response.json();

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `biblioteca-pessoal-${getToday()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('Dados exportados com sucesso!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Erro ao exportar dados', 'error');
    }
}


// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input input');
        if (searchInput) searchInput.focus();
    }

    // Escape: Close modals
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal-overlay.active');
        if (modal) {
            // Alpine.js will handle the close via x-data
            modal.click();
        }
    }
});


// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
});
