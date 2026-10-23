# Local language-model feasibility

Status: deferred until after the local MVP, at the user's explicit direction. The later GenAI release remains required. This note preserves researched options; it does not select a model, establish benchmark results, or authorize a feasibility test during MVP work. Model and runtime selection, local tests, downloads, and summary-service implementation will be revisited after MVP completion.

## Cost and hardware facts

Using a hosted language-model API can incur usage charges. Ollama's official pricing includes running models on local hardware in its free offering. Local execution consumes the developer's hardware, electricity, and storage rather than requiring a hosted inference subscription. Ollama also supports disabling its cloud features, so a local-only deployment can explicitly exclude cloud inference.

Small local models are feasible candidates on this hardware; acceptable application performance has not been established. LM Studio's published requirements list Apple Silicon and recommend 16 GB or more RAM, illustrating that this class of hardware can support local inference. That does not establish any particular model's latency, memory use alongside other services, or ability to produce grounded claim briefs.

## Existing downloads

Read-only local checks on 2026-10-22 found Ollama client 0.31.2 and the following model listing:

| Model tag | Listed stored size |
| --- | --- |
| gemma3:4b | 3.3 GB |
| gemma4:e4b | 9.6 GB |
| qwen3.5:4b | 3.4 GB |

The version query warned that a service connection was unavailable, while the model listing succeeded. Treat service readiness as unverified. No model was loaded, no inference was run, and no download or service change was performed. Stored size is not runtime memory use. Existing tags must be resolved to exact model artifacts and their licenses before selection. The official Qwen3.5-4B model card lists Apache 2.0, but that alone does not identify the exact locally stored artifact.

## Proposed later feasibility experiment

First evaluate an existing smaller model with local-only inference, one request at a time, short structured synthetic claim records, and bounded output length. Avoid running heavy training and Kubernetes experiments concurrently. Verify artifact identity and license, then record peak resource use, response time, output-schema validity, unsupported statements, and accuracy of field citations.

The model's task is to summarize approved facts from the claim record. The predictive severity model remains a separate component trained by this project. Summary output must pass evidence checks before display; the original project already requires a deterministic fallback for failures. A template fallback is not evidence of completed GenAI functionality.

If the experiment fails, keep the GenAI delivery constraint visible and reassess models or execution options. Do not silently substitute paid inference, claim untested hardware performance, or mark the required GenAI stage complete based on a template or mock response.

## Official sources

- [Ollama pricing](https://ollama.com/pricing): local execution is included in the free offering.
- [Ollama FAQ](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features): local-only mode and disabling cloud features.
- [LM Studio system requirements](https://lmstudio.ai/docs/app/system-requirements): Apple Silicon support and 16 GB RAM recommendation.
- [Qwen3.5-4B model card](https://huggingface.co/Qwen/Qwen3.5-4B): model information and Apache 2.0 license declaration.

Sources checked on 2026-10-22. These establish available options, not measured project results.
