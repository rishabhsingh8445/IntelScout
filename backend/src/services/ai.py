from openai import AsyncOpenAI
from src.config import settings

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=settings.NVIDIA_API_KEY
)
MODEL_NAME = "meta/llama-3.3-70b-instruct"
FAST_MODEL = "meta/llama-3.3-70b-instruct"

import json
import asyncio

llm_semaphore = asyncio.Semaphore(10)

async def generate_research_plan(company_name: str, timeframe: str) -> list[str]:
    prompt = f"""
    You are a Research Director. Generate 2 distinct, highly-specific internet search queries to deeply research the company '{company_name}' for the timeframe '{timeframe}'.
    The queries should cover:
    1. Financials & Valuation
    2. Recent Product Launches / Tech
    
    Output ONLY a valid JSON array of 2 strings. Do not include markdown formatting or any other text.
    Example: ["Tesla financials 2026", "Tesla lawsuits 2026"]
    """
    try:
        async with llm_semaphore:
            response = await client.chat.completions.create(
                model=FAST_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.2,
                timeout=45.0
            )
        content = response.choices[0].message.content.strip()
        import re
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            queries = json.loads(match.group(0))
            if isinstance(queries, list) and len(queries) > 0:
                return queries[:2]
    except Exception as e:
        print(f"Error generating research plan: {e}")
        
    # Fallback queries
    return [
        f"{company_name} company overview history timeline",
        f"{company_name} latest product launches updates",
        f"{company_name} funding rounds investors financials",
        f"{company_name} lawsuits data privacy controversies",
        f"{company_name} top competitors market share"
    ]

async def _generate_detailed_report(company_name: str, timeframe: str, research_data: str) -> str:
    sections = [
        {"title": "Executive Summary, History & Financial Teardown", "instruction": "Write a deep executive summary and history timeline. Then write an exhaustive financial teardown. Include a detailed markdown table of investments, acquisitions, or revenue. Provide bullet points for key investors."},
        {"title": "Products, Technical Stack & Competitor Analysis", "instruction": "Analyze all products, technological architecture, and tech stack in detail. Then write a comparative analysis against top competitors. Include a markdown table comparing features or market share."},
        {"title": "Customer Voice, Controversies & Future Outlook", "instruction": "Analyze user reviews, complaints, lawsuits, and public controversies. Then predict the company's future trajectory based on current data."}
    ]
    
    async def generate_section(sec):
        prompt = f"""
        You are an elite Competitive Intelligence Analyst for a top-tier consulting firm.
        Write ONLY the section "{sec['title']}" for the company '{company_name}' covering the timeframe '{timeframe}'.
        
        INSTRUCTIONS:
        {sec['instruction']}
        
        CRITICAL RULES:
        1. DO NOT HALLUCINATE. Use only facts from the RESEARCH DATA.
        2. Write expansively (at least 3-4 deep paragraphs). Use formatting like bolding, lists, and tables where appropriate.
        3. Do not include a main report title (like # Report). Only include the section heading `## {sec['title']}`.
        
        RESEARCH DATA:
        {research_data[:8000]}
        """
        try:
            async with llm_semaphore:
                response = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    temperature=0.3,
                    timeout=45.0
                )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in detailed section: {e}")
            return f"## {sec['title']}\nError generating this section."

    results = await asyncio.gather(*(generate_section(sec) for sec in sections))
    
    header = f"# 🕵️‍♂️ Massive Intelligence Report: {company_name}"
    return header + "\n\n" + "\n\n---\n\n".join(results)


async def generate_deep_dive_report(company_name: str, timeframe: str, research_data: str, report_type: str = "Short") -> str:
    """
    Synthesizes massive research data into a beautifully formatted Markdown report.
    """
    if report_type in ["Detailed", "Long"]:
        return await _generate_detailed_report(company_name, timeframe, research_data)
        
    prompt = f"""
    You are an elite Competitive Intelligence Analyst for a top-tier consulting firm.
    Your objective is to generate an exhaustive, highly-detailed Professional Project Report for the company '{company_name}'.
    The user requested this report to cover the timeframe: {timeframe}.
    
    Analyze the following raw internet research data (search snippets and scraped pages):
    
    RESEARCH DATA:
    {research_data[:8000]}
    
    CRITICAL RULES:
    1. DO NOT HALLUCINATE. You must ONLY use facts, numbers, and events present in the RESEARCH DATA.
    2. If the data does not contain information for a section, write "No verified data available for this timeframe."
    3. Generate the report exactly in the structure below.
    4. You MUST include at least one detailed MARKDOWN TABLE in the Financials & Market Position section (e.g. comparing metrics, investments, or competitors).
    5. Write expansively. Do not just write a sentence; write rich, detailed paragraphs like a professional McKinsey or BCG intelligence report.
    
    Write the report exactly with these sections:
    # 🕵️‍♂️ Intelligence Project Report: {company_name}
    
    ## 📅 Journey & Milestones ({timeframe})
    (Write detailed paragraphs summarizing verified product launches, achievements, and timeline based ONLY on data)
    
    ## 💰 Financials & Market Position
    (Write detailed analysis of funding, acquisitions, competitors, market share. YOU MUST INCLUDE A MARKDOWN TABLE HERE summarizing the key financial or competitive metrics found).
    
    ## 📉 Failures, Controversies & Mistakes
    (Write detailed analysis of verified issues, lawsuits, bad decisions, negative press)
    
    ## 🗣️ Voice of the Customer
    (Write detailed paragraphs summarizing actual user sentiment, Reddit quotes, or complaints found in the data)
    """

    try:
        async with llm_semaphore:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.3,
                timeout=45.0
            )
        return response.choices[0].message.content
    except Exception as api_err:
        print(f"NVIDIA API Error: {api_err}")
        return "## Error\nFailed to generate report due to LLM API error."

async def answer_rag_question(question: str, context: str) -> str:
    prompt = f"""
    You are an intelligent assistant for a competitive intelligence platform.
    Answer the user's question STRICTLY based on the provided context. If the answer is not in the context, say "I don't have enough data in the current report context to answer that."
    
    CONTEXT:
    {context[:15000]}
    
    QUESTION: {question}
    """
    try:
        async with llm_semaphore:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1,
                timeout=45.0
            )
        return response.choices[0].message.content
    except Exception as e:
        print(f"RAG Error: {e}")
        return "Error querying the AI model."

async def generate_battlecard(comp_a: str, comp_a_data: str, comp_b: str, comp_b_data: str) -> str:
    prompt = f"""
    You are an elite Competitive Intelligence Analyst.
    Your task is to generate a comprehensive 'Head-to-Head Battlecard' comparing {comp_a} and {comp_b}.
    
    Data for {comp_a}:
    {comp_a_data[:15000]}
    
    Data for {comp_b}:
    {comp_b_data[:15000]}
    
    Write a beautifully formatted Markdown report with these sections:
    # ⚔️ Battlecard: {comp_a} vs {comp_b}
    
    ## 📊 Head-to-Head Matrix
    (MUST include a markdown table comparing Valuation, Funding, Key Products, Market Position, and Strengths)
    
    ## 🥊 Competitive Advantage ({comp_a})
    (Bullet points on why {comp_a} is winning or what they do better)
    
    ## 🥊 Competitive Advantage ({comp_b})
    (Bullet points on why {comp_b} is winning or what they do better)
    
    ## 🎯 Attack Playbook (Objection Handling)
    (Provide an exact 2-3 sentence script for a sales rep. E.g., 'If a customer says {comp_b} is better because X, you should counter with Y based on their recent weaknesses.')
    
    ## 🔮 Verdict & Market Prediction
    (A deep analytical paragraph on who is likely to win the market in the long run)
    """
    try:
        async with llm_semaphore:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.3,
                timeout=45.0
            )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Battlecard Error: {e}")
        return "Failed to generate battlecard due to AI error."

async def extract_key_insights(company_name: str, research_data: str) -> list:
    prompt = f"""
    You are an elite Competitive Intelligence Analyst.
    Your task is to extract 3 to 5 critical, breaking "Signals" or "Insights" from the provided raw internet research data.
    
    CRITICAL RULE: The signal MUST be explicitly and primarily about the company '{company_name}'. 
    Ignore news where {company_name} is only mentioned in passing or if the news is primarily about a different company (e.g., if researching Anthropic, ignore "Google announces Bard").
    
    A signal could be: a new product launch, a financial milestone, a lawsuit, a major leadership change, or a significant strategic pivot for '{company_name}'.
    
    RAW RESEARCH DATA:
    {research_data[:15000]}
    
    Output ONLY a valid JSON array of objects. Do not include markdown formatting or any other text.
    Each object must have exactly these keys:
    - "title": A short, punchy headline (e.g. "{company_name} Launches New Product")
    - "summary": A 1-2 sentence description of the insight
    - "category": Choose one of: "Product Launch", "Financial", "Leadership", "Controversy", "Strategic Move", "Other"
    - "confidence_score": An integer from 0 to 100 representing how confident you are that this is a real event based on the text.
    """
    try:
        async with llm_semaphore:
            response = await client.chat.completions.create(
                model=FAST_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
                timeout=45.0
            )
        content = response.choices[0].message.content.strip()
        import re
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            insights = json.loads(match.group(0))
            if isinstance(insights, list):
                return insights[:5]
    except Exception as e:
        print(f"Error extracting insights: {e}")
        
    return []
