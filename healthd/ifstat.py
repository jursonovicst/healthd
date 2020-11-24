import logging
import time
from threading import Thread, Event, Lock

import psutil


class IFStat(Thread):
    def __init__(self, event: Event, interval=1):
        Thread.__init__(self)
        self.stopped = event
        self._iterval = interval

        self._last_ts = None
        self._last_snetios = None
        self._kpis = {}
        self._kpis_lock = Lock()

    def run(self):
        while not self.stopped.wait(self._iterval):
            try:
                # get new ts and interface statistics
                ts = time.time()
                snetios = psutil.net_io_counters(pernic=True)

                # build difference, if there is already a last one
                if self._last_ts is not None and self._last_snetios is not None:
                    if not self._kpis_lock.acquire(timeout=0.2):
                        raise TimeoutError(f"Timeout accessing kpi for writing.")

                    for iface, snetio in snetios.items():
                        self._kpis[iface] = {}
                        self._kpis[iface]['bytes_sent'] = (snetio.bytes_sent - self._last_snetios[iface].bytes_sent) / (
                                ts - self._last_ts)
                    self._kpis_lock.release()

                # update last one
                self._last_ts = ts
                self._last_snetios = snetios
            except Exception as e:
                logging.warning(e)

    def get(self, iface: str, kpi: str):
        try:
            if not self._kpis_lock.acquire(timeout=1):
                raise TimeoutError(f"Timeout accessing kpi for reading.")

            value = self._kpis[iface][kpi]
            self._kpis_lock.release()
            return value

        except KeyError:
            raise ValueError(f"Interface {iface} or kpi {kpi} not found!")
