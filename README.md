# skale-stats-collector
Agent that collects statistics from SKALE network

## Install and run

1. Create `.env` file from `template.env`
2. Put skale-manager contracts ABI into `data/abi.json`
3. Run `./run.sh`

## Environment variables

Variable| Description | Required?
-|-|-
ETH_ENDPOINT | Geth Endpoint for network | +
PROXY_DOMAIN | Domain of sChains Proxy | +
ETH_API_KEY | Key to interact with etherscan API | +
SCHAIN_NAMES | Names of the specific chains to collect statistics from | -
FLASK_APP_HOST | `0.0.0.0` by default | -
FLASK_APP_PORT | `5000` by default | -
FLASK_HOST_PORT | Port to run stats API (`3009` by default) | -
AWS_S3_BUCKET_NAME | 
AWS_REGION |
AWS_ACCESS_KEY |
AWS_SECRET_KEY |
UPTIME_KUMA_URL |

