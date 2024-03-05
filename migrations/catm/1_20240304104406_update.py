from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `key_pair` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY COMMENT '密钥ID',
    `public_key` VARCHAR(1024) NOT NULL  COMMENT '公钥',
    `private_key` VARCHAR(1024) NOT NULL  COMMENT '私钥',
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='密钥';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `key_pair`;"""
