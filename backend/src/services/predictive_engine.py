from src.services.ai import client, MODEL_NAME

async def generate_future_predictions(company_name: str, insights: list[dict]) -> str:
    """
    Predictive 'What-If' Engine.
    Reads recent signals and predicts the competitor's next moves.
    """
    if not insights:
        return "Not enough data to generate predictions."

    insights_text = "\n".join([f"- [{ins.get('category')}] {ins.get('title')}: {ins.get('summary')}" for ins in insights])
    
    prompt = f"""
    You are an elite Business Strategist and Futurist.
    Your objective is to predict the next 6 to 12 months for the company '{company_name}' based ONLY on their recent breaking signals.
    
    RECENT SIGNALS:
    {insights_text}
    
    INSTRUCTIONS:
    1. Connect the dots between these signals. For example, if they had layoffs and a product delay, predict a pivot or budget cuts.
    2. Write exactly 3 "What-If" scenarios (e.g. "If they launch X, here is how they will position it...").
    3. Output the result in clean Markdown format with the header `### 🔮 Future Predictions (What-If Analysis)`.
    """
    
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Predictive Engine Error: {e}")
        return "Failed to generate predictions."
