from itertools import product
import datetime
from tabulate import tabulate

# Define mappings
DAY_TO_INT = {
    'Pazartesi': 0,
    'Salı': 1,
    'Çarşamba': 2,
    'Perşembe': 3,
    'Cuma': 4,
}

INT_TO_DAY = {v: k for k, v in DAY_TO_INT.items()}


def parse_lectures(parse):
    lines = parse.strip().split('\n')
    lecture_list = []
    current_priority = None

    for line in lines:
        if line.isdigit():
            current_priority = int(line)
        else:
            parts = line.split('\t')
            if len(parts) != 6:
                continue

            code, name, section, day, start, end = parts
            day_int = DAY_TO_INT.get(day)
            if day_int is None:
                continue

            s_time = datetime.datetime.strptime(start, '%H:%M')
            e_time = datetime.datetime.strptime(end, '%H:%M')
            lecture_list.append({
                'priority': current_priority,
                'code': code,
                'name': name,
                'section': section,
                'day': day_int,
                'start_time': s_time,
                'end_time': e_time
            })

    return lecture_list


def overlap(lecture1, lecture2):
    if lecture1['day'] != lecture2['day']:
        return False
    return not (lecture1['end_time'] <= lecture2['start_time'] or lecture1['start_time'] >= lecture2['end_time'])


def generate_schedules(lectures):
    grouped_lectures = {}
    for lecture in lectures:
        code = lecture['code']
        if code not in grouped_lectures:
            grouped_lectures[code] = []
        grouped_lectures[code].append(lecture)

    all_combinations = list(product(*grouped_lectures.values()))
    valid_schedules = []

    for combination in all_combinations:
        # Sort lectures by priority within the combination
        sorted_combination = sorted(combination, key=lambda l: l['priority'])
        fixed_schedule = []

        for lecture in sorted_combination:
            # Check if the lecture overlaps with any already added lecture
            is_conflicting = False
            for fixed_lecture in fixed_schedule:
                if overlap(lecture, fixed_lecture):
                    is_conflicting = True
                    break

            if not is_conflicting:
                fixed_schedule.append(lecture)

        # Only add to valid_schedules if we have any lectures in the fixed_schedule
        if fixed_schedule:
            valid_schedules.append(fixed_schedule)

    # Sort schedules by the number of lectures in descending order
    valid_schedules.sort(key=len, reverse=True)

    return valid_schedules


def read_input_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def generate_hours(start_time, end_time, interval_minutes=60):
    hours = []
    current_time = start_time
    while current_time <= end_time:
        hours.append(current_time.strftime('%H:%M'))
        current_time += datetime.timedelta(minutes=interval_minutes)
    return hours


def round_up_to_next_half_hour(dt):
    # Round up to the next 30 minutes mark
    if dt.minute <= 30:
        return dt.replace(minute=30, second=0, microsecond=0)
    else:
        return (dt + datetime.timedelta(minutes=(60 - dt.minute))).replace(second=0, microsecond=0)


def create_schedule_table(schedule, start_time, end_time):
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']

    # Generate hour slots from start_time to end_time
    hours = generate_hours(start_time, end_time)

    # Create an empty table with days as columns and hours as rows
    table_data = [['' for _ in range(len(days))] for _ in range(len(hours))]

    for cls in schedule:
        day_index = cls['day']
        start_hour = cls['start_time'].time()
        end_hour = round_up_to_next_half_hour(cls['end_time']).time()

        # Find row indices for start and end times
        start_idx = hours.index(start_hour.strftime('%H:%M'))
        end_idx = hours.index(end_hour.strftime('%H:%M'))

        # Fill the table cells with class information
        for idx in range(start_idx, end_idx):
            table_data[idx][day_index] += f"{cls['code']} ({cls['section']})\n{cls['name']}\n"

    # Add the header row for days
    table_data.insert(0, days)

    return hours, table_data


def save_schedule_table_to_file(hours, table_data, title, file):
    # Prepare table data for tabulate
    table = tabulate(table_data, headers="firstrow", tablefmt="grid", showindex=hours)

    with open(file, 'a') as f:
        f.write(f"\n{title}\n")
        f.write(table)
        f.write("\n\n")



file_path = 'lectures.txt'
input_text = read_input_file(file_path)
lectures = parse_lectures(input_text)
schedules = generate_schedules(lectures)

# Table start/end time
start_time = datetime.datetime.strptime('08:30', '%H:%M')
end_time = datetime.datetime.strptime('19:30', '%H:%M')

output_file = 'schedules.txt'
open(output_file, 'w').close()

# Create and save tables for each schedule
for i, schedule in enumerate(schedules):
    hours, table_data = create_schedule_table(schedule, start_time, end_time)
    save_schedule_table_to_file(hours, table_data, f"Schedule {i + 1}", output_file)

    print(f"Schedule {i + 1}:")
    for lecture in schedule:
        day_name = INT_TO_DAY[lecture['day']]
        print(f"{lecture['code']} - {lecture['name']} ({day_name}, {lecture['start_time'].strftime('%H:%M')} to {lecture['end_time'].strftime('%H:%M')})")
    print()

print(f"Schedules have been saved to {output_file}")
