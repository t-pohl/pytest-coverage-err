import os

# This file basically transforms all configurations which is done via env vars to pyhton vars which are bundled into a
# class. This way the code does not have to reference the env vars and mocking for tests is way more straightforward.


class Settings:
    db_user: str
    db_password: str
    db_host: str
    db_name: str
    db_port: int

    default_page_size: int

    def __init__(self) -> None:
        # defaults to gitlab ci settings
        self.db_host = os.getenv("DB_HOST", "lizard_db_tests")
        self.db_port = int(os.getenv("DB_PORT", 5432))
        self.db_name = os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "postgres"))
        self.db_user = os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres"))
        self.db_password = os.getenv(
            "DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        self.default_page_size = int(os.getenv("DEFAULT_PAGE_SIZE", 50))


settings = Settings()
