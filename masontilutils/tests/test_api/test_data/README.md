# Test Data for PerplexitySonarExecutiveAPI

This directory should contain a CSV file named `companies.csv` with the following columns:

- `company_name`: Name of the company
- `city`: City where the company is located
- `state`: State where the company is located
- `contact`: Name of the known executive/contact person (for comparison)

## Example Format

```csv
company_name,city,state,contact
Acme Corp,San Francisco,CA,John Smith
XYZ Inc,New York,NY,Jane Doe
```

## Notes

1. The test will compare the API's executive search results with the known contacts in the CSV file
2. Names are compared case-insensitively
3. The test will skip companies where the contact field is empty
4. Make sure to use real company data for accurate testing
5. Do not commit actual company data to version control

## Usage

1. Create your CSV file with the required columns
2. Place it in this directory as `companies.csv`
3. Run the tests:
   ```bash
   python -m unittest masontilutils/tests/test_executive_api.py
   ``` 