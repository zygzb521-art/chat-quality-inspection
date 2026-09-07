import json
import logging
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

ATTITUDE_PROMPT = """你是一个电商客服质检专家。分析以下客服聊天记录，判断客服的服务态度是否存在问题。

请输出JSON格式：
{
  "is_polite": true/false,
  "is_patient": true/false,
  "is_professional": true/false,
  "issues": ["问题1", "问题2"] (如果无问题则为空数组),
  "score": 0-100 (态度评分),
  "detail": "简要分析说明"
}

聊天记录：
{messages}"""

SKILL_PROMPT = """你是一个电商销售技巧评估专家。分析以下客服聊天记录，评估客服的销售技巧。

请输出JSON格式：
{
  "pain_point_grasped": true/false (是否准确抓取客户痛点),
  "recommendation_matched": true/false (推荐是否匹配需求),
  "followup_adequate": true/false (跟进是否充分),
  "cross_sell_attempted": true/false (是否有连带推荐),
  "score": 0-100 (销售技巧评分),
  "detail": "简要分析说明"
}

聊天记录：
{messages}"""

SUGGESTION_PROMPT = """你是一个电商客服培训专家。根据以下聊天记录和已检测到的违规项，给出具体的改进建议。

聊天记录：
{messages}

已检测违规：
{violations}

请输出JSON格式：
{
  "suggestions": ["建议1", "建议2", "建议3"],
  "priority": "high/medium/low",
  "training_focus": "建议培训方向"
}"""


class LLMClient:
    """OpenAI-compatible LLM client (DeepSeek / Qwen / OpenAI)."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.api_url = settings.LLM_API_URL.rstrip('/')
        self.model = settings.LLM_MODEL
        self.timeout = 60

    def _chat(self, system_prompt: str, user_prompt: str) -> dict | None:
        if not self.api_key:
            logger.warning('LLM_API_KEY not configured, skipping AI analysis')
            return None

        try:
            resp = requests.post(
                f'{self.api_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt},
                    ],
                    'temperature': 0.3,
                    'max_tokens': 1024,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            content = resp.json()['choices'][0]['message']['content']
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            return json.loads(content)
        except requests.Timeout:
            logger.error('LLM request timed out after %ss', self.timeout)
            return None
        except Exception as e:
            logger.error('LLM request failed: %s', e)
            return None

    def analyze_attitude(self, messages_text: str) -> dict | None:
        return self._chat(ATTITUDE_PROMPT.format(messages=messages_text), '请分析以上聊天记录的服务态度')

    def analyze_skill(self, messages_text: str) -> dict | None:
        return self._chat(SKILL_PROMPT.format(messages=messages_text), '请评估以上聊天记录的销售技巧')

    def generate_suggestions(self, messages_text: str, violations: str) -> dict | None:
        return self._chat(
            SUGGESTION_PROMPT.format(messages=messages_text, violations=violations),
            '请给出改进建议',
        )