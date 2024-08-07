import pandas as pd
import plotly
import plotly.express as px
import plotly.figure_factory as ff
from datetime import timedelta

def visualize_solution(df):

    # --WE CAN REMOVE IT AFTER THE TESTING
    #df = pd.DataFrame()

    #for machine in machines:
    #    # Sort by starting time.
    #    #print(type(machine))
    #    #assigned_jobs[machine].sort()
    #    for assigned_task in assigned_jobs[machine]:
    #        #print(type(assigned_task.job))
    #        #name = f"job_{assigned_task.job}_task_{assigned_task.index}"
    #        start = float(assigned_task.start/10 ** max_decimal_length)
    #        duration = float(assigned_task.duration/10 ** max_decimal_length)
    #        end = start + duration
    #        time_shift_start = starting_point + timedelta(hours=start)
    #        time_shift_end = starting_point + timedelta(hours=end)
    #        row_data = {"Machine": str(machine), "Start": time_shift_start, "Finish": time_shift_end, "Operation_No":str(assigned_task.index),  "Job": str(assigned_task.job)}
    #        df = df._append(row_data, ignore_index = True)
        
    #NOTE Sort by machine y axis
    #machine_order = ((df['Machine'].unique()).tolist())
    #machine_order.sort()
    #print("Machine_order [Solution]", machine_order)

    #Sort by job id
    job_id_order = ((df['Job'].unique()).tolist())
    job_id_order.sort()

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Machine", color="Job", hover_data=['Operation_No'], color_discrete_sequence=px.colors.qualitative.Dark24, category_orders={"Job": job_id_order})
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_text="Quantum Annealing Optimized Solution", height=2000)

    plotly.offline.plot(fig, filename="exports/job_shop_scheduling_solution_annealing_sampler_run.html", auto_open=False)

def visualize_reference_solution(df):
    '''
    Visualize reference solution
    '''

    #NOTE Sort by machine y axis
    #machine_order = (df['Machine'].unique()).tolist()
    #print("Machine_oreder", machine_order)

    # Sort by job id
    job_id_order = ((df['Job'].unique()).tolist())
    job_id_order.sort()

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Machine", color="Job", hover_data=['Operation_No'], color_discrete_sequence=px.colors.qualitative.Dark24, category_orders={"Job": job_id_order})
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_text="Reference Solution", height=2000)


    plotly.offline.plot(fig, filename="exports/job_shop_scheduling_reference_solution_annealing_sampler_run.html", auto_open=False)
    