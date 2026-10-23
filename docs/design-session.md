# Design interview record

This records confirmed direction from the design interview. It is not implementation evidence. The repository currently contains a project plan and design documentation; application code has not been built.

## Purpose and delivery

- Primary learning targets: ML Engineer and MLOps/ML Platform Engineer, with supporting data, cloud, DevOps, and SRE skills.
- Build and verify a complete local data-to-prediction MVP before cloud deployment.
- Train the project's own baseline and candidate models using synthetic data.
- Later capabilities remain required, delivered through separate releases rather than one combined completion gate.
- No fixed deadline; development follows the user's available time.
- Avoid personal spending. Use local tools, Databricks Free Edition where supported, and carefully bounded AWS credit-funded validation where feasible.
- The normal local startup launches the web application, application database, prediction service, and login service. Training, detailed monitoring, and Kubernetes experiments have separate documented start/stop commands and resource profiles.
- Collect measured results and supporting evidence throughout development.
- Produce a final report in simple language explaining concepts, implementation choices, alternatives, evidence, failure modes, interview discussion, and the actual AWS stack used.

## Application and documentation

- Build one proper web application using React, TypeScript, and Vite, connected to the FastAPI backend. Do not use Streamlit.
- The application shows claims, severity predictions, review priority, explanations, and prediction history. A grounded brief follows with the later GenAI release.
- Provide detailed operational metrics in Grafana and document access rather than building a second custom dashboard.
- Use the root README as the navigation hub for startup commands, application and metrics access, and clearly labeled documentation links. Add folder documentation where useful.
- Keep the first data-to-prediction milestone focused on the API; the web application follows as required work.
- The application serves internal claims reviewers working with synthetic policyholders.
- Confirmed screens: searchable claim queue, claim details, and prediction history showing what information changed and when estimates were produced.
- Include preloaded synthetic claims and forms to create demonstration claims and add information to existing claims.
- Use local PostgreSQL for application claim records, updates, reviewer actions, and prediction history; Delta remains the historical preparation and analytical store.
- Transfer saved application changes to Bronze/Silver/Gold through a repeatable batch job, manually triggered locally and schedulable later. Saving a claim does not wait for Spark, and training remains a separate deliberate action.
- Reviewers can record a chosen review priority and a reason while preserving the system recommendation separately. Reviewer choices do not automatically become model-training labels.
- Reviewers save changed claim information before explicitly selecting Update prediction. Show when saved information has changed since the last successful prediction.
- A new prediction preserves the reviewer-selected priority and reason. Show any disagreement with the new system recommendation so the reviewer can reconsider it.
- If prediction fails, retain saved claim information and the last successful prediction, identify the failed attempt, and provide Retry. Label older predictions with their date and the information they used; never present an unsuccessful attempt as a new prediction.
- The first web release includes login with pre-created demonstration reviewer accounts and attributes updates and decisions to an account.
- Use self-hosted Keycloak locally for the login service, integrating through OIDC. No paid identity subscription or hosted third-party login service is required. It uses local CPU, memory, and storage; a later cloud deployment has its own resource costs.
- Role boundaries, session handling, and the remaining review actions are unresolved. See the access-control design for accepted scope and proposals.
- The user provisionally accepted the three proposed application roles but requested a simpler explanation of access control. Separate model-governance identities are not yet accepted. The project has one human operator; different demonstration accounts would illustrate permissions rather than imply separate employees or independent approval.
- The first web application uses a shared synthetic claim queue for reviewers. Individual claim assignments and assignment-based access restrictions are a later learning stage; do not require them for the first web release.

## Domain and operations

- Focus on synthetic personal motor-insurance claims.
- Predict eventual final paid amount; derive human-review priority through transparent rules.
- Initial predictions are informational; meaningful new information can lead to later predictions while preserving history.
- Train using sufficiently mature closed claims with known final paid amounts.
- Treat priority as a recommendation and require evaluation and approval before replacing deployed models.
- Approve a new candidate model through a documented engineering command locally, and later an approval-gated deployment workflow where available. The sole operator reviews evaluation evidence and explicitly approves activation; lack of cloud deployment does not remove the manual approval step. Claims review remains in the web application. Exact permission separation remains unresolved.
- Cap synthetic traffic and storage and isolate local failure experiments, since simulated requests consume real resources.
- Provide named, guided synthetic scenarios for a new claim, new evidence, reviewer disagreement, and a prediction-service failure followed by retry. Each scenario includes instructions, expected behavior, and evidence to capture.
- The GenAI release remains required after the MVP. Explicitly defer language-model selection, runtime selection, local feasibility tests, downloads, and summary-service implementation until the local MVP is complete. These decisions do not block MVP development. The user requested evidence that local language models can operate without a paid third-party service and expressed concern about hardware feasibility. See the local LLM feasibility note; no model has been selected or benchmarked for this project.

## Interview continuity

### Local environment facts checked during design

On 2026-10-22, read-only checks reported Apple Silicon with 8 CPU cores, 16 GB RAM, and approximately 27 GiB of available disk space. Docker's client is installed, but sandbox restrictions prevented checking the daemon or its allocated memory. A Java runtime was unavailable; kind, Helm, and Terraform were not on PATH. These are observations to recheck at setup, not proof that any project workflow runs. Prefer bounded datasets and phased service profiles; exact resource limits remain to be measured.

A read-only follow-up found an installed Ollama client (0.31.2). Its model listing reported gemma3:4b (3.3 GB), gemma4:e4b (9.6 GB), and qwen3.5:4b (3.4 GB). A version query warned about connecting to the service, so service status remains uncertain despite the successful listing. Listed model sizes are not inference RAM requirements. No inference, service startup, installations, or model downloads were performed.

The interrupted wording of questions Q32-Q37 was unavailable when the session resumed. Their numeric answers have not been used to infer additional decisions. The reconstructed Q38-Q42 were explicitly accepted together.
