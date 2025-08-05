// Reusable UI Components for Smart Research Assistant

class Components {
  // Toast notification system
  static showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = this.getToastIcon(type);

    toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

    // Add toast styles for close button
    const style = toast.querySelector('.toast-close');
    if (style) {
      Object.assign(style.style, {
        background: 'none',
        border: 'none',
        color: 'inherit',
        cursor: 'pointer',
        padding: '0',
        marginLeft: 'auto'
      });
    }

    container.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, duration);

    return toast;
  }

  static getToastIcon(type) {
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
  }

  // Loading spinner component
  static createLoadingSpinner(text = 'Loading...') {
    return `
            <div class="loading">
                <div class="spinner"></div>
                <p>${text}</p>
            </div>
        `;
  }

  // Paper item component
  static createPaperItem(paper, index) {
    const citations = paper.citations || 0;
    const year = paper.year || 'N/A';
    const authors = paper.authors || 'Unknown authors';
    const snippet = paper.snippet || 'No abstract available';
    const pdfIcon = paper.pdf_url ? '<i class="fas fa-file-pdf text-red-500"></i>' : '';

    return `
            <div class="paper-item" data-paper-id="${paper.id}">
                <div class="paper-checkbox">
                    <input type="checkbox" id="paper-${index}" value="${index}" onchange="App.updateSelectedPapers()">
                    <div class="paper-content">
                        <div class="paper-title">
                            <label for="paper-${index}">
                                ${paper.url ? `<a href="${paper.url}" target="_blank" onclick="event.stopPropagation()">` : ''}
                                ${paper.title}
                                ${paper.url ? '</a>' : ''}
                            </label>
                        </div>
                        <div class="paper-meta">
                            <span><i class="fas fa-user"></i> ${authors}</span>
                            <span><i class="fas fa-calendar"></i> ${year}</span>
                            <span><i class="fas fa-quote-left"></i> ${citations} citations</span>
                            ${pdfIcon}
                        </div>
                        <div class="paper-snippet">${snippet}</div>
                        <div class="paper-actions">
                            ${paper.pdf_url ? `
                                <button class="btn btn-small btn-secondary" onclick="App.downloadPDF('${paper.pdf_url}', '${paper.id}')">
                                    <i class="fas fa-download"></i> Download PDF
                                </button>
                            ` : ''}
                            ${paper.url ? `
                                <button class="btn btn-small btn-secondary" onclick="App.extractAbstract('${paper.url}', '${paper.id}')">
                                    <i class="fas fa-search"></i> Extract Abstract
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
  }

  // Topic category component
  static createTopicCategory(title, items, type = 'list') {
    if (type === 'keywords') {
      const keywordTags = items.map(item =>
        `<span class="keyword-tag">${item}</span>`
      ).join('');

      return `
                <div class="topic-category">
                    <h3>${title}</h3>
                    <div class="keywords-grid">
                        ${keywordTags}
                    </div>
                </div>
            `;
    }

    if (type === 'topics') {
      const topicItems = items.map(item => `
                <li class="topic-item">
                    <strong>${item.description || 'Research Topic'}</strong>
                    ${item.terms ? `<br><small>Key terms: ${item.terms.join(', ')}</small>` : ''}
                </li>
            `).join('');

      return `
                <div class="topic-category">
                    <h3>${title}</h3>
                    <ul class="topic-list">
                        ${topicItems}
                    </ul>
                </div>
            `;
    }

    // Default list type
    const listItems = items.map(item =>
      `<li class="topic-item">${item}</li>`
    ).join('');

    return `
            <div class="topic-category">
                <h3>${title}</h3>
                <ul class="topic-list">
                    ${listItems}
                </ul>
            </div>
        `;
  }

  // Statistics card component
  static createStatCard(label, value, icon) {
    return `
            <div class="stat-card">
                <div class="stat-number">
                    <i class="${icon}"></i>
                    ${value}
                </div>
                <div class="stat-label">${label}</div>
            </div>
        `;
  }

  // Upload item component
  static createUploadItem(filename, abstract, metadata = {}) {
    return `
            <div class="upload-item">
                <h4>
                    <i class="fas fa-file-pdf"></i>
                    ${filename}
                </h4>
                ${metadata.page_count ? `<p><strong>Pages:</strong> ${metadata.page_count}</p>` : ''}
                ${metadata.file_size ? `<p><strong>Size:</strong> ${this.formatFileSize(metadata.file_size)}</p>` : ''}
                <div class="upload-abstract">
                    <strong>Extracted Abstract:</strong><br>
                    ${abstract}
                </div>
            </div>
        `;
  }

  // Utility function to format file size
  static formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  // Modal component
  static createModal(title, content, actions = []) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            margin: 1rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        `;

    const modalHeader = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.25rem; font-weight: 600;">${title}</h3>
                <button onclick="this.closest('.modal-overlay').remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #64748b;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

    const modalActions = actions.length > 0 ? `
            <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
                ${actions.map(action => `
                    <button class="btn ${action.class}" onclick="${action.onclick}">
                        ${action.icon ? `<i class="${action.icon}"></i>` : ''}
                        ${action.text}
                    </button>
                `).join('')}
            </div>
        ` : '';

    modalContent.innerHTML = modalHeader + content + modalActions;
    modal.appendChild(modalContent);

    // Close on overlay click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });

    // Close on Escape key
    const escapeHandler = (e) => {
      if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', escapeHandler);
      }
    };
    document.addEventListener('keydown', escapeHandler);

    document.body.appendChild(modal);
    return modal;
  }

  // Progress bar component
  static createProgressBar(progress = 0) {
    return `
            <div class="progress-bar" style="width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                <div class="progress-fill" style="width: ${progress}%; height: 100%; background: var(--primary-color); transition: width 0.3s ease;"></div>
            </div>
        `;
  }

  // Update progress bar
  static updateProgressBar(element, progress) {
    const fill = element.querySelector('.progress-fill');
    if (fill) {
      fill.style.width = `${progress}%`;
    }
  }

  // Error message component
  static createErrorMessage(message, showRetry = false) {
    return `
            <div class="error-message" style="text-align: center; padding: 2rem; color: var(--error-color);">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.7;"></i>
                <h3 style="margin-bottom: 1rem;">Something went wrong</h3>
                <p style="margin-bottom: 1.5rem; color: var(--text-secondary);">${message}</p>
                ${showRetry ? '<button class="btn btn-primary" onclick="location.reload()"><i class="fas fa-redo"></i> Try Again</button>' : ''}
            </div>
        `;
  }

  // Empty state component
  static createEmptyState(title, message, action = null) {
    return `
            <div class="empty-state" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <i class="fas fa-search" style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.3;"></i>
                <h3 style="margin-bottom: 1rem; color: var(--text-primary);">${title}</h3>
                <p style="margin-bottom: 1.5rem;">${message}</p>
                ${action ? `<button class="btn btn-primary" onclick="${action.onclick}"><i class="${action.icon}"></i> ${action.text}</button>` : ''}
            </div>
        `;
  }
}

// Export for use in other modules
window.Components = Components;
