from typing import List
from core.interfaces.text_simplifier_interface import ITextSimplifier


class BasicTextSimplifier(ITextSimplifier):
    """Fallback text simplifier using basic sentence splitting"""
    
    async def simplify_text(self, text: str) -> List[str]:
        """Simple sentence splitting as fallback"""
        if not text or not text.strip():
            return []
        
        # Basic sentence splitting by period
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return sentences
