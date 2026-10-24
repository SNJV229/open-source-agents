# API Contract Drift Agent

An autonomous AI agent designed for microservice ecosystems to eliminate silent interface failures by analyzing backend controller code against OpenAPI/Swagger specifications.

## The Problem

In distributed microservice architectures, backend endpoints change rapidly. Developers rename fields, introduce enum constraints, or alter HTTP verb mappings in controller code without updating the corresponding OpenAPI schemas. Downstream consumer teams (frontends, third-party microservices) continue deserializing against outdated schemas, resulting in breaking runtime incidents in production.

## Features

- **AST & Semantic Analysis**: Evaluates route annotations and return models against OpenAPI definitions.
- **Categorized Severity**: Flags issues as `BREAKING`, `WARNING`, or `INFO`.
- **Automated Spec Patching**: Suggests JSON/YAML patch blocks to bring the OpenAPI spec back into sync with production code.
- **CI/CD Friendly**: Outputs formatted terminal summaries and exports `drift_report.md` for PR checks.

## Security & Guardrails

To prevent common agent attack vectors and ensure safe deployment in enterprise CI/CD environments, this agent enforces three layers of defense:

1. **Pre-Execution Scanning**:
   - **Secret Leak Prevention**: Rejects processing if source files contain credentials (e.g., Bearer tokens, private keys, AWS secrets) to prevent accidental exfiltration to external models.
   - **Path Traversal Defense**: Enforces path resolution bounds and limits single-file input payloads to <=256 KB.
   - **Prompt Injection Defense**: Evaluates input code comments for adversarial system override sequences before sending requests to the API.

2. **Model Safeguards**:
   - **Prompt Encapsulation**: Analyzed code and spec definitions are isolated inside strict `<analyzed_artifacts>` boundaries.
   - **Safety Filters**: Configured with strict harm blocking thresholds.
   - **Deterministic Decoding**: Runs with `temperature=0.0` for repeatable contract evaluation.

3. **Post-Execution Output Validation**:
   - **Schema Adherence**: Responses are strictly typed against Pydantic models.
   - **Patch Syntax Validator**: Validates suggested OpenAPI patches for structural JSON/YAML syntax before saving to disk.

## Prerequisites

- Python 3.10+
- A Google Gemini API key

## Installation

```bash
cd agents/api-contract-drift-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and supply your GEMINI_API_KEY