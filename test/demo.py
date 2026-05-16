import tomli

with open('../secrets.toml', 'rb') as file:
    config = tomli.load(file)
print(config)
