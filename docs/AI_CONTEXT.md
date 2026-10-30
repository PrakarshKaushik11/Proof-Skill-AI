# AI Context & Model Integration Guide
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  

---

## 1. Fine-Tuned Model Specification

### 1.1 Model Details (Provided by Team)
| Property | Value |
|----------|-------|
| **Base Model** | TBD (e.g., Llama-3-8B, Mistral-7B, CodeLlama-7B) |
| **Fine-tuning Method** | LoRA / QLoRA / Full FT |
| **Training Data** | Code Q&A, repo analysis, viva simulations |
| **Format** | GGUF (llama.cpp) / ONNX / Safetensors (HF) |
| **Context Window** | 4096 / 8192 / 16384 tokens |
| **Quantization** | 4-bit / 8-bit / FP16 |

### 1.2 Inference Requirements
```python
# src/services/model_client.py
class ModelConfig:
    model_path: str = "models/fine_tuned/"  # Directory with model files
    device: str = "cuda"                     # "cuda", "cpu", "mps"
    n_gpu_layers: int = -1                   # -1 = all layers on GPU
    n_ctx: int = 4096                        # Context window
    n_batch: int = 512                       # Batch size for prompt processing
    temperature: float = 0.3                 # Low for structured output
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    max_tokens: int = 1024                   # Max generation per call
```

### 1.3 Loading Strategy (Priority Order)
1. **GGUF + llama-cpp-python** — Fastest on CPU/GPU, lowest memory
2. **ONNX + onnxruntime** — Good cross-platform, optimized
3. **Hugging Face + transformers + accelerate** — Most flexible, needs GPU
4. **vLLM / TGI** — If running as separate inference server

---

## 2. Prompt Templates

### 2.1 Question Generation Prompt
```python
QUESTION_GEN_PROMPT = """You are an expert technical interviewer conducting a viva for a fresher candidate.

CANDIDATE PROOF CARD:
{proof_card_json}

REPOSITORY ANALYSES:
{repo_analyses_json}

GENERATE {num_questions} QUESTIONS covering these types:
1. CODE_WALKTHROUGH - "Walk me through how you implemented X in repo Y"
2. ALTERNATIVE_APPROACH - "How would you handle [specific problem] differently?"
3. DEBUG - "This function has a bug when input is X. Fix it." (provide code snippet)
4. EXTEND - "Add [feature] to this module." (provide context)
5. BEHAVIORAL - STAR format situation questions for soft skills
6. KNOWLEDGE - Conceptual questions for skills with only assessment evidence

RULES:
- Every technical question MUST reference specific files/functions from the candidate's repos
- NO generic questions (e.g., "What is OOP?")
- Questions should match the candidate's claimed skill level
- Include code snippets inline for DEBUG/EXTEND questions
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
```

### 2.2 Response Evaluation Prompt
```python
EVALUATION_PROMPT = """You are evaluating a candidate's answer to a viva question.

QUESTION:
{question_json}

CANDIDATE ANSWER:
{answer_text}

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
```

### 2.3 Skill Confidence Calibration Prompt
```python
CONFIDENCE_CALIBRATION_PROMPT = """Given evidence for a skill, compute confidence 0-100.

EVIDENCE:
{evidence_json}

SKILL: {skill_name}

WEIGHTS:
- Primary author in complex repo: 60
- Contributor in repo: 35
- Assessment score (0-100): 30 * (score/100)
- Resume claim only: 10
- Viva confirmation: +20 per strong answer, -15 per weak answer

OUTPUT: Single integer 0-100 with brief reasoning."""
```

---

## 3. Question Type Specifications

### 3.1 CODE_WALKTHROUGH
- **Trigger**: Candidate has repo evidence for skill
- **Context**: Specific file + function/class from repo analysis
- **Expected**: Architecture, data flow, design decisions, error handling
- **Follow-up**: "Why this pattern?" "How does it scale?"

### 3.2 ALTERNATIVE_APPROACH
- **Trigger**: Repo shows a specific implementation choice
- **Context**: Code snippet + "You used X. Why not Y?"
- **Expected**: Trade-offs, constraints, team context, learning
- **Examples**: 
  - "You used sync SQLAlchemy. Why not async?"
  - "You used Redux. Why not Context API?"

### 3.3 DEBUG
- **Trigger**: Any code file in repo
- **Context**: Function with intentional bug (off-by-one, null pointer, race condition, SQL injection)
- **Expected**: Identify bug, explain fix, suggest test
- **Generation**: Model creates buggy variant from real code

### 3.4 EXTEND_FEATURE
- **Trigger**: Modular, extensible code in repo
- **Context**: Interface + "Add pagination / caching / auth / logging"
- **Expected**: Design, implementation sketch, testing approach

### 3.5 BEHAVIORAL (STAR)
- **Trigger**: No repo evidence OR soft skill evaluation
- **Context**: Situation relevant to fresher experience
- **Examples**:
  - "Tell me about a time you debugged a hard issue in a team project"
  - "Describe a conflict with a teammate and how you resolved it"
  - "How did you learn a new technology for a project?"

### 3.6 KNOWLEDGE_CHECK
- **Trigger**: Only assessment evidence
- **Context**: Concept from skill taxonomy
- **Expected**: Accurate explanation, practical implications

---

## 4. Voice Pipeline Configuration

### 4.1 ElevenLabs TTS
```python
ELEVENLABS_CONFIG = {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel (clear, professional)
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    },
    "output_format": "mp3_44100_128"
}
```

**Voice Selection for Different Tones:**
| Scenario | Voice ID | Settings |
|----------|----------|----------|
| Intro/Welcome | Rachel (default) | Warm, welcoming |
| Technical Question | Antoni | Clear, precise |
| Behavioral | Domi | Conversational |
| Feedback | Brian | Encouraging, constructive |

### 4.2 Whisper STT
```python
WHISPER_CONFIG = {
    "model": "large-v3",          # Best accuracy
    "device": "cuda",             # GPU required for speed
    "compute_type": "float16",    # FP16 for speed
    "language": "en",             # Force English
    "beam_size": 5,               # Better accuracy
    "vad_filter": True,           # Voice activity detection
    "vad_parameters": {
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "max_speech_duration_s": 30
    }
}
```

**Fallback Chain:**
1. `large-v3` on CUDA (best)
2. `medium` on CUDA (faster)
3. `base` on CPU (emergency)
4. Text-only mode (if all fail)

---

## 5. Model Serving Options

### Option A: In-Process (llama-cpp-python)
```python
# Pros: Simple, no network overhead, low memory with GGUF
# Cons: Blocks Streamlit thread during generation
from llama_cpp import Llama

llm = Llama(
    model_path="models/fine_tuned/model.gguf",
    n_gpu_layers=-1,
    n_ctx=4096,
    n_batch=512,
    verbose=False
)

# Run in ThreadPoolExecutor to not block UI
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(llm.create_completion, prompt, max_tokens=1024)
    result = future.result(timeout=30)
```

### Option B: Separate Model Server (vLLM)
```bash
# Terminal 1: Start vLLM server
vllm serve models/fine_tuned/ --host 0.0.0.0 --port 8000 --gpu-memory-utilization 0.9
```

```python
# Terminal 2: Streamlit calls HTTP
import httpx

async def generate(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8000/v1/completions",
            json={"model": "fine-tuned", "prompt": prompt, "max_tokens": 1024, "temperature": 0.3},
            timeout=60
        )
        return resp.json()["choices"][0]["text"]
```
**Preferred for hackathon**: Option A (simpler deployment)

---

## 6. Prompt Engineering Guidelines

| Principle | Application |
|-----------|-------------|
| **Specificity** | Always inject candidate's actual code/file paths |
| **Structure** | Demand JSON output with strict schema |
| **Few-shot** | Include 2-3 examples in prompt for each task |
| **Chain-of-thought** | "Think step by step" for evaluation |
| **Constraint** | "NO generic questions" repeated prominently |
| **Temperature** | 0.3 for generation, 0.1 for evaluation |

---

## 7. Evaluation Metrics for Model Outputs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Question provenance | 100% | Every technical question references candidate's repo |
| JSON validity | 100% | Parseable without repair |
| Latency (question gen) | < 5s | End-to-end |
| Latency (evaluation) | < 3s | Per response |
| Hallucination rate | < 2% | Manual audit on sample |

---

## 8. Fallback Strategies

| Failure | Fallback |
|---------|----------|
| Model OOM | Switch to 4-bit GGUF, reduce n_ctx, CPU offload |
| Model timeout | Return cached/generic questions, log for retry |
| TTS failure | Browser speechSynthesis API (lower quality) |
| STT failure | Text input only mode (always available) |
| Fine-tuned model unavailable | Fallback to GPT-4o-mini via API (if key available) |

---

## 9. Testing Model Outputs

```python
# tests/test_model_prompts.py
def test_question_generation():
    proof_card = load_test_proof_card("with_github")
    questions = model.generate_questions(proof_card)
    
    assert len(questions) >= 8
    for q in questions:
        assert q.type in VALID_TYPES
        if q.type in TECHNICAL_TYPES:
            assert q.context.get("repo") is not None
            assert q.context.get("code_snippet") is not None
        assert q.id.startswith("q")

def test_evaluation_consistency():
    # Same answer should get similar score
    scores = [model.evaluate_response(q, answer) for _ in range(5)]
    assert stdev([s.score for s in scores]) < 0.05
```

---

*End of AI Context*