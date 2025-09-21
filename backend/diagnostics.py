\
def run_local_diagnostics():
    # This simulates system/service checks; extend to call real monitors
    results = []
    results.append({'check':'disk_usage','value':'95%','note':'/var > 90%'})
    results.append({'check':'vpn_status','value':'down','note':'VPN unreachable'})
    return results
