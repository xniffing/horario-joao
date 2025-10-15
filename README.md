# OR-Tools Shift Scheduler

A shift scheduling system using Google OR-Tools to generate monthly schedules for 5 workers across 4 shift types.

## Features

- **5 Workers**: Each worker follows a 4-days-on, 2-days-off pattern
- **4 Shift Types**: 
  - 7h-16h (Morning)
  - 15h-00h (Evening) 
  - 00h-08h (Night)
  - 9h-21h (Extended) - Not available on Sundays
- **Coverage**: 2 workers per shift
- **Monthly Generation**: Generate schedules for any calendar month
- **Streamlit Interface**: Interactive web interface for schedule generation and visualization

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Select month/year and generate schedule

## Constraints

- Each worker works 4 consecutive days, then 2 days off
- Workers maintain the same shift type during their 4-day blocks
- Exactly 2 workers assigned to each shift
- Sunday restrictions: Only 3 shifts available (7h-16h, 15h-00h, 00h-08h)
- No worker can have a full week off
