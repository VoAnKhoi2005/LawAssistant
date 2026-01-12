"""
Bước 2: LLM-based Refinement
- Sửa lỗi chính tả
- Đơn giản hóa câu phức tạp
- Trích xuất nội dung cốt lõi
"""

import logging
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# ============================================================================
#                           PROMPT
# ============================================================================

SYSTEM_PROMPT = """Bạn là chuyên gia xử lý ngôn ngữ pháp luật Việt Nam.

NHIỆM VỤ:
Xử lý đoạn văn/câu hỏi của người dùng và trả về đoạn văn đã được tinh chỉnh.

QUY TẮC XỬ LÝ:

1. SỬA LỖI CHÍNH TẢ:
   Sửa lỗi đánh máy, lỗi chính tả tiếng Việt.

2. ĐƠN GIẢN HÓA CÂU:
   - Tách câu phức tạp thành các câu đơn.
   - Mỗi câu đơn ngăn cách bởi dấu chấm.
   - Mỗi câu chỉ chứa một ý chính.

3. TRÍCH XUẤT NỘI DUNG CỐT LÕI:
   - Loại bỏ từ để hỏi: "là gì", "như thế nào", "bao nhiêu", "ở đâu", "khi nào", "có...không", "ai".
   - Giữ lại: thực thể, hành động, thuộc tính quan trọng.
   - Bỏ từ đệm, từ thừa.

4. CHUẨN HÓA:
   - Đưa về dạng khẳng định (không dùng câu hỏi).
   - Dùng thuật ngữ pháp luật chuẩn.
   - Viết thường, không viết hoa đầu câu (trừ tên riêng).

CHỈ TRẢ VỀ ĐOẠN VĂN ĐÃ XỬ LÝ. KHÔNG GIẢI THÍCH."""


class LLMRefiner:
    """
    Sử dụng LLM để tinh chỉnh query

    Usage:
        refiner = LLMRefiner(api_key="your-key")
        result = refiner.refine("Thủ tục đkkd ntn?")
    """

    def __init__(
            self,
            api_key: str,
            model: str = "gpt-4o-mini",
            temperature: float = 0.1,
            max_tokens: int = 1024,
            base_url: Optional[str] = None
    ):
        """
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
            temperature: Creativity (0-1), lower = more deterministic
            max_tokens: Max output tokens
            base_url: Custom API endpoint (optional)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # OpenAI client
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)

        # Full prompt
        self.system_prompt = SYSTEM_PROMPT

        logger.info(f"LLMRefiner initialized with model: {model}")

    def refine(self, text: str) -> str:
        """
        Tinh chỉnh query

        Args:
            text: Query đã qua normalize

        Returns:
            Query đã được tinh chỉnh
        """
        if not text or not text.strip():
            return ""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result = response.choices[0].message.content

            if result:
                result = result.strip()

            if not result:
                logger.warning("LLM returned empty, using original")
                return text

            return result

        except Exception as e:
            logger.error(f"LLM error: {e}")
            return text

    def refine_batch(self, texts: list[str]) -> list[str]:
        """Tinh chỉnh nhiều queries"""
        return [self.refine(t) for t in texts]


__all__ = ["LLMRefiner", "SYSTEM_PROMPT"]