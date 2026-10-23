# Store application records in PostgreSQL alongside the analytical lakehouse

The reviewer application needs persistent claim records, information updates, reviewer actions, and prediction history. Use PostgreSQL for these operational records while retaining Delta tables for historical data preparation, training, and monitoring analysis. PostgreSQL supports transactions for related record changes and fits the application's record-by-record access patterns.

This introduces a second data store and requires an explicit, repeatable path from application changes into the analytical pipeline. It avoids making the browser's claim workflow depend on analytical Spark jobs. The synchronization contract and timing remain open decisions; model inference and cloud services must not be called while holding a long database transaction.
