import httpx
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(300.0))  # 5 minutes timeout
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a chat completion request to Ollama
        
        Args:
            model: The model to use (e.g., "llama3.2:3b")
            messages: List of messages in OpenAI format
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            # Format request according to Ollama API
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            # Add any additional options
            if kwargs:
                payload["options"].update(kwargs)
                
            logger.info(f"Sending chat request to Ollama: {model}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            if stream:
                return await self._handle_stream_response(response)
            else:
                result = response.json()
                logger.debug(f"Ollama response: {result}")
                
                if "message" in result and "content" in result["message"]:
                    return result["message"]["content"]
                else:
                    logger.error(f"Unexpected response format: {result}")
                    return ""
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Ollama: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Ollama API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error to Ollama: {e}")
            raise Exception(f"Failed to connect to Ollama: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Ollama chat: {e}")
            raise
            
    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Send a generate request to Ollama (legacy format)
        
        Args:
            model: The model to use
            prompt: The prompt to generate from
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if kwargs:
                payload["options"].update(kwargs)
                
            logger.info(f"Sending generate request to Ollama: {model}")
            
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            if stream:
                return await self._handle_stream_response(response)
            else:
                result = response.json()
                return result.get("response", "")
                
        except Exception as e:
            logger.error(f"Error in Ollama generate: {e}")
            raise
            
    async def _handle_stream_response(self, response: httpx.Response) -> str:
        """Handle streaming response from Ollama"""
        full_response = ""
        
        async for line in response.aiter_lines():
            if line.strip():
                try:
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        full_response += chunk["message"]["content"]
                    elif "response" in chunk:
                        full_response += chunk["response"]
                except json.JSONDecodeError:
                    continue
                    
        return full_response
        
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama"""
        try:
            url = f"{self.base_url}/api/tags"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            result = response.json()
            return result.get("models", [])
            
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            raise
            
    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            url = f"{self.base_url}/api/pull"
            
            payload = {"name": model}
            
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            return False
            
    async def check_model_exists(self, model: str) -> bool:
        """Check if a model exists in Ollama"""
        try:
            models = await self.list_models()
            return any(m["name"] == model for m in models)
        except Exception:
            return False
            
    async def health_check(self) -> bool:
        """Check if Ollama is healthy and accessible"""
        try:
            models = await self.list_models()
            return True
        except Exception:
            return False
            
    async def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from a response that might contain extra text"""
        try:
            # Try to parse as direct JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
                    
            # Try to find JSON array
            start_idx = response.find('[')
            end_idx = response.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
                    
            raise ValueError("No valid JSON found in response")
            
    async def get_structured_response(
        self,
        model: str,
        prompt: str,
        response_format: str = "json",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Get a structured response from Ollama with retry logic
        
        Args:
            model: The model to use
            prompt: The prompt to send
            response_format: Expected response format (json, etc.)
            max_retries: Maximum number of retries
            
        Returns:
            Parsed structured response
        """
        system_prompt = f"""
        You are a helpful assistant that always responds in valid {response_format} format.
        Do not include any explanatory text outside of the {response_format} structure.
        Ensure your response is valid {response_format} that can be parsed.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        for attempt in range(max_retries):
            try:
                response = await self.chat(
                    model=model,
                    messages=messages,
                    temperature=0.3  # Lower temperature for more consistent structured output
                )
                
                if response_format == "json":
                    return await self.extract_json_from_response(response)
                else:
                    return {"response": response}
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Brief delay before retry
                
        raise Exception("Max retries exceeded for structured response")
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 