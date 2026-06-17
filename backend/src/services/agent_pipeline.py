import asyncio
import json
from sqlalchemy import select, desc
from src.database import AsyncSessionLocal
from src.models import Competitor, CompetitorSnapshot, Alert
from src.services.ai import client, FAST_MODEL, MODEL_NAME, llm_semaphore
import httpx
import os

async def send_slack_alert(alert: Alert, company_name: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print(f"[SLACK SIMULATION] Would have sent alert to Slack for {company_name}")
        return
        
    color = "#FF0000" if alert.threat_level == "High" else "#FFA500" if alert.threat_level == "Medium" else "#00FF00"
    payload = {
        "text": f"🚨 *New Intelligence Alert: {company_name}* 🚨",
        "attachments": [
            {
                "color": color,
                "fields": [
                    {"title": "Threat Level", "value": alert.threat_level, "short": True},
                    {"title": "Confidence", "value": f"{alert.confidence_score * 100:.1f}%", "short": True},
                    {"title": "Detected Change", "value": alert.detected_changes, "short": False},
                    {"title": "Strategy Recommendation", "value": alert.recommended_action, "short": False}
                ]
            }
        ]
    }
    try:
        async with httpx.AsyncClient() as c:
            await c.post(webhook_url, json=payload, timeout=5.0)
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")

async def research_and_monitoring_agent(company_name: str, raw_context: str) -> dict:
    """
    Agent 1: Extracts structured monitoring data from raw research context.
    """
    prompt = f"""
    You are an elite Competitive Monitoring Agent.
    Your task is to extract the current state of '{company_name}' based on the raw research data provided.
    
    RAW DATA:
    {raw_context[:12000]}
    
    Extract exactly 5 key areas:
    1. Pricing Data (Any mention of price, tiers, discounts)
    2. Feature List (Any mention of new or core features)
    3. Messaging (How they position themselves, slogans, target audience)
    4. Sentiment (Overall customer sentiment. Must be exactly one of: "Positive", "Neutral", "Negative")
    5. Sentiment Reason (Why the sentiment is what it is, e.g. "Users complaining about bugs")
    
    Output ONLY a valid JSON object with the keys "pricing", "features", "messaging", "sentiment", "sentiment_score" (float between 0.0 and 1.0 indicating intensity), and "sentiment_reason".
    If data is missing for a key, output "Not found" (or 0.5 for score).
    """
    try:
        async with llm_semaphore:
            res = await client.chat.completions.create(
                model=FAST_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.1
            )
        content = res.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"Monitoring Agent Error: {e}")
    return {"pricing": "Error", "features": "Error", "messaging": "Error", "sentiment": "Neutral", "sentiment_score": 0.5, "sentiment_reason": "Error parsing data"}

async def change_detection_agent(company_name: str, old_state: dict, new_state: dict) -> dict:
    """
    Agent 2: Detects changes between old and new state, outputs threat level and why.
    """
    prompt = f"""
    You are an elite Intelligence Change Detection Engine for a B2B strategy firm.
    Compare the PREVIOUS state and the CURRENT state of '{company_name}'.
    
    PREVIOUS STATE:
    {json.dumps(old_state, indent=2)}
    
    CURRENT STATE:
    {json.dumps(new_state, indent=2)}
    
    CRITICAL RULE: Values like "Not found", "Unknown", or "Error" mean our data scraper missed the information. 
    DO NOT treat changes between "Error" and "Not found" as a business change! 
    ONLY generate an alert if there is a real, tangible change in business strategy (e.g., a real price changed, a real feature was added).
    
    Identify what actually changed in the business. If nothing significant changed, or if it's just missing data, set "has_changes" to false.
    If there are real business changes, or if Customer Sentiment shifted (e.g. from Positive to Negative), analyze:
    1. What changed (in business or in customer sentiment)?
    2. Why did it change?
    3. What is the impact?
    4. What is the possible goal of this change?
    5. What is the Threat Level (Low, Medium, High)?
    6. Confidence Score (0.0 to 1.0) of this assessment.
    
    Output ONLY a valid JSON object with these keys:
    "has_changes" (boolean),
    "detected_changes" (string),
    "possible_goal" (string),
    "threat_level" (string: "Low", "Medium", "High"),
    "impact" (string),
    "confidence_score" (float)
    """
    try:
        async with llm_semaphore:
            res = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2
            )
        content = res.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"Change Detection Error: {e}")
    
    return {"has_changes": False}

async def strategy_agent(company_name: str, changes_detected: dict) -> str:
    """
    Agent 3: Generates executive recommended counter actions based on detected changes.
    """
    if not changes_detected.get("has_changes"):
        return "Continue monitoring. No immediate strategic counter-action required."
        
    prompt = f"""
    You are an Executive Strategy Agent advising the CEO.
    Our competitor '{company_name}' has made the following moves:
    
    Detected Changes: {changes_detected.get('detected_changes')}
    Possible Goal: {changes_detected.get('possible_goal')}
    Impact: {changes_detected.get('impact')}
    Threat Level: {changes_detected.get('threat_level')}
    
    Write a concise, highly actionable "Recommended Counter-Action" (2-3 sentences) that our sales and marketing teams should immediately execute to neutralize this threat.
    Do not use markdown formatting.
    """
    try:
        async with llm_semaphore:
            res = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.4
            )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"Strategy Agent Error: {e}")
        return "Error generating strategy."

async def run_autonomous_pipeline(competitor_id: int):
    """
    Executes the V2 Agentic Pipeline for a competitor.
    1. Research & Monitor -> 2. Change Detection -> 3. Strategy
    """
    # 0. We assume `raw_context` has already been populated by `_inner_run_scraping_job`
    async with AsyncSessionLocal() as session:
        comp = (await session.execute(select(Competitor).where(Competitor.id == competitor_id))).scalar_one_or_none()
        if not comp or not comp.raw_context:
            print("No competitor or raw context found.")
            return

        print(f"Starting Agent Pipeline for {comp.name}...")

        # 1. Research & Monitoring Phase
        current_state = await research_and_monitoring_agent(comp.name, comp.raw_context)
        
        # Save Current Snapshot
        new_snapshot = CompetitorSnapshot(
            competitor_id=comp.id,
            pricing_data=current_state.get("pricing"),
            feature_list=current_state.get("features"),
            messaging=current_state.get("messaging"),
            sentiment=current_state.get("sentiment"),
            sentiment_score=current_state.get("sentiment_score"),
            sentiment_reason=current_state.get("sentiment_reason"),
            raw_context=comp.raw_context[:5000] # store partial context
        )
        
        # Fetch Previous Snapshot
        prev_snapshot_result = await session.execute(
            select(CompetitorSnapshot)
            .where(CompetitorSnapshot.competitor_id == comp.id)
            .order_by(desc(CompetitorSnapshot.snapshot_date))
            .limit(1)
        )
        prev_snapshot = prev_snapshot_result.scalar_one_or_none()
        session.add(new_snapshot)
        await session.commit()
        
    old_state_dict = {}
    if prev_snapshot:
        old_state_dict = {
            "pricing": prev_snapshot.pricing_data,
            "features": prev_snapshot.feature_list,
            "messaging": prev_snapshot.messaging,
            "sentiment": prev_snapshot.sentiment,
            "sentiment_reason": prev_snapshot.sentiment_reason
        }
    else:
        # If no previous snapshot, we assume everything is "new" but no massive change event
        old_state_dict = {"pricing": "Unknown", "features": "Unknown", "messaging": "Unknown", "sentiment": "Neutral"}
        
    # 2. Change Detection Phase
    print(f"Running Change Detection for {comp.name}...")
    changes = await change_detection_agent(comp.name, old_state_dict, current_state)
    
    if changes.get("has_changes") and prev_snapshot:
        # 3. Strategy Phase
        print(f"Running Strategy Agent for {comp.name}...")
        recommended_action = await strategy_agent(comp.name, changes)
        
        # Save Alert
        async with AsyncSessionLocal() as session:
            new_alert = Alert(
                competitor_id=comp.id,
                detected_changes=changes.get("detected_changes", "Unknown changes"),
                possible_goal=changes.get("possible_goal", "Unknown goal"),
                threat_level=changes.get("threat_level", "Medium"),
                recommended_action=recommended_action,
                confidence_score=float(changes.get("confidence_score", 0.0))
            )
            session.add(new_alert)
            await session.commit()
            print(f"Alert generated for {comp.name}.")
        
        await send_slack_alert(new_alert, comp.name)
    else:
        print(f"No significant changes detected for {comp.name}.")
