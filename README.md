# healthd
Checks system KPIs over HTTP listening on a UNIX domain socket

# HTTP api

http:///<path>?<kpi_name>=<kpi_limit>&<kpi_name>=<kpi_limit>...

The request <path> is ignored. The query string is parsed, and searched for the supported <kpi_name> and <kpi_limit>:

| kpi_name      | Description   | unit  | expression |
| ------------- |:------------- | ---------------:| -----------:|
| loadavg_1     | system load 1 minute average  | - | kpi < limit |
| loadavg_1     | system load 5 minute average  | - | kpi < limit |
| loadavg_15    | system load 15 minute average | - | kpi < limit |
| cpu_idle      | CPU in IDLE state (over 1 second) | percent | kpi > limit |
| mem_free      | free memory                   | byte | kpi > limit |
| iface, txthroughput | interface name, interface transmit throughput | string, bps | kpi[iface] < limit

KPI expressions evaluations are combined with AND relation. If the results is true, the --ok-string is returned. The 
individual KPIs can also be returned with the --return-kpis argument.

## Examples:

```bash
 ~ % curl  -v --unix-socket /tmp/healthd.sock 'http:/test?loadavg_1=100'
*   Trying /tmp/healthd.sock...
* Connected to test (/tmp/healthd.sock) port 80 (#0)
> GET /?loadavg_1=100 HTTP/1.1
> Host: test
> User-Agent: curl/7.64.1
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: healthd/1.0
< Date: Mon, 23 Nov 2020 21:28:44 GMT
< Content-type: text/html
< Content-Length: 11
< 
* Closing connection 0
webisonline%                            
 ~ % curl  -v --unix-socket /tmp/healthd.sock 'http:/test?loadavg_1=0.6'
*   Trying /tmp/healthd.sock...
* Connected to test (/tmp/healthd.sock) port 80 (#0)
> GET /?loadavg_1=0.6 HTTP/1.1
> Host: test
> User-Agent: curl/7.64.1
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: healthd/1.0
< Date: Mon, 23 Nov 2020 21:28:33 GMT
< Content-type: text/html
< Content-Length: 8
< 
* Closing connection 0
critical% 
 ~ %
```                                                                                                                                               jursonovicst@Tamas-MacBook-Pro ~ %  