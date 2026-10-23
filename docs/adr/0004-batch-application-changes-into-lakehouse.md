# Transfer application changes into the lakehouse in batches

The reviewer application saves operational changes immediately in PostgreSQL. Transfer those changes into Bronze, Silver, and Gold through a repeatable batch job, triggered with a documented command locally and schedulable in later environments. Model training remains a separate deliberate action.

This keeps interactive claim updates independent of Spark execution and provides a reproducible application-to-training path. Analytical data becomes available after a completed batch rather than immediately after each save. Continuous change-data capture or streaming would add operational complexity before the project needs lower analytical latency. The change-export contract, checkpointing, and recovery mechanism will be specified during pipeline design.
