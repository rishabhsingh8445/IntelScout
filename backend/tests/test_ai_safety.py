import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.services.ai import extract_key_insights, generate_research_plan, answer_rag_question


@pytest.mark.asyncio
async def test_extract_key_insights_schema_validation():
    mock_response = AsyncMock()
    mock_choice = AsyncMock()
    mock_choice.message.content = '[{"title": "Competitor Launch", "summary": "New AI Feature", "category": "Product Launch", "confidence_score": 90}]'
    mock_response.choices = [mock_choice]
    mock_create = AsyncMock(return_value=mock_response)

    with patch("src.services.ai.client.chat.completions.create", mock_create):
        insights = await extract_key_insights("TestComp", "Scraped content text")
        assert len(insights) == 1
        assert insights[0]["title"] == "Competitor Launch"
        assert insights[0]["confidence_score"] == 90


@pytest.mark.asyncio
async def test_extract_key_insights_fallback_on_error():
    with patch("src.services.ai.client.chat.completions.create", side_effect=Exception("API Timeout")):
        insights = await extract_key_insights("TestComp", "Scraped content text")
        assert insights == []


@pytest.mark.asyncio
async def test_generate_research_plan_fallback():
    with patch("src.services.ai.client.chat.completions.create", side_effect=Exception("LLM Rate Limit")):
        queries = await generate_research_plan("AcmeCorp", "Since Launch")
        assert len(queries) == 5
        assert "AcmeCorp" in queries[0]
