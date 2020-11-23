import argparse
import logging
import os

from healthd import UnixHTTPServer, HealthHTTPRequestHandler


def mode_type(x):
    x = int(x)
    if x < 0 or x > 0o777:
        raise argparse.ArgumentTypeError(f"Invalid file mode: {x:o}.")
    return x


parser = argparse.ArgumentParser('healthd', description='Provides a resource check daemon over a unix domain socket.')
parser.add_argument('socket', type=str, help='Unix domain socket path to listen on.')
#parser.add_argument('--file-mode', type=mode_type, default=0o660,
#                    help='File permissions to open socket with (default 660)') TODO: fix this
parser.add_argument('--log-file', type=str, default='-',
                    help='File path to write logs to. Use - for stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', type=str, default='WARNING', choices=levels,
                    help='Logging severity. (default: %(default)s')
parser.add_argument('--ok-string', type=str, default='webisonline',
                    help='String to return in case of all KPIs are healthy. (default: %(default)s')
parser.add_argument('--return-kpis', type=bool, default=False,
                    help='Return the detailed KPIs in the HTTP response. (default: %(default)s')

args = parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(level=args.log_level, format='%(levelname)s healthd %(message)s')

    try:
        logging.info(f"Starting daemon on {args.socket}.")

        # Make sure the socket does not exist
        if os.path.exists(args.socket):
            raise FileExistsError(f"Socket {args.socket} already exists!")

        # Create the server, binding to the socket
        with UnixHTTPServer(args.socket, HealthHTTPRequestHandler) as server:
            # pass over arguments
            server.args = args

            # Activate the server; this will keep running until you interrupt the program with Ctrl-C
            server.serve_forever()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
        exit(-1)
    finally:
        os.unlink(args.socket)
        logging.info("Exited.")
