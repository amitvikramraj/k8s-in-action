#!/bin/sh

host=${1:-1.1.1.1}

echo "Checking network connectivity for ${host}"

# ping it once using `-c 1` flag and redirect the output(both stdout/stderr) to /dev/null
ping ${host} -c1 > /dev/null 2>&1  # works with all Unix shells
# ping ${host} -c 1 &> /dev/null # for bash 4.0+

# capture the exit code of last run command (ping)
pingExitCode=$?

if [ $pingExitCode = 0 ]; then
  echo "Host appears to be reachable"
  exit 0
else
  echo "Host unreachable!"
  exit 1
fi
