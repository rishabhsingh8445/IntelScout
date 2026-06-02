from src.services.ai import client, MODEL_NAME
import json

async def generate_feature_matrix(our_company: str, competitor: str, our_data: str, their_data: str) -> list:
    """
    Analyzes research data for two companies and returns a JSON array comparing their features.
    """
    prompt = f"""
    You are an expert Competitive Intelligence Analyst.
    Your task is to analyze '{our_company}' and '{competitor}' and create a 'Feature Gap Matrix' comparison.
    
    Data for {our_company}:
    {our_data[:3000]}
    
    Data for {competitor}:
    {their_data[:3000]}
    
    Output exactly a JSON array of 12 to 15 key features/capabilities.
    Each object must have exactly these keys:
    "feature": string (name of the feature, e.g., "24/7 Support", "AI Assistant", "SOC2 Compliance")
    "us": boolean (true if {our_company} has it, false if not or unknown)
    "them": boolean (true if {competitor} has it, false if not or unknown)
    
    CRITICAL: Do not output any markdown formatting like ```json. Just a raw JSON array starting with [ and ending with ].
    """
    
    res = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.2
    )
    
    raw_response = res.choices[0].message.content.strip()
    
    import re
    match = re.search(r'\[.*\]', raw_response, re.DOTALL)
    if match:
        raw_response = match.group(0)
        
    try:
        matrix = json.loads(raw_response.strip())
        return matrix
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        # Fallback dummy matrix
        return [
            {"feature": "Data Parsing Error", "us": False, "them": False}
        ]
