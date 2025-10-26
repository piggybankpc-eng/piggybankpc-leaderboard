# Create Dedicated PiggyBankPC Tunnel

Run these commands:

```bash
# Create new tunnel
cloudflared tunnel create piggybankpc

# This will output a Tunnel ID like: 4c170ccf-78cc-4580-8947-cf5e6f19e339
# Save this ID!

# Create config file
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

Add this content (replace TUNNEL-ID with your actual ID):
```yaml
tunnel: TUNNEL-ID
credentials-file: /home/john/.cloudflared/TUNNEL-ID.json

ingress:
  - hostname: piggybankpc.uk
    service: http://localhost:5555
  - hostname: ap.piggybankpc.uk
    service: http://localhost:5555
  - service: http_status:404
```

Then:
```bash
# Route DNS
cloudflared tunnel route dns piggybankpc piggybankpc.uk

# Install and start service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```
