/**
 * Rival Comp - Single Page Application Core Controller
 */
import API from './api.js';
import Components from './components.js';

let currentView = 'home';
let currentParams = null;
let autocompleteTimer = null;
let currentDiscoveryData = null;



function toggleMobileNav() {
  const dropdown = document.getElementById('mobile-dropdown');
  if (dropdown) {
    dropdown.classList.toggle('open');
  }
}

// Navigation / Router
async function navigate(view, params = null) {
  currentView = view;
  currentParams = params;
  
  // Close any open modals
  closeModal();

  // Update hash
  if (view === 'competitor' && params) {
    window.location.hash = `#competitor/${params}`;
  } else if (view === 'home') {
    window.location.hash = '#home';
  } else {
    window.location.hash = `#${view}`;
  }

  // Update active nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });
  const activeLink = document.getElementById(`nav-${view}`);
  if (activeLink) activeLink.classList.add('active');

  await renderCurrentView();
}

async function renderCurrentView() {
  const main = document.getElementById('main-content');
  if (!main) return;

  main.innerHTML = `
    <div class="loading-initial">
      <div class="spinner"></div>
      <p class="text-secondary mt-2">Loading...</p>
    </div>
  `;

  try {
    switch (currentView) {
      case 'home':
        main.innerHTML = Components.renderLandingHero();
        // Load recent top competitor cards below hero
        loadHomeOverview(main);
        break;

      case 'my-company':
        await loadMyCompanyView(main);
        break;

      case 'dashboard':
        await loadDashboardView(main);
        break;

      case 'alerts':
        await loadAlertsView(main);
        break;

      case 'compare':
        await loadCompareView(main, currentParams);
        break;

      case 'analytics':
        await loadAnalyticsView(main);
        break;

      case 'pricing':
        main.innerHTML = Components.renderPricingView();
        break;

      case 'report':
        await loadReportView(main);
        break;

      case 'competitor':
        await loadCompetitorDetailView(main, currentParams);
        break;

      default:
        main.innerHTML = Components.renderLandingHero();
        loadHomeOverview(main);
        break;
    }
  } catch (err) {
    console.error('Error rendering view:', err);
    main.innerHTML = `
      <div style="text-align:center;padding:4rem 1rem">
        <h2 style="color:var(--accent-red)">Something went wrong</h2>
        <p style="color:var(--text-secondary);margin-top:0.5rem">${Components.escapeHtml(err.message || 'Failed to load content.')}</p>
        <button class="btn btn-primary mt-2" onclick="App.navigate('home')">Return Home</button>
      </div>
    `;
  }
}

// ============================================
// ADMIN COMPANY PROFILE & NICHE RECOMMENDATIONS
// ============================================
const DEFAULT_ADMIN_COMPANY = {
  name: 'Zoxima Solutions',
  website: 'https://zoxima.com',
  industry: 'CRM & Enterprise Sales Automation',
  tagline: 'Enterprise CRM implementation, AI workflow automation, and digital sales transformation.',
  description: 'Zoxima empowers mid-market and enterprise organizations with customized CRM platforms, AI-driven lead scoring, sales automation pipelines, and multi-channel customer engagement workflows.',
  pricingModel: 'Enterprise Customized & Tiered SaaS ($49 - $149/user/month)',
  targetAudience: 'Mid-Market & Enterprise Sales, Customer Success, and Revenue Operations Teams',
  keyStrengths: 'High customization flexibility, dedicated solution architects, seamless ERP integration, rapid deployment and transparent pricing.',
  adminEmail: 'admin@zoxima.com',
  adminName: 'Chief Strategy Officer'
};

function getAdminProfile() {
  try {
    const stored = localStorage.getItem('rivalcomp_admin_company') || localStorage.getItem('competeiq_admin_company');
    if (stored) {
      return { ...DEFAULT_ADMIN_COMPANY, ...JSON.parse(stored) };
    }
  } catch { /* ignore */ }
  return { ...DEFAULT_ADMIN_COMPANY };
}

function saveAdminProfile(profile) {
  try {
    localStorage.setItem('rivalcomp_admin_company', JSON.stringify(profile));
  } catch { /* ignore */ }
}

function getNicheRecommendations(industry) {
  const db = Components.NICHE_COMPETITOR_DATABASE || {};
  if (db[industry]) return db[industry];
  return db['CRM & Enterprise Sales Automation'] || [];
}

async function loadMyCompanyView(main) {
  const adminProfile = getAdminProfile();
  const competitors = await API.dashboard.overview();
  const nicheRecs = getNicheRecommendations(adminProfile.industry);
  main.innerHTML = Components.renderMyCompanyView(adminProfile, competitors, nicheRecs);
}

async function loadCompareView(main, targetCompetitorNameOrId) {
  const competitors = await API.dashboard.overview();
  const adminProfile = getAdminProfile();
  
  let initialIndex = 0;
  if (targetCompetitorNameOrId && competitors && competitors.length > 0) {
    const target = String(targetCompetitorNameOrId).toLowerCase();
    const found = competitors.findIndex(c => 
      c.name.toLowerCase() === target || 
      String(c.competitor_id) === target
    );
    if (found !== -1) initialIndex = found;
  }

  main.innerHTML = Components.renderCompareView(competitors, adminProfile, initialIndex);
}

function showEditCompanyModal() {
  const adminProfile = getAdminProfile();
  const modalContainer = document.getElementById('modal-container');
  if (modalContainer) {
    modalContainer.innerHTML = Components.renderEditCompanyModal(adminProfile);
  }
}

async function handleSaveCompanyProfile(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const updatedProfile = {
    ...getAdminProfile(),
    name: formData.get('name') || '',
    website: formData.get('website') || '',
    industry: formData.get('industry') || '',
    tagline: formData.get('tagline') || '',
    description: formData.get('description') || '',
    pricingModel: formData.get('pricingModel') || '',
    targetAudience: formData.get('targetAudience') || '',
    keyStrengths: formData.get('keyStrengths') || '',
  };

  saveAdminProfile(updatedProfile);
  closeModal();
  Components.showToast(`Company profile updated for ${updatedProfile.name}!`, 'success');

  const main = document.getElementById('main-content');
  if (main) {
    if (currentView === 'my-company') {
      await loadMyCompanyView(main);
    } else if (currentView === 'compare') {
      await loadCompareView(main);
    }
  }
}

async function handleSignupSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const companyName = formData.get('companyName') || 'My Company';
  const companyWebsite = formData.get('companyWebsite') || 'https://example.com';
  const companyIndustry = formData.get('companyIndustry') || 'CRM & Enterprise Sales Automation';
  const adminName = formData.get('adminName') || 'Administrator';
  const adminEmail = formData.get('adminEmail') || 'admin@example.com';

  const newProfile = {
    ...getAdminProfile(),
    name: companyName,
    website: companyWebsite,
    industry: companyIndustry,
    adminName: adminName,
    adminEmail: adminEmail,
    tagline: `${companyName} — ${companyIndustry} Platform.`,
    description: `${companyName} delivers cutting-edge solutions in ${companyIndustry}.`,
  };

  saveAdminProfile(newProfile);
  closeModal();
  Components.showToast(`Welcome ${adminName}! Your workspace for ${companyName} is ready.`, 'success');
  await navigate('my-company');
}

async function addCompetitorFromNiche(nicheKey, btnEl) {
  const adminProfile = getAdminProfile();
  const recs = getNicheRecommendations(adminProfile.industry);
  const rec = recs.find(r => r.key === nicheKey);
  if (!rec) return;

  if (btnEl) {
    btnEl.disabled = true;
    btnEl.innerHTML = '<div class="spinner" style="width:12px;height:12px;border-width:2px;display:inline-block;margin-right:4px"></div> Adding...';
  }

  try {
    await API.discovery.batchAdd({
      industry: rec.industry,
      competitors: [{
        name: rec.name,
        website: rec.website,
        industry: rec.industry,
        description: rec.description,
        sources: [
          { source_type: 'company_website', url: rec.website, scrape_frequency: 1440 },
          { source_type: 'pricing_page', url: `${rec.website.replace(/\/$/, '')}/pricing`, scrape_frequency: 1440 }
        ]
      }]
    });

    if (btnEl) {
      btnEl.disabled = true;
      btnEl.className = 'btn btn-secondary btn-sm';
      btnEl.textContent = '✓ In Directory';
    }
    Components.showToast(`Added ${rec.name} to your monitored competitors!`, 'success');

    const main = document.getElementById('main-content');
    if (main && currentView === 'my-company') {
      await loadMyCompanyView(main);
    }
  } catch (err) {
    Components.showToast(`Could not add competitor: ${err.message}`, 'error');
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.textContent = '➕ Add as Competitor';
    }
  }
}

async function compareWithAdminCompany(competitorName) {
  await navigate('compare');
  const main = document.getElementById('main-content');
  if (main) {
    await loadCompareView(main, competitorName);
  }
}

async function loadHomeOverview(container) {
  try {
    const competitors = await API.dashboard.overview();
    if (competitors && competitors.length > 0) {
      const section = document.createElement('div');
      section.style.marginTop = '3rem';
      section.innerHTML = `
        <div class="section-header" style="margin-bottom:1rem">
          <div>
            <h2>Monitored Competitors (${competitors.length})</h2>
            <p style="color:var(--text-secondary)">Quick snapshot of recently active market players</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="App.navigate('dashboard')">View All →</button>
        </div>
        <div class="card-grid">
          ${competitors.slice(0, 6).map(c => Components.renderCompetitorCard(c)).join('')}
        </div>
      `;
      container.appendChild(section);
    }
  } catch (e) {
    console.warn('Could not load home overview:', e);
  }
}

async function loadDashboardView(main) {
  const competitors = await API.dashboard.overview();
  let schedulerStatus = null;
  try {
    schedulerStatus = await API.scraper.schedulerStatus();
  } catch { /* ignore */ }

  const statusBanner = schedulerStatus ? `
    <div class="card mb-2" style="background:var(--bg-surface-2);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;padding:0.75rem 1.25rem">
      <div style="display:flex;align-items:center;gap:0.75rem">
        <div style="width:10px;height:10px;border-radius:50%;background:${schedulerStatus.running ? 'var(--accent-green)' : 'var(--text-muted)'}"></div>
        <span style="font-size:0.875rem">
          <strong>Background Sweep:</strong> ${schedulerStatus.running ? 'Active (Auto-checks hourly)' : 'Paused'}
        </span>
      </div>
      <div style="display:flex;gap:0.5rem">
        <button class="btn btn-secondary btn-sm" onclick="App.triggerSchedulerNow()">⚡ Run Sweep Now</button>
      </div>
    </div>
  ` : '';

  if (!competitors || competitors.length === 0) {
    main.innerHTML = `
      ${statusBanner}
      <div style="text-align:center;padding:4rem 1rem">
        <h2>No Competitors Tracked Yet</h2>
        <p style="color:var(--text-secondary);margin-top:0.5rem">Start tracking your competitors to receive automated intelligence and alerts.</p>
        <button class="btn btn-primary mt-2" onclick="App.navigate('my-company')">View Niche Recommendations</button>
      </div>
    `;
    return;
  }

  main.innerHTML = `
    ${statusBanner}
    <div class="section-header" style="margin-bottom:1.5rem">
      <div>
        <h1>Monitored Competitors (${competitors.length})</h1>
        <p style="color:var(--text-secondary)">Real-time intelligence feed and tracked public sources.</p>
      </div>
      <div style="display:flex;gap:0.5rem">
        <button class="btn btn-secondary btn-sm" onclick="App.navigate('my-company')">🏢 My Company Workspace</button>
        <button class="btn btn-primary btn-sm" onclick="App.navigate('home')">+ Add Competitor</button>
      </div>
    </div>
    <div class="card-grid">
      ${competitors.map(c => Components.renderCompetitorCard(c)).join('')}
    </div>
  `;
}

async function loadAlertsView(main) {
  const alerts = await API.alerts.listAll();
  main.innerHTML = Components.renderAlertsPage(alerts);
}

async function loadAnalyticsView(main) {
  const analytics = await API.dashboard.analytics();
  const competitors = await API.dashboard.overview();
  main.innerHTML = Components.renderAnalyticsView(analytics, competitors);
}

async function loadReportView(main) {
  const competitors = await API.dashboard.overview();
  main.innerHTML = `
    <div style="margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center">
      <button class="btn btn-secondary btn-sm" onclick="App.navigate('analytics')">← Back to Analytics</button>
      <button class="btn btn-primary btn-sm" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>
    ${Components.renderExecutiveReport(competitors)}
  `;
}

async function loadCompetitorDetailView(main, competitorId) {
  if (!competitorId) {
    await navigate('dashboard');
    return;
  }
  const detail = await API.dashboard.competitorDetail(competitorId);
  main.innerHTML = Components.renderCompetitorDetail(detail);
}

// Search & Autocomplete
function handleTypeaheadInput(e) {
  const q = e.target.value.trim();
  const dropdown = document.getElementById('autocomplete-dropdown');
  if (!dropdown) return;

  clearTimeout(autocompleteTimer);
  if (!q || q.length < 2) {
    dropdown.innerHTML = '';
    dropdown.style.display = 'none';
    return;
  }

  autocompleteTimer = setTimeout(async () => {
    try {
      const results = await API.discovery.autocomplete(q);
      if (results && results.length > 0) {
        dropdown.innerHTML = results.map(item => `
          <div class="autocomplete-item" onclick="App.selectAutocomplete('${item.name.replace(/'/g, "\\'")}')">
            ${Components.renderCompanyLogo(item.logo || item.clearbit_logo, item.name, item.domain, 'autocomplete-logo')}
            <div>
              <div style="font-weight:600;font-size:0.875rem">${Components.escapeHtml(item.name)}</div>
              <div style="font-size:0.75rem;color:var(--text-muted)">${Components.escapeHtml(item.industry || item.domain || '')}</div>
            </div>
          </div>
        `).join('');
        dropdown.style.display = 'block';
      } else {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
      }
    } catch {
      dropdown.style.display = 'none';
    }
  }, 250);
}

function selectAutocomplete(name) {
  const input = document.getElementById('hero-search-input');
  if (input) input.value = name;
  const dropdown = document.getElementById('autocomplete-dropdown');
  if (dropdown) dropdown.style.display = 'none';
  quickSearch(name);
}

function quickSearch(companyName) {
  const input = document.getElementById('hero-search-input');
  if (input) input.value = companyName;
  executeSearch(companyName);
}

async function handleHeroSearch(e) {
  e.preventDefault();
  const input = document.getElementById('hero-search-input');
  if (!input) return;
  const q = input.value.trim();
  if (q) executeSearch(q);
}

let currentSearchResults = [];

async function executeSearch(companyName) {
  const btn = document.getElementById('hero-search-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:6px"></div> Searching...';
  }

  try {
    const discovery = await API.discovery.search(companyName);
    const primary = discovery.company;
    const recs = discovery.recommended_competitors || [];
    currentSearchResults = primary ? [primary, ...recs] : recs;

    const modalContainer = document.getElementById('modal-container');
    if (modalContainer) {
      modalContainer.innerHTML = Components.renderDiscoveryModal(currentSearchResults, companyName);
    }
  } catch (err) {
    Components.showToast(`Search failed: ${err.message}`, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = 'Analyze Company';
    }
  }
}

async function addSingleCompetitorFromSearch(index, btnEl) {
  const comp = currentSearchResults[index];
  if (!comp) return;

  if (btnEl) {
    btnEl.disabled = true;
    btnEl.innerHTML = '<div class="spinner" style="width:12px;height:12px;border-width:2px;display:inline-block;margin-right:4px"></div> Adding...';
  }

  try {
    const res = await API.discovery.batchAdd({
      industry: comp.industry,
      competitors: [comp],
    });

    if (btnEl) {
      btnEl.disabled = true;
      btnEl.className = 'btn btn-sm';
      btnEl.style.background = 'rgba(16, 185, 129, 0.15)';
      btnEl.style.color = '#10b981';
      btnEl.style.borderColor = 'rgba(16, 185, 129, 0.3)';
      btnEl.textContent = '✓ Added';
    }
    Components.showToast(`Added ${comp.name} to monitored competitors!`, 'success');

    if (currentView === 'dashboard') {
      const main = document.getElementById('main-content');
      if (main) loadDashboardView(main);
    }
  } catch (err) {
    Components.showToast(`Failed to add competitor: ${err.message}`, 'error');
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.textContent = '➕ Add to Competitors';
    }
  }
}

async function analyzeCompanyFromSearch(index, btnEl) {
  const comp = currentSearchResults[index];
  if (!comp) return;

  if (btnEl) {
    btnEl.disabled = true;
    btnEl.innerHTML = '<div class="spinner" style="width:12px;height:12px;border-width:2px;display:inline-block;margin-right:4px"></div> Loading...';
  }

  try {
    const res = await API.discovery.batchAdd({
      industry: comp.industry,
      competitors: [comp],
    });

    let compId = null;
    if (res.added && res.added.length > 0) {
      compId = res.added[0].competitor_id;
    } else {
      const all = await API.competitors.list();
      const match = all.find(c => c.name.toLowerCase() === comp.name.toLowerCase());
      if (match) compId = match.id;
    }

    closeModal();
    if (compId) {
      Components.showToast(`Opening intelligence for ${comp.name}...`, 'info');
      await navigate('competitor', compId);
    } else {
      await navigate('dashboard');
    }
  } catch (err) {
    Components.showToast(`Analysis failed: ${err.message}`, 'error');
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.textContent = '⚡ Analyze';
    }
  }
}

// Scrape Actions
async function scrapeSource(sourceId) {
  const btn = document.getElementById(`scrape-btn-${sourceId}`);
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:14px;height:14px;border-width:2px;display:inline-block;margin-right:4px"></div> Scraping...';
  }

  try {
    const res = await API.scraper.scrapeSource(sourceId);
    if (res.has_changed) {
      Components.showToast(`Scrape completed! Changes detected & analyzed.`, 'success');
    } else {
      Components.showToast(`Scraped. No new text changes detected.`, 'info');
    }
    if (currentView === 'competitor' && currentParams) {
      await loadCompetitorDetailView(document.getElementById('main-content'), currentParams);
    }
  } catch (err) {
    Components.showToast(`Scrape failed: ${err.message}`, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = '⚡ Scrape Now';
    }
  }
}

async function scrapeAllSources(competitorId) {
  const btn = document.getElementById('scrape-all-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:14px;height:14px;border-width:2px;display:inline-block;margin-right:4px"></div> Scraping All...';
  }

  try {
    const res = await API.scraper.scrapeAll(competitorId);
    Components.showToast(`Triggered full scrape for ${res.sources_queued || 'all'} sources!`, 'success');
    setTimeout(async () => {
      if (currentView === 'competitor' && currentParams) {
        await loadCompetitorDetailView(document.getElementById('main-content'), currentParams);
      }
    }, 1500);
  } catch (err) {
    Components.showToast(`Scrape all failed: ${err.message}`, 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = '⚡ Scrape All Sources';
    }
  }
}

async function triggerSchedulerNow() {
  try {
    await API.scraper.triggerScheduler();
    Components.showToast('Background sweep triggered successfully!', 'success');
  } catch (err) {
    Components.showToast(`Scheduler error: ${err.message}`, 'error');
  }
}

async function deleteCompetitor(competitorId) {
  if (!confirm('Are you sure you want to stop tracking this competitor and delete all history?')) {
    return;
  }
  try {
    await API.competitors.delete(competitorId);
    Components.showToast('Competitor deleted.', 'info');
    await navigate('dashboard');
  } catch (err) {
    Components.showToast(`Delete failed: ${err.message}`, 'error');
  }
}

async function confirmAddAsCompetitor(competitorId, name) {
  const btn = document.getElementById(`btn-add-comp-${competitorId}`);
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:12px;height:12px;border-width:2px;display:inline-block;margin-right:4px"></div> Saving...';
  }

  try {
    await API.competitors.update(competitorId, { is_active: true });
    Components.showToast(`✓ ${name} confirmed in monitored competitor directory!`, 'success');
    if (btn) {
      btn.disabled = true;
      btn.className = 'btn btn-sm';
      btn.style.background = 'rgba(16, 185, 129, 0.15)';
      btn.style.color = '#10b981';
      btn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
      btn.textContent = '✓ In Competitor Directory';
    }
  } catch (err) {
    Components.showToast(`Error adding competitor: ${err.message}`, 'error');
    if (btn) {
      btn.disabled = false;
      btn.textContent = '➕ Add this as Competition';
    }
  }
}

async function toggleCompetitorTracking(competitorId) {
  const btn = document.getElementById(`btn-track-comp-${competitorId}`);
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:12px;height:12px;border-width:2px;display:inline-block;margin-right:4px"></div> Updating...';
  }

  try {
    const detail = await API.dashboard.competitorDetail(competitorId);
    const currentActive = detail.competitor.is_active !== false;
    const newStatus = !currentActive;

    await API.competitors.update(competitorId, { is_active: newStatus });
    Components.showToast(newStatus ? `Live tracking active for ${detail.competitor.name}` : `Tracking paused for ${detail.competitor.name}`, 'info');

    const main = document.getElementById('main-content');
    if (main && currentView === 'competitor') {
      await loadCompetitorDetailView(main, competitorId);
    }
  } catch (err) {
    Components.showToast(`Failed to update tracking: ${err.message}`, 'error');
    if (btn) {
      btn.disabled = false;
      btn.textContent = '📡 Track this Company';
    }
  }
}

async function markAlertSent(alertId, btnEl) {
  try {
    await API.alerts.markSent(alertId);
    if (btnEl) btnEl.remove();
    Components.showToast('Alert marked as sent.', 'success');
  } catch (err) {
    Components.showToast(`Error: ${err.message}`, 'error');
  }
}

// Navbar Search & Autocomplete
let navbarAutocompleteTimer = null;

function toggleNavbarSearch(open) {
  const wrapper = document.getElementById('navbar-search-wrapper');
  const input = document.getElementById('navbar-search-input');
  const dropdown = document.getElementById('navbar-autocomplete-dropdown');
  if (!wrapper) return;

  if (open) {
    wrapper.classList.add('expanded');
    if (input) {
      setTimeout(() => input.focus(), 100);
    }
  } else {
    wrapper.classList.remove('expanded');
    if (input) input.value = '';
    if (dropdown) {
      dropdown.innerHTML = '';
      dropdown.style.display = 'none';
    }
  }
}

function handleNavbarTypeaheadInput(e) {
  const q = e.target.value.trim();
  const dropdown = document.getElementById('navbar-autocomplete-dropdown');
  if (!dropdown) return;

  clearTimeout(navbarAutocompleteTimer);
  if (!q || q.length < 2) {
    dropdown.innerHTML = '';
    dropdown.style.display = 'none';
    return;
  }

  navbarAutocompleteTimer = setTimeout(async () => {
    try {
      const results = await API.discovery.autocomplete(q);
      if (results && results.length > 0) {
        dropdown.innerHTML = results.map(item => `
          <div class="autocomplete-item" onclick="App.selectNavbarAutocomplete('${item.name.replace(/'/g, "\\'")}')">
            ${Components.renderCompanyLogo(item.logo || item.clearbit_logo, item.name, item.domain, 'autocomplete-logo')}
            <div>
              <div style="font-weight:600;font-size:0.875rem">${Components.escapeHtml(item.name)}</div>
              <div style="font-size:0.75rem;color:var(--text-muted)">${Components.escapeHtml(item.industry || item.domain || '')}</div>
            </div>
          </div>
        `).join('');
        dropdown.style.display = 'block';
      } else {
        dropdown.innerHTML = '';
        dropdown.style.display = 'none';
      }
    } catch {
      dropdown.style.display = 'none';
    }
  }, 250);
}

function selectNavbarAutocomplete(name) {
  toggleNavbarSearch(false);
  executeSearch(name);
}

function handleNavbarSearchSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('navbar-search-input');
  if (!input) return;
  const q = input.value.trim();
  if (q) {
    toggleNavbarSearch(false);
    executeSearch(q);
  }
}

// Modal handling
function showLoginModal(defaultTab = 'login') {
  const modalContainer = document.getElementById('modal-container');
  if (modalContainer) {
    modalContainer.innerHTML = Components.renderLoginModal(defaultTab);
  }
}

function switchAuthTab(tab) {
  const loginTab = document.getElementById('auth-tab-login');
  const signupTab = document.getElementById('auth-tab-signup');
  const loginPane = document.getElementById('auth-pane-login');
  const signupPane = document.getElementById('auth-pane-signup');

  if (loginTab && signupTab && loginPane && signupPane) {
    if (tab === 'signup') {
      loginTab.classList.remove('active');
      signupTab.classList.add('active');
      loginPane.style.display = 'none';
      signupPane.style.display = 'block';
    } else {
      signupTab.classList.remove('active');
      loginTab.classList.add('active');
      signupPane.style.display = 'none';
      loginPane.style.display = 'block';
    }
  }
}

function closeModal() {
  const modalContainer = document.getElementById('modal-container');
  if (modalContainer) modalContainer.innerHTML = '';
}

// Router hashchange listener
function handleHashChange() {
  const hash = window.location.hash.replace('#', '') || 'home';
  if (hash.startsWith('competitor/')) {
    const id = hash.split('/')[1];
    navigate('competitor', id);
  } else if (hash.startsWith('company/')) {
    const id = hash.split('/')[1];
    navigate('competitor', id);
  } else {
    navigate(hash);
  }
}

// Expose on window for inline HTML onclick handlers
const App = {
  toggleMobileNav,
  navigate,
  toggleNavbarSearch,
  handleNavbarTypeaheadInput,
  selectNavbarAutocomplete,
  handleNavbarSearchSubmit,
  handleHeroSearch,
  handleTypeaheadInput,
  selectAutocomplete,
  quickSearch,
  addSingleCompetitorFromSearch,
  analyzeCompanyFromSearch,
  confirmAddAsCompetitor,
  toggleCompetitorTracking,
  scrapeSource,
  scrapeAllSources,
  triggerSchedulerNow,
  deleteCompetitor,
  markAlertSent,
  showLoginModal,
  switchAuthTab,
  closeModal,
  showEditCompanyModal,
  handleSaveCompanyProfile,
  handleSignupSubmit,
  addCompetitorFromNiche,
  compareWithAdminCompany,
  getAdminProfile,
  saveAdminProfile,
};

window.App = App;

// Initial bootstrap on DOM ready
function bootstrap() {
  window.addEventListener('hashchange', handleHashChange);
  
  // Close autocomplete on click outside
  document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('autocomplete-dropdown');
    if (dropdown && !e.target.closest('.search-wrapper')) {
      dropdown.style.display = 'none';
    }

    const navbarSearchWrapper = document.getElementById('navbar-search-wrapper');
    const navbarDropdown = document.getElementById('navbar-autocomplete-dropdown');
    if (navbarSearchWrapper && !e.target.closest('.navbar-search-wrapper')) {
      const input = document.getElementById('navbar-search-input');
      if (!input || !input.value.trim()) {
        toggleNavbarSearch(false);
      } else if (navbarDropdown) {
        navbarDropdown.style.display = 'none';
      }
    }
  });

  // Handle initial route
  handleHashChange();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

export default App;
