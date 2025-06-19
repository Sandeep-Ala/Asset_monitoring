import glob
import os

pattern = r'D:\Asset Monitoring System\Data-Backup\site=UK_Tollgate\year=2025\month=*\day=*\equipment=*\dcu=*\*.parquet'
files = glob.glob(pattern)

months = set()
days = set()
dcu=set()
for path in files:
    parts = path.split(os.sep)
    
    for part in parts:
        if part.startswith('month='):
            months.add(part)
        elif part.startswith('equipment='):
            days.add(part)
        elif part.startswith('dcu='):
            dcu.add(part)

print("Months found:", sorted(months))
print("equipment found:", sorted(days))
print("dcu found:", sorted(days))

