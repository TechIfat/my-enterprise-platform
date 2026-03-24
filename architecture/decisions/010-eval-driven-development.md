# ADR 010: Eval-Driven Development (EDD) and CI/CD Automation

## Context
Large Language Models exhibit non-deterministic behavior. Traditional unit testing frameworks cannot reliably validate whether a multi-agent swarm is adhering to critical compliance rules or security guardrails across prompt updates or model migrations.

## Decision
We implemented an automated Eval-Driven Development (EDD) pipeline (`src/eap/evals/run_evals.py`) utilising deterministic substring evaluation to verify critical semantic boundaries (e.g., ensuring prompt injections trigger the "SECURITY BLOCK" state).

## Reasoning
* **CI/CD Integration:** The evaluation suite utilises standard UNIX exit codes (`sys.exit(1)` on failure). This allows native integration into GitHub Actions or Jenkins, strictly preventing corrupted prompt logic from merging into the production `main` branch.
* **Regression Testing:** By maintaining a "Golden Dataset" of mandatory compliance questions and adversarial attacks, we ensure that updates to the Risk Assessor or Supervisor nodes do not degrade historical safety performance.
* **Telemetry Sync:** Because the evals run through the standard API entrypoint, all test runs are automatically captured in LangSmith, providing a visual audit trail of the CI/CD pipeline's validation process.

## Consequences & Validation
* **Role Boundary Enforcement:** During initial pipeline execution, the Evals caught a semantic overlap bug where the Market Analyst attempted to provide generic risk advice, causing the Supervisor to bypass the mandatory Vector DB compliance check. 
* **Outcome:** The CI/CD pipeline successfully blocked the deployment (`Exit Code 1`). This forced a prompt-engineering refactor to enforce strict "Role Fences" (restricting the Analyst strictly to quantitative data), after which the pipeline cleared for production. This proved the absolute necessity of EDD in multi-agent architectures.