import requests
import pyodbc
import assets
import config
import users
import configparser


# Run sync for both users and assets

print("hi")
assets.pull_assets(config.DATABASE, config.IIQ_INSTANCE, config.IIQ_TOKEN)


if __name__ == '__main__':
    print("I am the runner")