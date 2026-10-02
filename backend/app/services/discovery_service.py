# app/services/discovery_service.py
"""
AI Web Discovery Service & Company Autocomplete Engine.
Provides instant typeahead search (<10ms), comprehensive global company directory,
robust domain extraction, multi-tier high-res logo resolution, and niche-aware competitor discovery.
"""

import json
import re
from functools import lru_cache
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# ============================================
# EXTENSIVE GLOBAL COMPANY & TECH DIRECTORY
# ============================================
_KNOWN_COMPANIES = [
    # CRM & Sales Automation
    {"name": "Zoxima Solutions", "domain": "zoxima.com", "industry": "CRM & Enterprise Sales Automation", "description": "Custom CRM implementation, AI sales workflow automation, and enterprise pipeline intelligence."},
    {"name": "Salesforce", "domain": "salesforce.com", "industry": "CRM & Enterprise Sales Automation", "description": "Global enterprise cloud CRM platform offering Sales Cloud, Service Cloud, and Agentforce AI."},
    {"name": "HubSpot", "domain": "hubspot.com", "industry": "CRM & Enterprise Sales Automation", "description": "Inbound marketing, sales pipeline automation, customer service, and CRM platform."},
    {"name": "Zoho", "domain": "zoho.com", "industry": "CRM & Enterprise Sales Automation", "description": "Comprehensive business software suite with omnichannel CRM, Zia AI, and 50+ integrated apps."},
    {"name": "Pipedrive", "domain": "pipedrive.com", "industry": "CRM & Enterprise Sales Automation", "description": "Visual sales pipeline CRM software built for deal tracking and revenue closing velocity."},
    {"name": "Freshworks", "domain": "freshworks.com", "industry": "CRM & Enterprise Sales Automation", "description": "Modern SaaS customer engagement and IT service management suite."},
    {"name": "ActiveCampaign", "domain": "activecampaign.com", "industry": "CRM & Enterprise Sales Automation", "description": "Customer experience automation platform combining email marketing and CRM."},

    # AI & Machine Learning
    {"name": "OpenAI", "domain": "openai.com", "industry": "AI & Machine Learning", "description": "AI research and deployment laboratory behind ChatGPT, GPT-4o, and o1 reasoning models."},
    {"name": "Anthropic", "domain": "anthropic.com", "industry": "AI & Machine Learning", "description": "AI safety and research laboratory behind Claude 3.5 Sonnet and Haiku foundation models."},
    {"name": "Mistral AI", "domain": "mistral.ai", "industry": "AI & Machine Learning", "description": "High-efficiency open-weights and commercial frontier language models."},
    {"name": "Cohere", "domain": "cohere.com", "industry": "AI & Machine Learning", "description": "Enterprise AI platform for search, retrieval-augmented generation (RAG), and language models."},
    {"name": "Perplexity AI", "domain": "perplexity.ai", "industry": "AI & Machine Learning", "description": "Conversational search and discovery engine delivering citation-backed real-time intelligence."},
    {"name": "Hugging Face", "domain": "huggingface.co", "industry": "AI & Machine Learning", "description": "The open-source AI community platform and model repository."},
    {"name": "Midjourney", "domain": "midjourney.com", "industry": "AI & Machine Learning", "description": "Independent research lab exploring new mediums of generative visual AI."},
    {"name": "Scale AI", "domain": "scale.com", "industry": "AI & Machine Learning", "description": "Data infrastructure and RLHF fine-tuning platform for foundation AI models."},

    # Big Tech & Cloud Platforms
    {"name": "Microsoft", "domain": "microsoft.com", "industry": "Cloud & Enterprise Software", "description": "Global technology leader providing Azure cloud, Microsoft 365, Copilot, and enterprise solutions."},
    {"name": "Google", "domain": "google.com", "industry": "Cloud & Internet Services", "description": "Global internet, search, Google Cloud Platform, and Gemini AI technology giant."},
    {"name": "Apple", "domain": "apple.com", "industry": "Consumer Electronics & Services", "description": "Global technology company designing smartphones, personal computers, and digital services."},
    {"name": "Amazon", "domain": "amazon.com", "industry": "Cloud & E-Commerce", "description": "World leader in e-commerce, cloud computing infrastructure (AWS), and digital streaming."},
    {"name": "Meta", "domain": "meta.com", "industry": "Social Media & AI", "description": "Social technology company connecting people through Facebook, Instagram, WhatsApp, and Llama AI."},
    {"name": "Tesla", "domain": "tesla.com", "industry": "Automotive & Energy", "description": "Electric vehicle manufacturing, clean energy generation, and autonomous AI systems."},

    # Cloud, DevOps & Cybersecurity
    {"name": "Datadog", "domain": "datadoghq.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "Observability and security platform monitoring cloud infrastructure, traces, and metrics."},
    {"name": "CrowdStrike", "domain": "crowdstrike.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "Falcon cloud-native endpoint protection, identity protection, and threat intelligence."},
    {"name": "Palo Alto Networks", "domain": "paloaltonetworks.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "Global cybersecurity leader delivering next-generation firewalls and Prisma cloud security."},
    {"name": "Snyk", "domain": "snyk.io", "industry": "Cloud, DevOps & Cybersecurity", "description": "Developer security platform finding and fixing vulnerabilities in code, dependencies, and containers."},
    {"name": "Cloudflare", "domain": "cloudflare.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "Global cloud network providing DDoS protection, CDN, DNS, and serverless computing."},
    {"name": "New Relic", "domain": "newrelic.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "All-in-one observability platform for full-stack telemetry and APM performance."},
    {"name": "Okta", "domain": "okta.com", "industry": "Cloud, DevOps & Cybersecurity", "description": "Identity and access management platform for workforce and customer authentication."},

    # FinTech & Payments
    {"name": "Stripe", "domain": "stripe.com", "industry": "FinTech & Payments", "description": "Financial infrastructure platform for internet commerce, payments, billing, and issuing."},
    {"name": "Adyen", "domain": "adyen.com", "industry": "FinTech & Payments", "description": "Global end-to-end payments and financial technology platform for enterprise merchants."},
    {"name": "Plaid", "domain": "plaid.com", "industry": "FinTech & Payments", "description": "Data network connecting consumer bank accounts to financial applications and fintech tools."},
    {"name": "Brex", "domain": "brex.com", "industry": "FinTech & Payments", "description": "AI-powered spend management, corporate cards, and banking for high-growth companies."},
    {"name": "Ramp", "domain": "ramp.com", "industry": "FinTech & Payments", "description": "Finance automation platform combining corporate cards, expense management, and bill pay."},
    {"name": "Razorpay", "domain": "razorpay.com", "industry": "FinTech & Payments", "description": "Leading payments gateway and neo-banking platform for digital businesses."},
    {"name": "Square", "domain": "squareup.com", "industry": "FinTech & Payments", "description": "Commerce and point-of-sale ecosystem for businesses of all sizes."},
    {"name": "PayPal", "domain": "paypal.com", "industry": "FinTech & Payments", "description": "Global digital payments platform enabling money transfers and merchant checkout."},

    # Developer Tools & Data
    {"name": "Snowflake", "domain": "snowflake.com", "industry": "Data & Developer Tools", "description": "Data Cloud platform for data warehousing, data lakes, and data science workloads."},
    {"name": "Databricks", "domain": "databricks.com", "industry": "Data & Developer Tools", "description": "Unified data analytics, Lakehouse architecture, and enterprise AI platform."},
    {"name": "MongoDB", "domain": "mongodb.com", "industry": "Data & Developer Tools", "description": "Developer data platform with flexible document database and Atlas cloud services."},
    {"name": "Supabase", "domain": "supabase.com", "industry": "Data & Developer Tools", "description": "Open-source Firebase alternative providing Postgres, Auth, Instant APIs, and Storage."},
    {"name": "Vercel", "domain": "vercel.com", "industry": "Data & Developer Tools", "description": "Frontend cloud platform for Next.js, web development, and serverless hosting."},
    {"name": "Postman", "domain": "postman.com", "industry": "Data & Developer Tools", "description": "API platform for building, testing, documenting, and collaborating on APIs."},
    {"name": "GitHub", "domain": "github.com", "industry": "Data & Developer Tools", "description": "AI-powered developer platform for version control, GitHub Actions, and Copilot."},
    {"name": "GitLab", "domain": "gitlab.com", "industry": "Data & Developer Tools", "description": "The One DevOps Platform for software innovation, CI/CD, and security."},

    # B2B SaaS, Productivity & Collaboration
    {"name": "Notion", "domain": "notion.so", "industry": "B2B SaaS & Productivity", "description": "Connected workspace for notes, wiki knowledge bases, docs, and AI project management."},
    {"name": "Figma", "domain": "figma.com", "industry": "B2B SaaS & Productivity", "description": "Collaborative cloud design and prototyping platform for product teams."},
    {"name": "Linear", "domain": "linear.app", "industry": "B2B SaaS & Productivity", "description": "Purpose-built project management and issue tracking tool for modern software teams."},
    {"name": "Asana", "domain": "asana.com", "industry": "B2B SaaS & Productivity", "description": "Work management and team coordination platform connecting company goals to daily tasks."},
    {"name": "Monday.com", "domain": "monday.com", "industry": "B2B SaaS & Productivity", "description": "Work OS platform enabling teams to build custom workflow management apps."},
    {"name": "ClickUp", "domain": "clickup.com", "industry": "B2B SaaS & Productivity", "description": "All-in-one productivity platform for tasks, docs, chat, goals, and automations."},
    {"name": "Slack", "domain": "slack.com", "industry": "B2B SaaS & Productivity", "description": "AI-powered messaging and productivity workspace connecting teams and apps."},
    {"name": "Atlassian", "domain": "atlassian.com", "industry": "B2B SaaS & Productivity", "description": "Software development and collaboration tools including Jira, Confluence, and Trello."},
    {"name": "Canva", "domain": "canva.com", "industry": "B2B SaaS & Productivity", "description": "Online visual communication and graphic design platform for presentations, social, and print."},

    # E-Commerce & Retail
    {"name": "Shopify", "domain": "shopify.com", "industry": "E-Commerce & Retail Tech", "description": "Global commerce platform powering millions of online storefronts and retail point-of-sale."},
    {"name": "BigCommerce", "domain": "bigcommerce.com", "industry": "E-Commerce & Retail Tech", "description": "Open SaaS e-commerce platform for fast-growing and enterprise brands."},
    {"name": "Klaviyo", "domain": "klaviyo.com", "industry": "E-Commerce & Retail Tech", "description": "Intelligent marketing automation platform for email, SMS, and customer data segmentation."},

    # HRTech & Workforce
    {"name": "Rippling", "domain": "rippling.com", "industry": "HRTech & Workforce", "description": "Workforce management platform unifying HR, IT, and Finance in a single system."},
    {"name": "Deel", "domain": "deel.com", "industry": "HRTech & Workforce", "description": "Global payroll, compliance, and hiring platform for international remote teams."},
    {"name": "Workday", "domain": "workday.com", "industry": "HRTech & Workforce", "description": "Enterprise cloud platform for human resources, financial management, and planning."},
    {"name": "Gusto", "domain": "gusto.com", "industry": "HRTech & Workforce", "description": "Modern online payroll, benefits, and HR platform for growing businesses."},
    {"name": "Greenhouse", "domain": "greenhouse.com", "industry": "HRTech & Workforce", "description": "Hiring and applicant tracking software designed to optimize recruiting pipelines."}
]


def extract_clean_domain(query_or_url: str) -> str:
    """
    Intelligently extracts and normalizes domain from any user query, URL, or company string.
    Examples:
    - 'https://zoxima.com/pricing' -> 'zoxima.com'
    - 'http://www.hubspot.com' -> 'hubspot.com'
    - 'zoxima solutions' -> 'zoxima.com'
    - 'salesforce inc' -> 'salesforce.com'
    - 'notion.so' -> 'notion.so'
    - 'linear.app' -> 'linear.app'
    """
    if not query_or_url:
        return ""
    
    text = query_or_url.strip().lower()
    
    # 1. If contains URL scheme or slashes
    if "://" in text or "/" in text:
        text = text.replace("https://", "").replace("http://", "").replace("www.", "")
        text = text.split("/")[0].split("?")[0].split(":")[0].strip()

    # 2. If it already looks like a domain with known TLD
    domain_match = re.search(r'([a-z0-9\-]+\.(?:com|org|net|io|ai|so|app|co|dev|tech|us|in|co\.uk|de|fr|ca|edu|gov))', text)
    if domain_match:
        return domain_match.group(1)

    # 3. Check known company map directly
    clean_name = re.sub(r'\b(solutions|technologies|technology|software|inc|corp|corporation|llc|ltd|limited|group|crm|platform|labs|ai)\b', '', text).strip()
    clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
    
    for item in _KNOWN_COMPANIES:
        item_clean = re.sub(r'[^a-z0-9]', '', item["name"].lower())
        if clean_name and (clean_name == item_clean or clean_name in item_clean or item_clean in clean_name):
            return item["domain"]

    # 4. Fallback: sanitize clean name and append .com
    sanitized = re.sub(r'[^a-z0-9\-]', '', clean_name if clean_name else text.replace(" ", ""))
    return f"{sanitized}.com" if sanitized else "example.com"


def get_logo_url(domain_or_url: str) -> str:
    """
    Generates guaranteed high-resolution favicon logo URL using Google S2 Favicon API.
    Works for any valid domain globally.
    """
    domain = extract_clean_domain(domain_or_url)
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"


def get_clearbit_logo_url(domain_or_url: str) -> str:
    """Returns Clearbit logo URL."""
    domain = extract_clean_domain(domain_or_url)
    return f"https://logo.clearbit.com/{domain}"


@lru_cache(maxsize=512)
def autocomplete_companies(query: str) -> List[Dict]:
    """
    Instant typeahead search handler (<10ms). Returns live company suggestions
    with guaranteed logos, clean domains, and industry tags.
    """
    if not query or len(query.strip()) == 0:
        return []

    q = query.strip().lower()
    matches = []
    seen_domains = set()

    # 1. Exact, prefix or substring match against known directory
    for item in _KNOWN_COMPANIES:
        name_lower = item["name"].lower()
        domain_lower = item["domain"].lower()
        industry_lower = item["industry"].lower()

        if q in name_lower or q in domain_lower or q in industry_lower:
            if item["domain"] not in seen_domains:
                seen_domains.add(item["domain"])
                matches.append({
                    "name": item["name"],
                    "domain": item["domain"],
                    "website": f"https://{item['domain']}",
                    "logo": get_logo_url(item["domain"]),
                    "clearbit_logo": get_clearbit_logo_url(item["domain"]),
                    "industry": item["industry"],
                    "description": item["description"]
                })

    # 2. Dynamic live fallback if query is not in known directory
    if len(matches) < 6 and len(q) >= 2:
        clean_domain = extract_clean_domain(query)
        if clean_domain not in seen_domains:
            brand_name = query.strip()
            # Clean up brand name if it was a URL
            if "://" in brand_name or "." in brand_name:
                brand_name = clean_domain.split(".")[0].capitalize()
            else:
                brand_name = " ".join([word.capitalize() for word in brand_name.split()])

            matches.append({
                "name": brand_name,
                "domain": clean_domain,
                "website": f"https://{clean_domain}",
                "logo": get_logo_url(clean_domain),
                "clearbit_logo": get_clearbit_logo_url(clean_domain),
                "industry": "Technology / Software",
                "description": f"Explore live signals and competitor intelligence for {brand_name}."
            })

    return matches[:6]


def _build_niche_fallback_competitors(industry: str, exclude_domain: str) -> List[Dict]:
    """Finds top relevant competitors from the directory matching the industry."""
    recs = []
    for item in _KNOWN_COMPANIES:
        if item["domain"] != exclude_domain:
            if industry.lower() in item["industry"].lower() or item["industry"].lower() in industry.lower():
                recs.append({
                    "name": item["name"],
                    "website": f"https://{item['domain']}",
                    "domain": item["domain"],
                    "logo": get_logo_url(item["domain"]),
                    "industry": item["industry"],
                    "description": item["description"],
                    "sources": [
                        {"source_type": "company_website", "url": f"https://{item['domain']}"},
                        {"source_type": "pricing_page", "url": f"https://{item['domain']}/pricing"}
                    ]
                })
        if len(recs) >= 4:
            break
            
    # Fallback to CRM / AI if no specific industry match
    if not recs:
        for item in _KNOWN_COMPANIES[:3]:
            if item["domain"] != exclude_domain:
                recs.append({
                    "name": item["name"],
                    "website": f"https://{item['domain']}",
                    "domain": item["domain"],
                    "logo": get_logo_url(item["domain"]),
                    "industry": item["industry"],
                    "description": item["description"],
                    "sources": [{"source_type": "company_website", "url": f"https://{item['domain']}"}]
                })
    return recs[:4]


_DISCOVERY_PROMPT = """You are an expert market intelligence and company research analyst.

User Company Query: "{query}"

Analyze this company and return ONLY a valid JSON object (no markdown fences, no explanatory text) with the following structure:
{{
  "company": {{
    "name": "Full Official Company Name",
    "website": "https://official-domain.com",
    "industry": "Industry Category (e.g. CRM & Enterprise Sales Automation, AI & Machine Learning, FinTech & Payments, Cloud & Cybersecurity, B2B SaaS, E-Commerce, HRTech)",
    "description": "2-3 sentence overview of what the company does and its core value proposition",
    "sources": [
      {{ "source_type": "company_website", "url": "https://official-domain.com" }},
      {{ "source_type": "pricing_page", "url": "https://official-domain.com/pricing" }},
      {{ "source_type": "blog", "url": "https://official-domain.com/blog" }},
      {{ "source_type": "career_page", "url": "https://official-domain.com/careers" }}
    ]
  }},
  "recommended_competitors": [
    {{
      "name": "Top Competitor 1 Name",
      "website": "https://competitor1-domain.com",
      "industry": "Industry Category",
      "description": "Brief overview of what Competitor 1 offers and key market overlap",
      "sources": [
        {{ "source_type": "company_website", "url": "https://competitor1-domain.com" }},
        {{ "source_type": "pricing_page", "url": "https://competitor1-domain.com/pricing" }}
      ]
    }},
    {{
      "name": "Top Competitor 2 Name",
      "website": "https://competitor2-domain.com",
      "industry": "Industry Category",
      "description": "Brief overview of what Competitor 2 offers",
      "sources": [
        {{ "source_type": "company_website", "url": "https://competitor2-domain.com" }}
      ]
    }},
    {{
      "name": "Top Competitor 3 Name",
      "website": "https://competitor3-domain.com",
      "industry": "Industry Category",
      "description": "Brief overview of what Competitor 3 offers",
      "sources": [
        {{ "source_type": "company_website", "url": "https://competitor3-domain.com" }}
      ]
    }}
  ]
}}
"""


@lru_cache(maxsize=256)
def discover_company_cached(query: str) -> str:
    """Cached discovery query execution with robust AI & directory fallbacks."""
    clean_q = query.strip()
    clean_domain = extract_clean_domain(clean_q)

    # 1. Check if company is in our known directory first
    for item in _KNOWN_COMPANIES:
        if (clean_q.lower() == item["name"].lower() or 
            clean_domain == item["domain"] or 
            clean_q.lower() == item["domain"].lower()):
            
            recs = _build_niche_fallback_competitors(item["industry"], item["domain"])
            return json.dumps({
                "company": {
                    "name": item["name"],
                    "website": f"https://{item['domain']}",
                    "domain": item["domain"],
                    "logo": get_logo_url(item["domain"]),
                    "clearbit_logo": get_clearbit_logo_url(item["domain"]),
                    "industry": item["industry"],
                    "description": item["description"],
                    "sources": [
                        {"source_type": "company_website", "url": f"https://{item['domain']}"},
                        {"source_type": "pricing_page", "url": f"https://{item['domain']}/pricing"},
                        {"source_type": "blog", "url": f"https://{item['domain']}/blog"},
                        {"source_type": "career_page", "url": f"https://{item['domain']}/careers"}
                    ]
                },
                "recommended_competitors": recs
            })

    # 2. If Gemini API key is available, execute live AI synthesis
    if settings.GEMINI_API_KEY:
        import google.generativeai as genai
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(_DISCOVERY_PROMPT.format(query=clean_q))
            text = response.text.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            # Validate JSON parse
            parsed = json.loads(text)
            if "company" in parsed and "name" in parsed["company"]:
                return json.dumps(parsed)
        except Exception as exc:
            logger.error("discovery_gemini_failed", extra={"error": str(exc), "query": clean_q})

    # 3. Dynamic smart fallback for any arbitrary company/website on the web
    brand_title = clean_q
    if "://" in brand_title or "." in brand_title:
        brand_title = clean_domain.split(".")[0].capitalize()
    else:
        brand_title = " ".join([w.capitalize() for w in brand_title.split()])

    # Guess industry based on keywords
    q_lower = clean_q.lower()
    if any(k in q_lower for k in ["crm", "sales", "pipeline", "lead", "deal"]):
        industry = "CRM & Enterprise Sales Automation"
    elif any(k in q_lower for k in ["ai", "gpt", "model", "llm", "neural", "bot"]):
        industry = "AI & Machine Learning"
    elif any(k in q_lower for k in ["pay", "bank", "card", "fintech", "bill", "money", "crypto"]):
        industry = "FinTech & Payments"
    elif any(k in q_lower for k in ["cloud", "monitor", "security", "devops", "trace", "guard"]):
        industry = "Cloud, DevOps & Cybersecurity"
    elif any(k in q_lower for k in ["shop", "store", "commerce", "cart", "retail"]):
        industry = "E-Commerce & Retail Tech"
    elif any(k in q_lower for k in ["hr", "hire", "recruit", "payroll", "people", "staff"]):
        industry = "HRTech & Workforce"
    else:
        industry = "B2B SaaS & Technology"

    recs = _build_niche_fallback_competitors(industry, clean_domain)

    return json.dumps({
        "company": {
            "name": brand_title,
            "website": f"https://{clean_domain}",
            "domain": clean_domain,
            "logo": get_logo_url(clean_domain),
            "clearbit_logo": get_clearbit_logo_url(clean_domain),
            "industry": industry,
            "description": f"{brand_title} provides software products, public online services, and platform capabilities in {industry}.",
            "sources": [
                {"source_type": "company_website", "url": f"https://{clean_domain}"},
                {"source_type": "pricing_page", "url": f"https://{clean_domain}/pricing"},
                {"source_type": "blog", "url": f"https://{clean_domain}/blog"},
                {"source_type": "career_page", "url": f"https://{clean_domain}/careers"}
            ]
        },
        "recommended_competitors": recs
    })


def discover_company(query: str) -> dict:
    """Public discovery accessor with multi-tier logo injection and URL sanitization."""
    raw_json = discover_company_cached(query.strip())
    data = json.loads(raw_json)

    # Attach Google Favicon and Clearbit logo URLs to discovered company & competitors
    if "company" in data:
        website = data["company"].get("website", "")
        clean_dom = extract_clean_domain(website or query)
        data["company"]["domain"] = clean_dom
        data["company"]["logo"] = get_logo_url(clean_dom)
        data["company"]["clearbit_logo"] = get_clearbit_logo_url(clean_dom)
        if not data["company"].get("website") or data["company"]["website"] == "https://":
            data["company"]["website"] = f"https://{clean_dom}"

    for comp in data.get("recommended_competitors", []):
        comp_site = comp.get("website", "")
        clean_dom = extract_clean_domain(comp_site or comp.get("name", ""))
        comp["domain"] = clean_dom
        comp["logo"] = get_logo_url(clean_dom)
        comp["clearbit_logo"] = get_clearbit_logo_url(clean_dom)
        if not comp.get("website") or comp["website"] == "https://":
            comp["website"] = f"https://{clean_dom}"

    return data

