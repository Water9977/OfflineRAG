import os
from typing import List, Generator
# pyrefly: ignore [missing-import]
from openai import OpenAI

class LMStudioClient:
    """
    Client wrapper for LM Studio's local server APIs.
    Communicates with both the LLM (Qwen3-8B) and the Embedding Model (nomic-embed-text)
    using the standard OpenAI-compatible API protocol.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1"):
        self.base_url = base_url
        # Standard OpenAI client pointing to the local LM Studio server
        self.client = OpenAI(base_url=self.base_url, api_key="lm-studio")
        
    def get_embedding(self, text: str, model: str = "text-embedding-nomic-embed-text-v1.5@q8_0") -> List[float]:
        """
        Converts a block of text into a mathematical coordinate vector (embedding)
        using the active embedding model running in LM Studio.
        """
        try:
            # Strip newlines as they can add noise to embedding calculations
            clean_text = text.replace("\n", " ")
            response = self.client.embeddings.create(
                input=[clean_text],
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            raise ConnectionError(
                f"Failed to generate embedding from LM Studio at {self.base_url}.\n"
                f"Error: {e}\n"
                f"Please ensure LM Studio is running, the local server is started, "
                f"and '{model}' is active."
            )

    def stream_chat(self, messages: List[dict], model: str = "qwen/qwen3-8b", temperature: float = 0.2) -> Generator[str, None, None]:
        """
        Sends a list of chat messages to the local LLM (Qwen3-8B) and yields
        response tokens as they are generated in real-time (streaming).
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            raise ConnectionError(
                f"Failed to communicate with LM Studio local LLM at {self.base_url}.\n"
                f"Error: {e}\n"
                f"Please verify that LM Studio local server is active, "
                f"and '{model}' is loaded."
            )

