// Main Application Logic for Smart Research Assistant

class SmartResearchApp {
  constructor() {
    this.apiBaseUrl = '/api';
    this.currentPapers = [];
    this.selectedPapers = [];
    this.currentTopics = null;

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupNavigation();
    this.setupFileUpload();
    this.loadStatistics();
  }

  // Event Listeners Setup
  setupEventListeners() {
    // Search form
    const searchForm = document.getElementById('search-form');
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.performSearch();
    });

    // Generate topics button
    const generateTopicsBtn = document.getElementById('generate-topics-btn');
    generateTopicsBtn.addEventListener('click', () => {
      this.generateTopics();
    });

    // Select all button
    const selectAllBtn = document.getElementById('select-all-btn');
    selectAllBtn.addEventListener('click', () => {
      this.toggleSelectAll();
    });

    // Window resize handler
    window.addEventListener('resize', this.handleResize.bind(this));
  }

  // Navigation Setup
  setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        this.switchTab(tabName);

        // Update active state
        navButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  // Tab Switching
  switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.remove('active');
    });

    // Show selected tab
    const targetTab = document.getElementById(`${tabName}-tab`);
    if (targetTab) {
      targetTab.classList.add('active');

      // Load tab-specific content
      this.loadTabContent(tabName);
    }
  }

  // Load content for specific tabs
  loadTabContent(tabName) {
    switch (tabName) {
      case 'stats':
        this.loadStatistics();
        break;
      case 'topics':
        if (this.currentTopics) {
          this.displayTopics(this.currentTopics);
        }
        break;
    }
  }

  // Search Functionality
  async performSearch() {
    const query = document.getElementById('search-query').value.trim();
    const maxResults = parseInt(document.getElementById('max-results').value);
    const yearFrom = document.getElementById('year-from').value;
    const yearTo = document.getElementById('year-to').value;

    if (!query) {
      Components.showToast('Please enter a search query', 'warning');
      return;
    }

    // Prepare search data
    const searchData = {
      query: query,
      max_results: maxResults
    };

    // Add year range if specified
    if (yearFrom && yearTo) {
      searchData.year_range = [parseInt(yearFrom), parseInt(yearTo)];
    }

    // Show loading state
    this.showLoading('search-results', 'Searching academic papers...');
    this.setButtonLoading('search-btn', true);

    try {
      const response = await fetch(`${this.apiBaseUrl}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchData)
      });

      const result = await response.json();

      if (result.success) {
        this.currentPapers = result.data.papers;
        this.displaySearchResults(result.data);

        if (result.data.from_cache) {
          Components.showToast('Results loaded from cache', 'info');
        } else {
          Components.showToast(`Found ${this.currentPapers.length} papers`, 'success');
        }
      } else {
        throw new Error(result.error || 'Search failed');
      }

    } catch (error) {
      console.error('Search error:', error);
      this.showError('search-results', 'Failed to search papers. Please try again.');
      Components.showToast(`Search failed: ${error.message}`, 'error');
    } finally {
      this.setButtonLoading('search-btn', false);
    }
  }

  // Display search results
  displaySearchResults(data) {
    const resultsContainer = document.getElementById('search-results');
    const papersList = document.getElementById('papers-list');

    if (!data.papers || data.papers.length === 0) {
      papersList.innerHTML = Components.createEmptyState(
        'No papers found',
        'Try adjusting your search terms or criteria',
        {
          text: 'New Search',
          icon: 'fas fa-search',
          onclick: "document.getElementById('search-query').focus()"
        }
      );
    } else {
      papersList.innerHTML = data.papers.map((paper, index) =>
        Components.createPaperItem(paper, index)
      ).join('');
    }

    resultsContainer.classList.remove('hidden');
    this.updateSelectedPapers();
  }

  // Update selected papers count and button state
  updateSelectedPapers() {
    const checkboxes = document.querySelectorAll('#papers-list input[type="checkbox"]:checked');
    const generateBtn = document.getElementById('generate-topics-btn');

    this.selectedPapers = Array.from(checkboxes).map(cb => {
      const index = parseInt(cb.value);
      return this.currentPapers[index];
    });

    generateBtn.disabled = this.selectedPapers.length === 0;
    generateBtn.textContent = this.selectedPapers.length > 0
      ? `Generate Topics (${this.selectedPapers.length} selected)`
      : 'Generate Topics';
  }

  // Toggle select all papers
  toggleSelectAll() {
    const checkboxes = document.querySelectorAll('#papers-list input[type="checkbox"]');
    const selectAllBtn = document.getElementById('select-all-btn');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);

    checkboxes.forEach(cb => {
      cb.checked = !allChecked;
    });

    selectAllBtn.innerHTML = allChecked
      ? '<i class="fas fa-check-square"></i> Select All'
      : '<i class="fas fa-square"></i> Deselect All';

    this.updateSelectedPapers();
  }

  // Generate Topics
  async generateTopics() {
    if (this.selectedPapers.length === 0) {
      Components.showToast('Please select at least one paper', 'warning');
      return;
    }

    // Switch to topics tab and show loading
    this.switchTab('topics');
    document.querySelector('[data-tab="topics"]').classList.add('active');
    document.querySelector('[data-tab="search"]').classList.remove('active');

    this.showLoading('topics-results', 'Generating research topics using AI...');

    try {
      const response = await fetch(`${this.apiBaseUrl}/generate-topics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          papers: this.selectedPapers,
          n_topics: 5
        })
      });

      const result = await response.json();

      if (result.success) {
        this.currentTopics = result.data;
        this.displayTopics(result.data);
        Components.showToast(`Generated ${result.data.cluster_based_topics?.length || 0} topic categories`, 'success');
      } else {
        throw new Error(result.error || 'Topic generation failed');
      }

    } catch (error) {
      console.error('Topic generation error:', error);
      this.showError('topics-results', 'Failed to generate topics. Please try again.');
      Components.showToast(`Topic generation failed: ${error.message}`, 'error');
    }
  }

  // Display generated topics
  displayTopics(data) {
    const resultsContainer = document.getElementById('topics-results');

    let html = '';

    // Keywords
    if (data.keywords && data.keywords.length > 0) {
      html += Components.createTopicCategory('🏷️ Key Research Terms', data.keywords, 'keywords');
    }

    // Cluster-based topics
    if (data.cluster_based_topics && data.cluster_based_topics.length > 0) {
      html += Components.createTopicCategory('🎯 Research Focus Areas', data.cluster_based_topics, 'topics');
    }

    // LDA-based topics
    if (data.lda_based_topics && data.lda_based_topics.length > 0) {
      html += Components.createTopicCategory('📊 Thematic Categories', data.lda_based_topics, 'topics');
    }

    // Research questions
    if (data.research_questions && data.research_questions.length > 0) {
      html += Components.createTopicCategory('❓ Potential Research Questions', data.research_questions);
    }

    // Summary
    if (data.summary) {
      const summaryItems = [
        `📚 Analyzed ${data.summary.total_papers} papers`,
        `🔍 Extracted ${data.summary.text_sources} text sources`,
        `🏷️ Top keywords: ${data.summary.top_keywords?.join(', ') || 'N/A'}`
      ];
      html += Components.createTopicCategory('📋 Analysis Summary', summaryItems);
    }

    resultsContainer.innerHTML = html;
    resultsContainer.classList.remove('hidden');
  }

  // File Upload Setup
  setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('pdf-upload');

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');

      const files = Array.from(e.dataTransfer.files).filter(file =>
        file.type === 'application/pdf'
      );

      if (files.length > 0) {
        this.uploadPDFs(files);
      } else {
        Components.showToast('Please drop only PDF files', 'warning');
      }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
      const files = Array.from(e.target.files);
      if (files.length > 0) {
        this.uploadPDFs(files);
      }
    });
  }

  // Upload PDF files
  async uploadPDFs(files) {
    const resultsContainer = document.getElementById('upload-results');
    resultsContainer.innerHTML = '';
    resultsContainer.classList.remove('hidden');

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      await this.uploadSinglePDF(file, i, files.length);
    }

    Components.showToast(`Successfully processed ${files.length} PDF(s)`, 'success');
  }

  // Upload single PDF
  async uploadSinglePDF(file, index, total) {
    const resultsContainer = document.getElementById('upload-results');

    // Create upload item placeholder
    const uploadItem = document.createElement('div');
    uploadItem.className = 'upload-item';
    uploadItem.innerHTML = `
            <h4><i class="fas fa-file-pdf"></i> ${file.name}</h4>
            <div class="progress-container">
                ${Components.createProgressBar(0)}
                <p>Uploading and processing...</p>
            </div>
        `;
    resultsContainer.appendChild(uploadItem);

    try {
      const formData = new FormData();
      formData.append('pdf', file);

      // Simulate upload progress
      const progressBar = uploadItem.querySelector('.progress-bar');
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress > 90) progress = 90;
        Components.updateProgressBar(progressBar, progress);
      }, 200);

      const response = await fetch(`${this.apiBaseUrl}/upload-pdf`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      clearInterval(progressInterval);
      Components.updateProgressBar(progressBar, 100);

      if (result.success) {
        const metadata = {
          filename: result.data.filename,
          timestamp: result.data.timestamp
        };

        uploadItem.innerHTML = Components.createUploadItem(
          file.name,
          result.data.abstract,
          metadata
        );
      } else {
        throw new Error(result.error || 'Upload failed');
      }

    } catch (error) {
      console.error('Upload error:', error);
      uploadItem.innerHTML = `
                <h4><i class="fas fa-file-pdf"></i> ${file.name}</h4>
                <div class="error-message" style="color: var(--error-color); padding: 1rem;">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to process: ${error.message}
                </div>
            `;
    }
  }

  // Load application statistics
  async loadStatistics() {
    const statsContent = document.getElementById('stats-content');

    this.showLoading('stats-content', 'Loading statistics...');

    try {
      const response = await fetch(`${this.apiBaseUrl}/stats`);
      const result = await response.json();

      if (result.success) {
        this.displayStatistics(result.data);
      } else {
        throw new Error(result.error || 'Failed to load statistics');
      }

    } catch (error) {
      console.error('Statistics error:', error);
      statsContent.innerHTML = Components.createErrorMessage(
        'Failed to load statistics. Please refresh the page.',
        true
      );
    }
  }

  // Display statistics
  displayStatistics(stats) {
    const statsContent = document.getElementById('stats-content');

    const statCards = [
      { label: 'Total Searches', value: stats.total_searches || 0, icon: 'fas fa-search' },
      { label: 'Papers Found', value: stats.total_papers || 0, icon: 'fas fa-file-alt' },
      { label: 'Topics Generated', value: stats.total_topics_generated || 0, icon: 'fas fa-lightbulb' },
      { label: 'PDFs Processed', value: stats.total_pdfs_processed || 0, icon: 'fas fa-file-pdf' },
      { label: 'Recent Searches', value: stats.recent_searches || 0, icon: 'fas fa-clock' }
    ];

    let html = statCards.map(stat =>
      Components.createStatCard(stat.label, stat.value, stat.icon)
    ).join('');

    // Add top queries if available
    if (stats.top_queries && stats.top_queries.length > 0) {
      const topQueries = stats.top_queries.map(q =>
        `${q.query} (${q.count} searches)`
      );
      html += Components.createTopicCategory('🔥 Popular Search Terms', topQueries);
    }

    // Add papers by year if available
    if (stats.papers_by_year && stats.papers_by_year.length > 0) {
      const yearData = stats.papers_by_year.map(y =>
        `${y.year}: ${y.count} papers`
      );
      html += Components.createTopicCategory('📅 Papers by Publication Year', yearData);
    }

    statsContent.innerHTML = html;
  }

  // Utility Functions
  showLoading(containerId, message = 'Loading...') {
    const container = document.getElementById(containerId);
    container.innerHTML = Components.createLoadingSpinner(message);
    container.classList.remove('hidden');
  }

  showError(containerId, message) {
    const container = document.getElementById(containerId);
    container.innerHTML = Components.createErrorMessage(message, true);
    container.classList.remove('hidden');
  }

  setButtonLoading(buttonId, loading) {
    const button = document.getElementById(buttonId);
    if (loading) {
      button.disabled = true;
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
    } else {
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-search"></i> Search';
    }
  }

  handleResize() {
    // Handle responsive layout changes
    const isMobile = window.innerWidth < 768;
    document.body.classList.toggle('mobile', isMobile);
  }

  // Additional features
  async downloadPDF(pdfUrl, paperId) {
    try {
      Components.showToast('Starting PDF download...', 'info');

      const response = await fetch(`${this.apiBaseUrl}/download-pdf/${paperId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pdf_url: pdfUrl })
      });

      const result = await response.json();

      if (result.success) {
        Components.showToast('PDF downloaded and processed successfully', 'success');
        if (result.data.abstract) {
          Components.createModal(
            'Extracted Abstract',
            `<div class="upload-abstract">${result.data.abstract}</div>`,
            [{
              text: 'Close',
              class: 'btn-secondary',
              onclick: 'this.closest(".modal-overlay").remove()'
            }]
          );
        }
      } else {
        throw new Error(result.error || 'Download failed');
      }

    } catch (error) {
      Components.showToast(`Download failed: ${error.message}`, 'error');
    }
  }

  async extractAbstract(paperUrl, paperId) {
    try {
      Components.showToast('Extracting abstract from paper...', 'info');

      // This would need to be implemented in the backend
      const response = await fetch(`${this.apiBaseUrl}/extract-abstract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper_url: paperUrl,
          paper_id: paperId
        })
      });

      const result = await response.json();

      if (result.success) {
        Components.showToast('Abstract extracted successfully', 'success');
        Components.createModal(
          'Extracted Abstract',
          `<div class="upload-abstract">${result.data.abstract}</div>`,
          [{
            text: 'Close',
            class: 'btn-secondary',
            onclick: 'this.closest(".modal-overlay").remove()'
          }]
        );
      } else {
        throw new Error(result.error || 'Extraction failed');
      }

    } catch (error) {
      Components.showToast(`Abstract extraction failed: ${error.message}`, 'error');
    }
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.App = new SmartResearchApp();
});

// Export for global access
window.SmartResearchApp = SmartResearchApp;
