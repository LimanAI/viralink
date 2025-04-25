from pydantic import BaseModel


class UserTGData(BaseModel):
    id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    language_code: str = ""
    is_bot: bool = False
