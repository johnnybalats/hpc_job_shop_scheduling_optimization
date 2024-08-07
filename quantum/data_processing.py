import pandas as pd
from datetime import datetime, timedelta

def read_input_file(filepath):
    '''
    Read the data input file
    '''

    df = pd.read_excel(filepath)

    return df

def calculate_decimal_length(floating_number):
    '''
    Calculate decimal length of a given floating number
    '''
    parts = str(floating_number).split('.')
    if len(parts) == 2:
        decimal_length = len(parts[1])
    else:
        decimal_length = 0
    
    return decimal_length

def calculate_max_decimal_length(df):
    '''
    The OR-Tools uses integers for calculations. Some durations in the data set
    are floating so we need to identify the max length of decimal digits
    in order to rescale our data to integers
    '''
    max_decimal_length = 0
    for index, row in df.iterrows():
        
        decimal_length = max(calculate_decimal_length(row['STANDARD_QTY_ACT1']),
                            calculate_decimal_length(row['STANDARD_QTY_ACT2']),
                            calculate_decimal_length(row['STANDARD_QTY_ACT3']))
        
        if decimal_length > max_decimal_length:
            max_decimal_length = decimal_length


    return max_decimal_length

def retrieve_tasks_of_single_job(df_single_job, max_decimal_length):
    '''
    We retrieve the tasks of a single job as a list in a sorted timeline
    '''
    # TODO test assert as a different function for integers handling

    task_list = []

    for index, row in df_single_job.iterrows():

        task_dict = {}

        task_dict['operation_number'] = row['OPERATION_NUMBER']
        # OR-Tools uses integers so we can convert the hours into minutes
        # We also check if the seconds is not decimal number
        task_dict['activity_1_duration'] = row['STANDARD_QTY_ACT1'] * 10 ** max_decimal_length
        if task_dict['activity_1_duration'] != int(task_dict['activity_1_duration']):
            print("Error on convertion to minutes. We want integers")
            fault_data_job_ids.append((material_key,process_order))
        else:
            task_dict['activity_1_duration'] = int(task_dict['activity_1_duration'])
        task_dict['activity_2_duration'] = row['STANDARD_QTY_ACT2'] * 10 ** max_decimal_length
        if task_dict['activity_2_duration'] != int(task_dict['activity_2_duration']):
            print("Error on convertion to minutes. We want integers")
            fault_data_job_ids.append((material_key,process_order))
        else:
            task_dict['activity_2_duration'] = int(task_dict['activity_2_duration'])
        task_dict['activity_3_duration'] = row['STANDARD_QTY_ACT3'] * 10 ** max_decimal_length
        if task_dict['activity_3_duration'] != int(task_dict['activity_3_duration']):
            print("Error on convertion to minutes. We want integers")
            fault_data_job_ids.append((material_key,process_order))
        else:
            task_dict['activity_3_duration'] = int(task_dict['activity_3_duration'])


        task_dict['machine'] = row['WORK_CENTER_RESOURCE']
        task_dict['duration'] = task_dict['activity_1_duration'] + task_dict['activity_2_duration'] + task_dict['activity_3_duration']

        task_list.append(task_dict)
    
    # Sort the list by Operation Number to create the timeline
    sorted_task_list = sorted(task_list, key=lambda x: x['operation_number'])

    return sorted_task_list

def create_job_structure(material_key_value, process_order, task_list):
    '''
    This fucntion creates a job structered dictionary for the given fields
    '''

    job = {}
    job_id = material_key_value + "_" + process_order
    job['job_id'] = job_id
    job['tasks_list'] = task_list

    return job

def convert_dataframe_to_jobs_structure_list(df, max_decimal_length):
    '''
    The function converts dataframe -> job structure list
    The contents of every job within the return list is the following
    job:{
        job_id: 
        tasks_list: [
            {
                operation_number:
                activity_1_duration:
                activity_2_duration:
                activity_3_duration:
                machine:
                duration:
            }
        ]
    }
    '''

    jobs = []
    jobs_ids = set()

    for index, row in df.iterrows():
        material_key = row['MATERIAL_KEY']
        process_order = row['PROCESS_ORDER']
        job_id = (material_key, process_order)
        
        # We check if the specific job_id combination has already been parsed or not
        if job_id in jobs_ids:
            continue

        filtered_job_df = df[(df['MATERIAL_KEY'] == material_key) & (df['PROCESS_ORDER'] == process_order)]
    
        task_list = retrieve_tasks_of_single_job(filtered_job_df, max_decimal_length)

        job = create_job_structure(material_key, process_order, task_list)

        jobs.append(job)

        jobs_ids.add(job_id)

    return jobs

def structure_solvers_dataset(jobs, task_times, max_decimal_length, starting_point):
    """
    Structure solution dataset
    """

    df = pd.DataFrame()

    for i in jobs:
        for j in i['tasks_list']:
            for task_start in task_times[i['job_id']]:
                start = float(task_start/10 ** max_decimal_length)
                duration = float(j['duration']/10 ** max_decimal_length)
                end = start + duration
                time_shift_start = starting_point + timedelta(hours=start)
                time_shift_end = starting_point + timedelta(hours=end)
                row_data = {"Machine": str(j['machine']), "Start": time_shift_start, "Finish": time_shift_end, "Operation_No":str(j['operation_number']),  "Job": str(i['job_id'])}
                df = df._append(row_data, ignore_index = True)
    
    return df

def structure_reference_dataset(df, max_jobs_for_scheduling):
    '''
    Structure reference dataset
    '''

    jobs_ids = set()
    structured_df = pd.DataFrame()

    n = 0

    for index, row in df.iterrows():

        material_key = row['MATERIAL_KEY']
        process_order = row['PROCESS_ORDER']
        job_id = (material_key, process_order)
        
        # We check if the specific job_id combination has already been parsed or not
        if job_id in jobs_ids:
            continue

        filtered_job_df = df[(df['MATERIAL_KEY'] == material_key) & (df['PROCESS_ORDER'] == process_order)].sort_values(by=['OPERATION_NUMBER'])

        job = "".join([str(row['MATERIAL_KEY']), "_" , str(row['PROCESS_ORDER'])])

        n += 1

        for filter_index, filter_row in filtered_job_df.iterrows():

            machine = str(filter_row["WORK_CENTER_RESOURCE"])

            #TODO check if we can read from the file directly with "0" at the beginning at the specific column
            start_exec_time = str(filter_row["LATEST_SCHEDULED_START_EXEC_TIME"])
            if len(start_exec_time) < 6:
                start_exec_time = "0"*(6-len(start_exec_time)) + start_exec_time
            year, month, day = (str(filter_row["EARLIEST_TARGET_START_DATE"]).split()[0]).split('-')
            
            start = datetime(year=int(year), month=int(month), day=int(day), hour=int(start_exec_time[:2]), minute=int(start_exec_time[2:4]), second=int(start_exec_time[4:6]))

            #TODO check if we can read from the file directly with "0" at the beginning at the specific column 
            finish_exec_time = str(filter_row["LATEST_SCHEDULED_FINISH_EXEC_TIME"])
            if len(finish_exec_time) < 6:
                finish_exec_time = "0"*(6-len(finish_exec_time)) + finish_exec_time
            year, month, day = (str(filter_row["EARLIEST_TARGET_FINISH_DATE"]).split()[0]).split('-')

            finish = datetime(year=int(year), month=int(month), day=int(day), hour=int(finish_exec_time[:2]), minute=int(finish_exec_time[2:4]), second=int(finish_exec_time[4:6]))
            
            row_data = {"Machine": machine, "Start": start, "Finish": finish, "Operation_No": filter_row["OPERATION_NUMBER"], "Job": job}

            structured_df = structured_df._append(row_data, ignore_index=True)

        jobs_ids.add(job_id)

        if n >= max_jobs_for_scheduling:
            break
    
    structured_df_sorted = structured_df.sort_values(by='Machine')
    
    return structured_df_sorted
    