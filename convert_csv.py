import csv
import sys
import argparse
from datetime import datetime
from collections import defaultdict

# Global variables for argparse arguments
args = None

def parse_args():
    global args
    parser = argparse.ArgumentParser(description="Process CSV file and output family information.")
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--start', type=int, default=1, help='Start processing from Nth record')
    parser.add_argument('--end', type=int, default=float('inf'), help='End processing at Mth record')
    parser.add_argument('--local-city', default='Jackson', help='Local city name (default: Jackson)')
    parser.add_argument('--local-state', default='MN', help='Local state code (default: MN)')
    parser.add_argument('--local-zip', default='56143', help='Local ZIP code (default: 56143)')
    parser.add_argument('input_file', help='Input CSV file')
    args = parser.parse_args()

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        return None

def get_age(age_str):
    if not age_str:
        return 18
    try:
        return int(age_str)
    except ValueError:
        return 18

def determine_primary_adult(family_members):
    head = next((m for m in family_members if m['Family Role'] == 'Head of Household'), None)
    if head:
        return head

    adults = [m for m in family_members if m['Family Role'] in ['Adult', 'Spouse']]
    if not adults:
        return None

    # Sort adults by age (oldest first) and then by gender (male first)
    adults.sort(key=lambda m: (get_age(m['Age']), m['Gender'] == 'Female'), reverse=True)
    return adults[0]

def determine_second_adult(family_members, primary_adult):
    spouse = next((m for m in family_members if m['Family Role'] == 'Spouse'), None)
    if spouse and spouse != primary_adult:
        return spouse

    adults = [m for m in family_members if m['Family Role'] == 'Adult' and m != primary_adult]
    if adults:
        return adults[0]

    return None

def process_csv(input_file):
    families = defaultdict(list)
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, 1):
            if i < args.start:
                continue
            if i > args.end:
                break

            if args.debug:
                print(f"Processing record {i}: {row}", file=sys.stderr)

            family_id = row['Family']
            families[family_id].append({
                'Breeze ID': row['Breeze ID'],
                'First Name': row['First Name'].strip(),
                'Last Name': row['Last Name'].strip(),
                'Nickname': row['Nickname'].strip(),
                'Gender': row['Gender'],
                'Birthdate': parse_date(row['Birthdate']),
                'Age': get_age(row['Age']),
                'Family Role': row['Family Role'],
                'Mobile': row['Mobile'].strip(),
                'Home': row['Home'].strip(),
                'Street Address': row['Street Address'].strip(),
                'City': row['City'].strip(),
                'State': row['State'].strip(),
                'Zip': row['Zip'].strip()
            })

    return families

def format_name(member):
    name = f"{member['Last Name']}, {member['First Name']}"
    if member['Nickname']:
        name += f" ({member['Nickname']})"
    return name

def format_family(family_members):
    primary_adult = determine_primary_adult(family_members)
    if not primary_adult:
        return []

    second_adult = determine_second_adult(family_members, primary_adult)
    dependents = [m for m in family_members if m not in [primary_adult, second_adult]]

    lines = []

    # First line
    if second_adult:
        if primary_adult['Last Name'] == second_adult['Last Name']:
            first_line = f"{primary_adult['Last Name']}, {primary_adult['First Name']} & {second_adult['First Name']}"
        else:
            first_line = f"{primary_adult['Last Name']}, {primary_adult['First Name']} and {second_adult['First Name']} {second_adult['Last Name']}"

        if primary_adult['Nickname']:
            first_line = first_line.replace(primary_adult['First Name'], f"{primary_adult['First Name']} ({primary_adult['Nickname']})")
        if second_adult['Nickname']:
            first_line = first_line.replace(second_adult['First Name'], f"{second_adult['First Name']} ({second_adult['Nickname']})")
    else:
        first_line = format_name(primary_adult)

    address = primary_adult['Street Address']
    if primary_adult['City'].lower() != args.local_city.lower() or \
       primary_adult['State'].lower() != args.local_state.lower() or \
       primary_adult['Zip'] != args.local_zip:
        address += f", {primary_adult['City']}, {primary_adult['State']} {primary_adult['Zip']}"

    # Collect all unique phone numbers for the family
    all_phone_numbers = set()
    phone_numbers = []

    # Process primary adult's phone numbers
    if primary_adult['Mobile'] and primary_adult['Age'] >= 18:
        if second_adult:
            phone = f"{primary_adult['Mobile']} ({primary_adult['Nickname'] or primary_adult['First Name']})"
        else:
            phone = f"{primary_adult['Mobile']} (C)"
        if primary_adult['Mobile'] not in all_phone_numbers:
            all_phone_numbers.add(primary_adult['Mobile'])
            phone_numbers.append(phone)

    if primary_adult['Home'] and primary_adult['Age'] >= 18:
        phone = primary_adult['Home']
        # Only add (H) if there are other phone numbers
        if primary_adult['Mobile'] or (second_adult and (second_adult['Mobile'] or second_adult['Home'])) or \
           any(d['Mobile'] or d['Home'] for d in dependents if d['Age'] >= 18):
            phone += " (H)"
        if primary_adult['Home'] not in all_phone_numbers:
            all_phone_numbers.add(primary_adult['Home'])
            phone_numbers.append(phone)

    # Process second adult's phone numbers
    if second_adult and second_adult['Age'] >= 18:
        if second_adult['Mobile']:
            phone = f"{second_adult['Mobile']} ({second_adult['Nickname'] or second_adult['First Name']})"
            if second_adult['Mobile'] not in all_phone_numbers:
                all_phone_numbers.add(second_adult['Mobile'])
                phone_numbers.append(phone)

        if second_adult['Home']:
            phone = f"{second_adult['Home']} (H)"
            if second_adult['Home'] not in all_phone_numbers:
                all_phone_numbers.add(second_adult['Home'])
                phone_numbers.append(phone)

    # Process dependents' phone numbers
    for dependent in dependents:
        if dependent['Age'] >= 18:
            if dependent['Mobile']:
                phone = f"{dependent['Mobile']} ({dependent['Nickname'] or dependent['First Name']})"
                if dependent['Mobile'] not in all_phone_numbers:
                    all_phone_numbers.add(dependent['Mobile'])
                    phone_numbers.append(phone)

            if dependent['Home']:
                phone = f"{dependent['Home']} (H)"
                if dependent['Home'] not in all_phone_numbers:
                    all_phone_numbers.add(dependent['Home'])
                    phone_numbers.append(phone)

    first_line_with_phone = f"{first_line}\t{address}\t{phone_numbers[0] if phone_numbers else ''}"
    lines.append(first_line_with_phone)

    # Second line (if there are dependents)
    if dependents:
        dependent_names = ", ".join(m['First Name'] for m in dependents)
        second_line_with_phone = f"{dependent_names}\t\t{phone_numbers[1] if len(phone_numbers) > 1 else ''}"
        lines.append(second_line_with_phone)

    # Additional lines for remaining phone numbers
    for phone in phone_numbers[2:]:
        lines.append(f"\t\t{phone}")

    return lines

def main():
    parse_args()
    families = process_csv(args.input_file)

    # Process families and create grouped output
    grouped_output = []
    for family_members in families.values():
        family_lines = format_family(family_members)
        if family_lines:
            # Use the first line (which contains the primary adult) for sorting
            sort_key = get_sort_key(family_lines[0])
            grouped_output.append((sort_key, family_lines))

    # Sort the grouped output
    grouped_output.sort(key=lambda x: x[0])

    # Print the sorted output
    for _, family_lines in grouped_output:
        print("<BREAK>".join(family_lines))

def get_sort_key(line):
    name_part = line.split('\t')[0]
    parts = name_part.split(', ')
    if len(parts) < 2:
        return ('', '')  # Handle unexpected format

    last_name = parts[0]
    first_name_part = parts[1]

    if '&' in first_name_part:
        first_name = first_name_part.split(' & ')[0]
    else:
        first_name = first_name_part

    # Remove any nickname in parentheses
    first_name = first_name.split(' (')[0]

    return (last_name, first_name)

if __name__ == "__main__":
    main()
