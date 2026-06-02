from src.services.ai import client, MODEL_NAME
import asyncio

async def run_multi_agent_debate(competitor_name: str, our_company: str, competitor_data: str) -> str:
    """
    Simulates a debate between two AI agents to find the ultimate winning sales argument against a competitor.
    """
    
    # Agent 1 (Defense Lawyer)
    async def agent_defense():
        prompt = f"""
        You are the Defense Lawyer for '{competitor_name}'. Your rival is '{our_company}'.
        Based on this data: {competitor_data[:5000]}
        Argue exactly 3 reasons why {competitor_name} is fundamentally superior and invincible compared to {our_company}.
        Be aggressive and highly persuasive.
        """
        res = await client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}], max_tokens=300)
        return res.choices[0].message.content

    defense_argument = await agent_defense()

    # Agent 2 (Attack Strategist)
    async def agent_attack(defense_points: str):
        prompt = f"""
        You are the Attack Strategist for '{our_company}'. Your rival is '{competitor_name}'.
        The competitor's Defense Lawyer just argued this:
        {defense_points}
        
        Using this raw data about their flaws: {competitor_data[:5000]}
        Write a vicious, factual counter-attack that completely destroys their defense. 
        Give 3 devastating counter-points.
        """
        res = await client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}], max_tokens=400)
        return res.choices[0].message.content

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
        res = await client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}], max_tokens=400)
        return res.choices[0].message.content

    final_verdict = await agent_judge(defense_argument, attack_argument)
    return final_verdict
