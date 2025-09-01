import re
from typing import List, Literal

class TextProcessor:
    """A class to chunk text using different strategies."""

    def _chunk_by_characters(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk the text based on a fixed number of characters.
        
        Args:
            text: The text to chunk.
            chunk_size: Maximum size of each chunk.
            overlap: Number of characters to overlap between chunks.
            
        Returns:
            List of text chunks.
        """
        chunks: List[str] = []
        start: int = 0
        while start < len(text):
            end: int = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk the text into individual sentences.
        
        Args:
            text: The text to chunk.
            
        Returns:
            List of sentences.
        """
        sentences: List[str] = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, 
                   text: str, 
                   strategy: Literal["char", "sentence"], 
                   chunk_size: int = 500, 
                   overlap: int = 50) -> List[str]:
        """Chunk the given text based on the specified strategy.
        
        Args:
            text: The raw text to be processed.
            strategy: The chunking strategy to use ("char" or "sentence").
            chunk_size: The maximum size of a chunk for character-based strategy.
            overlap: The number of characters to overlap between chunks.
        
        Returns:
            The list of chunks.
        
        Raises:
            ValueError: If an unknown chunking strategy is provided.
        """
        if strategy == "char":
            return self._chunk_by_characters(text, chunk_size, overlap)
        elif strategy == "sentence":
            return self._chunk_by_sentences(text)
        else:
            raise ValueError(f"Unknown chunking strategy '{strategy}'. Please use 'char' or 'sentence'.")