"""
Streamlit Interface for OR-Tools Shift Scheduler

Interactive web interface for generating and visualizing shift schedules.
"""

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from scheduler import ShiftScheduler


def main():
    st.set_page_config(
        page_title="Shift Scheduler",
        page_icon="📅",
        layout="wide"
    )
    
    st.title("📅 OR-Tools Shift Scheduler")
    st.markdown("Generate monthly shift schedules for 5 workers with optimized constraints")
    
    # Initialize scheduler (will be recreated with new parameters when needed)
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Schedule Configuration")
        
        # Month/Year selector
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Month",
                options=list(range(1, 13)),
                format_func=lambda x: calendar.month_name[x],
                index=datetime.now().month - 1
            )
        with col2:
            year = st.selectbox(
                "Year",
                options=list(range(2024, 2030)),
                index=0
            )
        
        st.markdown("---")
        st.markdown("### 👥 Workforce Settings")
        
        # Configurable parameters
        num_workers = st.slider(
            "Number of Workers",
            min_value=3,
            max_value=10,
            value=5,
            help="Total number of workers in the system"
        )
        
        workers_per_shift = st.slider(
            "Workers per Shift",
            min_value=1,
            max_value=4,
            value=2,
            help="Number of workers assigned to each shift"
        )
        
        st.markdown("### 📅 Working Days per Week")
        col1, col2 = st.columns(2)
        with col1:
            min_working_days = st.slider(
                "Min Days",
                min_value=1,
                max_value=6,
                value=3,
                help="Minimum working days per week"
            )
        with col2:
            max_working_days = st.slider(
                "Max Days",
                min_value=2,
                max_value=7,
                value=5,
                help="Maximum working days per week"
            )
        
        # Validate min/max
        if min_working_days >= max_working_days:
            st.error("Min days must be less than max days")
            st.stop()
        
        # Generate button
        generate_btn = st.button("🚀 Generate Schedule", type="primary", use_container_width=True)
        
        # Display shift information
        st.markdown("---")
        st.markdown("### 📋 Shift Information")
        st.markdown("""
        **Weekdays (Mon-Sat):**
        - 7h-16h (Morning)
        - 15h-00h (Evening)
        - 00h-08h (Night)
        - 9h-21h (Extended)
        
        **Sundays:**
        - 7h-16h (Morning)
        - 15h-00h (Evening)
        - 00h-08h (Night)
        """)
        
        st.markdown("### 📊 Constraints")
        st.markdown("""
        - 5 workers total
        - 4 consecutive working days, then 2 days off
        - 2 workers per shift
        - Same shift type during working days
        - No full week off
        """)
    
    # Main content area
    if generate_btn:
        # Create scheduler with current parameters
        scheduler = ShiftScheduler(
            num_workers=num_workers,
            workers_per_shift=workers_per_shift,
            min_working_days=min_working_days,
            max_working_days=max_working_days
        )
        
        with st.spinner("Generating schedule... This may take a few moments."):
            result = scheduler.solve_schedule(year, month)
        
        if result:
            st.success(f"✅ Schedule generated successfully for {calendar.month_name[month]} {year}")
            
            # Store result in session state
            st.session_state.schedule_result = result
            st.session_state.scheduler = scheduler
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📅 Calendar View", "👥 Worker View", "📊 Coverage Analysis", "📁 Export"])
            
            with tab1:
                st.subheader("📅 Schedule by Day and Shift")
                schedule_df = scheduler.format_schedule(result)
                
                if not schedule_df.empty:
                    # Filter out unassigned shifts
                    assigned_df = schedule_df[schedule_df['Count'] > 0].copy()
                    
                    # Color code the shifts
                    def color_shift(val):
                        colors = {
                            '7h-16h': 'background-color: #e8f5e8',    # Light green
                            '15h-00h': 'background-color: #fff3cd',  # Light yellow
                            '00h-08h': 'background-color: #d1ecf1',  # Light blue
                            '9h-21h': 'background-color: #f8d7da'   # Light red
                        }
                        return colors.get(val, '')
                    
                    # Apply styling
                    styled_df = assigned_df.style.applymap(color_shift, subset=['Shift'])
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Days", len(schedule_df['Date'].unique()))
                    with col2:
                        st.metric("Total Shifts", len(assigned_df))
                    with col3:
                        coverage = len(assigned_df[assigned_df['Count'] == 2]) / len(assigned_df) * 100
                        st.metric("Coverage %", f"{coverage:.1f}%")
                else:
                    st.warning("No schedule data available")
            
            with tab2:
                st.subheader("👥 Schedule by Worker")
                worker_df = scheduler.get_worker_schedule(result)
                
                if not worker_df.empty:
                    # Create worker selector
                    selected_worker = st.selectbox(
                        "Select Worker to View",
                        options=[f"Worker {i+1}" for i in range(scheduler.num_workers)],
                        key="worker_selector"
                    )
                    
                    # Filter data for selected worker
                    worker_data = worker_df[worker_df['Worker'] == selected_worker]
                    
                    # Display worker schedule
                    st.dataframe(worker_data, use_container_width=True)
                    
                    # Worker statistics
                    working_days = len(worker_data[worker_data['Status'] == 'Working'])
                    off_days = len(worker_data[worker_data['Status'] == 'Off'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Working Days", working_days)
                    with col2:
                        st.metric("Days Off", off_days)
                    
                    # Visualize worker pattern
                    fig = px.bar(
                        worker_data, 
                        x='Date', 
                        y='Status',
                        color='Status',
                        title=f"{selected_worker} Schedule Pattern",
                        color_discrete_map={'Working': '#2E8B57', 'Off': '#DC143C'}
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No worker schedule data available")
            
            with tab3:
                st.subheader("📊 Coverage Analysis")
                
                if 'schedule_result' in st.session_state:
                    schedule_df = scheduler.format_schedule(result)
                    
                    if not schedule_df.empty:
                        # Shift coverage analysis
                        shift_coverage = schedule_df.groupby('Shift')['Count'].agg(['sum', 'mean', 'count']).reset_index()
                        shift_coverage.columns = ['Shift', 'Total Workers', 'Avg Workers', 'Days']
                        shift_coverage['Coverage %'] = (shift_coverage['Total Workers'] / (shift_coverage['Days'] * 2) * 100).round(1)
                        
                        st.subheader("Shift Coverage Summary")
                        st.dataframe(shift_coverage, use_container_width=True)
                        
                        # Visualize coverage
                        fig = px.bar(
                            shift_coverage,
                            x='Shift',
                            y='Coverage %',
                            title='Shift Coverage Percentage',
                            color='Coverage %',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Daily coverage heatmap
                        daily_coverage = schedule_df.pivot_table(
                            index='Date', 
                            columns='Shift', 
                            values='Count', 
                            fill_value=0
                        )
                        
                        fig = px.imshow(
                            daily_coverage.T,
                            title='Daily Shift Coverage Heatmap',
                            color_continuous_scale='RdYlGn',
                            aspect='auto'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No coverage data available")
            
            with tab4:
                st.subheader("📁 Export Schedule")
                
                if 'schedule_result' in st.session_state:
                    schedule_df = scheduler.format_schedule(result)
                    worker_df = scheduler.get_worker_schedule(result)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📅 Daily Schedule (CSV)**")
                        csv_schedule = schedule_df.to_csv(index=False)
                        st.download_button(
                            label="Download Daily Schedule",
                            data=csv_schedule,
                            file_name=f"schedule_{year}_{month:02d}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        st.markdown("**👥 Worker Schedule (CSV)**")
                        csv_workers = worker_df.to_csv(index=False)
                        st.download_button(
                            label="Download Worker Schedule",
                            data=csv_workers,
                            file_name=f"workers_{year}_{month:02d}.csv",
                            mime="text/csv"
                        )
                    
                    # Display preview of data to export
                    st.markdown("**Preview of Export Data:**")
                    preview_tab1, preview_tab2 = st.tabs(["Daily Schedule", "Worker Schedule"])
                    
                    with preview_tab1:
                        st.dataframe(schedule_df.head(10), use_container_width=True)
                    
                    with preview_tab2:
                        st.dataframe(worker_df.head(10), use_container_width=True)
        else:
            st.error("❌ Unable to generate a feasible schedule. The constraints may be too restrictive for this month.")
            st.markdown("""
            **Possible solutions:**
            - Try a different month
            - The 4-days-on/2-days-off pattern may not align well with this month's calendar
            - Consider adjusting constraints if needed
            """)
    
    # Display instructions if no schedule generated yet
    if 'schedule_result' not in st.session_state:
        st.markdown("""
        ## 🚀 Getting Started
        
        1. **Select Month/Year** in the sidebar
        2. **Click "Generate Schedule"** to create the schedule
        3. **View Results** in the different tabs:
           - **Calendar View**: See which workers are assigned to each shift
           - **Worker View**: See each worker's individual schedule
           - **Coverage Analysis**: Analyze shift coverage and patterns
           - **Export**: Download schedules as CSV files
        
        ## 📋 About the Scheduler
        
        This system uses Google OR-Tools to solve complex scheduling constraints:
        - **5 Workers** with rotating schedules
        - **4 Shift Types** (3 on Sundays)
        - **2 Workers per Shift** for proper coverage
        - **4 Days On, 2 Days Off** pattern
        - **Consistent Shift Types** during working periods
        """)
        
        # Show example of what the schedule looks like
        st.markdown("### 📊 Example Schedule Preview")
        example_data = {
            'Date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
            'Day': ['Monday', 'Monday', 'Monday', 'Monday'],
            'Shift': ['7h-16h', '15h-00h', '00h-08h', '9h-21h'],
            'Workers': ['Worker 1, Worker 2', 'Worker 3, Worker 4', 'Worker 5, Worker 1', 'Worker 2, Worker 3'],
            'Count': [2, 2, 2, 2]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)


if __name__ == "__main__":
    main()
