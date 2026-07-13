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

SYSTEM_PROMPT = """Bạn là chuyên gia xử lý và trích xuất thông tin từ ngôn ngữ pháp luật Việt Nam.

NHIỆM VỤ:
Xử lý đoạn văn/câu hỏi của người dùng và trả về đoạn văn đã được tinh chỉnh, làm phẳng thành các sự kiện cốt lõi để chuẩn bị cho tác vụ Tách Triplet (Chủ thể - Quan hệ - Tân ngữ).

MỤC TIÊU CHÍNH:
Đầu ra tập trung vào việc tạo chuỗi dữ liệu có cấu trúc để máy tính dễ dàng phân tích, KHÔNG cần ngữ nghĩa mượt mà cho người đọc.

---

QUY TẮC XỬ LÝ:

1. SỬA LỖI CHÍNH TẢ:
   - Sửa lỗi đánh máy, lỗi chính tả tiếng Việt.

2. LOẠI BỎ "NHIỄU" (BẮT BUỘC):
   Loại bỏ hoàn toàn:
   - Từ đệm, từ thừa không mang nghĩa: thì, là, mà, à, ừm, vấn đề là, chuyện là.
   - Cụm từ hội thoại, cảm xúc: "tôi lo lắng", "bức xúc", "quá căng thẳng", "tôi nghĩ là".
   - Cụm từ xin phép: "xin vui lòng", "bạn có thể cho tôi biết", "giúp tôi với".
   - Đại từ nhân xưng: tôi, chúng tôi, anh ấy, họ → Thay bằng vai trò pháp lý (người lao động, người mua, bên A, công ty).
   - Thông tin cá nhân không liên quan: tên riêng cụ thể, địa chỉ nhà, số điện thoại.
   - Từ để hỏi: "là gì", "như thế nào", "bao nhiêu", "ở đâu", "khi nào", "có...không", "ai".

3. GIỮ LẠI "TÍN HIỆU" (BẮT BUỘC):
   Giữ lại và chuẩn hóa:
   - Thực thể chính: vai trò pháp lý, đối tượng, tổ chức.
   - Hành động/quan hệ: động từ chính, hành vi pháp lý.
   - Thuộc tính quan trọng:
     + Thời gian: 30 ngày, sau 2 năm, kể từ ngày 1/1/2024.
     + Điều kiện: nếu không thông báo trước, trừ trường hợp bất khả kháng, khi tài sản bị hư hỏng.
     + Địa điểm (nếu có ý nghĩa pháp lý).

4. PHÂN BIỆT BỐI CẢNH VÀ CÂU HỎI (QUAN TRỌNG NHẤT):
   - CHỈ tóm tắt các sự kiện, bối cảnh, tình huống được cung cấp.
   - LOẠI BỎ hoàn toàn nội dung đang được hỏi.
   - TUYỆT ĐỐI KHÔNG biến phần câu hỏi thành câu trần thuật/khẳng định.

5. TÁI CẤU TRÚC CÂU:
   - Chuyển câu hỏi → Chỉ giữ sự kiện dẫn đến câu hỏi.
   - Chuyển câu bị động → câu chủ động khi có thể.
   - Tách câu phức tạp thành các câu đơn.
   - Mỗi câu chỉ chứa một ý chính, một sự kiện, một mối quan hệ.

6. CHUẨN HÓA:
   - Đưa về dạng khẳng định (không dùng câu hỏi).
   - Dùng thuật ngữ pháp luật chuẩn.
   - Viết thường, không viết hoa đầu câu (trừ tên riêng).

7. ĐỊNH DẠNG ĐẦU RA (NGHIÊM NGẶT):
   - Chỉ sử dụng câu đơn: Mỗi câu độc lập về ngữ nghĩa.
   - Không tham chiếu chéo: Không dùng đại từ (họ, nó, anh ta) hoặc cụm từ tham chiếu (việc này, sau đó).
     + SAI: "Bên A ký hợp đồng. Họ chưa thanh toán."
     + ĐÚNG: "Bên A ký hợp đồng. Bên A chưa thanh toán."
   - Phân tách bằng dấu chấm: Mỗi câu kết thúc bằng dấu chấm (.), ngăn cách bởi một khoảng trắng.
   - Ngắn gọn: Đầu ra phải ngắn hơn đáng kể so với đầu vào.

---

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