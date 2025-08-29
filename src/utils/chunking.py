import re
from typing import List, Literal, Tuple

class TextProcessor:
    """
    A class to chunk text using different strategies, accepting the text 
    during the function call.
    """

    def _chunk_by_characters(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Chunks the text based on a fixed number of characters.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def _chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunks the text into individual sentences.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, 
                   text: str, 
                   strategy: Literal["char", "sentence"], 
                   chunk_size: int = 500, 
                   overlap: int = 50) -> List[str]:
        """
        Chunks the given text based on the specified strategy.
        
        Args:
            text (str): The raw text to be processed.
            strategy (Literal["char", "sentence"]): The chunking strategy to use.
                                                     "char" for character-based.
                                                     "sentence" for sentence-based.
            chunk_size (int): The maximum size of a chunk for character-based strategy.
            overlap (int): The number of characters to overlap between chunks (for character-based).
        
        Returns:
            List[str]: The list of chunks.
        
        Raises:
            ValueError: If an unknown chunking strategy is provided.
        """
        if strategy == "char":
            return self._chunk_by_characters(text, chunk_size, overlap)
        elif strategy == "sentence":
            return self._chunk_by_sentences(text)
        else:
            raise ValueError(f"Unknown chunking strategy '{strategy}'. Please use 'char' or 'sentence'.")