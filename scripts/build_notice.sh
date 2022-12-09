#!/usr/bin/env bash
echo "[*] You probably want to push tags to git:"
echo "	$ git push origin" $(cat src/__version__.py | awk -F"= " '{print $2}')
echo "[*] You may also want to reinstall econ:"
echo "	$ pip install dist/roboteconomist-"$(cat src/__version__.py | awk -F"= " '{print $2}')"-py3-none-any.whl --force-reinstall"
echo "[*] Often followed by a push to pypi also:"
echo "	$ make pypi && pip install --upgrade --force-reinstall"
