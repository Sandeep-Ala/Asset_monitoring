import duckdb

sql = r'''SELECT * FROM (
            SELECT time_bucket(INTERVAL '10 hour', CAST(t_sampling_time AS TIMESTAMP), TIMESTAMP '2025-02-02T00:00:00Z') AS bucket_time, AVG(n_soc) AS n_soc
            FROM (
                SELECT * FROM read_parquet('D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate\year=2025\month=*\day=*\equipment=bsc\dcu=2\*.parquet')
                WHERE t_sampling_time BETWEEN '2025-03-02T00:00:00Z' AND '2025-03-10T23:59:59Z' AND n_bank=2    
            )
            GROUP BY 1
        )
        WHERE bucket_time BETWEEN '2025-03-02T00:00:00Z' AND '2025-03-10T23:59:59Z'
        ORDER BY bucket_time
'''

con = duckdb.connect(database=':memory:')
try: 
    result = con.execute(sql).fetchdf()
except Exception as e:
    print("Error:", e)
    result = None

print(result)
