import pypfsense
from dns import update, query, rcode, resolver
from datetime import datetime
import json
import yaml
import sys

# Get config file path from YAML file from args if provided

if len(sys.argv) > 1:
    _config_path = sys.argv[1]
else:
    _config_path = "config.yaml"

# Load configuration from YAML file
with open(_config_path, "r") as config_file:
    config = yaml.safe_load(config_file)

_dns_server = config["dns_server"]
_sites = config["sites"]
_zone = config["zone"]
_pfsense_config = config["pfsense"]


def update_dns(record_name, record_type, record_ttl, record_value, record_zone=_zone):
    # Create an update message
    update_record = update.Update(record_zone)

    # Add record
    update_record.replace(record_name, record_ttl, record_type, record_value)

    # Send the update to the DNS server
    response = query.tcp(update_record, _dns_server)  # Use UDP instead of TCP if needed

    # Return record details and response rcode
    return {  # Record details
        "name": record_name,
        "type": record_type,
        "ttl": record_ttl,
        "value": record_value,
        "zone": record_zone,
        # Response rcode
        "rcode": rcode.to_text(response.rcode()),
    }


def process_lease(lease):
    # Leaase as json
    lease_json = json.dumps(lease)

    # Configuration
    ip = lease["ip"]
    octet = ip.split(".")[2]
    site = _sites[octet]
    ttl = 300
    record_name_a = lease["hostname"] + "." + site + ".cctv"
    record_name_ptr = lease["ip"].split(".")[3]

    lease["update_dns"] = {"a": {}, "ptr": {}, "txt": {}}

    # Update DNS A record
    lease["update_dns"]["a"] = update_dns(record_name_a, "A", ttl, ip)

    # Update DNS TXT record with lease MAC address
    lease["update_dns"]["txt"] = update_dns(record_name_a, "TXT", ttl, lease["mac"])

    # Update DNS PTR record
    lease["update_dns"]["ptr"] = update_dns(
        record_name_ptr,
        "PTR",
        ttl,
        record_name_a + "." + _zone + ".",
        octet + ".168.192.in-addr.arpa",
    )

    # Leaase as json
    lease_json = json.dumps(lease)

    # Print lease
    print(lease_json)


# Create a connection to the pfSense firewall
pfsense = pypfsense.Client(
    _pfsense_config["url"],
    _pfsense_config["username"],
    _pfsense_config["password"],
    # Get the verify_ssl option from the config file
    opts=(
        {"verify_ssl": _pfsense_config["verify_ssl"]}
        if "verify_ssl" in _pfsense_config
        else {}
    ),
)

leases = pfsense.get_dhcp_leases()

# Filter leases with no hostname or empty hostname and 3rd octet in IP address is in _sites
filtered_leases = [
    lease
    for lease in leases
    if lease["hostname"]
    and lease["hostname"] != ""
    and lease["ip"].split(".")[2] in _sites.keys()
]

# Loop through filtered leases and process them
for lease in filtered_leases:
    process_lease(lease)
