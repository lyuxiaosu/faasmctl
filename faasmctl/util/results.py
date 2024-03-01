def get_execution_time_from_message_results(result, unit="s"):
    valid_units = ["s", "ms", "us"]
    if unit not in valid_units:
        print(
            "Unrecognised time unit '{}', must be one in: {}".format(unit, valid_units)
        )
        raise RuntimeError("Unrecognised time unit!")

    # Faasm gives us the timestamps in us
    planner_decision_cost = 0
    planner_nng_req_cost = 0
    planner_before_schedule_cost = 0
    planner_send_mapping_cost = 0
    total_turnover_cost = 0
    worker_enqueue_cost = 0
    worker_before_exe_cost = 0
    worker_exe_cost = 0
    worker_snapshot_related_cost = 0
    worker_release_cost = 0
    worker_turnover_no_send_cost = 0
    try:
        # Get arrival timestamp 
        planner_decision_cost = min([msg.plannerScheduleDecision for msg in result.messageResults])
        planner_nng_req_cost = min([msg.plannerNngReq for msg in result.messageResults])
        planner_before_schedule_cost = min([msg.plannerBeforeSchedule for msg in result.messageResults])
        planner_send_mapping_cost = min([msg.plannerSendMapping for msg in result.messageResults])
        total_turnover_cost = min([msg.totalTurnover for msg in result.messageResults])
        worker_enqueue_cost = min([msg.workerEnqueueReq for msg in result.messageResults])
        worker_before_exe_cost = min([msg.workerBeforeExe for msg in result.messageResults])
        worker_exe_cost = min([msg.workerExe for msg in result.messageResults])
        worker_snapshot_related_cost = min([msg.workerSnapShortRelated for msg in result.messageResults])
        worker_release_cost = min([msg.workerRelease for msg in result.messageResults])
        worker_turnover_no_send_cost = min([msg.workerTurnoverNoSend for msg in result.messageResults])
        # We have recently changed the name of the protobuf field, so support
        # both names for backwards compatibility
        start_ts = min([msg.startTimestamp for msg in result.messageResults])
    except AttributeError:
        print(f"AttributeError: {e}")
        raise
        #start_ts = min([msg.timestamp for msg in result.messageResults])
    end_ts = max([msg.finishTimestamp for msg in result.messageResults])

    #if unit == "s":
    #    return float(total_turnover_us/ 1e6), float(half_nng_rtt_us/ 1e6), float(worker_turnover_us / 1e6), float(planner_turnover_us / 1e6), float(execution_us / 1e6)

    #if unit == "ms":
    #    return float(total_turnover_us/ 1e3), float(half_nng_rtt_us/ 1e3), float(worker_turnover_us / 1e3), float(planner_turnover_us / 1e3), float(execution_us / 1e3)

    return planner_decision_cost, planner_nng_req_cost, planner_before_schedule_cost, planner_send_mapping_cost, total_turnover_cost, worker_enqueue_cost, worker_before_exe_cost, worker_exe_cost, worker_snapshot_related_cost, worker_release_cost, worker_turnover_no_send_cost 


def get_return_code_from_message_results(result):
    def get_return_code_from_message(message):
        rv = message.returnValue
        return rv

    # if len(message_results) == 1:
    # return get_return_code_from_message(message_results[0])

    rvs = set(
        [get_return_code_from_message(message) for message in result.messageResults]
    )
    assert len(rvs) == 1, "Differing return values for same app! (rv: {})".format(rvs)

    return rvs.pop()
