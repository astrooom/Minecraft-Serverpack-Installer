import sys
import yaml
def change_installpath(file, installpath):
    # yaml.preserve_quotes = True
    with open(file) as fp:
        data = yaml.safe_load(fp)
        data["install"]["baseInstallPath"] = installpath

    with open(file, "w") as f:
        yaml.dump(data, f)