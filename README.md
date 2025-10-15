# OR-Tools Shift Scheduler

A shift scheduling system using Google OR-Tools to generate monthly schedules with configurable workforce and flexible constraints.

## Features

- **Configurable Workers**: 3-10 workers with flexible scheduling patterns
- **4 Shift Types**: 
  - 7h-16h (Morning)
  - 15h-00h (Evening) 
  - 00h-08h (Night)
  - 9h-21h (Extended) - Not available on Sundays
- **Flexible Coverage**: 1-4 workers per shift
- **Pattern Options**: Strict 4+2 pattern or flexible scheduling
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

- **Working Pattern**: **MANDATORY** 4 consecutive working days followed by 2 rest days
- **Configurable Coverage**: 1 worker per shift (minimum 4 workers total)
- **Working Days**: Configurable min/max working days per week (1-7 days)
- **Shift Consistency**: **MANDATORY** - Workers maintain the same shift during their working period until they rest (can change shift after rest days)
- **Sunday Restrictions**: Only 3 shifts available on Sundays (7h-16h, 15h-00h, 00h-08h)
- **No Full Week Off**: Workers cannot have 7 consecutive days off

## Recommended Configurations

- ✅ **4 workers, 1 per shift**: High success rate
- ✅ **5 workers, 1 per shift**: Good balance
- ✅ **8 workers, 2 per shift**: Full coverage
- ❌ **5 workers, 2 per shift**: Not viable (insufficient workers)
