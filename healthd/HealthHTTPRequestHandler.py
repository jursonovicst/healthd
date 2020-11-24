import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import psutil


class HealthHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        response = ''
        healthy = True

        try:
            logging.debug("GET request,\nPath: %s\nHeaders: »»»%s«««", str(self.path), str(self.headers))

            parameters = parse_qs(urlparse(self.path).query)

            if 'loadavg_1' in parameters or 'loadavg_5' in parameters or 'loadavg_15' in parameters:
                (loadavg_1, loadavg_5, loadavg_15) = psutil.getloadavg()
                logging.debug(f"loadavgs: {loadavg_1, loadavg_5, loadavg_15}")

                if 'loadavg_1' in parameters:
                    kpi = loadavg_1 < float(parameters['loadavg_1'][0])
                    if self.server.args.return_kpis:
                        response += f"\r\nloadavg_1: {loadavg_1} < {float(parameters['loadavg_1'][0])}: {'OK' if kpi else 'CRIT'}"
                    logging.debug(response.strip())
                    if not kpi:
                        healthy = False

                if 'loadavg_5' in parameters:
                    kpi = loadavg_5 < float(parameters['loadavg_5'][0])
                    if self.server.args.return_kpis:
                        response += f"\r\nloadavg_5: {loadavg_5} < {float(parameters['loadavg_5'][0])}: {'OK' if kpi else 'CRIT'}"
                    logging.debug(response.strip())
                    if not kpi:
                        healthy = False

                if 'loadavg_15' in parameters:
                    kpi = loadavg_15 < float(parameters['loadavg_15'][0])
                    if self.server.args.return_kpis:
                        response += f"\r\nloadavg_15: {loadavg_15} < {float(parameters['loadavg_15'][0])}: {'OK' if kpi else 'CRIT'}"
                    logging.debug(response.strip())
                    if not kpi:
                        healthy = False

            if 'cpu_idle' in parameters:
                scputimes = psutil.cpu_times_percent(interval=1)
                logging.debug(f"cpu: {scputimes}")

                if 'cpu_idle' in parameters:
                    kpi = scputimes.idle > float(parameters['cpu_idle'][0])
                    if self.server.args.return_kpis:
                        response += f"\r\ncpu_idle: {scputimes.idle} > {float(parameters['cpu_idle'][0])}: {'OK' if kpi else 'CRIT'}"
                    logging.debug(response.strip())
                    if not kpi:
                        healthy = False

            if 'mem_free' in parameters:
                mem = psutil.virtual_memory()
                logging.debug(f"mem: {mem}")

                if 'mem_free' in parameters:
                    kpi = mem.free > float(parameters['mem_free'][0])
                    if self.server.args.return_kpis:
                        response += f"\r\nmem_free: {mem.free} > {float(parameters['mem_free'][0])}: {'OK' if kpi else 'CRIT'}"
                    logging.debug(response.strip())
                    if not kpi:
                        healthy = False

            if 'iface' in parameters and ('txthroughput' in parameters):
                snetio = psutil.net_io_counters(pernic=True)
                logging.debug(f"iface: {snetio}")

                if parameters['iface'][0] in snetio:
                    if 'txthroughput' in parameters:
                        kpi = snetio[parameters['iface'][0]].bytes_sent < float(parameters['txthroughput'][0])
                        if self.server.args.return_kpis:
                            response += f"\r\ntx_{parameters['iface'][0]}: {snetio[parameters['iface'][0]].bytes_sent} < {float(parameters['txthroughput'][0])}: {'OK' if kpi else 'CRIT'}"
                        logging.debug(response.strip())
                        if not kpi:
                            healthy = False
                else:
                    raise ValueError(f"No interface '{parameters['iface'][0]}'")

        except ValueError as err:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', f"{int(len(str(err)))}")
            self.end_headers()
            self.wfile.write(str(err).encode('ascii'))

        except FileNotFoundError as err:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', f"{int(len(str(err)))}")
            self.end_headers()
            self.wfile.write(str(err).encode('ascii'))

        else:
            body = f"{self.server.args.ok_string if healthy else self.server.args.fail_string}{response}"

            self.send_response(self.server.args.ok_status_code if healthy else self.server.args.fail_status_code)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', f"{int(len(body))}")
            self.end_headers()
            self.wfile.write(body.encode('ascii'))

    def address_string(self):
        """Return the client address."""

        return self.client_address

    def version_string(self):
        return "healthd/1.0"
