import csv
from typing import List

cols = {
    "motionRotationRateX(rad/s)": "rotation_x",
    "motionRotationRateY(rad/s)": "rotation_y",
    "motionRotationRateZ(rad/s)": "rotation_z",
    "motionUserAccelerationX(G)": "acceleration_x",
    "motionUserAccelerationY(G)": "acceleration_y",
    "motionUserAccelerationZ(G)": "acceleration_z",
    "sessionId": "session_id",
    "activity": "activity"
}


for k in [list(cols.keys())]:
    print(k)
# [list(cols.keys())].rename(cols)

with open('test.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            print(f'\t{row[0]} has {row[1]} {row[2]} {row[2]} {row[2]}.')
            line_count += 1
    print(f'Processed {line_count} lines.')