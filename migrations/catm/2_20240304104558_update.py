from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `key_pair` MODIFY COLUMN `private_key` VARCHAR(2048) NOT NULL  COMMENT '私钥';
        ALTER TABLE `key_pair` MODIFY COLUMN `public_key` VARCHAR(2048) NOT NULL  COMMENT '公钥';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `key_pair` MODIFY COLUMN `private_key` VARCHAR(1024) NOT NULL  COMMENT '私钥';
        ALTER TABLE `key_pair` MODIFY COLUMN `public_key` VARCHAR(1024) NOT NULL  COMMENT '公钥';"""
