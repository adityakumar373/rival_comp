/**
 * Reusable UI Components for Rival Comp SaaS Platform.
 * Fixed: evidence links, alerts section, real analytics, Compare picker,
 *        global Alerts page, Scrape-All button, missing badge CSS mapping.
 */

/* ============================================
   UTILS
   ============================================ */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  const d = document.createElement('div');
  d.textContent = String(str);
  return d.innerHTML;
}

function timeAgo(dateString) {
  if (!dateString) return 'Never';
  const diff = Math.floor((Date.now() - new Date(dateString).getTime()) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function getImpactLevel(score) {
  if (score >= 70) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

function getImpactColor(score) {
  if (score >= 70) return 'var(--accent-red)';
  if (score >= 40) return 'var(--accent-amber)';
  return 'var(--text-secondary)';
}

function getCategoryEmoji(category) {
  const map = {
    pricing: '💰', hiring: '👥', product: '🚀', partnership: '🤝',
    marketing: '📣', news: '📰', market_activity: '📈', other: '🔍',
  };
  return map[category] || '🔍';
}

function shortenUrl(url, maxLen = 45) {
  if (!url) return '';
  try {
    const u = new URL(url);
    const short = u.hostname + u.pathname;
    return short.length > maxLen ? short.slice(0, maxLen) + '…' : short;
  } catch {
    return url.length > maxLen ? url.slice(0, maxLen) + '…' : url;
  }
}

/* ============================================
   ROBUST COMPANY LOGO / AVATAR RENDERER
   ============================================ */
function renderCompanyLogo(logoUrl, companyName = '', domain = '', className = 'search-result-logo') {
  const name = String(companyName || domain || 'Company').trim();
  const initial = (name.charAt(0) || 'C').toUpperCase();
  const cleanDom = String(domain || logoUrl || name)
    .replace(/^https?:\/\//i, '')
    .replace(/^www\./i, '')
    .split('/')[0]
    .split('?')[0];
  const googleFavicon = cleanDom ? `https://www.google.com/s2/favicons?domain=${cleanDom}&sz=128` : '';
  const clearbitLogo = cleanDom ? `https://logo.clearbit.com/${cleanDom}` : '';
  const primarySrc = logoUrl || clearbitLogo || googleFavicon;

  if (!primarySrc) {
    return `<div class="company-avatar-fallback ${className}">${escapeHtml(initial)}</div>`;
  }

  return `
    <div style="position:relative;display:inline-flex;align-items:center;flex-shrink:0">
      <img src="${escapeHtml(primarySrc)}" 
           class="${className}" 
           alt="${escapeHtml(name)}"
           loading="lazy"
           onerror="if(this.src!=='${googleFavicon}' && '${googleFavicon}'){this.src='${googleFavicon}'}else{this.style.display='none';if(this.nextElementSibling){this.nextElementSibling.style.display='inline-flex'}}">
      <div class="company-avatar-fallback ${className}" style="display:none">${escapeHtml(initial)}</div>
    </div>
  `;
}

/* ============================================
   LANDING HERO & SEARCH
   ============================================ */
function renderLandingHero() {
  return `
    <section class="hero-section">
      <div class="hero-badge">
        <span>✨ Powered by Gemini AI & Real-time Web Scraping</span>
      </div>
      <h1 class="hero-title">Continuous AI Competitor Intelligence</h1>
      <p class="hero-subtitle">
        Automatically track competitor products, pricing updates, hiring surges, and marketing strategies. Turn raw web signals into actionable business insights.
      </p>

      <div class="search-wrapper">
        <form class="hero-search-box" onsubmit="App.handleHeroSearch(event)" autocomplete="off">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9499b0" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input type="text" id="hero-search-input" class="hero-search-input" placeholder="Type company name (e.g. OpenAI, Notion, Stripe, Zoxima)..." oninput="App.handleTypeaheadInput(event)" required>
          <button type="submit" class="btn btn-primary" id="hero-search-btn">
            Analyze Company
          </button>
        </form>
        <div class="autocomplete-dropdown" id="autocomplete-dropdown"></div>
      </div>

      <div class="trending-chips">
        <span>Popular searches:</span>
        <button class="chip-btn" onclick="App.quickSearch('OpenAI')">OpenAI</button>
        <button class="chip-btn" onclick="App.quickSearch('Salesforce')">Salesforce</button>
        <button class="chip-btn" onclick="App.quickSearch('HubSpot')">HubSpot</button>
        <button class="chip-btn" onclick="App.quickSearch('Stripe')">Stripe</button>
        <button class="chip-btn" onclick="App.quickSearch('Zoxima')">Zoxima</button>
        <button class="chip-btn" onclick="App.quickSearch('Anthropic')">Anthropic</button>
      </div>

      <!-- Feature highlights -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-top:3.5rem;text-align:left">
        ${[
          ['🔍', 'Web Intelligence', 'Scrapes pricing, blog, careers & product pages automatically'],
          ['🤖', 'Gemini AI Analysis', 'Classifies changes by type, impact score & business reasoning'],
          ['🔔', 'Smart Alerts', 'Notifies on high-impact events above your threshold'],
          ['📊', 'Trend Dashboard', 'Visualises competitor activity and strategic signals'],
        ].map(([icon, title, desc]) => `
          <div style="background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:1.25rem">
            <div style="font-size:1.5rem;margin-bottom:0.5rem">${icon}</div>
            <div style="font-weight:700;margin-bottom:0.25rem">${title}</div>
            <div style="font-size:0.8125rem;color:var(--text-secondary)">${desc}</div>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}

/* ============================================
   SEARCH RESULTS & DISCOVERY MODAL
   ============================================ */
function renderDiscoveryModal(companies, query = '') {
  const list = Array.isArray(companies) ? companies : (companies.company ? [companies.company, ...(companies.recommended_competitors || [])] : []);

  return `
    <div class="modal-overlay" onclick="if(event.target === this) App.closeModal()">
      <div class="modal" style="max-width:760px">
        <div class="modal-header" style="padding:1.25rem 1.5rem;border-bottom:1px solid var(--border)">
          <div>
            <h2 style="font-size:1.25rem;margin-bottom:0.25rem">Relevant Companies (${list.length})</h2>
            <p style="color:var(--text-secondary);font-size:0.8125rem;margin:0">Search results for &ldquo;${escapeHtml(query)}&rdquo;. Choose to analyze or add to monitored competitors.</p>
          </div>
          <button class="modal-close" onclick="App.closeModal()" aria-label="Close modal">✕</button>
        </div>

        <div class="search-results-list">
          ${list.map((c, idx) => `
            <div class="search-result-item" id="search-result-item-${idx}">
              <div class="search-result-info">
                <div style="display:flex;align-items:center;gap:0.625rem;margin-bottom:0.35rem">
                  ${renderCompanyLogo(c.logo || c.clearbit_logo, c.name, c.domain || c.website, 'search-result-logo')}
                  <h3 style="margin:0;font-size:1rem;font-weight:700">${escapeHtml(c.name)}</h3>
                  <span class="industry-tag">${escapeHtml(c.industry || 'Technology')}</span>
                </div>
                <p style="color:var(--text-secondary);font-size:0.8125rem;margin:0 0 0.5rem 0;line-height:1.4">${escapeHtml(c.description || 'Public company and market competitor.')}</p>
                <div style="display:flex;gap:0.35rem;align-items:center;flex-wrap:wrap">
                  ${(c.sources || []).map(s => `<span class="badge badge-${escapeHtml(s.source_type || 'company_website')}">${escapeHtml((s.source_type || 'website').replace('_', ' '))}</span>`).join('')}
                  ${c.website ? `<a href="${escapeHtml(c.website)}" target="_blank" style="font-size:0.75rem;color:var(--accent-blue);margin-left:0.35rem">Visit site ↗</a>` : ''}
                </div>
              </div>
              <div class="search-result-actions">
                <button class="btn btn-secondary btn-sm" id="btn-analyze-${idx}" onclick="App.analyzeCompanyFromSearch(${idx}, this)" title="Analyze intelligence and preview details">
                  ⚡ Analyze
                </button>
                <button class="btn btn-primary btn-sm" id="btn-add-${idx}" onclick="App.addSingleCompetitorFromSearch(${idx}, this)" title="Add this company to monitored competitors">
                  ➕ Add to Competitors
                </button>
              </div>
            </div>
          `).join('')}
        </div>

        <div class="modal-footer" style="padding:1rem 1.5rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:0.8125rem;color:var(--text-muted)">Companies are only tracked when you click &ldquo;Add to Competitors&rdquo;.</span>
          <button class="btn btn-secondary btn-sm" onclick="App.closeModal()">Close</button>
        </div>
      </div>
    </div>
  `;
}

/* ============================================
   COMPETITOR CARD (DASHBOARD OVERVIEW)
   ============================================ */
function renderCompetitorCard(c) {
  const alertBadge = c.unsent_alert_count > 0
    ? `<span class="badge" style="background:rgba(239,68,68,0.2);color:var(--accent-red)">🔔 ${c.unsent_alert_count} Alert${c.unsent_alert_count > 1 ? 's' : ''}</span>`
    : '';

  const impactColor = c.avg_impact_score >= 70 ? 'var(--accent-red)'
    : c.avg_impact_score >= 40 ? 'var(--accent-amber)'
    : 'var(--text-secondary)';

  return `
    <div class="card card-clickable" onclick="App.navigate('competitor', '${c.competitor_id}')">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem">
        <div style="display:flex;align-items:center;gap:0.625rem">
          ${renderCompanyLogo(c.logo, c.name, c.website, 'search-result-logo')}
          <div>
            <h3 style="margin-bottom:0.15rem">${escapeHtml(c.name)}</h3>
            <span class="industry-tag">${escapeHtml(c.industry || 'Technology')}</span>
          </div>
        </div>
        ${alertBadge}
      </div>
      <div style="display:flex;gap:1.5rem;margin:1rem 0">
        <div>
          <span style="font-size:1.375rem;font-weight:800">${c.source_count}</span>
          <span style="display:block;font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em">Sources</span>
        </div>
        <div>
          <span style="font-size:1.375rem;font-weight:800">${c.insight_count}</span>
          <span style="display:block;font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em">Insights</span>
        </div>
        <div>
          <span style="font-size:1.375rem;font-weight:800;color:${impactColor}">${c.avg_impact_score !== null ? c.avg_impact_score : '—'}</span>
          <span style="display:block;font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em">Avg Impact</span>
        </div>
      </div>
      <div style="border-top:1px solid var(--border);padding-top:0.75rem;font-size:0.8125rem;color:var(--text-muted);display:flex;justify-content:space-between">
        <span>Last checked: ${timeAgo(c.last_scraped_at)}</span>
        <span style="color:var(--accent-blue)">View Detail →</span>
      </div>
    </div>
  `;
}

/* ============================================
   INSIGHT CARD (with evidence link)
   ============================================ */
function renderInsightCard(insight, showCompetitor = false) {
  const level = getImpactLevel(insight.impact_score);
  const emoji = getCategoryEmoji(insight.category);
  const category = insight.category || 'other';
  const sourceUrl = insight.source_url || null;
  const competitorName = insight.competitor_name || '';

  return `
    <div class="insight-card">
      <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.625rem;flex-wrap:wrap">
        <span class="impact-score impact-${level}">${insight.impact_score}</span>
        <span class="badge badge-${category}">${emoji} ${escapeHtml(category.replace('_', ' '))}</span>
        ${showCompetitor && competitorName ? `<span style="font-size:0.75rem;color:var(--text-secondary);font-weight:600">${escapeHtml(competitorName)}</span>` : ''}
        <span style="margin-left:auto;font-size:0.75rem;color:var(--text-muted)">
          Confidence: ${Math.round(insight.confidence_score * 100)}%
          ${insight.created_at ? `· ${timeAgo(insight.created_at)}` : ''}
        </span>
      </div>
      <p style="font-weight:600;margin-bottom:0.25rem;color:var(--text-primary)">${escapeHtml(insight.summary)}</p>
      <p style="color:var(--text-secondary);font-size:0.875rem;line-height:1.5">${escapeHtml(insight.reasoning)}</p>
      ${sourceUrl ? `
        <div style="margin-top:0.625rem">
          <a href="${escapeHtml(sourceUrl)}" target="_blank" class="insight-evidence-link" title="${escapeHtml(sourceUrl)}">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            Evidence: ${escapeHtml(shortenUrl(sourceUrl))}
          </a>
        </div>
      ` : ''}
    </div>
  `;
}

/* ============================================
   SOURCE TYPE METADATA DEFINITIONS
   ============================================ */
const SOURCE_TYPE_METADATA = {
  company_website: {
    label: 'Company Website / Homepage',
    purpose: 'Monitors headline positioning, core value propositions, product messaging shifts, leadership announcements, and navigation changes.',
    dataCaptured: 'Hero copy, value propositions, buyer personas, leadership bios, website navigation hierarchy, and primary call-to-actions.'
  },
  pricing_page: {
    label: 'Pricing & Plans Page',
    purpose: 'Continuously tracks price shifts, feature gating boundaries, new tier additions, seat quotas, discounts, and enterprise contact gates.',
    dataCaptured: 'Plan names (Free, Starter, Pro, Enterprise), monthly/annual price numbers, feature allowance tables, seat limits, and add-on pricing.'
  },
  career_page: {
    label: 'Careers & Hiring Portal',
    purpose: 'Detects strategic department scaling, new R&D/AI investments, regional go-to-market hiring surges, and executive appointments.',
    dataCaptured: 'Open position titles, department allocations (AI/ML, Engineering, Sales, Product), office locations, and required tech keywords.'
  },
  blog: {
    label: 'Product Blog & Changelog',
    purpose: 'Captures major product release notes, technical feature deep-dives, strategic partnership announcements, and case studies.',
    dataCaptured: 'Article headlines, release changelogs, new capability rollouts, partner quotes, integration announcements, and customer metrics.'
  },
  news_feed: {
    label: 'Market News & Press Releases',
    purpose: 'Monitors third-party industry coverage, venture funding rounds, strategic acquisitions, executive transitions, and corporate PR.',
    dataCaptured: 'Press release articles, funding round amounts, investor names, company valuations, and executive quotes.'
  },
  linkedin: {
    label: 'LinkedIn Organization Feed',
    purpose: 'Tracks corporate headcount growth velocity, key executive hires or departures, and public company updates.',
    dataCaptured: 'Employee headcount metrics, executive appointments, company milestones, and public announcements.'
  },
  g2: {
    label: 'G2 Customer Reviews',
    purpose: 'Monitors real customer sentiment shifts, software reliability feedback, feature praise, and competitor comparison ratings.',
    dataCaptured: 'Aggregated star ratings, verified reviewer feedback, pros/cons breakdown, and competitor comparison ratings.'
  },
  trustpilot: {
    label: 'Trustpilot Sentiment Stream',
    purpose: 'Tracks post-sale customer satisfaction, billing and support experience issues, and user sentiment trends over time.',
    dataCaptured: 'TrustScore ratings, recent review sentiments, common customer pain points, and response rates.'
  }
};

/* ============================================
   NICHE COMPETITOR DATABASE & SUGGESTIONS
   ============================================ */
const NICHE_COMPETITOR_DATABASE = {
  'CRM & Enterprise Sales Automation': [
    {
      key: 'salesforce',
      name: 'Salesforce',
      website: 'https://salesforce.com',
      industry: 'CRM & Enterprise Sales Automation',
      overlapLevel: 'high',
      overlapText: 'Direct Market Leader',
      description: 'Global cloud CRM giant offering Sales Cloud, Service Cloud, Marketing Cloud, and Agentforce AI workflows.',
      pricingModel: 'Per-user tiered ($25 - $500/user/month) + custom enterprise agreements',
      keyStrengths: 'Deep enterprise ecosystem, AppExchange marketplace, vast brand trust, global partner network',
      whySuggested: 'Direct benchmark for enterprise sales pipelines, custom CRM object architectures, and AI agent integrations.'
    },
    {
      key: 'hubspot',
      name: 'HubSpot',
      website: 'https://hubspot.com',
      industry: 'CRM & Enterprise Sales Automation',
      overlapLevel: 'high',
      overlapText: 'Inbound & Sales Rival',
      description: 'Unified customer platform connecting Marketing, Sales, Customer Service, Content, and Operations.',
      pricingModel: 'Freemium to Enterprise ($50 - $1,500+/month seat/tier packages)',
      keyStrengths: 'Fast self-serve onboarding, inbound marketing leadership, intuitive modern UI, unified data model',
      whySuggested: 'Primary competitor for sales pipeline velocity, automated email sequencing, and mid-market expansion.'
    },
    {
      key: 'zoho',
      name: 'Zoho CRM',
      website: 'https://zoho.com/crm',
      industry: 'CRM & Enterprise Sales Automation',
      overlapLevel: 'high',
      overlapText: 'Value & Suite Rival',
      description: 'Feature-rich CRM with Zia AI predictive analytics, canvas design builder, and native business app ecosystem.',
      pricingModel: 'Aggressive value pricing ($14 - $52/user/month)',
      keyStrengths: 'High value-to-cost ratio, 50+ integrated enterprise apps, customizable workflow automations',
      whySuggested: 'Aggressive competitor targeting cost-conscious SMBs and enterprises evaluating high-cost CRM alternatives.'
    },
    {
      key: 'pipedrive',
      name: 'Pipedrive',
      website: 'https://pipedrive.com',
      industry: 'CRM & Enterprise Sales Automation',
      overlapLevel: 'med',
      overlapText: 'Pipeline Focused',
      description: 'Visual sales CRM and pipeline management software built specifically to boost sales rep closing velocity.',
      pricingModel: 'Per-seat tiers ($14 - $99/user/month)',
      keyStrengths: 'Visual Kanban deal tracking, AI sales assistant, email sync and automation',
      whySuggested: 'Popular competitor for agile sales organizations looking for clean deal execution without heavyweight CRM configuration.'
    }
  ],
  'AI & Machine Learning': [
    {
      key: 'openai',
      name: 'OpenAI',
      website: 'https://openai.com',
      industry: 'AI & Machine Learning',
      overlapLevel: 'high',
      overlapText: 'Frontier AI Leader',
      description: 'Creator of GPT-4o, o1 reasoning models, ChatGPT Enterprise, and developer API ecosystems.',
      pricingModel: 'Usage token pricing ($/1M tokens) + ChatGPT Enterprise ($20 - $60/user/mo)',
      keyStrengths: 'Unmatched brand mindshare, developer ecosystem, frontier reasoning capability',
      whySuggested: 'Benchmark for AI API pricing drops, reasoning token economics, and enterprise assistant feature rollouts.'
    },
    {
      key: 'anthropic',
      name: 'Anthropic',
      website: 'https://anthropic.com',
      industry: 'AI & Machine Learning',
      overlapLevel: 'high',
      overlapText: 'Safety & Frontier Model Rival',
      description: 'AI safety laboratory behind Claude 3.5 Sonnet and Haiku, leading in coding, reasoning, and context window size.',
      pricingModel: 'Usage API pricing + Claude Team/Enterprise subscriptions',
      keyStrengths: 'Top-tier code generation, 200k+ context window, constitutional AI steerability',
      whySuggested: 'Leading competitor in enterprise LLM adoption, coding benchmarks, and safety-focused deployments.'
    },
    {
      key: 'mistral',
      name: 'Mistral AI',
      website: 'https://mistral.ai',
      industry: 'AI & Machine Learning',
      overlapLevel: 'med',
      overlapText: 'Open & Efficient Models',
      description: 'European AI company delivering high-efficiency open weights (Mistral 7B, Mixtral 8x22B) and frontier commercial models.',
      pricingModel: 'Cost-effective token API + self-hosted open license',
      keyStrengths: 'Open-weights flexibility, low inference cost, on-premise private deployment',
      whySuggested: 'Key competitor for on-premise and privacy-sensitive enterprise AI deployments with aggressive token pricing.'
    },
    {
      key: 'perplexity',
      name: 'Perplexity AI',
      website: 'https://perplexity.ai',
      industry: 'AI & Machine Learning',
      overlapLevel: 'med',
      overlapText: 'AI Search & Knowledge',
      description: 'Conversational search engine delivering real-time citation-backed answers and enterprise research spaces.',
      pricingModel: 'Enterprise Pro ($40/user/month)',
      keyStrengths: 'Real-time citation search, multi-model switcher, fast research synthesis',
      whySuggested: 'Fast-growing challenger in workplace research automation and real-time citation-backed intelligence.'
    }
  ],
  'FinTech & Payments': [
    {
      key: 'stripe',
      name: 'Stripe',
      website: 'https://stripe.com',
      industry: 'FinTech & Payments',
      overlapLevel: 'high',
      overlapText: 'Payments & Billing Leader',
      description: 'Financial infrastructure platform for internet commerce, subscription billing, issuing, and fraud prevention.',
      pricingModel: '2.9% + 30c per transaction + tiered billing add-ons',
      keyStrengths: 'Unmatched developer APIs, global coverage, comprehensive ecosystem',
      whySuggested: 'Benchmark for payment processing rates, revenue recovery tools, and developer documentation.'
    },
    {
      key: 'adyen',
      name: 'Adyen',
      website: 'https://adyen.com',
      industry: 'FinTech & Payments',
      overlapLevel: 'high',
      overlapText: 'Global Omnichannel Rival',
      description: 'End-to-end payments and financial services platform for large global enterprises and cross-border commerce.',
      pricingModel: 'Interchange++ transparent pricing + processing fee',
      keyStrengths: 'Direct bank acquiring, single global platform, fraud mitigation',
      whySuggested: 'Key competitor for high-volume enterprise payment processing and international merchant accounts.'
    }
  ],
  'Cloud, DevOps & Cybersecurity': [
    {
      key: 'datadog',
      name: 'Datadog',
      website: 'https://datadoghq.com',
      industry: 'Cloud, DevOps & Cybersecurity',
      overlapLevel: 'high',
      overlapText: 'Observability Leader',
      description: 'Cloud-scale observability and security platform monitoring servers, databases, tools, and cloud services.',
      pricingModel: 'Usage-based per-host / per-GB ingest model ($15 - $23/host/mo)',
      keyStrengths: '600+ integrations, unified metrics/logs/traces, rapid product expansion',
      whySuggested: 'Direct competitor in cloud monitoring, telemetry retention pricing, and DevOps platform expansion.'
    },
    {
      key: 'crowdstrike',
      name: 'CrowdStrike',
      website: 'https://crowdstrike.com',
      industry: 'Cloud, DevOps & Cybersecurity',
      overlapLevel: 'high',
      overlapText: 'Endpoint Security Leader',
      description: 'Falcon platform delivering AI-powered endpoint detection, cloud security posture, and threat intelligence.',
      pricingModel: 'Annual subscription per endpoint/module ($59 - $180/endpoint/yr)',
      keyStrengths: 'Single agent architecture, threat graph intelligence',
      whySuggested: 'Primary benchmark for enterprise security licensing tiers and threat detection marketing.'
    }
  ]
};

/* ============================================
   MY COMPANY PROFILE & ADMIN WORKSPACE VIEW
   ============================================ */
function renderMyCompanyView(adminProfile, competitors = [], nicheRecs = []) {
  const compNames = new Set(competitors.map(c => c.name.toLowerCase()));

  return `
    <!-- TOP HEADER -->
    <div class="section-header" style="margin-bottom:1.5rem">
      <div>
        <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
          <h1 style="margin:0">🏢 My Company Workspace</h1>
          <span class="admin-badge">👑 Administrator Profile</span>
        </div>
        <p style="color:var(--text-secondary);margin-top:0.25rem">
          Manage your company profile, benchmark against market rivals, and discover AI-suggested competitors tailored to your niche.
        </p>
      </div>
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap">
        <button class="btn btn-secondary btn-sm" onclick="App.showEditCompanyModal()">✏️ Edit Company Profile</button>
        <button class="btn btn-primary btn-sm" onclick="App.navigate('compare')">⚡ Benchmark vs. Competitors</button>
      </div>
    </div>

    <!-- ADMIN COMPANY PROFILE CARD -->
    <div class="admin-profile-card">
      <div class="admin-profile-header">
        <div>
          <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
            <h2 style="margin:0;font-size:1.375rem">${escapeHtml(adminProfile.name)}</h2>
            <span class="industry-tag">${escapeHtml(adminProfile.industry)}</span>
            <span class="badge badge-primary" style="font-size:0.75rem">Our Benchmark Company</span>
          </div>
          <p style="color:var(--text-secondary);margin-top:0.35rem;font-size:0.9375rem">${escapeHtml(adminProfile.tagline || '')}</p>
        </div>
        <div>
          <a href="${escapeHtml(adminProfile.website)}" target="_blank" class="source-url-link" style="font-size:0.875rem">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            ${escapeHtml(adminProfile.website)}
          </a>
        </div>
      </div>

      <p style="color:var(--text-primary);font-size:0.9375rem;line-height:1.6;margin-bottom:1.25rem">
        ${escapeHtml(adminProfile.description)}
      </p>

      <div class="admin-profile-grid">
        <div class="admin-field-group">
          <span class="admin-field-label">💰 Pricing Strategy & Model</span>
          <p class="admin-field-value">${escapeHtml(adminProfile.pricingModel)}</p>
        </div>
        <div class="admin-field-group">
          <span class="admin-field-label">🎯 Target Customer Segment</span>
          <p class="admin-field-value">${escapeHtml(adminProfile.targetAudience)}</p>
        </div>
        <div class="admin-field-group">
          <span class="admin-field-label">🌟 Core Strategic Strengths</span>
          <p class="admin-field-value">${escapeHtml(adminProfile.keyStrengths)}</p>
        </div>
        <div class="admin-field-group">
          <span class="admin-field-label">👤 Admin Workspace Owner</span>
          <p class="admin-field-value">${escapeHtml(adminProfile.adminName)} <span style="color:var(--text-muted);font-size:0.75rem">(${escapeHtml(adminProfile.adminEmail)})</span></p>
        </div>
      </div>
    </div>

    <!-- NICHE COMPETITOR RECOMMENDATIONS -->
    <div class="niche-rec-section">
      <div class="section-header" style="margin-bottom:1rem">
        <div>
          <h2 style="margin:0;font-size:1.25rem">💡 AI Niche Competitor Recommendations</h2>
          <p style="color:var(--text-secondary);font-size:0.875rem;margin-top:0.25rem">
            Smart competitors suggested specifically for your niche: <strong>${escapeHtml(adminProfile.industry)}</strong>. Add them to monitor changes and compare head-to-head.
          </p>
        </div>
      </div>

      <div class="niche-rec-grid">
        ${nicheRecs.map(rec => {
          const isTracked = compNames.has(rec.name.toLowerCase());
          return `
            <div class="niche-rec-card">
              <div>
                <div class="niche-rec-header">
                  <div>
                    <h3 style="margin:0 0 0.25rem 0;font-size:1.125rem">${escapeHtml(rec.name)}</h3>
                    <a href="${escapeHtml(rec.website)}" target="_blank" style="font-size:0.75rem;color:var(--accent-blue)">${escapeHtml(rec.website)} ↗</a>
                  </div>
                  <span class="niche-overlap-pill ${rec.overlapLevel === 'high' ? 'niche-overlap-high' : 'niche-overlap-med'}">
                    ${escapeHtml(rec.overlapText)}
                  </span>
                </div>
                <p class="niche-rec-desc">${escapeHtml(rec.description)}</p>
                
                <div style="background:var(--bg-surface-2);border-radius:var(--radius-sm);padding:0.625rem 0.75rem;margin-bottom:0.75rem;border:1px solid var(--border)">
                  <span style="display:block;font-size:0.6875rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;margin-bottom:0.2rem">🎯 Why Suggested for You</span>
                  <span style="font-size:0.8125rem;color:var(--text-secondary);line-height:1.4">${escapeHtml(rec.whySuggested)}</span>
                </div>
              </div>

              <div class="niche-rec-actions">
                <button class="btn ${isTracked ? 'btn-secondary' : 'btn-primary'} btn-sm" id="btn-niche-${rec.key}" onclick="App.addCompetitorFromNiche('${rec.key}', this)" style="flex:1" ${isTracked ? 'disabled' : ''}>
                  ${isTracked ? '✓ In Directory' : '➕ Add as Competitor'}
                </button>
                <button class="btn btn-secondary btn-sm" onclick="App.compareWithAdminCompany('${rec.name}')" title="Compare side-by-side with ${escapeHtml(adminProfile.name)}">
                  ⚡ Compare
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>

    <!-- MONITORED COMPETITORS LIST QUICK-ACTION -->
    <div class="section-header" style="margin-bottom:1rem;margin-top:2rem">
      <div>
        <h2 style="margin:0;font-size:1.25rem">📊 Monitored Competitors in Platform (${competitors.length})</h2>
        <p style="color:var(--text-secondary);font-size:0.875rem;margin-top:0.25rem">
          Click &ldquo;Compare&rdquo; on any competitor to run a side-by-side benchmark against ${escapeHtml(adminProfile.name)}.
        </p>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="App.navigate('dashboard')">View All in Directory →</button>
    </div>

    ${competitors.length > 0 ? `
      <div class="card-grid">
        ${competitors.map(c => `
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">
              <h3 style="margin:0">${escapeHtml(c.name)}</h3>
              <span class="industry-tag">${escapeHtml(c.industry || 'Tech')}</span>
            </div>
            <p style="font-size:0.8125rem;color:var(--text-secondary);margin:0.5rem 0 1rem 0">
              ${c.source_count} sources monitored · ${c.insight_count} AI insights
            </p>
            <div style="display:flex;gap:0.5rem">
              <button class="btn btn-primary btn-sm w-full" onclick="App.compareWithAdminCompany('${c.name.replace(/'/g, "\\'")}')">
                ⚡ Compare with My Company
              </button>
              <button class="btn btn-secondary btn-sm" onclick="App.navigate('competitor', '${c.competitor_id}')">
                Detail →
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    ` : `<p style="color:var(--text-muted)">No competitors tracked yet. Add recommended competitors above or search any company.</p>`}
  `;
}

/* ============================================
   EDIT COMPANY PROFILE MODAL
   ============================================ */
function renderEditCompanyModal(profile) {
  const industries = [
    'CRM & Enterprise Sales Automation',
    'AI & Machine Learning',
    'FinTech & Payments',
    'Cloud, DevOps & Cybersecurity',
    'HRTech & Workforce Management',
    'E-Commerce Infrastructure & MarTech',
    'B2B SaaS & Team Productivity'
  ];

  return `
    <div class="modal-backdrop" onclick="App.closeModal()">
      <div class="modal-box" onclick="event.stopPropagation()" style="max-width:680px">
        <div class="modal-header">
          <div>
            <h3 style="margin:0;font-size:1.25rem">✏️ Edit Admin Company Profile</h3>
            <p style="font-size:0.8125rem;color:var(--text-secondary);margin-top:0.25rem">
              Update your company details to refine smart niche competitor suggestions and comparison benchmarks.
            </p>
          </div>
          <button class="modal-close" onclick="App.closeModal()">✕</button>
        </div>

        <form onsubmit="App.handleSaveCompanyProfile(event)" style="padding:1.5rem">
          <div class="form-grid-2col" style="margin-bottom:1rem">
            <div>
              <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">COMPANY NAME</label>
              <input type="text" name="name" class="input-styled" required value="${escapeHtml(profile.name || '')}">
            </div>
            <div>
              <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">WEBSITE URL</label>
              <input type="url" name="website" class="input-styled" required value="${escapeHtml(profile.website || '')}">
            </div>
          </div>

          <div style="margin-bottom:1rem">
            <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">INDUSTRY / NICHE</label>
            <select name="industry" class="input-styled" style="width:100%">
              ${industries.map(ind => `<option value="${escapeHtml(ind)}" ${profile.industry === ind ? 'selected' : ''}>${escapeHtml(ind)}</option>`).join('')}
            </select>
          </div>

          <div style="margin-bottom:1rem">
            <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">TAGLINE / ONE-LINE POSITIONING</label>
            <input type="text" name="tagline" class="input-styled" value="${escapeHtml(profile.tagline || '')}">
          </div>

          <div style="margin-bottom:1rem">
            <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">COMPANY DESCRIPTION & VALUE PROPOSITION</label>
            <textarea name="description" rows="3" class="input-styled" style="width:100%;resize:vertical">${escapeHtml(profile.description || '')}</textarea>
          </div>

          <div class="form-grid-2col" style="margin-bottom:1rem">
            <div>
              <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">PRICING MODEL & TIERS</label>
              <input type="text" name="pricingModel" class="input-styled" value="${escapeHtml(profile.pricingModel || '')}">
            </div>
            <div>
              <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">TARGET CUSTOMER AUDIENCE</label>
              <input type="text" name="targetAudience" class="input-styled" value="${escapeHtml(profile.targetAudience || '')}">
            </div>
          </div>

          <div style="margin-bottom:1.5rem">
            <label style="display:block;font-size:0.75rem;font-weight:700;color:var(--text-muted);margin-bottom:0.35rem">KEY COMPETITIVE STRENGTHS</label>
            <input type="text" name="keyStrengths" class="input-styled" value="${escapeHtml(profile.keyStrengths || '')}">
          </div>

          <div style="display:flex;justify-content:flex-end;gap:0.75rem;border-top:1px solid var(--border);padding-top:1rem">
            <button type="button" class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Profile & Refresh Niche Suggestions</button>
          </div>
        </form>
      </div>
    </div>
  `;
}

/* ============================================
   HEAD-TO-HEAD BENCHMARK & COMPARISON VIEW
   ============================================ */
function renderCompareView(competitors, adminProfile, initialCompetitorIndex = 0) {
  if (!competitors || competitors.length === 0) {
    return `
      <div style="text-align:center;padding:4rem 1rem">
        <h2>🏢 Company Comparison & Benchmark</h2>
        <p style="color:var(--text-secondary);margin-top:0.5rem">No competitors tracked yet. Add companies from your niche to run side-by-side benchmark comparisons.</p>
        <button class="btn btn-primary mt-2" onclick="App.navigate('my-company')">View My Company & Suggestions</button>
      </div>
    `;
  }

  const compJson = JSON.stringify(competitors).replace(/</g, '\\u003c').replace(/>/g, '\\u003e');
  const adminJson = JSON.stringify(adminProfile).replace(/</g, '\\u003c').replace(/>/g, '\\u003e');
  const activeIdx = Math.min(Math.max(0, initialCompetitorIndex), competitors.length - 1);
  const activeComp = competitors[activeIdx];

  return `
    <div class="section-header" style="margin-bottom:1.5rem">
      <div>
        <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
          <h1 style="margin:0">Side-by-Side Competitor Comparison</h1>
          <span class="benchmark-badge">Head-to-Head Benchmark</span>
        </div>
        <p style="color:var(--text-secondary);margin-top:0.25rem">
          Benchmark your company (<strong>${escapeHtml(adminProfile.name)}</strong>) against tracked competitors across positioning, pricing models, feature velocity, and market activity.
        </p>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="App.navigate('my-company')">🏢 My Company Workspace</button>
    </div>

    <!-- SCRIPT FOR DYNAMIC HEAD-TO-HEAD SWITCHING -->
    <script>
      window._compareAdmin = ${adminJson};
      window._compareCompetitors = ${compJson};

      function _onBenchmarkCompetitorChange() {
        const idx = parseInt(document.getElementById('benchmark-comp-select').value);
        const comp = window._compareCompetitors[idx];
        if (!comp) return;

        // Update headers & links
        document.getElementById('comp-header-name').textContent = comp.name;
        document.getElementById('comp-header-industry').textContent = comp.industry || 'Technology';
        document.getElementById('comp-detail-btn').onclick = function() {
          App.navigate('competitor', comp.competitor_id);
        };

        // Update metric boxes
        document.getElementById('comp-metric-sources').textContent = comp.source_count + ' Endpoints';
        document.getElementById('comp-metric-insights').textContent = comp.insight_count + ' Signals';
        document.getElementById('comp-metric-impact').textContent = (comp.avg_impact_score || '—') + (comp.avg_impact_score ? '/100' : '');
        document.getElementById('comp-metric-alerts').textContent = comp.unsent_alert_count + ' Active';

        // Update matrix table cells
        document.getElementById('matrix-comp-name').textContent = comp.name;
        document.getElementById('matrix-comp-sources').textContent = comp.source_count + ' Monitored Endpoints';
        document.getElementById('matrix-comp-insights').textContent = comp.insight_count + ' AI Classified Signals';
        document.getElementById('matrix-comp-impact').textContent = (comp.avg_impact_score || '—') + (comp.avg_impact_score ? '/100' : '');

        // Update Win/Loss threat
        document.getElementById('threat-comp-name').textContent = comp.name;
      }
    </script>

    <!-- BENCHMARK CONTAINER -->
    <div class="compare-container">
      <!-- LEFT COLUMN: OUR COMPANY BENCHMARK -->
      <div class="compare-column is-benchmark">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem">
          <span class="benchmark-badge">OUR COMPANY (BENCHMARK)</span>
          <span style="font-size:0.75rem;color:var(--accent-blue);font-weight:600">Admin Baseline</span>
        </div>
        <h3 style="margin:0 0 0.25rem 0;font-size:1.375rem">${escapeHtml(adminProfile.name)}</h3>
        <span class="industry-tag">${escapeHtml(adminProfile.industry)}</span>
        
        <div class="compare-metric-box">
          <span style="font-size:0.75rem;color:var(--text-muted);font-weight:700">CORE POSITIONING</span>
          <p style="font-size:0.9375rem;font-weight:600;margin-top:0.25rem">${escapeHtml(adminProfile.tagline || adminProfile.description.substring(0, 100) + '...')}</p>
        </div>
        <div class="compare-metric-box">
          <span style="font-size:0.75rem;color:var(--text-muted);font-weight:700">PRICING STRUCTURE</span>
          <p style="font-size:0.9375rem;font-weight:600;margin-top:0.25rem">${escapeHtml(adminProfile.pricingModel)}</p>
        </div>
        <div class="compare-metric-box">
          <span style="font-size:0.75rem;color:var(--text-muted);font-weight:700">KEY STRATEGIC STRENGTHS</span>
          <p style="font-size:0.9375rem;font-weight:600;margin-top:0.25rem;color:var(--accent-green)">${escapeHtml(adminProfile.keyStrengths)}</p>
        </div>
        <button class="btn btn-secondary btn-sm w-full mt-2" onclick="App.navigate('my-company')">Edit My Company Details →</button>
      </div>

      <!-- RIGHT COLUMN: SELECTED COMPETITOR -->
      <div class="compare-column">
        <div style="margin-bottom:0.75rem">
          <label style="display:block;font-size:0.6875rem;font-weight:700;color:var(--text-muted);letter-spacing:0.05em;text-transform:uppercase;margin-bottom:0.35rem">SELECT COMPETITOR TO COMPARE</label>
          <select class="compare-select" id="benchmark-comp-select" onchange="_onBenchmarkCompetitorChange()">
            ${competitors.map((c, i) => `<option value="${i}" ${i === activeIdx ? 'selected' : ''}>${escapeHtml(c.name)} (${c.source_count} sources)</option>`).join('')}
          </select>
        </div>

        <h3 id="comp-header-name" style="margin:0 0 0.25rem 0;font-size:1.375rem">${escapeHtml(activeComp.name)}</h3>
        <span id="comp-header-industry" class="industry-tag">${escapeHtml(activeComp.industry || 'Technology')}</span>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-top:1rem">
          <div class="compare-metric-box" style="margin-top:0">
            <span style="font-size:0.6875rem;color:var(--text-muted);font-weight:700">MONITORED SOURCES</span>
            <p id="comp-metric-sources" style="font-size:1.25rem;font-weight:800;margin-top:0.25rem;color:var(--accent-blue)">${activeComp.source_count} Endpoints</p>
          </div>
          <div class="compare-metric-box" style="margin-top:0">
            <span style="font-size:0.6875rem;color:var(--text-muted);font-weight:700">AI INSIGHTS</span>
            <p id="comp-metric-insights" style="font-size:1.25rem;font-weight:800;margin-top:0.25rem;color:var(--accent-purple)">${activeComp.insight_count} Signals</p>
          </div>
          <div class="compare-metric-box" style="margin-top:0">
            <span style="font-size:0.6875rem;color:var(--text-muted);font-weight:700">AVG IMPACT</span>
            <p id="comp-metric-impact" style="font-size:1.25rem;font-weight:800;margin-top:0.25rem;color:var(--accent-amber)">${activeComp.avg_impact_score ? activeComp.avg_impact_score + '/100' : '—'}</p>
          </div>
          <div class="compare-metric-box" style="margin-top:0">
            <span style="font-size:0.6875rem;color:var(--text-muted);font-weight:700">ACTIVE ALERTS</span>
            <p id="comp-metric-alerts" style="font-size:1.25rem;font-weight:800;margin-top:0.25rem;color:${activeComp.unsent_alert_count > 0 ? 'var(--accent-red)' : 'var(--text-secondary)'}">${activeComp.unsent_alert_count} Active</p>
          </div>
        </div>

        <button class="btn btn-primary btn-sm w-full mt-2" id="comp-detail-btn" onclick="App.navigate('competitor','${activeComp.competitor_id}')">
          View Competitor Intelligence Details →
        </button>
      </div>
    </div>

    <!-- DETAILED COMPARATIVE MATRIX TABLE -->
    <div style="margin-top:2.5rem">
      <h3 style="margin-bottom:0.75rem">📋 Strategic Comparison Matrix</h3>
      <table class="matrix-table">
        <thead>
          <tr>
            <th class="matrix-label-col">DIMENSION</th>
            <th class="matrix-benchmark-col">🏢 ${escapeHtml(adminProfile.name)} (Our Company)</th>
            <th class="matrix-competitor-col" id="matrix-comp-name">🎯 ${escapeHtml(activeComp.name)}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="matrix-label-col">Industry Niche</td>
            <td class="matrix-benchmark-col"><strong>${escapeHtml(adminProfile.industry)}</strong></td>
            <td class="matrix-competitor-col">${escapeHtml(activeComp.industry || adminProfile.industry)}</td>
          </tr>
          <tr>
            <td class="matrix-label-col">Value Proposition</td>
            <td class="matrix-benchmark-col">${escapeHtml(adminProfile.tagline || adminProfile.description)}</td>
            <td class="matrix-competitor-col">Public website messaging & detected feature focus</td>
          </tr>
          <tr>
            <td class="matrix-label-col">Pricing Architecture</td>
            <td class="matrix-benchmark-col">${escapeHtml(adminProfile.pricingModel)}</td>
            <td class="matrix-competitor-col">Monitored pricing page & tier limits</td>
          </tr>
          <tr>
            <td class="matrix-label-col">Target Customer</td>
            <td class="matrix-benchmark-col">${escapeHtml(adminProfile.targetAudience)}</td>
            <td class="matrix-competitor-col">Market segment & enterprise tiers</td>
          </tr>
          <tr>
            <td class="matrix-label-col">Monitored Data Sources</td>
            <td class="matrix-benchmark-col">Primary Business System</td>
            <td class="matrix-competitor-col" id="matrix-comp-sources">${activeComp.source_count} Monitored Endpoints</td>
          </tr>
          <tr>
            <td class="matrix-label-col">AI Signal Velocity</td>
            <td class="matrix-benchmark-col">Admin Baseline</td>
            <td class="matrix-competitor-col" id="matrix-comp-insights">${activeComp.insight_count} AI Classified Signals</td>
          </tr>
          <tr>
            <td class="matrix-label-col">Strategic Impact Threat</td>
            <td class="matrix-benchmark-col">Benchmark Baseline</td>
            <td class="matrix-competitor-col" id="matrix-comp-impact">${activeComp.avg_impact_score ? activeComp.avg_impact_score + '/100' : '—'}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- AI ADVANTAGE & THREAT BREAKDOWN -->
    <div class="win-loss-grid">
      <div class="win-card">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
          <span style="font-size:1.25rem">🟢</span>
          <h4 style="margin:0;color:var(--accent-green)">Where Our Company (${escapeHtml(adminProfile.name)}) Wins</h4>
        </div>
        <p style="font-size:0.875rem;color:var(--text-secondary);line-height:1.5;margin-bottom:0.75rem">
          ${escapeHtml(adminProfile.keyStrengths)}
        </p>
        <ul style="font-size:0.8125rem;color:var(--text-primary);padding-left:1.25rem;margin:0;line-height:1.6">
          <li>Customizable implementation architectures tailored to client workflows.</li>
          <li>Direct access to dedicated solution architects and rapid feature delivery.</li>
          <li>Transparent, flexible pricing without unexpected add-on gating penalties.</li>
        </ul>
      </div>

      <div class="threat-card">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
          <span style="font-size:1.25rem">⚠️</span>
          <h4 style="margin:0;color:var(--accent-red)">Competitor Signals & Threat Radar (<span id="threat-comp-name">${escapeHtml(activeComp.name)}</span>)</h4>
        </div>
        <p style="font-size:0.875rem;color:var(--text-secondary);line-height:1.5;margin-bottom:0.75rem">
          Rival Comp continuously monitors this competitor across pricing updates, career hiring surges, and product releases.
        </p>
        <ul style="font-size:0.8125rem;color:var(--text-primary);padding-left:1.25rem;margin:0;line-height:1.6">
          <li>Watch for enterprise packaging shifts and feature bundling changes.</li>
          <li>Monitor technical hiring posts to anticipate upcoming AI/product roadmaps.</li>
          <li>Track changelog releases to maintain competitive feature parity.</li>
        </ul>
      </div>
    </div>
  `;
}
function renderCompetitorDetail(detail) {
  const c = detail.competitor;
  const sources = detail.sources || [];
  const insights = detail.recent_insights || [];
  const alerts = detail.recent_alerts || [];

  // Metrics computation
  const impactScores = insights.map(i => i.impact_score || 0);
  const maxImpact = impactScores.length > 0 ? Math.max(...impactScores) : '—';
  const avgImpact = impactScores.length > 0 ? Math.round(impactScores.reduce((a, b) => a + b, 0) / impactScores.length) : '—';
  const isTracking = c.is_active !== false;

  // Category insights
  const pricingInsight = insights.find(i => i.category === 'pricing');
  const productInsight = insights.find(i => i.category === 'product');
  const hiringInsight = insights.find(i => i.category === 'hiring');
  const marketInsight = insights.find(i => i.category === 'marketing' || i.category === 'market');

  return `
    <button class="btn btn-secondary btn-sm mb-2" onclick="App.navigate('dashboard')">← Back to Dashboard</button>

    <!-- HEADER WITH ACTIONS -->
    <div class="competitor-detail-header">
      <div>
        <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
          <h1 style="margin:0">${escapeHtml(c.name)}</h1>
          <span class="industry-tag">${escapeHtml(c.industry || 'Technology')}</span>
          <span class="badge ${isTracking ? 'badge-primary' : 'badge-secondary'}" style="font-size:0.75rem">
            ${isTracking ? '🟢 Tracking Active' : '⏸️ Tracking Paused'}
          </span>
        </div>
        <p style="color:var(--text-secondary);margin-top:0.5rem;max-width:650px;font-size:0.9375rem;line-height:1.5">
          ${escapeHtml(c.description || 'Continuous competitive intelligence, public endpoint tracking, and AI-powered change detection.')}
        </p>
      </div>

      <div style="display:flex;gap:0.625rem;flex-wrap:wrap;align-items:center">
        <button class="btn btn-primary btn-sm" id="btn-add-comp-${c.id}" onclick="App.confirmAddAsCompetitor('${c.id}', '${escapeHtml(c.name)}')" title="Save/confirm this company in your competitor tracking directory">
          ➕ Add this as Competition
        </button>
        <button class="btn ${isTracking ? 'btn-secondary' : 'btn-primary'} btn-sm" id="btn-track-comp-${c.id}" onclick="App.toggleCompetitorTracking('${c.id}')" title="Toggle active continuous tracking for this company">
          ${isTracking ? '📡 Track this Company (Active)' : '▶️ Resume Tracking'}
        </button>
        <button class="btn btn-success btn-sm" id="scrape-all-btn" onclick="App.scrapeAllSources('${c.id}')" title="Run live scrape across all monitored web endpoints">
          ⚡ Scrape All Sources
        </button>
        <button class="btn btn-danger btn-sm" onclick="App.deleteCompetitor('${c.id}')" title="Remove competitor">
          Delete
        </button>
      </div>
    </div>

    <!-- AI EXECUTIVE ANALYSIS SUMMARY CARD -->
    <div class="analysis-summary-card">
      <div class="analysis-summary-header">
        <div style="display:flex;align-items:center;gap:0.625rem">
          <span class="analysis-ai-badge">🤖 AI Intelligence Analysis</span>
          <h3 style="margin:0;font-size:1.125rem">Executive Strategic Breakdown: ${escapeHtml(c.name)}</h3>
        </div>
        <span style="font-size:0.8125rem;color:var(--text-muted)">Last updated: ${timeAgo(c.last_scraped_at || c.updated_at)}</span>
      </div>

      <div class="analysis-overview-text">
        ${insights.length > 0 ? `
          Rival Comp AI is actively monitoring <strong>${escapeHtml(c.name)}</strong> across <strong>${sources.length} public endpoints</strong>. 
          A total of <strong>${insights.length} strategic signal${insights.length > 1 ? 's have' : ' has'} been classified</strong>, with peak impact score of <strong>${maxImpact}/100</strong> and an average impact rating of <strong>${avgImpact}/100</strong>. 
          The analysis below synthesizes recent changes across pricing models, product feature velocity, and hiring patterns.
        ` : `
          Rival Comp AI is currently configured to monitor <strong>${escapeHtml(c.name)}</strong> across <strong>${sources.length} public data sources</strong>. 
          The platform continuously tracks pricing tables, product feature releases, career hiring surges, and market press announcements. Click <strong>&ldquo;⚡ Scrape All Sources&rdquo;</strong> above to execute an on-demand analysis and synthesize real-time competitive intelligence.
        `}
      </div>

      <!-- KPI METRICS GRID -->
      <div class="analysis-kpi-grid">
        <div class="analysis-kpi-item">
          <span class="analysis-kpi-label">Monitored Sources</span>
          <span class="analysis-kpi-value" style="color:var(--accent-blue)">${sources.length} Endpoints</span>
        </div>
        <div class="analysis-kpi-item">
          <span class="analysis-kpi-label">AI Insights Generated</span>
          <span class="analysis-kpi-value" style="color:var(--accent-purple)">${insights.length} Signals</span>
        </div>
        <div class="analysis-kpi-item">
          <span class="analysis-kpi-label">Peak Impact Score</span>
          <span class="analysis-kpi-value" style="color:${typeof maxImpact === 'number' && maxImpact >= 70 ? 'var(--accent-red)' : 'var(--accent-amber)'}">${maxImpact !== '—' ? maxImpact + '/100' : '—'}</span>
        </div>
        <div class="analysis-kpi-item">
          <span class="analysis-kpi-label">Active Alerts</span>
          <span class="analysis-kpi-value" style="color:${alerts.length > 0 ? 'var(--accent-red)' : 'var(--text-secondary)'}">${alerts.length} Triggered</span>
        </div>
      </div>

      <!-- STRATEGIC PILLARS BREAKDOWN -->
      <div class="analysis-highlights-grid">
        <div class="highlight-box">
          <div class="highlight-box-title">💰 Pricing & Packaging</div>
          <p class="highlight-box-desc">
            ${pricingInsight ? escapeHtml(pricingInsight.summary) : 'Actively monitoring tier pricing, seat quotas, feature gating, and discount incentives.'}
          </p>
        </div>
        <div class="highlight-box">
          <div class="highlight-box-title">🚀 Product & Capabilities</div>
          <p class="highlight-box-desc">
            ${productInsight ? escapeHtml(productInsight.summary) : 'Tracking product changelogs, feature rollouts, platform updates, and integration roadmaps.'}
          </p>
        </div>
        <div class="highlight-box">
          <div class="highlight-box-title">👥 Hiring & Expansion</div>
          <p class="highlight-box-desc">
            ${hiringInsight ? escapeHtml(hiringInsight.summary) : 'Analyzing open engineering, AI/ML, and sales roles to predict product and regional scaling.'}
          </p>
        </div>
        <div class="highlight-box">
          <div class="highlight-box-title">📢 Market & PR Strategy</div>
          <p class="highlight-box-desc">
            ${marketInsight ? escapeHtml(marketInsight.summary) : 'Scanning third-party news, venture funding announcements, and corporate PR releases.'}
          </p>
        </div>
      </div>
    </div>

    <!-- DETAILED SOURCES LIST (NOT CARDS) -->
    <div class="section-header" style="margin-bottom:1rem">
      <div>
        <h3 style="margin:0">Monitored Web Sources (${sources.length})</h3>
        <p style="color:var(--text-secondary);font-size:0.875rem;margin-top:0.25rem">
          Comprehensive breakdown of public endpoints tracked for ${escapeHtml(c.name)}, their operational purpose, and extracted data points.
        </p>
      </div>
    </div>

    ${sources.length > 0 ? `
      <div class="sources-detailed-list">
        ${sources.map(s => {
          const meta = SOURCE_TYPE_METADATA[s.source_type] || {
            label: (s.source_type || 'web_source').replace(/_/g, ' '),
            purpose: 'Monitors content changes and updates on this public endpoint.',
            dataCaptured: 'Raw HTML structure, readable text content, headline tags, and link relationships.'
          };
          const isHealthy = Boolean(s.last_scraped);

          return `
            <div class="source-list-row">
              <div class="source-row-header">
                <div>
                  <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                    <span class="badge badge-${escapeHtml(s.source_type || 'company_website')}">${escapeHtml(meta.label)}</span>
                    <span class="source-status-pill ${isHealthy ? 'status-healthy' : 'status-pending'}">
                      ${isHealthy ? '● Scraped & Active' : '○ Pending First Scrape'}
                    </span>
                    <span style="font-size:0.75rem;color:var(--text-muted)">Interval: Every ${s.scrape_frequency >= 1440 ? Math.floor(s.scrape_frequency/1440)+'d' : (s.scrape_frequency || 60)+'m'}</span>
                  </div>
                  <a href="${escapeHtml(s.url)}" target="_blank" class="source-url-link" title="${escapeHtml(s.url)}">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                    ${escapeHtml(s.url)}
                  </a>
                </div>
                <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
                  <span style="font-size:0.75rem;color:var(--text-muted)">Last scraped: ${timeAgo(s.last_scraped)}</span>
                  <button class="btn btn-primary btn-sm" id="scrape-btn-${s.id}" onclick="App.scrapeSource('${s.id}')">
                    ⚡ Scrape Source Now
                  </button>
                </div>
              </div>

              <div class="source-details-grid">
                <div class="source-detail-box">
                  <span class="source-detail-tag">🎯 What this source is doing here</span>
                  <p class="source-detail-text">${escapeHtml(meta.purpose)}</p>
                </div>
                <div class="source-detail-box">
                  <span class="source-detail-tag">📊 What data is coming from here</span>
                  <p class="source-detail-text">${escapeHtml(meta.dataCaptured)}</p>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    ` : `<p style="color:var(--text-muted);margin-bottom:2rem">No sources configured for this competitor yet.</p>`}

    <!-- ALERTS -->
    ${alerts.length > 0 ? `
      <div class="section-header" style="margin-bottom:0.75rem">
        <h3>🔔 Triggered Intelligence Alerts (${alerts.length})</h3>
      </div>
      <div class="card mb-2" style="padding:0">
        ${alerts.map(a => `
          <div class="alert-feed-item">
            <div class="alert-impact-pill impact-${getImpactLevel(a.impact_score)}">${a.impact_score}</div>
            <div style="flex:1;min-width:0">
              <p style="font-weight:600;margin-bottom:0.125rem;color:var(--text-primary)">${escapeHtml(a.message)}</p>
              <span style="font-size:0.75rem;color:var(--text-muted)">${timeAgo(a.created_at)}${a.sent_at ? ' · ✓ Delivered' : ' · Pending delivery'}</span>
            </div>
          </div>
        `).join('')}
      </div>
    ` : ''}

    <!-- AI INSIGHTS -->
    <div class="section-header" style="margin-bottom:0.75rem">
      <h3>🤖 AI Classified Insights (${insights.length})</h3>
    </div>
    ${insights.length > 0
      ? insights.map(i => renderInsightCard(i, false)).join('')
      : `<p style="color:var(--text-muted)">No AI insights generated yet. Click "⚡ Scrape All Sources" above to trigger live intelligence synthesis.</p>`
    }
  `;
}

/* ============================================
   GLOBAL ALERTS FEED PAGE
   ============================================ */
function renderAlertsPage(alerts) {
  if (!alerts || alerts.length === 0) {
    return `
      <div style="text-align:center;padding:4rem 1rem">
        <div style="font-size:3rem;margin-bottom:1rem">🔔</div>
        <h2>No Alerts Yet</h2>
        <p style="color:var(--text-secondary);margin-top:0.5rem">High-impact competitive events will appear here once companies are monitored and scraped.</p>
        <button class="btn btn-primary mt-2" onclick="App.navigate('home')">Search & Add Company</button>
      </div>
    `;
  }

  return `
    <div class="section-header" style="margin-bottom:1.5rem">
      <div>
        <h1>🔔 Intelligence Alerts</h1>
        <p style="color:var(--text-secondary)">High-impact competitive events sorted by impact score.</p>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="App.navigate('home')">+ Add Company</button>
    </div>

    <div class="card" style="padding:0;margin-bottom:1.5rem">
      ${alerts.map(a => `
        <div class="alert-feed-item">
          <div class="alert-dot"></div>
          <div class="alert-impact-pill impact-${getImpactLevel(a.impact_score)}">${a.impact_score}</div>
          <div style="flex:1;min-width:0">
            <p style="font-weight:600;margin-bottom:0.125rem;color:var(--text-primary);white-space:normal">${escapeHtml(a.message)}</p>
            <span style="font-size:0.75rem;color:var(--text-muted)">
              ${timeAgo(a.created_at)}
              ${a.sent_at ? ' · ✓ Delivered' : ' · <span style="color:var(--accent-amber)">Pending</span>'}
            </span>
          </div>
          ${!a.sent_at ? `
            <button class="btn btn-sm btn-secondary" onclick="App.markAlertSent('${a.id}', this)" style="flex-shrink:0">
              Mark Sent
            </button>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;
}



/* ============================================
   ANALYTICS VIEW (Real Data)
   ============================================ */
function renderAnalyticsView(analytics, competitors) {
  const {
    total_insights = 0,
    total_changes = 0,
    total_alerts = 0,
    avg_impact_score = null,
    category_breakdown = [],
    top_insights = [],
    competitor_activity = [],
  } = analytics || {};

  const maxActivity = Math.max(...competitor_activity.map(c => c.insight_count), 1);

  const categoryColors = {
    pricing: 'var(--accent-amber)', hiring: 'var(--accent-green)',
    product: 'var(--accent-blue)', partnership: 'var(--accent-purple)',
    marketing: 'var(--accent-pink)', news: 'var(--accent-teal)',
    market_activity: 'var(--accent-amber)', other: 'var(--text-secondary)',
  };

  return `
    <div style="margin-bottom:2rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem">
      <div>
        <h1>Intelligence Analytics & Trends</h1>
        <p style="color:var(--text-secondary)">Real-time aggregated signals across all monitored competitors.</p>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="App.navigate('report')">🖨️ Export Report</button>
    </div>

    <!-- KPI Cards -->
    <div class="analytics-grid">
      <div class="analytics-stat-card">
        <div class="analytics-stat-value">${total_insights}</div>
        <div class="analytics-stat-label">Total AI Insights</div>
      </div>
      <div class="analytics-stat-card">
        <div class="analytics-stat-value">${total_changes}</div>
        <div class="analytics-stat-label">Changes Detected</div>
      </div>
      <div class="analytics-stat-card">
        <div class="analytics-stat-value">${total_alerts}</div>
        <div class="analytics-stat-label">Alerts Generated</div>
      </div>
      <div class="analytics-stat-card">
        <div class="analytics-stat-value" style="color:var(--accent-blue)">${avg_impact_score !== null ? avg_impact_score : '—'}</div>
        <div class="analytics-stat-label">Avg Impact Score</div>
      </div>
    </div>

    <!-- Competitor Activity Bar Chart -->
    ${competitor_activity.length > 0 ? `
      <div class="card mb-2">
        <h3 style="margin-bottom:0.5rem">Competitor Activity — Insights per Company</h3>
        <p style="font-size:0.8125rem;color:var(--text-muted);margin-bottom:1rem">Total AI-classified insights by competitor:</p>
        <div class="chart-bar-container">
          ${competitor_activity.map(c => `
            <div class="chart-bar-item">
              <div class="chart-bar" style="height:${Math.max(4, Math.round((c.insight_count / maxActivity) * 100))}%" title="${escapeHtml(c.name)}: ${c.insight_count} insights"></div>
              <span class="chart-label">${escapeHtml(c.name.length > 8 ? c.name.slice(0, 7) + '…' : c.name)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    ` : `
      <div class="card mb-2">
        <h3>Competitor Activity</h3>
        <p style="color:var(--text-muted);margin-top:0.5rem">No data yet. Scrape sources to generate insights.</p>
      </div>
    `}

    <!-- Category Breakdown -->
    ${category_breakdown.length > 0 ? `
      <div class="card mb-2">
        <h3 style="margin-bottom:0.75rem">Insight Category Breakdown</h3>
        <div class="category-pills-row">
          ${category_breakdown.sort((a, b) => b.count - a.count).map(cat => `
            <div class="category-pill" style="border-color:${categoryColors[cat.category] || 'var(--border)'}20;background:${categoryColors[cat.category] || 'var(--text-secondary)'}15">
              <span>${getCategoryEmoji(cat.category)}</span>
              <span style="color:${categoryColors[cat.category] || 'var(--text-secondary)'}">
                ${escapeHtml(cat.category.replace('_', ' '))}
              </span>
              <strong style="color:var(--text-primary)">${cat.count}</strong>
            </div>
          `).join('')}
        </div>
      </div>
    ` : ''}

    <!-- Top Insights by Impact -->
    ${top_insights.length > 0 ? `
      <div style="margin-bottom:1rem">
        <h3>🏆 Top Insights by Impact Score</h3>
        <p style="font-size:0.8125rem;color:var(--text-muted);margin-bottom:1rem">Highest-impact strategic signals detected:</p>
        ${top_insights.map(i => renderInsightCard(i, true)).join('')}
      </div>
    ` : ''}
  `;
}

/* ============================================
   EXECUTIVE BRIEF PRINT REPORT
   ============================================ */
function renderExecutiveReport(competitors) {
  const dateStr = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  return `
    <div class="report-paper">
      <div class="report-header">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <h1 class="report-title">Rival Comp Executive Intelligence Brief</h1>
          <span style="font-size:0.875rem;color:#64748b">${dateStr}</span>
        </div>
        <p style="color:#475569;margin-top:0.25rem">Automated Competitive Analysis & Market Shift Report</p>
      </div>

      <div class="report-section">
        <h3>1. Executive Summary</h3>
        <p style="line-height:1.6;color:#334155">
          This intelligence brief synthesizes public web signals across <strong>${competitors.length} tracked competitor(s)</strong>.
          Monitoring covers live pricing pages, corporate blogs, career portals, and product announcements.
          All change detections are verified against SHA-256 content hashes and classified by Gemini AI.
        </p>
      </div>

      <div class="report-section">
        <h3>2. Tracked Competitor Status</h3>
        <table style="width:100%;border-collapse:collapse;margin-top:0.5rem">
          <thead>
            <tr style="background:#f1f5f9;color:#334155;font-size:0.8125rem">
              <th style="padding:0.5rem;text-align:left">Company</th>
              <th style="padding:0.5rem;text-align:left">Industry</th>
              <th style="padding:0.5rem;text-align:center">Sources</th>
              <th style="padding:0.5rem;text-align:center">Insights</th>
              <th style="padding:0.5rem;text-align:center">Avg Impact</th>
              <th style="padding:0.5rem;text-align:center">Pending Alerts</th>
            </tr>
          </thead>
          <tbody>
            ${competitors.map(c => `
              <tr style="border-bottom:1px solid #e2e8f0;color:#1e293b;font-size:0.875rem">
                <td style="padding:0.5rem;font-weight:600">${escapeHtml(c.name)}</td>
                <td style="padding:0.5rem">${escapeHtml(c.industry || 'Tech')}</td>
                <td style="padding:0.5rem;text-align:center">${c.source_count}</td>
                <td style="padding:0.5rem;text-align:center">${c.insight_count}</td>
                <td style="padding:0.5rem;text-align:center;font-weight:700;color:#2563eb">${c.avg_impact_score || 'N/A'}</td>
                <td style="padding:0.5rem;text-align:center;color:${c.unsent_alert_count > 0 ? '#dc2626' : '#64748b'};font-weight:${c.unsent_alert_count > 0 ? '700' : '400'}">${c.unsent_alert_count}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div style="margin-top:3rem;text-align:center;display:flex;gap:0.75rem;justify-content:center">
        <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save as PDF</button>
        <button class="btn btn-secondary" onclick="App.navigate('dashboard')">← Back to Dashboard</button>
      </div>
    </div>
  `;
}

/* ============================================
   PRICING PLANS
   ============================================ */
function renderPricingView() {
  return `
    <div style="text-align:center;max-width:700px;margin:0 auto 3rem">
      <h1>Simple, Transparent Pricing</h1>
      <p style="color:var(--text-secondary)">Scale your competitive intelligence as your team grows.</p>
    </div>

    <div class="pricing-grid">
      <div class="pricing-card">
        <h3>Starter</h3>
        <p style="color:var(--text-muted);font-size:0.875rem">For individual analysts</p>
        <div class="pricing-price">$0 <span style="font-size:1rem;color:var(--text-muted)">/ mo</span></div>
        <ul style="list-style:none;text-align:left;margin:1.5rem 0;color:var(--text-secondary);font-size:0.875rem">
          <li style="margin-bottom:0.5rem">✓ Track up to 3 Competitors</li>
          <li style="margin-bottom:0.5rem">✓ Daily Scrape Frequency</li>
          <li style="margin-bottom:0.5rem">✓ Basic Change Diffs</li>
          <li style="margin-bottom:0.5rem">✓ Standard Gemini AI Analysis</li>
        </ul>
        <button class="btn btn-secondary w-full" onclick="App.navigate('home')">Current Plan</button>
      </div>

      <div class="pricing-card popular">
        <span class="hero-badge" style="position:absolute;top:-14px;left:50%;transform:translateX(-50%)">MOST POPULAR</span>
        <h3>Pro Intelligence</h3>
        <p style="color:var(--text-muted);font-size:0.875rem">For growing product & marketing teams</p>
        <div class="pricing-price">$49 <span style="font-size:1rem;color:var(--text-muted)">/ mo</span></div>
        <ul style="list-style:none;text-align:left;margin:1.5rem 0;color:var(--text-secondary);font-size:0.875rem">
          <li style="margin-bottom:0.5rem">✓ Unlimited Competitors</li>
          <li style="margin-bottom:0.5rem">✓ Hourly Scrape Frequency</li>
          <li style="margin-bottom:0.5rem">✓ Real-time Slack & Email Alerts</li>
          <li style="margin-bottom:0.5rem">✓ Gemini 2.5 Flash Deep Reasoning</li>
          <li style="margin-bottom:0.5rem">✓ Executive PDF Brief Exports</li>
        </ul>
        <button class="btn btn-primary w-full" onclick="App.showLoginModal()">Upgrade to Pro</button>
      </div>
    </div>
  `;
}

/* ============================================
   LOGIN & SIGNUP MODAL
   ============================================ */
function renderLoginModal(defaultTab = 'login') {
  return `
    <div class="modal-overlay" onclick="if(event.target === this) App.closeModal()">
      <div class="modal" style="max-width:440px">
        <div class="modal-header" style="border-bottom:1px solid var(--border);padding:1rem 1.5rem">
          <div class="auth-tabs" id="auth-modal-tabs">
            <button type="button" class="auth-tab ${defaultTab === 'login' ? 'active' : ''}" id="auth-tab-login" onclick="App.switchAuthTab('login')">Log In</button>
            <button type="button" class="auth-tab ${defaultTab === 'signup' ? 'active' : ''}" id="auth-tab-signup" onclick="App.switchAuthTab('signup')">Sign Up</button>
          </div>
          <button class="modal-close" onclick="App.closeModal()" aria-label="Close modal">✕</button>
        </div>

        <!-- Login Pane -->
        <div id="auth-pane-login" style="padding:1.5rem;display:${defaultTab === 'login' ? 'block' : 'none'}">
          <div style="margin-bottom:1.25rem">
            <h3 style="margin-bottom:0.25rem;font-size:1.125rem">Welcome back</h3>
            <p style="font-size:0.8125rem;color:var(--text-secondary)">Access your competitive intelligence dashboard.</p>
          </div>
          <form onsubmit="event.preventDefault(); App.closeModal(); Components.showToast('Logged in successfully!', 'success');">
            <div style="margin-bottom:1rem">
              <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:0.35rem;font-weight:600">WORK EMAIL</label>
              <input type="email" style="background:var(--bg-surface-2);width:100%;padding:0.625rem 0.75rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.875rem;outline:none" required placeholder="name@company.com">
            </div>
            <div style="margin-bottom:1.25rem">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem">
                <label style="font-size:0.75rem;color:var(--text-muted);font-weight:600">PASSWORD</label>
                <a href="javascript:void(0)" onclick="Components.showToast('Password reset link sent to your email.', 'info')" style="font-size:0.75rem;color:var(--accent-blue)">Forgot?</a>
              </div>
              <input type="password" style="background:var(--bg-surface-2);width:100%;padding:0.625rem 0.75rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.875rem;outline:none" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn btn-primary w-full" style="padding:0.6875rem">Sign In to Dashboard</button>
            <div style="text-align:center;margin-top:1rem;font-size:0.8125rem;color:var(--text-secondary)">
              Don't have an account? <a href="javascript:void(0)" onclick="App.switchAuthTab('signup')" style="color:var(--accent-blue);font-weight:600">Sign Up</a>
            </div>
          </form>
        </div>

        <!-- Signup Pane -->
        <div id="auth-pane-signup" style="padding:1.5rem;display:${defaultTab === 'signup' ? 'block' : 'none'}">
          <div style="margin-bottom:1.25rem">
            <h3 style="margin-bottom:0.25rem;font-size:1.125rem">Create Admin Workspace</h3>
            <p style="font-size:0.8125rem;color:var(--text-secondary)">Set up your company profile to receive tailored competitor intelligence.</p>
          </div>
          <form onsubmit="App.handleSignupSubmit(event)">
            <div class="form-grid-2col" style="margin-bottom:0.75rem">
              <div>
                <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">FULL NAME</label>
                <input type="text" name="adminName" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none" required placeholder="Alex Morgan">
              </div>
              <div>
                <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">WORK EMAIL</label>
                <input type="email" name="adminEmail" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none" required placeholder="alex@company.com">
              </div>
            </div>
            <div class="form-grid-2col" style="margin-bottom:0.75rem">
              <div>
                <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">YOUR COMPANY NAME</label>
                <input type="text" name="companyName" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none" required placeholder="e.g. Zoxima Solutions">
              </div>
              <div>
                <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">COMPANY WEBSITE</label>
                <input type="url" name="companyWebsite" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none" required placeholder="https://example.com">
              </div>
            </div>
            <div style="margin-bottom:0.75rem">
              <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">INDUSTRY / NICHE</label>
              <select name="companyIndustry" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none">
                <option value="CRM & Enterprise Sales Automation">CRM & Enterprise Sales Automation</option>
                <option value="AI & Machine Learning">AI & Machine Learning</option>
                <option value="FinTech & Payments">FinTech & Payments</option>
                <option value="Cloud, DevOps & Cybersecurity">Cloud, DevOps & Cybersecurity</option>
                <option value="HRTech & Workforce Management">HRTech & Workforce Management</option>
                <option value="E-Commerce Infrastructure & MarTech">E-Commerce Infrastructure & MarTech</option>
                <option value="B2B SaaS & Team Productivity">B2B SaaS & Team Productivity</option>
              </select>
            </div>
            <div style="margin-bottom:1.125rem">
              <label style="display:block;font-size:0.6875rem;color:var(--text-muted);margin-bottom:0.25rem;font-weight:700">PASSWORD</label>
              <input type="password" name="password" style="background:var(--bg-surface-2);width:100%;padding:0.5rem 0.625rem;border-radius:var(--radius-sm);border:1px solid var(--border);color:var(--text-primary);font-size:0.8125rem;outline:none" required placeholder="Create strong password">
            </div>
            <button type="submit" class="btn btn-primary w-full" style="padding:0.6875rem">Create Admin Workspace</button>
            <div style="text-align:center;margin-top:1rem;font-size:0.8125rem;color:var(--text-secondary)">
              Already have an account? <a href="javascript:void(0)" onclick="App.switchAuthTab('login')" style="color:var(--accent-blue);font-weight:600">Log In</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;
}

/* ============================================
   TOAST
   ============================================ */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.classList.add('fade-out'), 3500);
  setTimeout(() => toast.remove(), 4000);
}

const Components = {
  NICHE_COMPETITOR_DATABASE,
  renderLandingHero,
  renderDiscoveryModal,
  renderCompetitorCard,
  renderCompetitorDetail,
  renderMyCompanyView,
  renderEditCompanyModal,
  renderInsightCard,
  renderAlertsPage,
  renderCompareView,
  renderAnalyticsView,
  renderExecutiveReport,
  renderPricingView,
  renderLoginModal,
  renderCompanyLogo,
  showToast,
  escapeHtml,
  timeAgo,
  _timeAgo: timeAgo,
};

window.Components = Components;
export default Components;
