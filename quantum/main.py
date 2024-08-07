from datetime import datetime, timedelta
from ortools.sat.python import cp_model

from dwave.system.composites import EmbeddingComposite
from dwave.samplers import SimulatedAnnealingSampler
from dwave.system import LeapHybridSampler

from data_processing import read_input_file, calculate_max_decimal_length, convert_dataframe_to_jobs_structure_list, structure_solvers_dataset, structure_reference_dataset
from optimization_solver import calculate_horizon
from job_shop_scheduler import get_jss_bqm, is_auxiliary_variable
from visualization import visualize_solution, visualize_reference_solution

import collections
import json
import time

if __name__ == "__main__":

    MAX_JOBS_FOR_SCHEDULING = 2
    starting_point = datetime(2024, 1, 1, 7, 49)
    print(starting_point)

    df = read_input_file("Copy_of_Mappe1_small.xlsx")

    max_decimal_length = calculate_max_decimal_length(df)
    print("Max decimal: ", max_decimal_length)

    # Create the machines list
    machines = df['WORK_CENTER_RESOURCE'].unique()
    print("Machines are:", machines)

    # Calculate the horizon
    horizon = calculate_horizon(df, max_decimal_length)
    print("Horizon is:", horizon)
    print()
    jobs = convert_dataframe_to_jobs_structure_list(df, max_decimal_length)
    print(" === Jobs === ")
    print(jobs)

    # jobs = {jobs[0]['job_id']: [(jobs[0]['tasks_list'][0]['machine'], int(round(jobs[0]['tasks_list'][0]['duration']/10**max_decimal_length, 0))), (jobs[0]['tasks_list'][1]['machine'], int(round(jobs[0]['tasks_list'][1]['duration']/10**max_decimal_length, 0))), (jobs[0]['tasks_list'][2]['machine'], int(round(jobs[0]['tasks_list'][2]['duration']/10**max_decimal_length, 0)))],
    #         jobs[1]['job_id']: [(jobs[1]['tasks_list'][0]['machine'], int(round(jobs[1]['tasks_list'][0]['duration']/10**max_decimal_length, 0))), (jobs[1]['tasks_list'][0]['machine'], 2)]}
    jobs1 = {jobs[0]['job_id']: [(jobs[0]['tasks_list'][0]['machine'], jobs[0]['tasks_list'][0]['duration'])],
            # jobs[1]['job_id']: [(jobs[1]['tasks_list'][0]['machine'], jobs[1]['tasks_list'][0]['duration'])],
            # jobs[2]['job_id']: [(jobs[2]['tasks_list'][0]['machine'], jobs[2]['tasks_list'][0]['duration'])],
            jobs[1]['job_id']: [(jobs[1]['tasks_list'][0]['machine'], jobs[1]['tasks_list'][0]['duration'])], }
    print()
    print(" === Jobs 1 === ")
    print(jobs1)
    start_solving_time = time.time()
    max_time = 10  # Upperbound on how long the schedule can be; 4 is arbitrary
    bqm = get_jss_bqm(jobs1, max_time)

    # Here code for Quantum annealer 
    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, chain_strength=2, num_reads=1000,
                            label='Annealing Sampler - Job Shop Scheduling')
    
    # sampler = LeapHybridSampler(solver={'category': 'hybrid'})
    # sampleset = sampler.sample(bqm,
    #                         label='Annealing Sampler - Job Shop Scheduling')

    solution = sampleset.first.sample
    print()
    print(" === Solution === ")
    print(solution)
    # Grab selected nodes
    selected_nodes = [k for k, v in solution.items() if v == 1]

    # Parse node information
    task_times = {k: [-1]*len(v) for k, v in jobs1.items()}
    for node in selected_nodes:
        if is_auxiliary_variable(node):
            continue
        job_name, task_time = node.rsplit("_", 1)
        task_index, start_time = map(int, task_time.split(","))

        task_times[job_name][task_index] = start_time
    print()
    print(task_times)
    print()
    
    # Print problem and restructured solution
    print("Jobs and their machine-specific tasks:")
    for job, task_list in jobs1.items():
        print("{0:9}: {1}".format(job, task_list))

    print("\nJobs and the start times of each task:")
    for job, times in task_times.items():
        print("{0:9}: {1}".format(job, times))

    print("Solving execution time: {} seconds".format(time.time() - start_solving_time))

    structured_solvers_df = structure_solvers_dataset(jobs, task_times, max_decimal_length, starting_point)

    structured_ref_df = structure_reference_dataset(df, MAX_JOBS_FOR_SCHEDULING)

    start_visualization_time = time.time()

    visualize_solution(structured_solvers_df)

    visualize_reference_solution(structured_ref_df)

    print("Visualization execution time: {} seconds".format(time.time() - start_visualization_time))