#!/bin/sh
#
# Sidecar-style traffic meter: every 10s, print how many bytes were received
# (inbound) and sent (outbound) on the pod/host default network interface.
#
# In a Kubernetes pod, containers share the Network namespace, so this process
# sees the same eth0 (and /proc/net/dev stats) as the other containers.

echo "[traffic-meter] Starting traffic meter..."

# 1. Dynamically find the active default interface name (usually eth0 in a pod).
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: `route -n get default` prints a line like "interface: en5"
    INTERFACE=$(route -n get default | awk '/interface:/ {print $2}')
else
    # Linux: `ip route show default` ends with "default via 10.244.1.1 dev eth0" — field 5 is the name
    INTERFACE=$(ip route show default | awk '/default/ {print $5}')
fi


# Print two space-separated totals: "<rx_bytes> <tx_bytes>" for $INTERFACE.
count_bytes() {
    local rx
    local tx
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # netstat -b: byte counters; NR==2 skips the header row.
        # Fields 7 and 10 are Ibytes / Obytes on macOS netstat output.
        read -r rx tx <<< $(netstat -I "$INTERFACE" -b | awk 'NR==2 {print $7, $10}')
    else
        # /proc/net/dev lines look like: "  eth0: <rx_bytes> ... <tx_bytes> ..."
        # -v iface=... passes the shell INTERFACE into awk.
        # $1 ~ iface":" matches the "eth0:" label; $2 = RX bytes, $10 = TX bytes.
        # `read rx tx` splits that printed pair into two shell variables.
        read rx tx <<< $(awk -v iface="$INTERFACE" '$1 ~ iface":" {print $2, $10}' /proc/net/dev)
    fi

    echo "${rx}" "${tx}"
}

# Baseline totals at startup (cumulative since interface came up).
# <<< feeds count_bytes' output into read; -r disables backslash escaping.
read -r rx1 tx1 <<< "$(count_bytes)"

while true; do
  sleep 10

  # New cumulative totals after the sleep window.
  read -r rx2 tx2 <<< "$(count_bytes)"

  # Delta over the last 10s (cumulative counters only increase).
  rx_diff=$((rx2 - rx1))
  tx_diff=$((tx2 - tx1))

  echo "[traffic-meter] Inbound: $rx_diff bytes, Outbound: $tx_diff bytes (last 10s)"

  # Roll forward so the next iteration diffs against this sample.
  rx1=$rx2
  tx1=$tx2
done
