#!/bin/sh

echo "[traffic-meter] Starting traffic meter..."

# 1. Dynamically find the active default interface name
if [[ "$OSTYPE" == "darwin"* ]]; then
    # For macOS
    INTERFACE=$(route -n get default | awk '/interface:/ {print $2}')
else
    # For Linux
    INTERFACE=$(ip route show default | awk '/default/ {print $5}')
fi


count_bytes() {
    local rx
    local tx
    if [[ "$OSTYPE" == "darwin"* ]]; then
        read -r rx tx <<< $(netstat -I "$INTERFACE" -b | awk 'NR==2 {print $7, $10}')
    else
        read rx tx <<< $(awk -v iface="$INTERFACE" '$1 ~ iface":" {print $2, $10}' /proc/net/dev)
    fi

    echo "${rx}" "${tx}"
}

# Get initial byte counts
read -r rx1 tx1 <<< "$(count_bytes)"

while true; do
  sleep 10

  read -r rx2 tx2 <<< "$(count_bytes)"

  rx_diff=$((rx2 - rx1))
  tx_diff=$((tx2 - tx1))

  echo "[traffic-meter] Inbound: $rx_diff bytes, Outbound: $tx_diff bytes (last 10s)"

  rx1=$rx2
  tx1=$tx2
done