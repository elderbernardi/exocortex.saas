#!/usr/bin/env python3
import os
import re
import sys
import yaml
import shutil
import argparse
import subprocess
import urllib.request
import urllib.error
import json
from pathlib import Path

# --- Configuration & Paths ---
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
EXOCORTEX_HOME = Path(os.environ.get("EXOCORTEX_HOME", Path.home() / "exocortex")).expanduser()
ACERVO = Path(os.environ.get("ACERVO", EXOCORTEX_HOME / "acervo")).expanduser()
REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# ANSI Colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
NC = "\033[0m"

# LLM Judge API settings — aligned with skill_judge.py
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
JUDGE_MODEL_PRIMARY = "deepseek-chat"  # DeepSeek V4 Pro (direct API)
JUDGE_MODEL_FALLBACK = "deepseek/deepseek-chat"  # DeepSeek via OpenRouter


def get_api_key(var_name):
    """Retrieve API key from env or .secrets files."""
    key = os.environ.get(var_name)
    if key:
        return key
    for secrets_path in [REPO_ROOT / ".secrets", Path.home() / ".secrets"]:
        if secrets_path.is_file():
            try:
                for line in secrets_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == var_name:
                            return v.strip().strip("'").strip('"')
            except Exception:
                pass
    return None


def detect_hermes_bin():
    """Locate the hermes executable."""
    if shutil.which("hermes"):
        return "hermes"
    candidates = [
        HERMES_HOME / "hermes-agent" / "venv" / "bin" / "hermes",
        HERMES_HOME / "hermes-agent" / "hermes",
        Path.home() / ".local" / "bin" / "hermes",
    ]
    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)
    return None


def parse_personalization_profile():
    """Parse SOUL.md or fallback files from acervo/macro to get personalized context."""
    soul_file = ACERVO / "macro" / "SOUL.md"
    profile = {
        "identidade": "",
        "valores": "",
        "tom": "",
        "preferencias": "",
        "limites": ""
    }

    if soul_file.is_file():
        content = soul_file.read_text(encoding="utf-8")
        
        # Regex helper to extract sections
        def extract_section(section_name):
            pattern = rf"##\s+{section_name}\s*\n(.*?)(?=\n##\s+|\Z)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else ""

        profile["identidade"] = extract_section("Identidade Raiz")
        profile["valores"] = extract_section("Valores")
        profile["tom"] = extract_section("Tom de Comunicação")
        profile["preferencias"] = extract_section("Preferências Operacionais")
        profile["limites"] = extract_section("Limites Pessoais")
    else:
        # Fallback to separate files if SOUL.md is missing
        val_file = ACERVO / "macro" / "valores.md"
        est_file = ACERVO / "macro" / "estilo.md"
        s_file = ACERVO / "macro" / "soul.md"

        if val_file.is_file():
            profile["valores"] = val_file.read_text(encoding="utf-8").strip()
        if est_file.is_file():
            profile["tom"] = est_file.read_text(encoding="utf-8").strip()
        if s_file.is_file():
            profile["identidade"] = s_file.read_text(encoding="utf-8").strip()

    return profile


def load_calibration_cases():
    """Scan all skill directories and load calibration test cases from SKILL.md files."""
    cases = []
    skill_paths = sorted(SKILLS_DIR.glob("excrtx-*/SKILL.md"))
    
    for path in skill_paths:
        try:
            content = path.read_text(encoding="utf-8")
            # Parse YAML frontmatter
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                continue
            
            fm = yaml.safe_load(fm_match.group(1)) or {}
            calibration = fm.get("metadata", {}).get("hermes", {}).get("calibration", [])
            if not calibration:
                continue

            if isinstance(calibration, dict):
                calibration = [calibration]
            
            for case in calibration:
                case["skill_name"] = path.parent.name
                cases.append(case)
        except Exception as e:
            print(f"{RED}⚠️ Error parsing skill at {path}: {e}{NC}")
            
    # Sort cases by feature ID if available
    cases.sort(key=lambda x: x.get("feature_id", "EX-99"))
    return cases


def run_hermes_command(hermes_bin, prompt, session_id=None, model_override=None):
    """Run hermes chat command and return (stdout, session_id)."""
    args = [hermes_bin, "chat", "-q", prompt, "-Q"]
    if session_id:
        args += ["-r", session_id]
    if model_override:
        args += ["-m", model_override]
        
    try:
        completed = subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False
        )
        
        stdout = completed.stdout.strip()
        
        # Extract session_id from stdout or stderr
        new_session_id = None
        session_match = re.search(r"session_id:\s*([a-zA-Z0-9_-]+)", stdout + completed.stderr)
        if session_match:
            new_session_id = session_match.group(1)
            
        return stdout, new_session_id
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Command timed out after 120 seconds", None
    except Exception as e:
        return f"ERROR: {e}", None


def call_llm_api(prompt, api_url, api_key, model):
    """Execute API call to OpenRouter or DeepSeek."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "calibrate-hermes-judge/1.0"
    }
    data = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a calibration judge checking if an AI agent meets its behavioral criteria. Respond with JSON containing 'verdict': 'PASS'|'FAIL' and 'reasoning': 'string'."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.0,
        **(({"response_format": {"type": "json_object"}} if "deepseek" in model.lower() or "deepseek.com" in api_url else {}))
    }).encode("utf-8")

    try:
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content
    except Exception as e:
        print(f"      {YELLOW}⚠️ LLM Judge call error ({model}): {e}{NC}")
        return None


def call_llm_judge(test_prompt, agent_response, criteria):
    """LLM-as-a-judge for validating calibration results."""
    openrouter_key = get_api_key("OPENROUTER_API_KEY")
    deepseek_key = get_api_key("DEEPSEEK_API_KEY")
    
    if not openrouter_key and not deepseek_key:
        return None
        
    judge_prompt = f"""Evaluate if the following Agent Response satisfies the Acceptance Criteria for the given Test Prompt.

Test Prompt:
{test_prompt}

Agent Response:
{agent_response}

Acceptance Criteria:
{criteria}

Provide a JSON response with the following keys:
- "verdict": "PASS" or "FAIL"
- "reasoning": "A concise explanation of why the response did or did not meet the criteria, highlighting any gaps."
"""

    response = None
    deepseek_key = get_api_key("DEEPSEEK_API_KEY")
    openrouter_key = get_api_key("OPENROUTER_API_KEY")

    # Primary: DeepSeek V4 Pro (direct)
    if deepseek_key:
        response = call_llm_api(judge_prompt, DEEPSEEK_API_URL, deepseek_key, JUDGE_MODEL_PRIMARY)

    # Fallback: DeepSeek via OpenRouter
    if not response and openrouter_key:
        response = call_llm_api(judge_prompt, OPENROUTER_API_URL, openrouter_key, JUDGE_MODEL_FALLBACK)

    if response:
        try:
            clean = response.strip()
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```\s*$", "", clean)
            # Handle brace-depth matching for nested JSON
            start = clean.find("{")
            if start != -1:
                depth = 0
                end = start
                for i in range(start, len(clean)):
                    if clean[i] == "{":
                        depth += 1
                    elif clean[i] == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                clean = clean[start:end]
            parsed = json.loads(clean)
            return parsed.get("verdict"), parsed.get("reasoning")
        except Exception:
            pass
            
    return None


def run_calibration_flow():
    parser = argparse.ArgumentParser(description="Smart Hermes Cognitive Calibration Suite")
    parser.add_argument("--model", type=str, default=None, help="Override Hermes LLM model")
    parser.add_argument("--all", action="store_true", help="Run all features without asking")
    parser.add_argument("--dry-run", action="store_true", help="Load and validate cases without running Hermes")
    parser.add_argument("--report", type=str, default=None, help="Save JSON results to file")
    args = parser.parse_args()

    # --- Banner ---
    print(f"{CYAN}╔══════════════════════════════════════════════════════════╗{NC}")
    print(f"{CYAN}║     🧠 EXOCÓRTEX.IA — SMART CALIBRAÇÃO DO HERMES         ║{NC}")
    print(f"{CYAN}║            Prompt-Driven Development (PDD)               ║{NC}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════╝{NC}\n")

    hermes_bin = detect_hermes_bin()
    if not hermes_bin and not args.dry_run:
        print(f"{RED}✗ Error: hermes executable not found. Use --dry-run to validate cases without Hermes.{NC}")
        sys.exit(1)

    if args.dry_run:
        print(f"{YELLOW}⚡ DRY-RUN MODE — validating calibration cases only{NC}")
    else:
        print(f"{GREEN}✓{NC} Hermes CLI:           {BOLD}{hermes_bin}{NC}")
    print(f"{GREEN}✓{NC} Acervo do Exocórtex: {BOLD}{ACERVO}{NC}")
    
    # Ingest Personalization Profile
    profile = parse_personalization_profile()
    has_profile = any(profile.values())
    if has_profile:
        print(f"{GREEN}✓{NC} Personalized Profile loaded from acervo/macro/SOUL.md")
    else:
        print(f"{YELLOW}⚠ No personalization profile found in acervo/macro/. Using defaults.{NC}")
        
    # Load Cases
    cases = load_calibration_cases()
    print(f"{GREEN}✓{NC} Loaded {BOLD}{len(cases)}{NC} calibration cases from skills.\n")

    # Dry-run mode: just validate and exit
    if args.dry_run:
        results = []
        for idx, case in enumerate(cases):
            feat_id = case.get("feature_id", "EX-??")
            skill = case.get("skill_name", "unknown")
            has_prompt = bool(case.get("test_prompt", "").strip())
            has_criteria = bool(case.get("acceptance_criteria", "").strip())
            has_remediation = bool(case.get("remediation_tip", "").strip())
            status = "✅" if (has_prompt and has_criteria and has_remediation) else "⚠️"
            print(f"  {status} [{feat_id}] {skill} — prompt={'✓' if has_prompt else '✗'} criteria={'✓' if has_criteria else '✗'} remediation={'✓' if has_remediation else '✗'}")
            results.append({
                "feature_id": feat_id,
                "skill_name": skill,
                "has_prompt": has_prompt,
                "has_criteria": has_criteria,
                "has_remediation": has_remediation,
                "valid": has_prompt and has_criteria and has_remediation,
            })
        valid = sum(1 for r in results if r["valid"])
        print(f"\n  {GREEN}{valid}/{len(results)}{NC} cases fully valid.")
        if args.report:
            Path(args.report).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Report saved to {args.report}")
        return
    
    total_passed = 0
    total_failed = 0
    
    for idx, case in enumerate(cases):
        feat_id = case.get("feature_id", "EX-??")
        skill = case.get("skill_name", "unknown")
        test_prompt = case.get("test_prompt", "")
        calib_prompt = case.get("calibration_prompt", "")
        criteria = case.get("acceptance_criteria", "")
        remediation = case.get("remediation_tip", "")
        
        print(f"{BLUE}========================================================================={NC}")
        print(f"  [{idx + 1}/{len(cases)}] Feature: {BOLD}{feat_id}{NC} — Skill: {BOLD}{skill}{NC}")
        print(f"{BLUE}========================================================================={NC}\n")
        
        if not args.all:
            opt = ""
            while opt not in ["c", "p", "q"]:
                opt = input(f"Choose: [c] Calibrate/Test | [p] Skip | [q] Quit: ").strip().lower()
            if opt == "q":
                print("\nCalibration cancelled.")
                break
            elif opt == "p":
                print(f"Skipping {feat_id}...\n")
                continue
                
        # 1. Ingest Personalization Context as the first prompt of the session
        session_id = None
        if has_profile:
            context_prompt = f"""[PERSONALIZATION CONTEXT - EXOCÓRTEX]
Use as seguintes definições personalizadas do executivo para governar suas respostas:
- Identidade: {profile['identidade']}
- Valores: {profile['valores']}
- Tom de Comunicação: {profile['tom']}
- Preferências Operacionais: {profile['preferencias']}
- Limites Pessoais: {profile['limites']}
"""
            print("1. Injecting personalization context...")
            _, session_id = run_hermes_command(hermes_bin, context_prompt, model_override=args.model)
            
        # 2. Inject PDD Calibration Prompt
        print("2. Sending cognitive calibration prompt (PDD)...")
        _, session_id = run_hermes_command(hermes_bin, calib_prompt, session_id=session_id, model_override=args.model)
        
        if not session_id:
            print(f"{RED}✗ Error: Failed to establish chat session with Hermes.{NC}\n")
            total_failed += 1
            continue
            
        print(f"{GREEN}✓{NC} Session established: {YELLOW}{session_id}{NC}\n")
        
        # 3. Run Smoke Test Prompt
        print("3. Executing Smoke Test...")
        print(f"   Query: {MAGENTA}\"{test_prompt}\"{NC}")
        
        response, _ = run_hermes_command(hermes_bin, test_prompt, session_id=session_id, model_override=args.model)
        
        # Remove session_id tags from agent output display
        clean_response = re.sub(r"^session_id:\s*[a-zA-Z0-9_-]+", "", response, flags=re.MULTILINE).strip()
        
        print(f"\n{YELLOW}┌─ AGENT RESPONSE ───────────────────────────────────────────────────────{NC}")
        print(clean_response)
        print(f"{YELLOW}└────────────────────────────────────────────────────────────────────────{NC}\n")
        
        print(f"{CYAN}Acceptance Criteria:{NC}\n   {criteria}\n")
        
        # 4. LLM Judge Assist (if keys exist)
        judge_verdict, judge_reason = None, None
        judge_assisted = False
        try:
            judge_res = call_llm_judge(test_prompt, clean_response, criteria)
            if judge_res:
                judge_verdict, judge_reason = judge_res
                judge_assisted = True
                print(f"{CYAN}🤖 LLM Judge Verdict:{NC} "
                      f"{GREEN if judge_verdict == 'PASS' else RED}{BOLD}{judge_verdict}{NC}")
                print(f"   Reasoning: {judge_reason}\n")
        except Exception:
            pass
            
        # 5. User Decision
        ans = ""
        prompt_msg = "Does the response meet the criteria? (s/n/r for retry with remediation): "
        if judge_assisted:
            prompt_msg = f"Confirm LLM Judge Verdict? [s] Accept PASS / [n] Reject/FAIL / [r] Retry with remediation: "
            
        while ans not in ["s", "n", "r"]:
            ans = input(prompt_msg).strip().lower()
            if judge_assisted and ans == "s" and judge_verdict == "FAIL":
                # If LLM said fail and user says 's' to confirm, it is a Fail
                ans = "n"
            elif judge_assisted and ans == "s" and judge_verdict == "PASS":
                ans = "s"
                
        if ans == "s":
            print(f"\n{GREEN}✓ Calibrated successfully!{NC}\n")
            total_passed += 1
            continue
            
        if ans == "r":
            # Remediation Loop
            print(f"\nSending remediation tip: {BLUE}\"{remediation}\"{NC}")
            _, _ = run_hermes_command(hermes_bin, remediation, session_id=session_id, model_override=args.model)
            
            print("Re-executing Smoke Test...")
            response, _ = run_hermes_command(hermes_bin, test_prompt, session_id=session_id, model_override=args.model)
            clean_response = re.sub(r"^session_id:\s*[a-zA-Z0-9_-]+", "", response, flags=re.MULTILINE).strip()
            
            print(f"\n{YELLOW}┌─ NEW AGENT RESPONSE ───────────────────────────────────────────────────{NC}")
            print(clean_response)
            print(f"{YELLOW}└────────────────────────────────────────────────────────────────────────{NC}\n")
            
            ans = ""
            while ans not in ["s", "n"]:
                ans = input("Does the new response meet the criteria? (s/n): ").strip().lower()
                
        if ans == "s":
            print(f"\n{GREEN}✓ Calibrated after remediation!{NC}\n")
            total_passed += 1
        else:
            print(f"\n{RED}✗ Calibration failed. Marked for manual review.{NC}\n")
            total_failed += 1
            
    # --- Summary ---
    print(f"{CYAN}╔══════════════════════════════════════════════════════════╗{NC}")
    print(f"{CYAN}║                    CALIBRATION SUMMARY                   ║{NC}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════╝{NC}")
    print(f"  Features calibrated and aligned: {GREEN}{total_passed}{NC}")
    print(f"  Features failing/marked review:   {RED}{total_failed}{NC}\n")


if __name__ == "__main__":
    run_calibration_flow()
