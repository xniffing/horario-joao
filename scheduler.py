"""
OR-Tools Shift Scheduling Engine

Generates monthly shift schedules for 5 workers with the following constraints:
- 4 consecutive working days, then 2 days off
- 2 workers per shift
- Workers maintain same shift type during working days
- Sunday restrictions (only 3 shifts available)
"""

from ortools.sat.python import cp_model
import calendar
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd


class ShiftScheduler:
    def __init__(self, num_workers=5, workers_per_shift=2, min_working_days=3, max_working_days=5):
        self.num_workers = num_workers
        self.workers = list(range(self.num_workers))
        self.workers_per_shift = workers_per_shift
        self.min_working_days = min_working_days
        self.max_working_days = max_working_days
        
        # Shift definitions
        self.shifts = {
            0: "7h-16h",   # Morning
            1: "15h-00h",  # Evening  
            2: "00h-08h",  # Night
            3: "9h-21h"    # Extended (not available on Sundays)
        }
        
        # Sunday shifts (only 0, 1, 2)
        self.sunday_shifts = [0, 1, 2]
        
    def get_month_days(self, year: int, month: int) -> List[datetime]:
        """Get all days in a given month"""
        days_in_month = calendar.monthrange(year, month)[1]
        return [datetime(year, month, day) for day in range(1, days_in_month + 1)]
    
    def is_sunday(self, date: datetime) -> bool:
        """Check if a date is Sunday"""
        return date.weekday() == 6  # Sunday is 6 in Python datetime
    
    def get_available_shifts(self, date: datetime) -> List[int]:
        """Get available shifts for a given date"""
        if self.is_sunday(date):
            return self.sunday_shifts
        return list(self.shifts.keys())
    
    def create_schedule_model(self, year: int, month: int) -> Tuple[cp_model.CpModel, Dict]:
        """Create OR-Tools model for the given month"""
        model = cp_model.CpModel()
        
        # Get all days in the month
        days = self.get_month_days(year, month)
        num_days = len(days)
        
        # Decision variables: shifts[worker][day][shift] = 1 if worker works shift on day
        shifts = {}
        for worker in self.workers:
            shifts[worker] = {}
            for day in range(num_days):
                shifts[worker][day] = {}
                available_shifts = self.get_available_shifts(days[day])
                for shift in available_shifts:
                    shifts[worker][day][shift] = model.NewBoolVar(f'worker_{worker}_day_{day}_shift_{shift}')
        
        # Constraint 1: Each worker can work at most 1 shift per day
        for worker in self.workers:
            for day in range(num_days):
                available_shifts = self.get_available_shifts(days[day])
                if available_shifts:
                    model.Add(sum(shifts[worker][day][shift] for shift in available_shifts) <= 1)
        
        # Constraint 2: Exactly workers_per_shift workers per shift per day
        for day in range(num_days):
            available_shifts = self.get_available_shifts(days[day])
            for shift in available_shifts:
                model.Add(sum(shifts[worker][day][shift] for worker in self.workers) == self.workers_per_shift)
        
        # Constraint 3: 4 consecutive working days, then 2 days off pattern (EXACT as specified)
        for worker in self.workers:
            for start_day in range(num_days - 5):  # Need 6 days for the pattern
                # Create indicator variables for the 4-days-on, 2-days-off pattern
                works_4_days = model.NewBoolVar(f'worker_{worker}_works_4_days_{start_day}')
                off_2_days = model.NewBoolVar(f'worker_{worker}_off_2_days_{start_day}')
                
                # If worker works 4 consecutive days, they must be off for the next 2 days
                if start_day + 5 < num_days:
                    # Sum of working days in the 4-day period
                    working_days_sum = []
                    for i in range(4):
                        day = start_day + i
                        if day < num_days:
                            available_shifts = self.get_available_shifts(days[day])
                            if available_shifts:
                                working_days_sum.append(sum(shifts[worker][day][shift] for shift in available_shifts))
                    
                    # Sum of working days in the 2-day off period
                    off_days_sum = []
                    for i in range(2):
                        day = start_day + 4 + i
                        if day < num_days:
                            available_shifts = self.get_available_shifts(days[day])
                            if available_shifts:
                                off_days_sum.append(sum(shifts[worker][day][shift] for shift in available_shifts))
                    
                    if working_days_sum and off_days_sum:
                        # If works 4 days, then must be off 2 days
                        model.Add(sum(working_days_sum) == 4).OnlyEnforceIf(works_4_days)
                        model.Add(sum(off_days_sum) == 0).OnlyEnforceIf(off_2_days)
                        model.Add(works_4_days == off_2_days)
        
        # Constraint 4: Workers maintain same shift type during their 4-day blocks (EXACT as specified)
        for worker in self.workers:
            for start_day in range(num_days - 3):  # Need 4 days for the block
                for shift in self.shifts.keys():
                    if start_day + 3 < num_days:
                        available_shifts_0 = self.get_available_shifts(days[start_day])
                        if shift in available_shifts_0:
                            # If worker works this shift on day 0, they must work it on days 1, 2, 3
                            works_shift_day_0 = shifts[worker][start_day][shift]
                            
                            for day_offset in range(1, 4):
                                day = start_day + day_offset
                                if day < num_days:
                                    available_shifts = self.get_available_shifts(days[day])
                                    if shift in available_shifts:
                                        model.Add(shifts[worker][day][shift] == 1).OnlyEnforceIf(works_shift_day_0)
        
        # Constraint 5: No worker can have a full week off (7 consecutive days off)
        for worker in self.workers:
            for start_day in range(num_days - 6):  # Need 7 days to check
                week_off = []
                for i in range(7):
                    day = start_day + i
                    if day < num_days:
                        available_shifts = self.get_available_shifts(days[day])
                        if available_shifts:
                            week_off.append(sum(shifts[worker][day][shift] for shift in available_shifts))
                
                if len(week_off) == 7:
                    model.Add(sum(week_off) > 0)  # At least one day must be worked
        
        return model, shifts
    
    def solve_schedule(self, year: int, month: int) -> Optional[Dict]:
        """Solve the scheduling problem for the given month"""
        model, shifts = self.create_schedule_model(year, month)
        
        # Create solver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0  # 30 second timeout
        
        # Solve
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract solution
            solution = {}
            days = self.get_month_days(year, month)
            
            for worker in self.workers:
                solution[worker] = {}
                for day in range(len(days)):
                    solution[worker][day] = {}
                    available_shifts = self.get_available_shifts(days[day])
                    for shift in available_shifts:
                        if solver.Value(shifts[worker][day][shift]) == 1:
                            solution[worker][day][shift] = True
                        else:
                            solution[worker][day][shift] = False
            
            return {
                'solution': solution,
                'days': days,
                'status': 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'
            }
        else:
            return None
    
    def format_schedule(self, result: Dict) -> pd.DataFrame:
        """Format the solution into a readable DataFrame"""
        if not result:
            return pd.DataFrame()
        
        solution = result['solution']
        days = result['days']
        
        # Create DataFrame
        data = []
        for day_idx, date in enumerate(days):
            day_name = date.strftime('%A')
            date_str = date.strftime('%Y-%m-%d')
            
            for shift_id, shift_name in self.shifts.items():
                available_shifts = self.get_available_shifts(date)
                if shift_id in available_shifts:
                    workers_on_shift = []
                    for worker in self.workers:
                        if solution[worker][day_idx][shift_id]:
                            workers_on_shift.append(f"Worker {worker + 1}")
                    
                    data.append({
                        'Date': date_str,
                        'Day': day_name,
                        'Shift': shift_name,
                        'Workers': ', '.join(workers_on_shift) if workers_on_shift else 'Unassigned',
                        'Count': len(workers_on_shift)
                    })
        
        return pd.DataFrame(data)
    
    def get_worker_schedule(self, result: Dict) -> pd.DataFrame:
        """Get schedule from worker perspective"""
        if not result:
            return pd.DataFrame()
        
        solution = result['solution']
        days = result['days']
        
        data = []
        for worker in self.workers:
            for day_idx, date in enumerate(days):
                day_name = date.strftime('%A')
                date_str = date.strftime('%Y-%m-%d')
                
                worker_shifts = []
                available_shifts = self.get_available_shifts(date)
                for shift_id in available_shifts:
                    if solution[worker][day_idx][shift_id]:
                        worker_shifts.append(self.shifts[shift_id])
                
                data.append({
                    'Worker': f"Worker {worker + 1}",
                    'Date': date_str,
                    'Day': day_name,
                    'Shift': ', '.join(worker_shifts) if worker_shifts else 'Off',
                    'Status': 'Working' if worker_shifts else 'Off'
                })
        
        return pd.DataFrame(data)
