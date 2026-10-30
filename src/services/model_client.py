# src/services/model_client.py
"""
Fine-tuned Model Client — Load and run inference on the provided model.
Supports GGUF (llama.cpp), ONNX, and Hugging Face formats.
"""
import json
import os
import httpx
from pathlib import Path
from typing import List, Dict, Optional, Any
from src.models.schemas import *
from src.config.settings import settings


class RemoteModelError(RuntimeError):
    """Raised when the configured remote model cannot complete a request."""


class FineTunedModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_type = self._detect_model_type()
        self._load_model()
    
    def _detect_model_type(self) -> str:
        """Detect model format from MODEL_PATH."""
        if (
            settings.MODEL_BACKEND.lower() == "remote"
            and settings.MODEL_API_URL
            and settings.MODEL_API_KEY
        ):
            return "remote"
        model_path = Path(settings.MODEL_PATH)
        
        # Check for GGUF
        gguf_files = list(model_path.glob("*.gguf"))
        if gguf_files:
            return "gguf"
        
        # Check for ONNX
        onnx_files = list(model_path.glob("*.onnx"))
        if onnx_files:
            return "onnx"
        
        # Check for Hugging Face
        if (model_path / "config.json").exists():
            return "hf"
        
        # Check for safetensors
        safetensor_files = list(model_path.glob("*.safetensors"))
        if safetensor_files:
            return "hf"
        
        return "unknown"
    
    def _load_model(self):
        """Load model based on detected type."""
        if self.model_type == "remote":
            print(f"Using remote AI model: {settings.MODEL_API_URL}")
            return
        model_path = Path(settings.MODEL_PATH)
        
        if self.model_type == "gguf":
            self._load_gguf(model_path)
        elif self.model_type == "onnx":
            self._load_onnx(model_path)
        elif self.model_type == "hf":
            self._load_hf(model_path)
        else:
            # Fallback: mock model for development
            print("WARNING: No model found. Using mock model for development.")
            self.model_type = "mock"
    
    def _load_gguf(self, model_path: Path):
        """Load GGUF model with llama-cpp-python."""
        try:
            from llama_cpp import Llama
            
            gguf_files = list(model_path.glob("*.gguf"))
            if not gguf_files:
                raise FileNotFoundError("No GGUF file found")
            
            model_file = gguf_files[0]  # Use first GGUF file
            
            self.model = Llama(
                model_path=str(model_file),
                n_gpu_layers=settings.MODEL_N_GPU_LAYERS,
                n_ctx=settings.MODEL_MAX_LENGTH,
                n_batch=settings.MODEL_N_BATCH,
                verbose=False
            )
            print(f"Loaded GGUF model: {model_file.name}")
            
        except ImportError:
            print("llama-cpp-python not installed. Falling back to mock.")
            self.model_type = "mock"
        except Exception as e:
            print(f"Failed to load GGUF model: {e}. Falling back to mock.")
            self.model_type = "mock"
    
    def _load_onnx(self, model_path: Path):
        """Load ONNX model with onnxruntime."""
        try:
            import onnxruntime as ort
            
            onnx_files = list(model_path.glob("*.onnx"))
            if not onnx_files:
                raise FileNotFoundError("No ONNX file found")
            
            model_file = onnx_files[0]
            
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if settings.MODEL_DEVICE == "cuda" else ["CPUExecutionProvider"]
            self.model = ort.InferenceSession(str(model_file), providers=providers)
            
            # Try to load tokenizer
            try:
                from transformers import AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            except:
                pass
            
            print(f"Loaded ONNX model: {model_file.name}")
            
        except ImportError:
            print("onnxruntime not installed. Falling back to mock.")
            self.model_type = "mock"
        except Exception as e:
            print(f"Failed to load ONNX model: {e}. Falling back to mock.")
            self.model_type = "mock"
    
    def _load_hf(self, model_path: Path):
        """Load Hugging Face model with transformers."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            
            # Quantization config for 4-bit
            if settings.MODEL_DEVICE == "cuda":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16
                )
                model_kwargs = {"quantization_config": bnb_config, "device_map": "auto"}
            else:
                model_kwargs = {"device_map": "cpu"}
            
            self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            self.model = AutoModelForCausalLM.from_pretrained(str(model_path), **model_kwargs)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print(f"Loaded HF model from: {model_path}")
            
        except ImportError:
            print("transformers/torch not installed. Falling back to mock.")
            self.model_type = "mock"
        except Exception as e:
            print(f"Failed to load HF model: {e}. Falling back to mock.")
            self.model_type = "mock"
    
    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """Generate text from prompt."""
        if self.model_type == "remote":
            return self._generate_remote(prompt, max_tokens, temperature)
        if self.model_type == "mock":
            return self._mock_generate(prompt)
        
        try:
            if self.model_type == "gguf":
                return self._generate_gguf(prompt, max_tokens, temperature)
            elif self.model_type == "onnx":
                return self._generate_onnx(prompt, max_tokens, temperature)
            elif self.model_type == "hf":
                return self._generate_hf(prompt, max_tokens, temperature)
        except RemoteModelError:
            raise
        except Exception as e:
            if self.model_type == "remote":
                raise RemoteModelError(f"Remote AI generation failed: {e}") from e
            print(f"Generation error: {e}")
            return self._mock_generate(prompt)

    def _generate_remote(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate text through the configured Colab/FastAPI model server."""
        base_url = settings.MODEL_API_URL.rstrip("/")
        headers = {}
        if settings.MODEL_API_KEY:
            headers["X-API-Key"] = settings.MODEL_API_KEY
        try:
            response = httpx.post(
                f"{base_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                headers=headers,
                timeout=settings.MODEL_API_TIMEOUT,
            )
        except httpx.TimeoutException as exc:
            raise RemoteModelError(
                "The AI interviewer took too long to respond."
            ) from exc
        except httpx.RequestError as exc:
            raise RemoteModelError(
                "The AI interviewer service is unreachable."
            ) from exc
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if response.status_code == 404:
                raise RemoteModelError(
                    "The AI interviewer service is offline or its tunnel URL has changed."
                ) from exc
            if response.status_code in {401, 403}:
                raise RemoteModelError(
                    "The AI interviewer service authorization is invalid."
                ) from exc
            raise RemoteModelError(
                "The AI interviewer rejected the request."
            ) from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise RemoteModelError("Remote AI returned an invalid response") from exc
        if not isinstance(payload, dict):
            raise RemoteModelError("Remote AI returned an invalid response")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip():
            raise RemoteModelError("Remote AI returned no generated text")
        return text.strip()
    
    def _generate_gguf(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate with llama.cpp."""
        output = self.model.create_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["<|end|>", "```"]
        )
        return output["choices"][0]["text"].strip()
    
    def _generate_onnx(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate with ONNX runtime."""
        # This is simplified - real implementation needs proper tokenization loop
        import numpy as np
        
        if self.tokenizer:
            inputs = self.tokenizer(prompt, return_tensors="np")
            input_ids = inputs["input_ids"]
            
            # Simple greedy generation (not production quality)
            for _ in range(max_tokens):
                outputs = self.model.run(None, {"input_ids": input_ids})
                logits = outputs[0]
                next_token = np.argmax(logits[0, -1, :])
                input_ids = np.concatenate([input_ids, [[next_token]]], axis=1)
                
                if next_token == self.tokenizer.eos_token_id:
                    break
            
            return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)[len(prompt):]
        else:
            return self._mock_generate(prompt)
    
    def _generate_hf(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate with Hugging Face transformers."""
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return response.strip()
    
    def _mock_generate(self, prompt: str) -> str:
        """Mock generation for development/testing."""
        # Detect task type from prompt
        if "GENERATE" in prompt.upper() and "QUESTION" in prompt.upper():
            return self._mock_questions()
        elif "EVALUATE" in prompt.upper() or "EVALUATION" in prompt.upper():
            return self._mock_evaluation()
        elif "CONFIDENCE" in prompt.upper():
            return "75\nReasoning: Moderate evidence from resume and assessment."
        return "Mock response"
    
    def _mock_questions(self) -> str:
        """Return mock questions JSON."""
        return json.dumps({
            "questions": [
                {
                    "id": "q1",
                    "type": "CODE_WALKTHROUGH",
                    "skill": "Python",
                    "prompt": "In your ecommerce-api repo, walk me through the authentication flow in api/auth.py",
                    "context": {
                        "repo": "ecommerce-api",
                        "file": "api/auth.py",
                        "code_snippet": "class JWTAuth:\n    def verify_token(self, token: str) -> dict:\n        try:\n            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])\n            return payload\n        except jwt.ExpiredSignatureError:\n            raise AuthError('Token expired')\n        except jwt.InvalidTokenError:\n            raise AuthError('Invalid token')",
                        "function": "verify_token"
                    },
                    "expected_signals": ["JWT validation", "error handling", "token refresh"]
                },
                {
                    "id": "q2",
                    "type": "ALTERNATIVE_APPROACH",
                    "skill": "Python",
                    "prompt": "You used synchronous SQLAlchemy in your models. Why not async SQLAlchemy with asyncpg?",
                    "context": {
                        "repo": "ecommerce-api",
                        "file": "models/database.py",
                        "code_snippet": "from sqlalchemy import create_engine\nfrom sqlalchemy.orm import sessionmaker\n\nengine = create_engine(DATABASE_URL)\nSessionLocal = sessionmaker(bind=engine)",
                        "function": "get_db"
                    },
                    "expected_signals": ["async benefits", "trade-offs", "migration effort"]
                },
                {
                    "id": "q3",
                    "type": "DEBUG",
                    "skill": "Python",
                    "prompt": "This function from your API has a bug when the input list is empty. Identify and fix it.",
                    "context": {
                        "repo": "ecommerce-api",
                        "file": "api/products.py",
                        "code_snippet": "def get_cheapest_product(products: List[Product]) -> Product:\n    return min(products, key=lambda p: p.price)",
                        "function": "get_cheapest_product"
                    },
                    "expected_signals": ["empty list handling", "ValueError", "default/optional return"]
                },
                {
                    "id": "q4",
                    "type": "BEHAVIORAL",
                    "skill": "Problem Solving",
                    "prompt": "Tell me about a time you encountered a difficult bug in a team project. How did you approach debugging it?",
                    "context": {},
                    "expected_signals": ["systematic debugging", "collaboration", "root cause", "prevention"]
                }
            ]
        })
    
    def _mock_evaluation(self) -> str:
        """Return mock evaluation JSON."""
        score = 0.75
        delta = 5
        
        return json.dumps({
            "score": score,
            "feedback": f"Good understanding demonstrated. {'Strong' if score > 0.7 else 'Adequate'} response with {'minor gaps' if score > 0.7 else 'some gaps'}.",
            "signals_matched": ["core concept", "practical application"],
            "signals_missed": ["edge case handling"] if score < 0.8 else [],
            "confidence_delta": delta
        })

    @staticmethod
    def _decode_first_json_value(response: str):
        """Decode the first JSON value when an instruct model adds trailing text."""
        starts = [index for index in (response.find("{"), response.find("[")) if index >= 0]
        start = min(starts) if starts else -1
        if start < 0:
            raise json.JSONDecodeError("No JSON value found", response, 0)
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(response[start:])
        return data
    
    # High-level methods for VivaEngine
    
    def generate_questions(self, context: dict, max_questions: int = 10) -> List[VivaQuestion]:
        """Generate viva questions from context."""
        prompt = self._build_question_prompt(context, max_questions)
        response = self.generate(
            prompt,
            max_tokens=settings.MODEL_GENERATION_MAX_TOKENS,
            temperature=0.3,
        )
        
        try:
            data = self._decode_first_json_value(response)
            if isinstance(data, list):
                data = {"questions": data}
            if not isinstance(data, dict):
                raise ValueError("Expected a question object or array")
            questions = []
            for q_data in data.get("questions", []):
                q_data["context"] = VivaQuestionContext(**q_data.get("context", {}))
                question_type = str(q_data["type"])
                question_type = {
                    "EXTEND": QuestionType.EXTEND_FEATURE.value,
                    "CODE_CHALLENGE": QuestionType.DEBUG.value,
                }.get(question_type.upper(), question_type)
                try:
                    q_data["type"] = QuestionType(question_type.lower())
                except ValueError:
                    q_data["type"] = QuestionType[question_type.upper()]
                questions.append(VivaQuestion(**q_data))
            return questions
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            if self.model_type == "remote":
                raise RemoteModelError(
                    "Remote AI returned an invalid question response"
                ) from exc
            return self._parse_mock_questions(response)
    
    def _build_question_prompt(self, context: dict, max_questions: int) -> str:
        """Build prompt for question generation."""
        skills_info = "\n".join([
            f"- {s['skill']}: confidence={s['confidence']:.0f}%, repo_evidence={s.get('has_repo_evidence', False)}, clone_flag={s.get('tutorial_clone_flag', False)}"
            for s in context.get("skills", [])
        ])
        
        repo_info = "\n".join([
            f"- {r['repo']}: {r['skill']} ({r['evidence_type']})"
            for r in context.get("repo_details", [])
        ])
        
        clone_info = "\n".join([
            f"- {f['repo']}: {f['type']} ({f['confidence']:.0%})"
            for f in context.get("tutorial_clone_flags", [])
        ])
        
        return f"""You are an expert technical interviewer conducting a viva for a fresher candidate.

CANDIDATE SKILLS:
{skills_info}

REPOSITORY EVIDENCE:
{repo_info if repo_info else "No repository evidence available."}

TUTORIAL CLONE FLAGS:
{clone_info if clone_info else "No tutorial clones detected."}

GENERATE {max_questions} QUESTIONS covering these types:
1. CODE_WALKTHROUGH - "Walk me through how you implemented X in repo Y"
2. ALTERNATIVE_APPROACH - "How would you handle [specific problem] differently?"
3. DEBUG - "This function has a bug when input is X. Fix it." (provide code snippet)
4. EXTEND - "Add [feature] to this module." (provide context)
5. BEHAVIORAL - STAR format situation questions for soft skills
6. KNOWLEDGE_CHECK - Conceptual questions for skills with only assessment evidence

RULES:
- Every technical question MUST reference specific files/functions from the candidate's repos
- NO generic questions (e.g., "What is OOP?")
- Questions should match the candidate's claimed skill level
- Include code snippets inline for DEBUG/EXTEND questions
- Keep each prompt under 45 words and each code snippet under 120 words
- Return compact JSON with no markdown fences or commentary
- Output as JSON array of VivaQuestion objects

OUTPUT FORMAT:
{{
  "questions": [
    {{
      "id": "q1",
      "type": "CODE_WALKTHROUGH",
      "skill": "Python",
      "prompt": "In your ecommerce-api repo, walk me through the authentication flow in api/auth.py",
      "context": {{
        "repo": "ecommerce-api",
        "file": "api/auth.py",
        "code_snippet": "class JWTAuth: ...",
        "function": "verify_token"
      }},
      "expected_signals": ["JWT validation", "error handling", "token refresh"]
    }}
  ]
}}"""
    
    def _parse_mock_questions(self, response: str) -> List[VivaQuestion]:
        """Parse mock questions if JSON fails."""
        return [
            VivaQuestion(
                id="q1", type=QuestionType.CODE_WALKTHROUGH, skill="Python",
                prompt="Walk me through your authentication implementation.",
                context=VivaQuestionContext()
            ),
            VivaQuestion(
                id="q2", type=QuestionType.BEHAVIORAL, skill="Problem Solving",
                prompt="Describe a challenging bug you fixed.",
                context=VivaQuestionContext()
            )
        ]
    
    def evaluate_response(self, question: VivaQuestion, answer: str) -> ResponseEvaluation:
        """Evaluate candidate's answer."""
        prompt = self._build_evaluation_prompt(question, answer)
        response = self.generate(prompt, max_tokens=512, temperature=0.1)
        
        try:
            data = self._decode_first_json_value(response)
            if not isinstance(data, dict):
                raise ValueError("Expected an evaluation object")
            return ResponseEvaluation(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            if self.model_type == "remote":
                raise RemoteModelError(
                    "Remote AI returned an invalid evaluation response"
                ) from exc
            import random
            return ResponseEvaluation(
                score=round(random.uniform(0.5, 0.9), 2),
                feedback="Evaluated via mock (model unavailable).",
                signals_matched=["core concept"],
                signals_missed=[],
                confidence_delta=random.randint(0, 8)
            )
    
    def _build_evaluation_prompt(self, question: VivaQuestion, answer: str) -> str:
        """Build prompt for response evaluation."""
        return f"""You are evaluating a candidate's answer to a viva question.

QUESTION:
Type: {question.type.value}
Skill: {question.skill}
Prompt: {question.prompt}
Context: {question.context.model_dump_json() if question.context else '{}'}
Expected Signals: {question.expected_signals}

CANDIDATE ANSWER:
{answer}

EVALUATE:
1. Technical correctness (0-1)
2. Depth of understanding (0-1)
3. Communication clarity (0-1)
4. Signals matched from expected_signals (list)
5. Confidence delta (-20 to +20) for the skill

OUTPUT FORMAT:
{{
  "score": 0.85,
  "feedback": "Strong understanding of JWT validation. Correctly explained RS256 vs HS256. Missed token refresh edge case.",
  "signals_matched": ["JWT validation", "error handling"],
  "signals_missed": ["token refresh"],
  "confidence_delta": 5
}}"""