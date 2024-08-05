import logging

log = logging.getLogger("fp-logger")
log_level = logging.INFO
FORMAT = "%(asctime)-15s %(levelname)-8s %(module)-15s :%(lineno)-8s %(message)s"
logFormatter = logging.Formatter(FORMAT)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)
log.setLevel(log_level)
