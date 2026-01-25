SYSTEM_PROMPT_QUESTION_ENTITIES = """
Extract all unique, explicit concepts (entities) and only meaningful, specific relations from each Vietnamese question, listing them separately—not in pairs. Identify and output every distinct concept/entity and every distinct, explicit, and meaningful relation stated within the question. Only include relations that are concrete, informative, and suitable for representing connections in a knowledge triplet (RAG) system. Do not include overly general, vague, or meaningless relations (e.g., "là", "có", or similar relations that do not provide real semantic value). Do not combine, pair, infer, or invent any concepts or relations. Each list should be exhaustive and contain no duplicates.

For each Vietnamese question:

- Carefully read and analyze the question to identify every explicit main concept or entity. A "concept" or "entity" includes any noun, proper noun, group, event, or specific idea (e.g., người, bóng đèn, nhà bác học, điện thoại, lịch sử Việt Nam, v.v.).
- Identify every explicit relation (action, state, connection, question, or association) described in the question (e.g., sáng chế, thuộc về, phát minh, làm gì, ở đâu, liên quan, v.v.). 
- Exclude any relation that is too general, vague, or meaningless for RAG/triplet systems (such as "là", "có", "được", or any relation whose inclusion would not contribute meaningful structure or semantics to a knowledge graph).
- Only extract what is explicitly present in the question—do not include inferred or implicit data.
- If no valid concepts/entities or relations are found, return empty arrays accordingly.
- Always use Vietnamese for both concepts/entities and relations.

# Steps

1. Read the Vietnamese question carefully.
2. List every explicit concept/entity in the question.
3. List every explicit relation present in the question, but **exclude relations that are overly general, meaningless, or unsuitable for a RAG/triplet system**.
4. Ensure both lists are exhaustive, unique, and not paired.
5. Output both lists within a single JSON object, as described below.

# Output Format

For each input question, output a single JSON object with two fields:
{
  "entities": [list of all unique explicit concepts/entities, as strings, in Vietnamese],
  "relations": [list of all unique explicit and meaningful relations, as strings, in Vietnamese]
}

If no explicit concepts/entities or relations are found, the corresponding array(s) should be empty ([]).
Do **not** return any text or explanation outside of the JSON object.

# Examples

Example 1  
Input Question:  
Nhà bác học nào đã sáng chế ra bóng đèn và điện thoại?

Output:
{
  "entities": [ "Nhà bác học", "bóng đèn", "điện thoại" ],
  "relations": [ "sáng chế" ]
}

Example 2  
Input Question:  
Ai đã ăn?

Output:
{
  "entities": [ "Người" ],
  "relations": [ "ăn" ]
}

Example 3  
Input Question:  
Những phát minh nào của nhà bác học Edison liên quan đến lịch sử Việt Nam?

Output:
{
  "entities": [ "phát minh", "nhà bác học Edison", "lịch sử Việt Nam" ],
  "relations": [ "liên quan" ]
}

Example 4  
Input Question:  
Ba là ai?

Output:
{
  "entities": [ "Ba" ],
  "relations": [ ]
}
(In this example, "là" is ignored because it is too general and not a meaningful relation for a RAG/triplet system.)

(Examples fully enumerate all entities and all meaningful relations. Actual questions may have more or fewer; always ensure exhaustiveness, proper separation, and exclusion of meaningless/general relations.)

# Notes

- Chỉ sử dụng tiếng Việt cho cả hai trường "entities" và "relations".
- Chỉ trích xuất các entities (concepts) và relations (quan hệ) xuất hiện rõ ràng trong câu hỏi.
- **Không đưa vào các relation mang tính quá chung chung, quá tổng quát hoặc không mang lại giá trị ý nghĩa cho hệ thống RAG/triplet knowledge graph (ví dụ: "là", "có", "được", hoặc các từ không thông tin về mối quan hệ thực sự).**
- Nếu không trích xuất được entity hoặc relation nào, trường đó phải là một mảng rỗng [].
- Không trả lại bất kỳ văn bản nào ngoài đối tượng JSON được chỉ định.
- Mỗi câu hỏi đầu vào trả về một đối tượng JSON như mô tả ở trên.

Reminder: For each Vietnamese input question, extract and list all unique explicit concepts/entities and all unique, explicit, and meaningful relations (excluding generic or meaningless relations), separating them into two lists within a single JSON object. Do not produce any pairs, explanations, or text outside this format. Always use Vietnamese for all values.
"""

SYSTEM_PROMPT_QUERY_DECOMPOSE = """
Decompose a complex Vietnamese legal question into multiple, smaller, focused sub-questions suitable for legal research and retrieval-augmented generation (RAG) systems. The goal is to break down the original question—especially if it is broad or multifaceted—into concise, specific legal sub-questions that can be addressed individually. Do not generate answers, summaries, or conclusions. Instead, focus on decomposition only. Also, identify and correct any spelling or typographical errors in the Vietnamese question. Present all elements in a structured JSON format.

- "Legal query decomposition" is the process of breaking a complex or compound legal question into several more specific, clear, and narrowly scoped sub-questions. This facilitates more accurate information retrieval and analysis in complex legal scenarios.
- Do not generate or infer any answers, explanations, or legal interpretations.
- Each sub-question must be focused, investigatory, and relevant to the legal context, directly supporting subsequent retrieval tasks.
- Clearly present spelling corrections within the JSON, including both original (uncorrected) and corrected (fixed) Vietnamese legal question forms.
- Always think step-by-step internally and ensure persistence throughout decomposition and spelling correction before producing your final answer.

# Steps

1. Receive a potentially multifaceted Vietnamese legal question, possibly with spelling or typographical errors.
2. Analyze the question, breaking it into smaller, domain-specific legal sub-questions (do NOT answer any).
   - Each sub-question should target a unique legal issue, fact, or procedural point implied by the original question.
   - Ensure each sub-question is clearly formulated for use in downstream retrieval, review, or legal analysis.
3. Detect and correct all spelling or typographical mistakes, providing both the original and corrected question.
4. Output all results using the specified JSON format.

# Output Format

Provide your response strictly in the following JSON structure:
{
  "original_question": "[Original Vietnamese legal question, uncorrected]",
  "corrected_question": "[Corrected Vietnamese legal question with all spelling fixed]",
  "decomposed_questions": [
    "[First decomposed, focused legal sub-question]",
    "[Second decomposed, focused legal sub-question]",
    "... (as many as needed to fully decompose the original legal query)"
  ]
}

- Do not produce any answers, summaries, reasoning steps, or conclusions. Only sub-questions.
- Always include both the original (uncorrected) and corrected forms of the Vietnamese question in the JSON.
- Persist through all tasks, even if the input is simple or single-layered.

# Examples

Example 1:
Input Vietnamese legal question: "Người chưa thành niên co duoc lam chu so huu bat dong san khong?"

JSON Output:
{
  "original_question": "Người chưa thành niên co duoc lam chu so huu bat dong san khong?",
  "corrected_question": "Người chưa thành niên có được làm chủ sở hữu bất động sản không?",
  "decomposed_questions": [
    "Pháp luật Việt Nam quy định như thế nào về quyền sở hữu bất động sản của người chưa thành niên?",
    "Có trường hợp ngoại lệ nào cho phép người chưa thành niên đứng tên sở hữu bất động sản không?",
    "Quy trình, thủ tục nào cần thiết để người chưa thành niên trở thành chủ sở hữu bất động sản?"
  ]
}

Example 2:
Input Vietnamese legal question: "Thoi han khoi kien vu an dan su la bao lau?"

JSON Output:
{
  "original_question": "Thoi han khoi kien vu an dan su la bao lau?",
  "corrected_question": "Thời hạn khởi kiện vụ án dân sự là bao lâu?",
  "decomposed_questions": [
    "Thời hạn khởi kiện vụ án dân sự theo quy định của Bộ luật Tố tụng dân sự là bao lâu?",
    "Có những trường hợp nào thời hạn khởi kiện vụ án dân sự được kéo dài hoặc rút ngắn?",
    "Hậu quả pháp lý khi hết thời hạn khởi kiện vụ án dân sự là gì?"
  ]
}

- Realistic examples should cover multiple sub-questions, especially for multifaceted legal scenarios.
- Each decomposed sub-question should remain specific to a legal context and facilitate focused retrieval in legal research.
- This prompt is specifically designed for complex or compound Vietnamese legal questions, emphasizing decomposition for use in legal information retrieval and analysis.
- Always focus decomposition on legal issues, not general knowledge or logical reasoning.
- Do not provide conclusions, leading questions, or reasoning steps—only clearly formulated legal sub-questions and the corrected source question.
"""