"""Local Spark/Delta medallion pipeline for synthetic claim data."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def create_spark_session(app_name: str = "claims-local-lakehouse") -> Any:
    """Create a small local Spark session with Delta Lake support."""
    try:
        from delta import configure_spark_with_delta_pip
        from pyspark.sql import SparkSession
    except ImportError as error:
        raise RuntimeError(
            "Spark dependencies are missing; run "
            "`uv sync --extra spark --extra training --extra dev`"
        ) from error

    builder = (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


def build_delta_lakehouse(source_dir: Path, output_dir: Path) -> dict[str, int]:
    """Build Bronze, Silver, quarantine, and point-in-time Gold Delta tables."""
    from pyspark.sql import Window
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        DoubleType,
        IntegerType,
        StringType,
        StructField,
        StructType,
        TimestampType,
    )

    spark = create_spark_session()
    policy_schema = StructType(
        [
            StructField("policy_id", StringType(), False),
            StructField("policy_start_date", TimestampType(), False),
            StructField("coverage_type", StringType(), False),
            StructField("deductible_band", StringType(), False),
            StructField("region_code", StringType(), False),
            StructField("asset_age_years", IntegerType(), False),
            StructField("annual_usage_band", StringType(), False),
        ]
    )
    claim_schema = StructType(
        [
            StructField("claim_id", StringType(), False),
            StructField("policy_id", StringType(), False),
            StructField("incident_timestamp", TimestampType(), False),
            StructField("reported_timestamp", TimestampType(), False),
            StructField("claim_type", StringType(), False),
            StructField("channel", StringType(), False),
            StructField("initial_estimate", DoubleType(), False),
            StructField("damage_indicator_count", IntegerType(), False),
            StructField("weather_category", StringType(), False),
            StructField("final_paid_amount", DoubleType(), False),
            StructField("closed_timestamp", TimestampType(), False),
        ]
    )

    policies = (
        spark.read.option("header", True)
        .schema(policy_schema)
        .csv(str(source_dir / "policies.csv"))
    )
    claims = (
        spark.read.option("header", True).schema(claim_schema).csv(str(source_dir / "claims.csv"))
    )
    bronze = output_dir / "bronze"
    policies.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        str(bronze / "policies")
    )
    claims.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        str(bronze / "claims")
    )

    valid_policy_ids = policies.select("policy_id")
    valid_condition = (
        F.col("claim_id").isNotNull()
        & F.col("policy_id").isNotNull()
        & (F.col("initial_estimate") >= 0)
        & (F.col("final_paid_amount") >= 0)
        & (F.col("reported_timestamp") >= F.col("incident_timestamp"))
        & (F.col("closed_timestamp") >= F.col("reported_timestamp"))
    )
    structurally_valid = claims.filter(valid_condition)
    silver_claims = structurally_valid.join(valid_policy_ids, "policy_id", "left_semi").select(
        *claims.columns
    )
    invalid_claims = claims.subtract(silver_claims).withColumn(
        "quarantine_reason", F.lit("invalid values, timestamps, or policy reference")
    )
    silver = output_dir / "silver"
    silver_claims.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        str(silver / "claims")
    )
    invalid_claims.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        str(silver / "quarantine_claims")
    )

    order_seconds = F.col("reported_timestamp").cast("long")
    prior_year = (
        Window.partitionBy("policy_id").orderBy(order_seconds).rangeBetween(-365 * 86_400, -1)
    )
    feature_rows = (
        silver_claims.join(policies, "policy_id", "inner")
        .withColumn("policy_tenure_days", F.datediff("reported_timestamp", "policy_start_date"))
        .withColumn(
            "reporting_delay_hours",
            (F.unix_timestamp("reported_timestamp") - F.unix_timestamp("incident_timestamp"))
            / 3600,
        )
        .withColumn("prior_claim_count_365d", F.count("claim_id").over(prior_year))
    )

    current = feature_rows.alias("current")
    previous = silver_claims.select(
        F.col("policy_id").alias("prior_policy_id"),
        F.col("reported_timestamp").alias("prior_reported_timestamp"),
        F.col("closed_timestamp").alias("prior_closed_timestamp"),
        F.col("final_paid_amount").alias("prior_final_paid_amount"),
    ).alias("previous")
    point_in_time = (
        current.join(
            previous,
            (F.col("current.policy_id") == F.col("previous.prior_policy_id"))
            & (F.col("previous.prior_reported_timestamp") < F.col("current.reported_timestamp"))
            & (
                F.col("previous.prior_reported_timestamp")
                >= F.col("current.reported_timestamp") - F.expr("INTERVAL 730 DAYS")
            )
            & (F.col("previous.prior_closed_timestamp") <= F.col("current.reported_timestamp")),
            "left",
        )
        .groupBy(*[F.col(f"current.{name}") for name in feature_rows.columns])
        .agg(
            F.coalesce(F.sum("previous.prior_final_paid_amount"), F.lit(0.0)).alias(
                "prior_paid_amount_730d"
            )
        )
    )
    gold_path = output_dir / "gold" / "claim_features"
    point_in_time.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        str(gold_path)
    )
    result = {
        "bronze_claims": claims.count(),
        "silver_claims": silver_claims.count(),
        "quarantined_claims": invalid_claims.count(),
        "gold_feature_rows": point_in_time.count(),
    }
    spark.stop()
    return result
