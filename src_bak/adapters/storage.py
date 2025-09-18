
# Storage adapter stub (SQLite/Postgres). For now, rely on Streamlit session state.
class Storage:
    def save(self, key: str, data: dict) -> None:
        raise NotImplementedError

    def load(self, key: str) -> dict:
        raise NotImplementedError
