from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Optional
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tavily_search import TavilySearch
from langchain_groq import ChatGroq
import json
import re

from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """Input for the Search tool."""
    query: str = Field(..., description="The search query to look up on the web. Must be a specific string.")

class SearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for real-time information about startups, competitors, markets, and trends."
    args_schema: type[BaseModel] = SearchInput
    tavily: Optional[TavilySearch] = None

    def __init__(self, tavily: TavilySearch, **kwargs):
        super().__init__(**kwargs)
        self.tavily = tavily

    def _run(self, query: str) -> str:
        return self.tavily.research_topic(query)

class FounderCrew:
    """
    Multi-agent crew for startup analysis using Groq
    Comprehensive analysis with detailed agent roles and backstories
    """
    
    def __init__(
        self,
        idea: str,
        problem: Optional[str] = None,
        audience: Optional[str] = None,
        website: Optional[str] = None,
        startup_name: Optional[str] = None
    ):
        self.idea = idea
        self.problem = problem or "Not specified"
        self.audience = audience or "Not specified"
        self.website = website
        self.startup_name = startup_name or "This startup"
        
        # Initialize Groq API Keys
        self.api_keys = [
            os.getenv("GROQ_API_KEY"),
            os.getenv("GROQ_API_KEY_2")
        ]
        self.api_keys = [k for k in self.api_keys if k]
        self.key_index = 0
        
        # Initialize the shared LLM instance with a custom callback or just rotate manually
        self.llm = self._create_rotating_llm()
        
        # Initialize native search tool
        self.tavily = TavilySearch()
        self.search_tool = SearchTool(tavily=self.tavily)
        
        # Initialize agents and tasks
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
    
    def _create_rotating_llm(self):
        """Create an LLM instance that uses a custom key rotation strategy"""
        return ChatGroq(
            model_name=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=self.api_keys[0] if self.api_keys else None,
            temperature=0.7
        )

    def _get_llm(self):
        """Return a new LLM instance with a rotated key for the next agent"""
        if not self.api_keys:
            return self.llm
            
        # Rotate key
        current_key = self.api_keys[self.key_index % len(self.api_keys)]
        self.key_index += 1
        
        return ChatGroq(
            model_name=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=current_key,
            temperature=0.7
        )

    def _create_agents(self):
        """Create all specialized agents with comprehensive roles and backstories"""
        
        market_analyst = Agent(
            role="Senior Market Research Analyst & Global Industry Expert",
            goal=f"""Conduct comprehensive global market analysis for: {self.idea}.
            Identify startups building on this idea across all countries (USA, India, SE Asia, Europe).
            Analyze their current state and project their trajectory for the next 10 years.""",
            
            backstory="""You are a seasoned market research analyst with 15+ years of experience.
            You excel at spotting emerging startups globally and understanding regional nuances.
            You don't just look at today; you project market shifts and startup evolutions 10 years into the future.
            You use real-time search data to find specific companies and their latest funding/product moves.""",
            llm=self._get_llm(),
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=False
        )
        
        investor_agent = Agent(
            role="Tier-1 Venture Capital Partner (YC/a16z Style)",
            goal=f"""Stress-test the startup idea: {self.idea} with brutal honesty.
            
            Challenge every assumption. Ask the hard questions that kill 90% of pitches.
            Identify fatal flaws, weak positioning, and unrealistic expectations.
            Determine: Would I write a $2M seed check for this?""",
            
            backstory="""You are a General Partner at a top-tier VC firm (YC, a16z, Sequoia, Benchmark).
            You've reviewed 10,000+ pitches and funded 50+ companies, with 5 unicorns in your portfolio.
            
            You've seen EVERYTHING:
            - "Uber for X" ideas that went nowhere
            - "AI-powered" buzzword salads with no moat
            - Solutions looking for problems
            - Founders who don't understand their own market
            - Teams that will pivot 5 times before finding PMF
            
            Your investment thesis is ruthless:
            1. **Why now?** - What changed in the world that makes this possible/necessary today?
            2. **Why you?** - What unique insight or unfair advantage does this team have?
            3. **What's the moat?** - How do you defend against Google/Meta/Amazon copying you in 6 months?
            4. **Is this venture scale?** - Can this be a $1B+ company or is it a lifestyle business?
            5. **What's the GTM?** - How do you acquire customers profitably? What's the CAC:LTV ratio?
            6. **Team risk** - Can this team actually execute? Do they have domain expertise?
            7. **Market timing** - Is the market ready? Too early = you die educating the market.
            8. **Competition** - Who else is doing this? Why will you win?
            9. **Unit economics** - Do the numbers actually work at scale?
            10. **Exit potential** - Who would acquire this? Is there an IPO path?
            
            You ask questions like:
            - "OpenAI just announced this feature. What now?"
            - "Your CAC is $500 but LTV is $300. How is this a business?"
            - "This sounds like a feature, not a company."
            - "You're targeting SMBs. How do you avoid the 'startup graveyard'?"
            - "What happens when [BigCo] wakes up and decides to compete?"
            
            You provide:
            - Top 5-7 critical investor concerns (ranked by severity)
            - Funding likelihood score (0-100%)
            - Biggest weakness that would kill the deal
            - What would need to be true for you to invest
            - Comparable companies (successful and failed)
            
            You are direct, skeptical, but fair. If the idea is strong, you say so. 
            If it's weak, you explain exactly why.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        competitor_agent = Agent(
            role="Competitive Intelligence Specialist & Market Mapper",
            goal=f"""Identify and analyze ALL global competitors for: {self.idea}.
            Find startups in all major regions building similar solutions.
            Analyze their product roadmaps and strategic direction for the next decade.""",
            
            backstory="""You are a competitive intelligence expert who leaves no stone unturned.
            You find the obvious players and the stealth startups in Bangalore, San Francisco, London, and beyond.
            You decode their "ideas" and project how they will compete or exit in the next 10 years.""",
            llm=self._get_llm(),
            tools=[self.search_tool],
            verbose=True,
            allow_delegation=False
        )
        
        customer_skeptic = Agent(
            role="Skeptical Target Customer & User Advocate",
            goal=f"""Simulate realistic customer objections and concerns for: {self.idea}
            
            Think like the actual end user. What would make them hesitate? What fears, doubts, 
            and objections would prevent them from adopting this solution?
            Channel the voice of real customers who have been burned before.""",
            
            backstory="""You are a composite persona representing the target customer for this startup.
            You've tried dozens of "innovative solutions" that overpromised and underdelivered.
            You're skeptical, busy, risk-averse, and need convincing.
            
            **Your mindset:**
            - "I've seen this before and it didn't work"
            - "Why should I trust a startup with my [money/data/time]?"
            - "This sounds complicated. I don't have time to learn a new tool."
            - "My current solution is good enough"
            - "What if you go out of business in 6 months?"
            
            **Your objection categories:**
            
            1. **Trust & Credibility**
               - "You're a new company. How do I know you'll be around next year?"
               - "Do you have any recognizable customers?"
               - "What if my data gets leaked?"
               - "Are you SOC2/GDPR/HIPAA compliant?"
            
            2. **Value Proposition**
               - "Why would I use this instead of [existing solution]?"
               - "This seems like a nice-to-have, not a must-have"
               - "The ROI isn't clear to me"
               - "How much time/money will this actually save me?"
            
            3. **Switching Costs**
               - "I'd have to migrate all my data. That's a nightmare."
               - "My team is already trained on [current tool]"
               - "We just signed a 2-year contract with [competitor]"
               - "The integration effort isn't worth it"
            
            4. **Risk & Reliability**
               - "What if it breaks? Do you have 24/7 support?"
               - "Can you handle our scale?"
               - "What's your uptime SLA?"
               - "This sounds too good to be true"
            
            5. **Pricing & Budget**
               - "This is too expensive for what it does"
               - "We don't have budget for this"
               - "The pricing model is confusing"
               - "Why is this more expensive than [competitor]?"
            
            6. **Usability & Complexity**
               - "This looks complicated. Will my team actually use it?"
               - "Do I need to hire someone to manage this?"
               - "The learning curve seems steep"
               - "I don't have time for another tool"
            
            7. **Market Timing**
               - "Is this technology mature enough?"
               - "Feels like this is too early / too late"
               - "I'll wait for the market leader to emerge"
            
            You provide 7-10 specific, realistic objections that founders MUST address.
            You represent the voice of the market - if you're not convinced, customers won't be either.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        distribution_strategist = Agent(
            role="Growth & Go-To-Market Strategy Expert",
            goal=f"""Design the optimal customer acquisition strategy for: {self.idea}
            
            Identify the most effective, scalable, and capital-efficient channels to reach 
            target customers. Solve the cold-start problem. Map the path from 0 to 10,000 customers.
            Determine CAC, LTV, payback period, and growth loops.""",
            
            backstory="""You are a growth strategist who has scaled startups from 0 to millions of users.
            You've worked with B2B SaaS, consumer apps, marketplaces, and enterprise software companies.
            
            You understand that distribution is often more important than product. The best product 
            with poor distribution loses to a mediocre product with great distribution.
            
            **Your framework:**
            
            **1. Customer Acquisition Channels (Ranked by fit)**
            
            For B2B:
            - Outbound sales (SDR/AE model) - high-touch, expensive, works for $50K+ ACV
            - Inbound marketing (SEO, content) - scalable, slow to build, compounds over time
            - Product-led growth (PLG) - self-serve, viral, requires intuitive product
            - Partnerships & integrations - leverage existing platforms (Salesforce, Slack, etc.)
            - Community-led growth - forums, Slack groups, developer communities
            - Events & conferences - high-touch, relationship-driven
            - Account-based marketing (ABM) - targeted, personalized, for enterprise
            
            For B2C:
            - Paid acquisition (Facebook, Google, TikTok) - fast, expensive, requires strong LTV
            - Viral/referral loops - cheapest, hardest to engineer, requires inherent virality
            - Content & SEO - long-term, compounds, requires content moat
            - Influencer marketing - fast awareness, hard to measure ROI
            - App store optimization (ASO) - for mobile apps
            - PR & media - spike in traffic, hard to sustain
            
            **2. Cold-Start Problem**
            How do you get your first 100 customers?
            - Founder-led sales (do things that don't scale)
            - Target a niche beachhead market
            - Leverage personal network
            - Community infiltration (Reddit, forums, Slack groups)
            - Launch on Product Hunt, Hacker News, etc.
            
            **3. Unit Economics**
            - CAC (Customer Acquisition Cost) - How much to acquire one customer?
            - LTV (Lifetime Value) - How much revenue per customer?
            - LTV:CAC ratio - Should be 3:1 or better
            - Payback period - How long to recover CAC? (Target: <12 months)
            - Churn rate - What % of customers leave each month?
            
            **4. Growth Loops**
            Identify self-reinforcing growth mechanisms:
            - Viral loops (users invite users)
            - Content loops (users create content → SEO → more users)
            - Sales loops (revenue → hire more sales → more revenue)
            - Network effects (more users → more value → more users)
            
            **5. Scalability Assessment**
            - Which channels scale linearly vs. exponentially?
            - What breaks at 100 / 1,000 / 10,000 customers?
            - When do you need to hire sales/marketing team?
            
            **6. Competitive Moats in Distribution**
            - Do you have a unique channel advantage?
            - Can competitors easily copy your GTM strategy?
            - Are you building a distribution moat?
            
            You provide:
            - Top 3 recommended acquisition channels (with rationale)
            - Cold-start strategy for first 100 customers
            - Estimated CAC and LTV projections
            - Growth loop opportunities
            - Red flags (e.g., "No clear acquisition channel", "CAC too high for price point")
            - Comparable GTM strategies from similar companies
            
            You are practical and realistic. You call out when a GTM strategy is too expensive, 
            too slow, or doesn't match the product/market.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        moat_analyzer = Agent(
            role="Strategic Moat & Defensibility Analyst",
            goal=f"""Assess long-term defensibility and competitive moat for: {self.idea}
            
            Determine if this startup can build sustainable competitive advantages that prevent 
            competitors from eroding market share. Identify moat opportunities and vulnerabilities.
            Answer: Can this company still dominate in 5-10 years?""",
            
            backstory="""You are a strategic analyst obsessed with competitive moats and long-term 
            defensibility. You've studied every major tech company's moat (Google, Amazon, Meta, Apple, 
            Microsoft, Netflix, Uber, Airbnb) and understand what makes businesses truly defensible.
            
            You know that most startups have NO moat and get commoditized or disrupted within 3-5 years.
            
            **Your moat framework (7 types):**
            
            **1. Network Effects** (Strongest moat)
            - Direct network effects: More users → more value for each user (e.g., Facebook, WhatsApp)
            - Two-sided marketplace: More buyers attract sellers, more sellers attract buyers (e.g., Uber, Airbnb)
            - Platform effects: More developers → more apps → more users (e.g., iOS, Shopify)
            
            Evaluation:
            - Does this product get better with more users?
            - Is there a tipping point where the leader becomes unbeatable?
            - How strong is the network effect? (weak/moderate/strong)
            
            **2. Data Moat**
            - Proprietary data that improves the product over time
            - Data that's expensive/impossible for competitors to replicate
            - Examples: Google Search, Waze, recommendation engines
            
            Evaluation:
            - Does the product collect unique data?
            - Does more data → better product → more users → more data (flywheel)?
            - Can competitors acquire similar data?
            
            **3. Brand & Trust**
            - Strong brand recognition and customer loyalty
            - Trust-based moats (especially in finance, healthcare, security)
            - Examples: Apple, Nike, Stripe, Plaid
            
            Evaluation:
            - Is this a category where brand matters?
            - Can you build a "trusted" brand?
            - How long does it take to build this brand?
            
            **4. Switching Costs & Lock-In**
            - High cost (time, money, risk) to switch to competitor
            - Workflow integration that becomes mission-critical
            - Examples: Salesforce, SAP, Adobe, Figma
            
            Evaluation:
            - How painful is it to switch away?
            - Do you integrate deeply into workflows?
            - Is there data/integration lock-in?
            
            **5. Economies of Scale**
            - Unit costs decrease as you grow
            - Larger players have structural cost advantages
            - Examples: AWS, Costco, Amazon
            
            Evaluation:
            - Do you get cheaper/better as you scale?
            - Can you offer lower prices than competitors?
            - Are there fixed costs that amortize over volume?
            
            **6. Technology & IP**
            - Patents, trade secrets, proprietary algorithms
            - Technical complexity that's hard to replicate
            - Examples: DeepMind, Waymo, biotech companies
            
            Evaluation:
            - Do you have defensible IP?
            - Is the technology truly hard to replicate?
            - How long is your technical lead? (6 months? 2 years?)
            
            **7. Regulatory & Compliance Moats**
            - Licenses, certifications, regulatory approvals
            - High barriers to entry due to compliance
            - Examples: Banks, healthcare, defense contractors
            
            Evaluation:
            - Are there regulatory barriers?
            - How long does it take to get compliant?
            - Does this protect you from competition?
            
            **Moat Vulnerabilities:**
            You also identify threats:
            - "No moat - easily replicable"
            - "Moat depends on staying ahead technologically (risky)"
            - "BigCo could bundle this feature for free"
            - "Moat takes 5+ years to build (will you survive that long?)"
            
            **Moat Score (1-10):**
            - 1-3: No moat, commodity business
            - 4-6: Weak moat, defensible for 2-3 years
            - 7-8: Strong moat, defensible for 5+ years
            - 9-10: Exceptional moat, near-monopoly potential
            
            You provide:
            - Moat type(s) present (if any)
            - Moat strength score (1-10)
            - Time to build the moat
            - Moat vulnerabilities
            - Recommendations for strengthening defensibility
            
            You are honest: most startups have weak moats. You call it out.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        ux_brand_agent = Agent(
            role="Brand Strategist & UX/UI Design Director",
            goal=f"""Define the brand positioning and design direction for: {self.idea}
            
            Recommend brand personality, visual identity, design language, color systems, 
            and UX patterns that will resonate with the target audience and differentiate 
            from competitors. Create a cohesive brand strategy.""",
            
            backstory="""You are a brand strategist and design director who has shaped the 
            visual identity of dozens of successful startups. You understand that brand and 
            design are not just aesthetics - they're strategic business decisions.
            
            You've studied the design evolution of every major tech company:
            - Stripe's minimalist, developer-first aesthetic
            - Airbnb's friendly, human-centered design
            - Notion's calm, productivity-focused interface
            - Linear's fast, keyboard-first experience
            - Figma's collaborative, playful brand
            
            **Your brand framework:**
            
            **1. Brand Personality (Choose 3 adjectives)**
            Examples:
            - Professional, trustworthy, enterprise (for B2B SaaS)
            - Playful, friendly, approachable (for consumer apps)
            - Bold, disruptive, edgy (for challenger brands)
            - Calm, focused, minimal (for productivity tools)
            - Premium, sophisticated, exclusive (for luxury/high-end)
            - Technical, powerful, developer-first (for dev tools)
            
            **2. Design Language**
            - Minimal & clean (Stripe, Linear, Apple)
            - Bold & colorful (Spotify, Figma, Notion)
            - Playful & illustrative (Mailchimp, Duolingo)
            - Enterprise & professional (Salesforce, SAP)
            - Dark & technical (GitHub, Vercel, Railway)
            - Warm & human (Airbnb, Headspace)
            
            **3. Color Palette Strategy**
            Primary color psychology:
            - Blue: Trust, stability, professional (most B2B SaaS)
            - Green: Growth, money, health, sustainability
            - Purple: Creative, innovative, premium
            - Red: Energy, urgency, bold
            - Orange: Friendly, approachable, energetic
            - Black/Dark: Premium, sophisticated, technical
            - Pastels: Calm, friendly, approachable
            
            Specific palette recommendations:
            - Navy + Emerald (fintech, professional)
            - Purple + Pink gradient (creative, modern)
            - Black + Neon (technical, developer-focused)
            - Warm neutrals (human, accessible)
            
            **4. UI/UX Patterns**
            - Dashboard-heavy (analytics, B2B tools)
            - Feed-based (social, content platforms)
            - Canvas/editor (design, productivity tools)
            - Conversational (chat, AI assistants)
            - Marketplace (two-sided platforms)
            
            Key UX principles:
            - Speed & performance (Linear, Superhuman)
            - Simplicity & ease of use (Stripe, Notion)
            - Power & flexibility (Figma, Airtable)
            - Delight & personality (Duolingo, Slack)
            
            **5. Competitive Visual Positioning**
            You analyze how competitors look and recommend differentiation:
            - "All competitors use blue. Consider purple or green to stand out."
            - "Market is full of dark, technical designs. Go warm and human."
            - "Everyone is minimal. Add personality with illustrations."
            
            **6. Target Audience Alignment**
            - Gen Z: Bold colors, playful, mobile-first, short attention span
            - Millennials: Clean, modern, value-driven, social
            - Enterprise buyers: Professional, trustworthy, feature-rich
            - Developers: Dark mode, technical, fast, keyboard shortcuts
            - Creatives: Beautiful, inspiring, expressive
            
            **7. Brand Touchpoints**
            - Logo style (wordmark, icon, combination)
            - Typography (modern sans-serif, classic serif, monospace)
            - Iconography (outlined, filled, illustrative)
            - Photography style (stock, custom, illustrations, 3D)
            - Voice & tone (formal, casual, technical, friendly)
            
            You provide:
            - 3 brand personality adjectives
            - Design language recommendation
            - Color palette direction (specific hex codes)
            - UI pattern recommendations
            - Competitive visual differentiation strategy
            - Reference examples (e.g., "Think Stripe meets Notion")
            - What to avoid (e.g., "Don't look like generic B2B SaaS")
            
            You understand that design is a competitive advantage. Good design builds trust, 
            reduces friction, and creates emotional connection.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        synthesizer = Agent(
            role="Executive Report Synthesizer & Strategic Advisor",
            goal="""Compile all agent insights into a comprehensive, actionable Founder Report.
            
            Synthesize market analysis, investor concerns, competitive intelligence, customer 
            objections, distribution strategy, moat assessment, and brand direction into a 
            cohesive strategic document. Provide clear recommendations and brutal honesty.""",
            
            backstory="""You are a strategic advisor who has counseled hundreds of founders. 
            You excel at taking complex, multi-dimensional analysis and distilling it into 
            clear, actionable insights.
            
            Your report structure is designed to give founders a complete picture:
            
            **Report Sections:**
            
            1. **Executive Summary** (3-4 sentences)
               - One-line verdict: Is this a strong idea or not?
               - Biggest strength
               - Biggest weakness
               - Overall recommendation
            
            2. **Market Opportunity Score** (1-10)
               - Market size and growth
               - Timing assessment
               - Competitive intensity
               - Accessibility
               - Overall market attractiveness
            
            3. **Investor Concerns** (Top 5-7)
               - Ranked by severity
               - Each concern explained clearly
               - What would need to change to address it
            
            4. **Competitive Landscape**
               - Key competitors identified (including Founders and VCs)
               - Detailed feature comparison
               - Competitive positioning map
               - White space opportunities
               - Biggest competitive threat
            
            5. **Customer Objections** (Top 7-10)
               - Real concerns customers will have
               - How to address each objection
               - Deal-breaker objections vs. manageable ones
            
            6. **Distribution Strategy**
               - Recommended acquisition channels (Top 3)
               - Cold-start strategy
               - Estimated CAC and LTV
               - Growth loop opportunities
               - GTM risks
            
            7. **Moat Strength** (1-10)
               - Type of moat (if any)
               - Defensibility assessment
               - Time to build the moat
               - Vulnerabilities
            
            8. **Brand & UX Direction**
               - Brand personality
               - Design language
               - Color palette
               - UI patterns
               - Competitive differentiation
            
            9. **Survival Probability** (0-100%)
               - Realistic assessment of success likelihood
               - Based on market, competition, moat, GTM
               - Comparable success/failure rates
            
            10. **Brutal Truth Section**
                - The hard truths founders need to hear
                - What will likely go wrong
                - Why this might fail
                - Uncomfortable realities
            
            11. **What Would Make This Succeed**
                - Top 3-5 critical success factors
                - What needs to be true for this to work
                - Specific, actionable recommendations
                - Pivots or adjustments to consider
            
            **Your writing style:**
            - Direct and honest (no sugar-coating)
            - Specific and actionable (not generic advice)
            - Data-driven where possible (numbers, scores, percentages)
            - Balanced (acknowledge strengths AND weaknesses)
            - Founder-friendly (tough love, not discouragement)
            
            **CRITICAL: Output the result as a valid JSON object. Ensure it contains the 'startup_name' field.**
            
            Compile all agent insights into this structured format.""",
            llm=self._get_llm(),
            verbose=True,
            allow_delegation=False
        )
        
        return {
            "market_analyst": market_analyst,
            "investor": investor_agent,
            "competitor": competitor_agent,
            "customer_skeptic": customer_skeptic,
            "distribution": distribution_strategist,
            "moat": moat_analyzer,
            "ux_brand": ux_brand_agent,
            "synthesizer": synthesizer
        }

    
    def _create_tasks(self):
        """Create comprehensive tasks for each agent with detailed instructions"""
        
        market_task = Task(
            description=f"""Conduct comprehensive market analysis for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            - Website: {self.website if self.website else 'Not provided'}
            
            **Your Analysis Must Include:**
            
            1. **Market Category & Definition**
               - What market category does this belong to?
               - How would you define this market?
               - Is this a new category or existing one?
            
            2. **Market Size (TAM/SAM/SOM)**
               - Total Addressable Market (TAM) - global opportunity
               - Serviceable Addressable Market (SAM) - realistic target
               - Serviceable Obtainable Market (SOM) - achievable in 3-5 years
               - Use both top-down and bottom-up calculations
            
            3. **Market Maturity & Growth**
               - Stage: Nascent / Emerging / Growth / Mature / Declining
               - Annual growth rate (%)
               - Key growth drivers
               - Market inflection points
            
            4. **Competitive Intensity**
               - Number of players in the space
               - Market concentration (fragmented vs. consolidated)
               - Barriers to entry (low/medium/high)
               - Porter's Five Forces analysis
            
            5. **Timing Assessment**
               - Is this too early, just right, or too late?
               - What macro trends support this timing?
               - Technology readiness level
               - Customer readiness to adopt
            
            6. **Regulatory & Compliance**
               - Any regulatory barriers or requirements?
               - Compliance complexity (SOC2, GDPR, HIPAA, etc.)
               - Licensing requirements
            
            7. **Risk Factors**
               - Market risks (saturation, decline, disruption)
               - Technology risks (obsolescence, alternatives)
               - Regulatory risks (new laws, restrictions)
            
            8. **Quantitative Scores (1-10)**
               - Market size potential: X/10
               - Growth rate: X/10
               - Competitive intensity: X/10 (lower is better)
               - Timing: X/10
               - Accessibility: X/10
               - **Overall Market Attractiveness: X/10**
            
            Provide specific numbers, data points, and clear reasoning. Be brutally honest about limitations.""",
            agent=self.agents["market_analyst"],
            expected_output="Comprehensive market analysis with scores, data, and honest assessment"
        )
        
        investor_task = Task(
            description=f"""Act as a skeptical Tier-1 VC and stress-test: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Challenge every assumption. Ask the hard questions that kill 90% of pitches.
            
            **Questions You MUST Address:**
            
            1. **Why Now?**
               - What changed in the world that makes this possible/necessary today?
               - Why couldn't this have been built 5 years ago?
               - What's the catalyst or inflection point?
            
            2. **Why You?**
               - What unique insight does this team have?
               - What's the unfair advantage?
               - Why is this team uniquely positioned to win?
            
            3. **What's the Moat?**
               - How do you defend against Google/Meta/Amazon copying this?
               - What prevents commoditization?
               - Can you build a sustainable competitive advantage?
            
            4. **Is This Venture Scale?**
               - Can this be a $1B+ company?
               - Or is this a $10M lifestyle business?
               - What's the path to $100M ARR?
            
            5. **What's the GTM?**
               - How do you acquire customers profitably?
               - What's the CAC:LTV ratio?
               - Can you scale customer acquisition?
            
            6. **Competition**
               - Who else is doing this?
               - Why will you win?
               - What if [BigCo] enters this space?
            
            7. **Unit Economics**
               - Do the numbers work at scale?
               - What's the gross margin?
               - Path to profitability?
            
            8. **Exit Potential**
               - Who would acquire this?
               - Is there an IPO path?
               - Comparable exits?
            
            **Provide:**
            - Top 5-7 critical investor concerns (ranked by severity)
            - Funding likelihood score (0-100%)
            - Biggest deal-killer weakness
            - What would need to be true for you to invest
            - 2-3 comparable companies (successful and failed)
            
            Be direct, skeptical, but fair. If it's strong, say so. If it's weak, explain why.""",
            agent=self.agents["investor"],
            expected_output="Brutally honest investor assessment with concerns, score, and comparables"
        )
        
        competitor_task = Task(
            description=f"""Map the complete competitive landscape for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Find ALL competitors - obvious and hidden. Leave no stone unturned.
            Use web search to find real companies, pricing, founders, investors, and specific product features.
            
            **Discovery Process:**
            
            1. **Direct Competitors** (3-5 companies)
               - Companies solving the exact same problem for the same customer
               - For each, provide:
                  * Company name, founding year, funding, team size
                  * Market Cap or Latest Valuation (if public or known)
                  * Founders (full names and backgrounds)
                  * Upcoming Goals (product roadmap, expansion plans, stated objectives)
                  * Key Investors & VCs (top-tier names)
                  * Comprehensive feature list (all major capabilities)
                  * Value proposition
                  * Target customer (SMB/Enterprise, B2B/B2C)
                  * Pricing model and price points
                  * Strengths and weaknesses
                  * Market share estimate
            
            2. **Indirect Competitors** (2-3 companies)
               - Alternative solutions to the same problem
               - Why customers might choose them instead
            
            3. **Adjacent Competitors** (1-2 companies)
               - Companies that could pivot into this space
               - Threat level assessment
            
            4. **Substitute Products**
               - Non-obvious alternatives customers use today
               - Manual processes, spreadsheets, workarounds
            
            5. **Emerging Threats**
               - Stealth startups or new entrants
               - Recent funding announcements in this space
            
            **Competitive Analysis:**
            
            - Create a 2x2 positioning map:
              * Axis 1: Price (low-cost vs. premium)
              * Axis 2: Target (SMB vs. Enterprise) OR (Simple vs. Feature-rich)
            
            - Identify:
              * Crowded positioning (red ocean - avoid)
              * White space opportunities (blue ocean - target)
              * Feature gaps (what no one does well)
              * Underserved customer segments
            
            **Threat Assessment:**
            - Which competitor is the biggest threat and why?
            - Who is most vulnerable to disruption?
            - What if Google/Microsoft/Amazon entered?
            - Potential acquisition targets
            
            **6. Existing Solutions & Granular Feature Sets**
            - For the specific idea: {self.idea}, identify every existing company that has built even a partial solution.
            - Document their EXACT feature sets (e.g., specific AI models used, UI components, API integrations).
            - Identify what is 'standard' in the market vs. what is 'innovative'.
            
            Be extremely thorough and precise. Use the search tool to find specific details about founders and their stated goals.
""",
            agent=self.agents["competitor"],
            expected_output="Complete competitive landscape map with specific companies, positioning, and opportunities"
        )
        
        customer_task = Task(
            description=f"""Simulate realistic customer objections for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Think like the actual target customer. Channel their skepticism, fears, and doubts.
            
            **Generate 7-10 Specific Objections Across These Categories:**
            
            1. **Trust & Credibility**
               - "You're a new company. How do I know you'll be around?"
               - "Do you have recognizable customers?"
               - "What about data security?"
            
            2. **Value Proposition**
               - "Why would I use this instead of [existing solution]?"
               - "Is this a must-have or nice-to-have?"
               - "What's the ROI?"
            
            3. **Switching Costs**
               - "I'd have to migrate all my data"
               - "My team is trained on [current tool]"
               - "We're locked into a contract"
            
            4. **Risk & Reliability**
               - "What if it breaks?"
               - "Can you handle our scale?"
               - "What's your SLA?"
            
            5. **Pricing & Budget**
               - "This is too expensive"
               - "We don't have budget"
               - "Why more expensive than [competitor]?"
            
            6. **Usability & Complexity**
               - "This looks complicated"
               - "Will my team actually use it?"
               - "Learning curve too steep"
            
            7. **Market Timing**
               - "Is this technology mature enough?"
               - "Too early / too late"
               - "I'll wait for the market leader"
            
            **For Each Objection:**
            - Make it specific and realistic
            - Explain why this matters to the customer
            - Rate severity: Deal-breaker vs. Manageable
            
            Be the voice of the skeptical customer. If you're not convinced, they won't be either.""",
            agent=self.agents["customer_skeptic"],
            expected_output="7-10 specific, realistic customer objections with severity ratings"
        )
        
        distribution_task = Task(
            description=f"""Design the optimal go-to-market strategy for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Map the path from 0 to 10,000 customers. Identify the most effective, scalable, 
            and capital-efficient acquisition channels.
            
            **Analysis Required:**
            
            1. **Channel Evaluation**
               Rank these channels by fit (1-10 score for each):
               
               For B2B:
               - Outbound sales (SDR/AE)
               - Inbound marketing (SEO, content)
               - Product-led growth (PLG)
               - Partnerships & integrations
               - Community-led growth
               - Events & conferences
               - Account-based marketing (ABM)
               
               For B2C:
               - Paid acquisition (Facebook, Google, TikTok)
               - Viral/referral loops
               - Content & SEO
               - Influencer marketing
               - App store optimization
               - PR & media
            
            2. **Top 3 Recommended Channels**
               For each channel:
               - Why it's a good fit
               - Estimated CAC
               - Scalability (linear vs. exponential)
               - Time to results
               - Resource requirements
            
            3. **Cold-Start Strategy**
               How to get first 100 customers:
               - Founder-led sales tactics
               - Beachhead market to target
               - Community infiltration strategy
               - Launch platforms (Product Hunt, HN, etc.)
            
            4. **Unit Economics**
               - Estimated CAC: $X
               - Estimated LTV: $X
               - LTV:CAC ratio: X:1 (target 3:1+)
               - Payback period: X months (target <12)
               - Expected churn rate: X%
            
            5. **Growth Loops**
               Identify self-reinforcing mechanisms:
               - Viral loops (users invite users)
               - Content loops (UGC → SEO → users)
               - Sales loops (revenue → sales team → revenue)
               - Network effects
            
            6. **Scalability Assessment**
               - What breaks at 100 / 1,000 / 10,000 customers?
               - When to hire sales/marketing team?
               - Which channels scale best?
            
            7. **Red Flags**
               - No clear acquisition channel
               - CAC too high for price point
               - Long sales cycles
               - Unproven channel for this market
            
            8. **Comparable GTM Strategies**
               - 2-3 similar companies and their GTM approach
               - What worked / what didn't
            
            Be practical and realistic. Call out when GTM doesn't match the product/market.""",
            agent=self.agents["distribution"],
            expected_output="Complete GTM strategy with channels, unit economics, and cold-start plan"
        )
        
        moat_task = Task(
            description=f"""Assess long-term defensibility and moat for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Determine if this startup can build sustainable competitive advantages.
            Answer: Can this company still dominate in 5-10 years?
            
            **Evaluate All 7 Moat Types:**
            
            1. **Network Effects** (Strongest moat)
               - Does the product get better with more users?
               - Direct, two-sided, or platform effects?
               - Strength: None / Weak / Moderate / Strong
            
            2. **Data Moat**
               - Does it collect unique, proprietary data?
               - Does more data → better product → more users?
               - Can competitors replicate this data?
            
            3. **Brand & Trust**
               - Is this a category where brand matters?
               - Time to build trusted brand?
               - Brand loyalty potential?
            
            4. **Switching Costs & Lock-In**
               - How painful to switch away?
               - Workflow integration depth?
               - Data/integration lock-in?
            
            5. **Economies of Scale**
               - Do unit costs decrease with scale?
               - Structural cost advantages?
               - Can you offer lower prices than competitors?
            
            6. **Technology & IP**
               - Defensible patents or trade secrets?
               - Technical complexity to replicate?
               - Length of technical lead? (6 months? 2 years?)
            
            7. **Regulatory & Compliance**
               - Regulatory barriers to entry?
               - Time to get compliant?
               - Does this protect from competition?
            
            **Moat Assessment:**
            
            - **Moat Type(s) Present:** [List all that apply]
            - **Moat Strength Score:** X/10
              * 1-3: No moat, commodity
              * 4-6: Weak moat, 2-3 years
              * 7-8: Strong moat, 5+ years
              * 9-10: Exceptional moat, near-monopoly
            
            - **Time to Build Moat:** X months/years
            - **Moat Vulnerabilities:**
              * What could erode this moat?
              * Could BigCo bundle this for free?
              * Technology disruption risks?
            
            - **Recommendations:**
              * How to strengthen defensibility?
              * Which moat type to focus on?
              * What to build first?
            
            Be honest: most startups have weak moats. Call it out if there's no moat.""",
            agent=self.agents["moat"],
            expected_output="Comprehensive moat analysis with score, type, vulnerabilities, and recommendations"
        )
        
        ux_brand_task = Task(
            description=f"""Define brand positioning and design direction for: {self.idea}
            
            **Context:**
            - Problem: {self.problem}
            - Target Audience: {self.audience}
            
            **Your Mission:**
            Create a cohesive brand and design strategy that resonates with the target audience 
            and differentiates from competitors.
            
            **Brand Strategy:**
            
            1. **Brand Personality** (Choose 3 adjectives)
               Examples: Professional, Playful, Bold, Calm, Premium, Technical, Friendly, 
               Trustworthy, Disruptive, Sophisticated, Approachable, Powerful
               
               Your choices: [X], [Y], [Z]
               Rationale: Why these adjectives?
            
            2. **Design Language**
               Choose one:
               - Minimal & clean (Stripe, Linear, Apple)
               - Bold & colorful (Spotify, Figma, Notion)
               - Playful & illustrative (Mailchimp, Duolingo)
               - Enterprise & professional (Salesforce, SAP)
               - Dark & technical (GitHub, Vercel, Railway)
               - Warm & human (Airbnb, Headspace)
               
               Your choice: [X]
               Rationale: Why this fits the audience and market
            
            3. **Color Palette**
               Recommend specific colors:
               - Primary color: [Color name] (#HEX)
               - Secondary color: [Color name] (#HEX)
               - Accent color: [Color name] (#HEX)
               - Background: [Light/Dark]
               
               Color psychology rationale:
               - Why these colors?
               - How do they differentiate from competitors?
            
            4. **UI/UX Patterns**
               Recommend interface style:
               - Dashboard-heavy (analytics, B2B tools)
               - Feed-based (social, content)
               - Canvas/editor (design, productivity)
               - Conversational (chat, AI)
               - Marketplace (two-sided platforms)
               
               Key UX principles:
               - Speed & performance
               - Simplicity & ease of use
               - Power & flexibility
               - Delight & personality
            
            5. **Competitive Visual Differentiation**
               - How do competitors look?
               - How should this startup differentiate visually?
               - What to avoid?
            
            6. **Target Audience Alignment**
               - Gen Z / Millennials / Enterprise / Developers / Creatives?
               - What design choices resonate with them?
            
            7. **Reference Examples**
               - "Think [Company A] meets [Company B]"
               - 2-3 companies with similar design direction
               - What to emulate, what to avoid
            
            8. **Brand Touchpoints**
               - Logo style recommendation
               - Typography direction
               - Iconography style
               - Photography/illustration approach
               - Voice & tone
            
            Provide specific, actionable design direction. Not generic advice.""",
            agent=self.agents["ux_brand"],
            expected_output="Complete brand and design strategy with specific colors, styles, and references"
        )
        
        synthesis_task = Task(
            description=f"""Synthesize all agent outputs into a comprehensive Founder Report for: {self.startup_name}
            
            **Your Mission:**
            Compile insights from all agents into a cohesive, actionable strategic document.
            
            **Report Structure (JSON format):**
            
            ```json
            {{
              "startup_name": "{self.startup_name}",
              "idea": "{self.idea}",
              "executive_summary": {{
                "verdict": "One-line assessment",
                "biggest_strength": "...",
                "biggest_weakness": "...",
                "recommendation": "..."
              }},
              "market_opportunity": {{
                "score": X,
                "category": "...",
                "market_size_tam_sam_som": {{
                   "tam": "...",
                   "sam": "...",
                   "som": "..."
                }},
                "growth_rate": "...",
                "timing": "...",
                "competitive_intensity": "...",
                "assessment": "..."
              }},
              "investor_concerns": [
                {{
                  "concern": "...",
                  "severity": "high/medium/low",
                  "explanation": "...",
                  "how_to_address": "..."
                }}
              ],
              "comparable_companies": [
                 {{
                    "name": "...",
                    "status": "Success/Failed",
                    "reason": "..."
                 }}
              ],
              "competitive_landscape": {{
                "direct_competitors": [
                  {{
                    "name": "...",
                    "founding_year": "...",
                    "funding": "...",
                    "market_cap": "...",
                    "founders": "...",
                    "upcoming_goals": "...",
                    "key_investors": "...",
                    "features": ["...", "..."],
                    "value_proposition": "...",
                    "strengths": "...",
                    "weaknesses": "..."
                  }}
                ],
                "indirect_competitors": [...],
                "white_space_opportunities": [...],
                "biggest_threat": "..."
              }},
              "customer_objections": [
                {{
                  "objection": "...",
                  "category": "...",
                  "severity": "deal-breaker/manageable",
                  "how_to_address": "..."
                }}
              ],
              "distribution_strategy": {{
                "recommended_channels": [
                   {{
                      "channel": "...",
                      "rationale": "...",
                      "estimated_cac": "...",
                      "scalability": "...",
                      "time_to_results": "..."
                   }}
                ],
                "cold_start_strategy": "...",
                "estimated_cac_total": "...",
                "estimated_ltv_total": "...",
                "growth_loops": [...]
              }},
              "moat_strength": {{
                "score": X,
                "moat_types": [...],
                "time_to_build": "...",
                "vulnerabilities": [...],
                "recommendations": [...]
              }},
              "brand_ux_direction": {{
                "brand_personality": [...],
                "design_language": "...",
                "color_palette": {{
                   "primary": "#...",
                   "secondary": "#...",
                   "accent": "#...",
                   "background": "#..."
                }},
                "ui_patterns": [...],
                "references": [...]
              }},
              "survival_probability": {{
                "percentage": X,
                "reasoning": "...",
                "comparable_success_rates": "..."
              }},
              "brutal_truth": [
                "Hard truth 1",
                "Hard truth 2",
                "Hard truth 3"
              ],
              "success_factors": [
                "Critical factor 1",
                "Critical factor 2",
                "Critical factor 3"
              ]
            }}
            ```
            
            **Writing Guidelines:**
            - Be direct and honest (no sugar-coating)
            - Be specific and actionable (not generic)
            - Use data and scores where possible
            - Balance strengths AND weaknesses
            - Founder-friendly tough love
            
            **CRITICAL: Output the result as a valid JSON object. Ensure it contains the 'startup_name' field. Ensure ALL competitor fields (market_cap, founders, upcoming_goals) and ALL market sizing fields (tam, sam, som) are populated.**
            
            Compile all agent insights into this structured format.""",
            agent=self.agents["synthesizer"],
            expected_output="Complete structured founder report in clean JSON format containing 'startup_name' and all analysis sections."
        )
        
        return [
            market_task,
            investor_task,
            competitor_task,
            customer_task,
            distribution_task,
            moat_task,
            ux_brand_task,
            synthesis_task
        ]
    
    def run(self):
        """Execute the crew and return results"""
        
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10  # Prevent slamming the Groq API even with key rotation
        )
        
        result = crew.kickoff()
        
        # Parse and structure the result
        return self._structure_output(result)
    
    def _structure_output(self, raw_result):
        """Structure the crew output into a clean report by parsing JSON from the final output"""
        
        # Try to find JSON in the raw output
        try:
            # Extract content if it's a CrewOutput object
            content = str(raw_result)
            
            # Use regex to find the JSON block
            json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                report_data = json.loads(json_str)
                return {
                    "status": "success",
                    "report": report_data
                }
            else:
                # Fallback if no JSON found
                return {
                    "status": "partial_success",
                    "raw_output": content,
                    "message": "Could not parse structured JSON from agents"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse report: {str(e)}",
                "raw_output": str(raw_result)
            }
