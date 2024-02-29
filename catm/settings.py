from catm.env import Env


APP_NAME = Env.string("APP_NAME", default="catm")
# 数据库密码配置
MYSQL_DB_URL = Env.string("MYSQL_DB_URL")
TORTOISE_ORM = {
    "connections": {"default": MYSQL_DB_URL},
    "apps": {
        APP_NAME: {
            "models": ["catm.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "timezone": "Asia/Shanghai",
}
# DEBUG开关
DEBUG = Env.boolean("DEBUG", default=False)
