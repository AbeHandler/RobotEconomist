# cmd = "twine upload dist/*0.0.4*"
import os
with open("src/__version__.py", "r") as inf:
    version = inf.read().replace("\n", "").split("=").pop().strip()
cmd = "twine upload dist/*" + version + "*"

print(cmd)
os.system(cmd)
