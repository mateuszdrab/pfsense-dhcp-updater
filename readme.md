# DHCP Updater

`dhcp_updater.py` is a script designed to update DNS records based on DHCP leases from a pfSense firewall. It processes DHCP leases and updates the corresponding DNS A, PTR, and TXT records using anonymous updates to the DNS server. This works with Windows DNS servers once the zone is configured to allow anonymous updates.

## Requirements

- Python 3.x
- `pypfsense` library
- `dnspython` library
- `PyYAML` library

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/mateuszdrab/pfsense-dhcp-updater.git
    cd pfsense-dhcp-updater
    ```

2. Install the required Python libraries from the `requirements.txt` file:

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

Create a `config.yaml` file in the root directory with the following structure:

```yaml
dns_server: "your_dns_server_ip"
zone: "your_dns_zone"
sites:
  "10": "site1"
  "20": "site2"
pfsense:
  url: "https://your_pfsense_url"
  username: "your_pfsense_username"
  password: "your_pfsense_password"
  verify_ssl: false # Set to true if you want to verify the SSL certificate
```

# Sites Mapping

The code includes functionality to map different sites, which can be useful when one DHCP server is serving multiple sites or locations. The sites are mapped based on the third octet of the IP address, allowing for easy identification and handling of IP addresses based on their site or location.

# Records example

For a lease with name example-lease and IP address 192.23.45.67 and the domain example.com, the following records will be created:

- A record: example-lease.example.com with the IP address 192.23.45.67
- TXT record: example-lease.example.com with the MAC address of the lease
- PTR record: a PTR record for 67 in the 45.23.192.in-addr.arpa zone pointing to example-lease.example.com

## Usage

Run the script with the configuration file as an argument:

```sh
python app/app.py config.yaml
```

If no configuration file is provided, the script will default to `config.yaml`.

# Output

The script will output each obtained lease and the corresponding DNS records that were created or updated. The output will be in json format and therefore can be processed further if needed using other tools or scripts.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
