from typing import List, Dict, Any

class ContextPacker:
    def __init__(self, char_limit: int = 1200):
        """
        Initialize the context packer.
        
        Args:
            char_limit: Maximum characters for the packed context
        """
        self.char_limit = char_limit
    
    def pack(self, snippets: List[Dict[str, Any]], char_limit: int = None) -> str:
        """
        Pack snippets into numbered context blocks.
        
        Args:
            snippets: List of snippets with text, url, section
            char_limit: Override default character limit
            
        Returns:
            str: Formatted context string with numbered blocks
        """
        if char_limit is None:
            char_limit = self.char_limit
        
        if not snippets:
            return "No relevant context found."
        
        packed_context = []
        current_length = 0
        
        for i, snippet in enumerate(snippets, 1):
            text = snippet.get('text', '')
            url = snippet.get('url', '')
            section = snippet.get('section', '')
            
            if not text:
                continue
            
            # Truncate text if it would exceed char limit
            remaining_chars = char_limit - current_length
            if remaining_chars <= 0:
                break
            
            # Format the block
            if len(text) > remaining_chars:
                text = text[:remaining_chars].rsplit(' ', 1)[0] + "..."
            
            # Create the numbered block with better formatting
            if section:
                block = f"[{i}] {text}\n(source: {url}, section: {section})"
            else:
                block = f"[{i}] {text}\n(source: {url})"
            
            # Add namespace info for better context
            if hasattr(snippet, 'namespace') and snippet.get('namespace'):
                block += f" [namespace: {snippet['namespace']}]"
            
            packed_context.append(block)
            current_length += len(block) + 1  # +1 for newline
        
        return "\n\n".join(packed_context)
    
    def pack_with_metadata(self, snippets: List[Dict[str, Any]], char_limit: int = None) -> Dict[str, Any]:
        """
        Pack snippets and return with metadata about the packing process.
        
        Args:
            snippets: List of snippets with text, url, section
            char_limit: Override default character limit
            
        Returns:
            Dict: Packed context and metadata
        """
        packed_text = self.pack(snippets, char_limit)
        
        # Calculate statistics
        total_snippets = len(snippets)
        used_snippets = len([line for line in packed_text.split('\n') if line.startswith('[')])
        total_chars = len(packed_text)
        
        return {
            'context': packed_text,
            'metadata': {
                'total_snippets': total_snippets,
                'used_snippets': used_snippets,
                'total_chars': total_chars,
                'char_limit': char_limit or self.char_limit,
                'utilization': total_chars / (char_limit or self.char_limit) if char_limit else 1.0
            }
        }
    
    def estimate_packing(self, snippets: List[Dict[str, Any]], char_limit: int = None) -> Dict[str, Any]:
        """
        Estimate how many snippets can fit within the character limit.
        
        Args:
            snippets: List of snippets to estimate
            char_limit: Character limit to estimate against
            
        Returns:
            Dict: Estimation results
        """
        if char_limit is None:
            char_limit = self.char_limit
        
        estimated_snippets = []
        current_length = 0
        
        for i, snippet in enumerate(snippets):
            text = snippet.get('text', '')
            url = snippet.get('url', '')
            section = snippet.get('section', '')
            
            # Estimate block size
            block_size = len(f"[{i+1}] {text}\n(source: {url})")
            if section:
                block_size = len(f"[{i+1}] {text}\n(source: {url}, section: {section})")
            
            if current_length + block_size <= char_limit:
                estimated_snippets.append(snippet)
                current_length += block_size
            else:
                break
        
        return {
            'estimated_snippets': len(estimated_snippets),
            'estimated_chars': current_length,
            'char_limit': char_limit,
            'efficiency': current_length / char_limit if char_limit > 0 else 0
        }
