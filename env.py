from pydantic import BaseSettings

class Env(BaseSettings):
    LINE_TOKEN: str = 'test'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


env = Env()
