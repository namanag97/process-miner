import csv
import datetime

with open('tests/e2e/fixtures/large_valid.csv', 'w', newline='') as csvfile:
    fieldnames = ['case_id', 'activity', 'timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(100000):
        writer.writerow({
            'case_id': f'case_{i % 1000}',
            'activity': f'Activity_{i % 10}',
            'timestamp': datetime.datetime.now().isoformat()
        })
