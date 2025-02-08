# Directory Builder

A Python script to process a CSV file containing church member information from BreezeCHMS and generate a formatted directory.

## Usage

```bash
python directory_builder.py [--debug] [--start N] [--end M] input.csv
```

- `--debug`: Enable debug output to STDERR
- `--start N`: Start processing from the Nth record
- `--end M`: End processing at the Mth record
- `input.csv`: Input CSV file containing member information

## Notice

This is mostly AI generated slop, but you can use it as a starting point?

## Input Format

The input CSV file should have the following columns:

- Breeze ID
- First Name
- Last Name
- Nickname
- Gender
- Birthdate (MM/DD/YYYY format)
- Age
- Family
- Family Role
- Mobile
- Home
- Street Address
- City
- State
- Zip

## Output Format

The output is emitted to STDOUT in the following format:

- Sorted alphabetically by last name, then first name of the primary adult
- Each family's information is separated by a line break
- Within a family, lines are separated by `<BREAK>`
- Each line contains up to three tab-separated fields:
  1. Names:
     - Primary adult: `Lastname, Firstname`
     - Primary & secondary adults (same last name): `Lastname, Primary_Firstname & Secondary_Firstname`
     - Primary & secondary adults (different last names): `Primary_Lastname, Primary_Firstname and Secondary_Firstname Secondary_Lastname`
     - Dependents: Comma-separated list of first names
     - Nicknames are included in parentheses after first names
  2. Address of primary adult (full address if not in Jackson, MN or zip 56143)
  3. Phone numbers (one per line) for family members 18+:
     - For single adult families: `(C)` after mobile, `(H)` after home
     - For multiple adult families: Adult's nickname (or first name) in parentheses after their mobile number

## Dependencies

- Python 3.x
- No external libraries required (uses built-in `csv`, `sys`, `argparse`, `datetime`, and `collections`)

## Example Output

```
Doe, Jonathan (Johnny) & Jane<TAB>123 Any St.<TAB>(123) 555-1212 (Johnny)
Anna, Bradley, Charlene, Delilah<TAB><TAB>(123) 555-2121 (Jane)<BREAK><TAB><TAB>(123) 555-3333 (Anna)

Johnson, Mary<TAB>123 Main St., Anytown, ST 12345<TAB>(123) 456-7890 (C)
```

## Notes

- Families are grouped by the `Family` column in the input CSV
- Primary adult is determined by `Family Role` and age/gender when necessary
- Ages are converted to integers (default to 18 if missing or invalid)
- Only mobile and home phone numbers are included in the output
