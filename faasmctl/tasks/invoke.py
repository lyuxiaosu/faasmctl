from base64 import b64encode
from faasmctl.util.invoke import invoke_wasm
from faasmctl.util.planner import get_available_hosts
from faasmctl.util.results import (
    get_execution_time_from_message_results,
    get_return_code_from_message_results,
)
from invoke import task
from sys import exit
from time import time


@task(default=True)
def invoke(
    ctx,
    user,
    func,
    ini_file=None,
    cmdline=None,
    input_data=None,
    mpi_world_size=None,
    single_host=False,
    host_dist=None,
):
    """
    Invoke the execution of a user/func pair

    TODO: think how to enable all the possible command line values in a
    scalable way.
    """
    print("Modified by xiaosu")
    num_messages = 1
    req_dict = {"user": user, "function": func}
    msg_dict = {"user": user, "function": func}

    if cmdline is not None:
        msg_dict["cmdline"] = cmdline
    if input_data is not None:
        msg_dict["input_data"] = b64encode(input_data.encode("utf-8")).decode("utf-8")
    if mpi_world_size is not None:
        msg_dict["mpi_world_size"] = int(mpi_world_size)
    if single_host:
        req_dict["singleHost"] = single_host
    if host_dist:
        host_dist = host_dist.split(",")
        # Prepare a host distribution
        available_hosts = get_available_hosts()

        if len(host_dist) > len(available_hosts.hosts):
            print(
                "ERROR: requested execution among {} hosts but only {} "
                "available!".format(len(host_dist), len(available_hosts.hosts))
            )
            return 1

        # We assume that the available host list will always come in the same
        # order (for the same set of hosts)

        host_list = []
        for host in host_dist:
            host_ind = int(host.split(":")[0])
            num_in_host = int(host.split(":")[1])
            host_list += [available_hosts.hosts[host_ind].ip] * num_in_host
    else:
        host_list = None

    # Invoke WASM using main API function
    start_ts = time()
    result = invoke_wasm(
        msg_dict,
        num_messages=num_messages,
        req_dict=req_dict,
        ini_file=ini_file,
        host_list=host_list,
    )
    end_ts = time()

    # Pretty-print a summary of the execution

    user = result.messageResults[0].user
    function = result.messageResults[0].function
    output = result.messageResults[0].outputData
    ret_val = get_return_code_from_message_results(result)
    # Wall time is the time elapsed as measured from the calling python script
    wall_time = "{:.2f} us".format((end_ts - start_ts) * 1000000)
    # Exec time is the time the function actually executed inside Faasm
    #exec_time, turnover_time = "{:.2f} us".format(
    #    get_execution_time_from_message_results(result, unit="us")
    #)
    planner_decision, planner_nng_req, planner_before_schedule, planner_send_mapping, total_turnover, worker_enqueue, worker_before_exe, worker_exe, worker_snapshot_related, worker_release, worker_turnover_no_send = get_execution_time_from_message_results(result, unit="us")
    planner_cost = planner_decision + planner_nng_req + planner_before_schedule + planner_send_mapping
    total_turnover = "{:.2f} us".format(total_turnover)
    planner_decision = "{:.2f} us".format(planner_decision)
    planner_nng_req = "{:.2f} us".format(planner_nng_req)
    planner_before_schedule = "{:.2f} us".format(planner_before_schedule)
    planner_send_mapping = "{:.2f} us".format(planner_send_mapping)
    worker_enqueue = "{:.2f} us".format(worker_enqueue)
    worker_before_exe = "{:.2f} us".format(worker_before_exe)
    worker_exe = "{:.2f} us".format(worker_exe)
    worker_snapshot_related = "{:.2f} us".format(worker_snapshot_related)
    worker_release = "{:.2f} us".format(worker_release)
    worker_turnover_no_send = "{:.2f} us".format(worker_turnover_no_send)


    print("======================= Faasm Execution =========================")
    print("Function: \t\t\t{}/{}".format(user, function))
    print("Return value: \t\t\t{}".format(ret_val))
    print("Wall time: \t\t\t{}".format(wall_time))
    print("Total Turnover time: \t\t{}".format(total_turnover))
    
    print("                                                                 ")

    print("===================== Planner Cost > {} ==========================".format(planner_cost))
    print("Before Schedule Cost: \t\t{}".format(planner_before_schedule))
    print("Make Schedule Decision cost: \t{}".format(planner_decision))
    print("Send Mapping cost: \t\t{}".format(planner_send_mapping))
    print("NNG Send Req To Worker cost: \t{}".format(planner_nng_req))
   
    print("                                                                 ") 
    print("===================== Worker Cost > {} ==========================".format(worker_turnover_no_send))
    print("Enqueue Request cost:\t\t{}".format(worker_enqueue))
    print("Before Exe cost: \t\t{}".format(worker_before_exe))
    print("Exe cost: \t\t\t{}".format(worker_exe))
    print("Snapshot Related cost: \t\t{}".format(worker_snapshot_related))
    print("Release Fasslet cost(buggy): \t{}".format(worker_release))

    
    print("                                                                 ")

    print("-----------------------------------------------------------------")
    print("Output:\n{}".format(output))
    print("=================================================================")

    # Use sys/exit to propagate the error code to the bash process. If
    # execution fails, we want the bash process to have a non-zero exit code.
    # This is very helpful for testing environments like GHA
    exit(ret_val)
