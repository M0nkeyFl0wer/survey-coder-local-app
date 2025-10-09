"""
Classification service extracted from the original app.py.
Handles AI-powered survey response classification and codebook generation.
"""

import pandas as pd
from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models.survey_models import (
    Codebook, Code, ClassificationOutput, ClassificationEvidence,
    BatchClassificationOutput, BatchItem, UncoveredReview
)

# Constants from original app
BATCH_SIZE = 64
MAX_CONCURRENCY = 8

class ClassificationService:
    """Service for AI-powered survey response classification."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    def generate_structured_codebook(self, question: str, examples: List[str], 
                                   model: str = "gpt-4o") -> Optional[Codebook]:
        """Generate a structured codebook from survey responses.
        
        Args:
            question: The survey question
            examples: List of example responses
            model: OpenAI model to use
            
        Returns:
            Generated Codebook or None if failed
        """
        example_str = "\\n".join([f'"{ex}"' for ex in examples])
        prompt = f"""Analyze the survey question and responses to create a thematic codebook.
        **Question:** "{question}" **Responses:**\\n[{example_str}]\\n

        Identify themes, define a code and description for each, and select 3-5 verbatim examples. Include an "Other" code."""
        
        return self._call_openai_api(
            "You are an expert survey analyst.",
            prompt,
            model=model,
            pydantic_model=Codebook
        )
    
    def classify_response(self, question: str, response: str, codebook_text: str,
                         model: str = "gpt-4o-mini", multi_label: bool = False,
                         include_explanation: bool = True) -> Optional[ClassificationOutput]:
        """Classify a single response against a codebook.
        
        Args:
            question: The survey question
            response: Response to classify
            codebook_text: Codebook as text
            model: OpenAI model to use
            multi_label: Whether to allow multiple labels
            include_explanation: Whether to include explanations
            
        Returns:
            ClassificationOutput or None if failed
        """
        if multi_label:
            prompt = self._classify_response_prompt_multi(
                question, response, codebook_text, include_explanation
            )
            system_msg = "You are a multi-label survey coding assistant."
        else:
            prompt = self._classify_response_prompt(
                question, response, codebook_text, include_explanation
            )
            system_msg = "You are a survey coding assistant."
        
        return self._call_openai_api(
            system_msg, prompt, model=model, pydantic_model=ClassificationOutput
        )
    
    def classify_batch(self, question: str, responses: List[str], codebook_text: str,
                      model: str = "gpt-4o-mini", multi_label: bool = False,
                      include_explanation: bool = True) -> List[Dict[str, Any]]:
        """Classify a batch of responses.
        
        Args:
            question: The survey question
            responses: List of responses to classify
            codebook_text: Codebook as text
            model: OpenAI model to use
            multi_label: Whether to allow multiple labels
            include_explanation: Whether to include explanations
            
        Returns:
            List of classification results
        """
        if not responses:
            return []
        
        indexed = "\\n".join([f"[{i}] \\\"{resp}\\\"" for i, resp in enumerate(responses)])
        system_msg = "You are a survey coding assistant."
        explanation_field = ', "explanation": string' if include_explanation else ''
        explanation_note = '' if include_explanation else '\\nDo NOT include an "explanation" field.'
        single_rule = 'For single-label, each items list MUST contain exactly one item.' if not multi_label else ''
        
        prompt = f"""Analyze the indexed responses against the codebook.
Question: "{question}"
Codebook:\\n---\\n{codebook_text}\\n---
Responses (indexed):\\n{indexed}
Return ONLY JSON with this schema:
{{
  "results": [
    {{ "index": number, "items": [ {{ "label": string, "fragment": string, "pertinence": number (0-1){explanation_field} }} ] }}
  ]
}}{explanation_note}
{single_rule}
For uncovered responses, use an empty list for items.
"""
        
        parsed = self._call_openai_api(
            system_msg, prompt, model=model, pydantic_model=BatchClassificationOutput
        )
        
        # Build aligned results list
        aligned: List[Dict[str, Any]] = [{
            "Assigned Code": "No Code Applied", 
            "Details": []
        } for _ in responses]
        
        if not parsed or not parsed.results:
            return aligned
        
        for item in parsed.results:
            if not isinstance(item.index, int) or item.index < 0 or item.index >= len(responses):
                continue
            
            labels = [ev.label for ev in (item.items or [])]
            label_str = " | ".join(labels) if labels else "No Code Applied"
            details = [{
                "label": ev.label,
                "fragment": ev.fragment,
                "pertinence": ev.pertinence,
                "explanation": ev.explanation if include_explanation else None
            } for ev in (item.items or [])]
            
            aligned[item.index] = {
                "Assigned Code": label_str,
                "Details": details
            }
        
        return aligned
    
    def classify_batches_async(self, question: str, batched_responses: List[List[str]],
                              codebook_text: str, model: str = "gpt-4o-mini",
                              multi_label: bool = False, include_explanation: bool = True) -> List[List[Dict]]:
        """Classify multiple batches asynchronously.
        
        Args:
            question: The survey question
            batched_responses: List of response batches
            codebook_text: Codebook as text
            model: OpenAI model to use
            multi_label: Whether to allow multiple labels
            include_explanation: Whether to include explanations
            
        Returns:
            List of batch results
        """
        if not batched_responses:
            return []
        
        results: List[List[Dict]] = [None] * len(batched_responses)  # type: ignore
        
        def worker(idx: int, batch: List[str]) -> tuple[int, List[Dict]]:
            return idx, self.classify_batch(
                question, batch, codebook_text, model, multi_label, include_explanation
            )
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
            future_to_idx = {
                executor.submit(worker, i, b): i 
                for i, b in enumerate(batched_responses)
            }
            for future in as_completed(future_to_idx):
                i, res = future.result()
                results[i] = res
        
        return results
    
    def merge_codebooks(self, base_codebook: Codebook, new_codebook: Codebook,
                       user_instructions: str = "", model: str = "gpt-4o") -> Optional[Codebook]:
        """Merge two codebooks using LLM.
        
        Args:
            base_codebook: Base codebook
            new_codebook: New codebook to merge
            user_instructions: Additional merge instructions
            model: OpenAI model to use
            
        Returns:
            Merged Codebook or None if failed
        """
        prompt = self._create_merge_prompt(
            self._serialize_codebook_for_prompt(base_codebook),
            self._serialize_codebook_for_prompt(new_codebook),
            user_instructions
        )
        prompt += "\\n\\nReturn ONLY a JSON object with this exact schema: { \\\"codes\\\": [ { \\\"code\\\": string, \\\"description\\\": string, \\\"examples\\\": string[] } ] }"
        
        return self._call_openai_api(
            "You are a master survey analyst.",
            prompt,
            model=model,
            pydantic_model=Codebook
        )
    
    def reconstruct_codebook_text(self, codebook: Codebook) -> str:
        """Convert codebook to text format for prompts.
        
        Args:
            codebook: Codebook object
            
        Returns:
            Text representation of codebook
        """
        if not codebook or not codebook.codes:
            return ""
        
        return "\\n".join([
            f"- Code: {item.code}\\n  Description: {item.description}"
            for item in codebook.codes
        ]).strip()
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str,
                        model: str = "gpt-4o", pydantic_model=None):
        """Make API call to OpenAI.
        
        Args:
            system_prompt: System message
            user_prompt: User message
            model: Model to use
            pydantic_model: Pydantic model for structured output
            
        Returns:
            Parsed response or None if failed
        """
        try:
            if pydantic_model:
                completion = self.client.chat.completions.parse(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=pydantic_model
                )
                return completion.choices[0].message.parsed
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    def _classify_response_prompt(self, question: str, response: str, codebook_text: str,
                                 include_explanation: bool = True) -> str:
        """Generate prompt for single-label classification."""
        explanation_field = ', "explanation": string' if include_explanation else ''
        explanation_note = '' if include_explanation else '\\n    Do NOT include an "explanation" field.'
        
        return f"""Classify the response based on the codebook. Choose the single best code and provide evidence.
Question: "{question}"
Codebook:\\n---\\n{codebook_text}\\n---
Response: "{response}"
Return ONLY a JSON object with this schema:
{{
  "items": [
    {{ "label": string, "fragment": string, "pertinence": number (0-1){explanation_field} }}
  ]
}}{explanation_note}
For single-label, the list MUST contain exactly one item.
"""
    
    def _classify_response_prompt_multi(self, question: str, response: str, codebook_text: str,
                                       include_explanation: bool = True) -> str:
        """Generate prompt for multi-label classification."""
        explanation_field = ', "explanation": string' if include_explanation else ''
        explanation_note = '' if include_explanation else '\\n    Do NOT include an "explanation" field.'
        
        return f"""Analyze the response and identify ALL themes from the codebook that are present.
Question: "{question}"
Codebook:\\n---\\n{codebook_text}\\n---
Response: "{response}"
Return ONLY a JSON object with this schema:
{{
  "items": [
    {{ "label": string, "fragment": string, "pertinence": number (0-1){explanation_field} }}
  ]
}}{explanation_note}
If no codes apply, return {{ "items": [] }}.
"""
    
    def _create_merge_prompt(self, codebook1_json: str, codebook2_json: str,
                           user_instructions: str = "") -> str:
        """Create merge prompt for codebooks."""
        prompt = f"""You are a master survey analyst consolidating two codebooks. Your goal is to create the most accurate final codebook.
**Codebook A:**\\n{codebook1_json}\\n**Codebook B:**\\n{codebook2_json}\\n

**Analytical Process:**
1.  Identify codes with similar themes.
2.  For similar codes, examine their `examples` and evaluate if it possible to separate the example into two more distinct code. If they are truly redundant, consolidate them.
3.  Retain unique codes. Each code have to refer to an unique concept."""
        
        if user_instructions:
            prompt += f"""\\n\\n**CRITICAL USER INSTRUCTIONS:**\\nYou MUST follow these instructions. They override general guidance.\\n---\\n{user_instructions}\\n---"""
        
        return prompt
    
    def _serialize_codebook_for_prompt(self, codebook: Codebook) -> str:
        """Serialize codebook for prompt use."""
        try:
            payload = {
                "codes": [
                    {
                        "code": c.code,
                        "description": c.description,
                        "examples": c.examples or []
                    } for c in (codebook.codes or [])
                ]
            }
            return json.dumps(payload, indent=2)
        except Exception:
            return codebook.model_dump_json(indent=2)
    
    @staticmethod
    def chunk_list(items: List[str], size: int) -> List[List[str]]:
        """Split list into chunks of specified size."""
        return [items[i:i+size] for i in range(0, len(items), size)]