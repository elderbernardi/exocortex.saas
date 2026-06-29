Issue: Make Acervo MCP validation stricter by treating warnings as errors
Description:
Updated the validation scripts for Acervo Cognitivo to make the validation stricter by converting warnings to errors. This ensures that issues are caught early in the development process rather than being allowed as warnings.

Changes Made:
1. validate_log.py: Converted all validation warnings to errors (L-001 through L-030)
2. validate_frontmatter.py: Converted specific warnings to errors as requested:
   - V-004: Body should be non-empty
   - V-022: Title > 200 characters
   - V-025: Description should not contain newlines  
   - V-026: Description > 120 characters
   - V-072: promoted_at + class volátil
   - V-075: confidence should be low/medium/high
3. Updated test fixtures to include proper frontmatter in LOG_TEMPLATE
4. Verified all related tests pass

Verification:
- All related tests pass (test_acervo_semantic_core.py, test_acervo_ctl.py, test_acervo_mcp_server.py, test_docbrain_to_acervo.py, test_migrate_frontmatter.py)
- Manual validation confirms warnings are now treated as errors
- The validation can now be used as a strict gate in CI/CD pipelines

Related to: Issue #114 (DocBrain runtime) and Issue #121 (Acervo MCP Control Plane)

