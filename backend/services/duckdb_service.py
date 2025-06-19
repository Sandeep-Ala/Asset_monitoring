# services/duckdb_service.py

import duckdb
from config import BASE_PARQUET_PATH
import os
from datetime import datetime

def get_window_unit(FromDate: str, ToDate: str) -> str:
    """Calculate resampling window period for time-series data."""
    max_points = 100
    start = datetime.fromisoformat(FromDate.replace("Z", "+00:00"))
    end = datetime.fromisoformat(ToDate.replace("Z", "+00:00"))
    duration = (end - start) / max_points

    days, seconds = duration.days, duration.seconds
    hours, minutes = divmod(seconds, 3600)
    minutes, seconds = divmod(minutes, 60)

    parts = [
        f"{days}D" if days else "",
        f"{hours}h" if hours else "",
        f"{minutes}min" if minutes else "",
        f"{seconds}s" if seconds else "",
    ]
    return duration.seconds, "".join(filter(None, parts))

def query_parquet_data(filters):
    # Build wildcard path
    path_parts = [
        f"year={filters.year if filters.year else '*'}",
        f"month={str(filters.month).zfill(2) if filters.month else '*'}",
        f"day={str(filters.day).zfill(2) if filters.day else '*'}",
        f"equipment={filters.equipment if filters.equipment else '*'}",
        f"dcu={filters.dcu if filters.dcu else '*'}",
        "*.parquet"
    ]
    query_path = os.path.join(BASE_PARQUET_PATH, *path_parts)

    con = duckdb.connect(database=':memory:')

    selected_metrics = filters.metrics if filters.metrics else ["*"]

    # Build dynamic WHERE clause
    base_conditions = [
        f"t_sampling_time BETWEEN '{filters.start_time}' AND '{filters.end_time}'"
    ]
    if filters.where_args:
        base_conditions.extend(filters.where_args)

    where_clause = " AND ".join(base_conditions)

    # Determine time bucket
    if not filters.window_period:
        window_seconds = get_window_unit(filters.start_time, filters.end_time)
        bucket_expr = f"time_bucket(INTERVAL '{window_seconds} seconds', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{filters.start_time}') AS bucket_time"
    else:
        bucket_expr = f"time_bucket(INTERVAL '{filters.window_period}', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '{filters.start_time}') AS bucket_time"

    # Build SELECT expressions
    select_exprs = ", ".join(
        [f"AVG({metric}) AS {metric}" for metric in selected_metrics if metric != "t_sampling_time"]
    )

    # Final SQL
    sql = f"""
        SELECT * FROM (
            SELECT {bucket_expr}, {select_exprs}
            FROM (
                SELECT * FROM read_parquet('{query_path}')
                WHERE {where_clause}
            )
            GROUP BY 1
        )
        WHERE bucket_time BETWEEN '{filters.start_time}' AND '{filters.end_time}'
        ORDER BY bucket_time
    """

    print(sql)
    result = con.execute(sql).fetchdf()

    # Round numeric columns (skip bool)
    for col in selected_metrics:
        if col != "t_sampling_time" and col in result.columns:
            if result[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                result[col] = result[col].round(2)

    con.close()
    return result
