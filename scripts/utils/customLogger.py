import logging
from typing import cast


# =======  Custom Log Levels  =============================================== #

# Standard levels: DEBUG(10), INFO(20), WARNING(30), ERROR(40), CRITICAL(50)
SUCCESS = 21
ACTION = 22
QUESTION = 23
RESULT = 24

logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(ACTION, 'ACTION')
logging.addLevelName(QUESTION, 'QUESTION')
logging.addLevelName(RESULT, 'RESULT')

class MyLogger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        self._log(SUCCESS, self, msg, *args, **kwargs)

    def action(self, msg, *args, **kwargs):
        self._log(ACTION, msg, args, **kwargs)

    def result(self, msg, *args, **kwargs):
        self._log(RESULT, msg, args, **kwargs)

    def question(self, msg, *args, **kwargs):
        self._log(QUESTION, msg, args, **kwargs)


# =======  Custom Formatter  ================================================ #

class myFormatter(logging.Formatter):
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    MARKERS = {
        logging.DEBUG:    f"{CYAN}[#]{RESET}",
        logging.INFO:     f"{BLUE}[*]{RESET}",
        SUCCESS:          f"{GREEN}[+]{RESET}",
        logging.WARNING:  f"{YELLOW}[!]{RESET}",
        logging.ERROR:    f"{RED}[-]{RESET}",
        logging.CRITICAL: f"{RED}[-]{RESET}",
        ACTION:           f"{BLUE}[>]{RESET}",
        RESULT:           f"{BLUE}[<]{RESET}",
        QUESTION:         f"{YELLOW}[?]{RESET}",
    }

    def format(self, record):
        record.marker = self.MARKERS.get(record.levelno, "[*]")
        return super().format(record)
    
def get_logger() -> MyLogger:
    logging.setLoggerClass(MyLogger)
    logger = cast(MyLogger, logging.getLogger())
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    format_string = "%(marker)s %(message)s"

    formatter = myFormatter(format_string)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

LOGGER = get_logger()


# =======  Local Testing  =================================================== #

if __name__ == "__main__":
    log = get_logger()

    log.debug("Initializing exploit payload...")
    log.info("Connecting to target 192.168.1.100:445")
    log.action("Sending staging payload")
    log.result("Payload executed")
    log.warning("Connection is taking longer than expected")
    log.success("Meterpreter session 1 opened")
    log.question("Do you want to run migration? (Y/n)")
    log.error("Failed to migrate process")