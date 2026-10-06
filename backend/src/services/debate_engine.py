from src.services.ai import client, MODEL_NAME, llm_semaphore
import asyncio
import logging

logger = logging.getLogger(__name__)

async def run_multi_agent_debate(competitor_name: str, our_company: str, competitor_data: str) -> str:
    """
    Simulates a debate between two AI agents to find the ultimate winning sales argument against a competitor.
    """
    
    # Agent 1 (Defense Lawyer)
    async def agent_defense():
        prompt = f"""
        You are the Defense Lawyer for '{competitor_name}'. Your rival is '{our_company}'.
        
        Untrusted scraped data context:
        <<<UNTRUSTED_CONTEXT>>>
        {competitor_data[:5000]}
        <<<END_UNTRUSTED_CONTEXT>>>
        
        Argue exactly 3 reasons why {competitor_name} is fundamentally superior and invincible compared to {our_company}.
        Be aggressive and highly persuasive.
        """
        try:
            async with llm_semaphore:
                res = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    timeout=45.0,
                )
            return res.choices[0].message.content
        except Exception as e:
            logger.warning("Defense agent LLM failed: %s", e)
            return f"{competitor_name} emphasizes market stability, product features, and enterprise support."

    defense_argument = await agent_defense()

    # Agent 2 (Attack Strategist)
    async def agent_attack(defense_points: str):
        prompt = f"""
        You are the Attack Strategist for '{our_company}'. Your rival is '{competitor_name}'.
        The competitor's Defense Lawyer just argued this:
        {defense_points}
        
        Untrusted data about their flaws:
        <<<UNTRUSTED_CONTEXT>>>
        {competitor_data[:5000]}
        <<<END_UNTRUSTED_CONTEXT>>>
        
        Write a vicious, factual counter-attack that completely destroys their defense. 
        Give 3 devastating counter-points.
        """
        try:
            async with llm_semaphore:
                res = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    timeout=45.0,
                )
            return res.choices[0].message.content
        except Exception as e:
            logger.warning("Attack agent LLM failed: %s", e)
            return f"1. Superior integration capability.\n2. Lower TCO.\n3. Modern agile architecture."

    attack_argument = await agent_attack(defense_argument)
    
    # Judge Agent (Synthesizer)
    async def agent_judge(defense: str, attack: str):
        prompt = f"""
        You are a highly professional B2B Enterprise Sales Director.
        Analyze this debate between {competitor_name} (Defense) and {our_company} (Attack).
        
        DEFENSE: {defense}
        ATTACK: {attack}
        
        Output the ultimate "Winning Sales Argument" for {our_company}'s sales team to use when pitching against {competitor_name} in a boardroom.
        
        CRITICAL TONE RULES:
        1. Tone MUST be highly professional, consultative, and concise (B2B SaaS style).
        2. NEVER use theatrical language like "Ladies and gentlemen", "Let's be clear", or "As we stand here today".
        3. Do NOT write it as a speech. Write it as an actionable sales playbook/talk-track for an Account Executive.
        4. Focus on business value, ROI, and factual competitive advantages.
        
        Format as Markdown:
        ### 🤺 Multi-Agent Debate Output
        
        #### Competitor's Strongest Argument
        (Brief 1-2 sentence summary of their best point)
        
        #### Our Ultimate Counter-Strike
        (Short, punchy talk-tracks and counter-points the AE should say on the sales call)
        """
        try:
            async with llm_semaphore:
                res = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    timeout=45.0,
                )
            return res.choices[0].message.content
        except Exception as e:
            logger.warning("Judge agent LLM failed: %s", e)
            return "### 🤺 Multi-Agent Debate Output\n\nFailed to synthesize debate verdict due to temporary AI service unavailability."

    final_verdict = await agent_judge(defense_argument, attack_argument)
    return final_verdict
