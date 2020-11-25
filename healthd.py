import argparse
import logging
import os
from threading import Event

from healthd import UnixHTTPServer, HealthHTTPRequestHandler, IFStat


def mode_type(x):
    x = int(x)
    if x < 0 or x > 0o777:
        raise argparse.ArgumentTypeError(f"Invalid file mode: {x:o}.")
    return x


parser = argparse.ArgumentParser('healthd', description='Provides a resource check daemon over a unix domain socket.')
parser.add_argument('socket', type=str, help='Unix domain socket path to listen on.')
# parser.add_argument('--file-mode', type=mode_type, default=0o660,
#                    help='File permissions to open socket with (default 660)') TODO: fix this
parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='WARNING', choices=levels,
                    help='Logging severity. (default: %(default)s')
parser.add_argument('--ok-string', type=str, default='webisonline',
                    help='String to return if all KPIs are healthy. (default: %(default)s')
parser.add_argument('--fail-string', type=str, default='critical',
                    help='String to return if at least one KPI is unhealthy. (default: %(default)s')
parser.add_argument('--ok-status-code', type=int, default=200,
                    help='HTTP status code to return if all KPIs are healthy. (default: %(default)s')
parser.add_argument('--fail-status-code', type=int, default=503,
                    help='HTTP status codes to return if at least one KPI is unhealthy. (default: %(default)s')

parser.add_argument('--return-kpis', dest='return_kpis', action='store_true',
                    help='Return the detailed KPIs in the HTTP response. (default: %(default)s')

args = parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(level=args.log_level, format='%(levelname)s healthd %(message)s')

    try:
        logging.info(f"Starting daemon on {args.socket}.")

        stop_event = Event()
        instat = IFStat(stop_event)
        instat.start()

        # Make sure the socket does not exist
        if os.path.exists(args.socket):
            raise FileExistsError(f"Socket {args.socket} already exists!")

        # Create the server, binding to the socket
        with UnixHTTPServer(args.socket, HealthHTTPRequestHandler) as server:
            # pass over arguments
            server.args = args
            server.instat = instat

            # Activate the server; this will keep running until you interrupt the program with Ctrl-C
            server.serve_forever()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
        exit(-1)
    finally:
        stop_event.set()
        instat.join(1)
        os.unlink(args.socket)
        logging.info("Exited.")
