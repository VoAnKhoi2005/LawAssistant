from typing import List
import json
from core.interfaces.text_simplifier_interface import ITextSimplifier
from knowledge_graph.triplet_extraction.utils import clean_text
from openai import OpenAI


class OpenAITextSimplifier(ITextSimplifier):
    """OpenAI GPT-based text simplifier"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", system_prompt: str = None):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = system_prompt or self._default_system_prompt()
    
    async def simplify_text(self, text: str) -> List[str]:
        """Simplify text using OpenAI GPT"""
        if not text or not text.strip():
            return []
        
        cleaned_text = clean_text(text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f'Sentence need simplify: "{cleaned_text}"'}
                ]
            )
            
            raw_content = response.choices[0].message.content.strip()
            parsed = json.loads(raw_content)
            sentences = parsed.get("simplified_sentences", [])
            
            return [s.strip() for s in sentences if s.strip()]
            
        except Exception as e:
            print(f"Error in OpenAI sentence simplification: {str(e)}")
            # Fallback to basic sentence splitting
            return [s.strip() for s in text.split('.') if s.strip()]
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for Vietnamese legal text simplification"""
        return """
Role: You are a professional Legal and Linguistics AI Assistant specializing in Vietnamese law. Your task is to deconstruct complex legal texts into independent, direct simple sentences.
Objective: Transform legal clauses into standalone simple sentences. Each sentence must be a direct legal statement, avoiding introductory fillers or explanatory bridges.
Strict "Directness" Rules:
No Filler Subjects: Do not use phrases like "Một loại hành vi là..." (One type of behavior is...), "Bao gồm các loại..." (Includes types of...), or "Được xác định như sau" (Is defined as follows).
Direct Predication: Connect the main Subject directly to the specific Action or Object.
Incorrect: "Một loại hành vi vi phạm là làm sai lệch hồ sơ."
Correct: "Hành vi vi phạm quy định về hồ sơ bao gồm hành vi làm sai lệch hồ sơ." (Or simply: "Làm sai lệch hồ sơ là hành vi vi phạm quy định về hồ sơ.")
The "Simple Sentence" Constraint:
Exactly one Subject and one Predicate.
No conjunctions (và, hoặc, nhưng, mà, còn, rồi...).
No commas (,) or semicolons (;) to link clauses.
Copy Forward Context: If the input lists sub-items under a heading, integrate the full heading context into every single sub-item to ensure they are legally complete.
Output Format:
Return strictly a JSON object.
If information is insufficient: {"need_more_information": "..."}.
If successful: {"simplified_sentences": ["Direct Sentence 1.", "Direct Sentence 2."]}.
Example Transformation: Input: "Hành vi vi phạm quy định về hồ sơ địa giới bao gồm: (a) Làm sai lệch sơ đồ; (b) Làm sai lệch bảng tọa độ." Output: { "simplified_sentences": [ "Hành vi làm sai lệch sơ đồ là hành vi vi phạm quy định về hồ sơ địa giới.", "Hành vi làm sai lệch bảng tọa độ là hành vi vi phạm quy định về hồ sơ địa giới." ] }
"""
