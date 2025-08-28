import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone

class Retriever:
    def __init__(self, api_key: str, index_name: str, region: str):
        """
        Initialize the retriever with Pinecone and BGE embeddings.
        
        Args:
            api_key: Pinecone API key
            index_name: Pinecone index name
            region: Pinecone region
        """
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        
        # Enhanced namespace weights per intent for better relevance
        self.namespace_weights = {
            'intro': {'website': 2.5, 'personal': 2.0, 'medium': 1.5},
            'technical': {'personal': 2.2, 'website': 1.8, 'medium': 1.6},
            'hr': {'personal': 2.0, 'website': 1.5, 'medium': 1.0},
            'manager': {'website': 2.0, 'medium': 1.8, 'personal': 1.5}
        }
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embeddings for the query using BGE model.
        
        Args:
            query: The query string
            
        Returns:
            List[float]: Query embedding vector
        """
        # BGE prefix for retrieval
        query_with_prefix = f"Represent this sentence for retrieval: {query}"
        embedding = self.embedding_model.encode(query_with_prefix)
        return embedding.tolist()
    
    def retrieve(self, query: str, intent: str, k_context: int = 6) -> List[Dict[str, Any]]:
        """
        Retrieve relevant snippets from Pinecone based on intent and query.
        
        Args:
            query: The user's question
            intent: The routed intent
            k_context: Number of context snippets to return
            
        Returns:
            List[Dict]: List of snippets with text, url, section
        """
        # Get namespace weights for this intent
        weights = self.namespace_weights.get(intent, self.namespace_weights['technical'])
        
        # Embed the query
        query_vector = self.embed_query(query)
        
        all_results = []
        
        # Query each namespace with appropriate weights
        for namespace, weight in weights.items():
            try:
                # Query Pinecone for this namespace
                results = self.index.query(
                    vector=query_vector,
                    namespace=namespace,
                    top_k=12,
                    include_metadata=True
                )
                
                # Process and weight results
                for match in results.matches:
                    if match.metadata:
                        all_results.append({
                            'text': match.metadata.get('text', ''),
                            'url': match.metadata.get('url', ''),
                            'section': match.metadata.get('section', ''),
                            'score': match.score * weight,
                            'namespace': namespace
                        })
            except Exception as e:
                print(f"Error querying namespace {namespace}: {e}")
                continue
        
        # Sort by weighted score and deduplicate
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplicate by URL and text similarity
        seen = set()
        unique_results = []
        
        for result in all_results:
            # Create a deduplication key
            text_preview = result['text'][:64] if result['text'] else ''
            dedup_key = (result['url'], text_preview)
            
            if dedup_key not in seen:
                seen.add(dedup_key)
                unique_results.append({
                    'text': result['text'],
                    'url': result['url'],
                    'section': result['section']
                })
                
                if len(unique_results) >= k_context:
                    break
        
        return unique_results
    
    def get_namespace_info(self) -> Dict[str, Any]:
        """
        Get information about available namespaces and their stats.
        
        Returns:
            Dict: Namespace statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return {
                'namespaces': stats.namespaces,
                'total_vector_count': stats.total_vector_count
            }
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {'namespaces': {}, 'total_vector_count': 0}
