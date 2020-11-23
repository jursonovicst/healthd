import argparse
import logging
import os

from healthd import UnixHTTPServer, HealthHTTPRequestHandler

parser = argparse.ArgumentParser('healthd', description='Provides a health check daemon over a unix domain socket.')
parser.add_argument('socket', type=str, help='Unix domain socket path.')
parser.add_argument('--logfile', type=str, default='-',
                    help='File path to write logs. Use - to use stdout. (default: %(default)s')
levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
parser.add_argument('--log-level', default='WARNING', choices=levels)
args = parser.parse_args()

if __name__ == "__main__":

    logging.basicConfig(level=args.log_level, format='%(levelname)s healthd %(message)s')

    try:
        logging.info(f"Starting daemon on {args.socket}.")

        # Make sure the socket does not exist
        try:
            os.unlink(args.socket)
        except FileNotFoundError:
            # everithing is ok, socket must not exist.
            pass

        # Create the server, binding to the socket
        with UnixHTTPServer(args.socket, HealthHTTPRequestHandler) as server:
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
