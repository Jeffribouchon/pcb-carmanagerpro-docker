# utils/logging_config.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Mapping pour LOG_LEVEL depuis .env
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

class HybridRotatingFileHandler(TimedRotatingFileHandler):
    """
    Handler personnalisé : combine rotation par jour + rotation par taille.
    """
    def __init__(self, filename, when="midnight", interval=1, backupCount=7,
                 encoding="utf-8", delay=False, utc=False, maxBytes=5*1024*1024):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)
        self.maxBytes = maxBytes

    def shouldRollover(self, record):
        """
        Vérifie à la fois la taille et le changement de jour.
        """
        if self.stream is None:  # Ouvre le fichier si nécessaire
            self.stream = self._open()
        if self.maxBytes > 0:
            self.stream.seek(0, 2)  # fin du fichier
            if self.stream.tell() >= self.maxBytes:
                return 1
        return super().shouldRollover(record)


def setup_logging(log_dir="logs", log_file="deepseek.log"):
    """Configure le logging global avec rotation journalière + taille."""
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # Lecture du niveau depuis l'environnement
    env_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level = LOG_LEVELS.get(env_level, logging.INFO)

    # Handlers
    console_handler = logging.StreamHandler()
    file_handler = HybridRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=7,            # Garde 7 jours de logs
        encoding="utf-8",
        maxBytes=5 * 1024 * 1024  # 5 Mo max par fichier avant split
    )

    # Format
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Application configuration
    logging.basicConfig(level=level, handlers=[console_handler, file_handler])

    logger = logging.getLogger("App")
    logger.info(f"📜 Logging initialisé avec niveau: {env_level} (rotation journalière + 5Mo)")
    return logger
