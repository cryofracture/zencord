#!/usr/bin/env bash

# Change directory to the location of the script
cd "$(dirname "${BASH_SOURCE[0]}")" || exit

docker stop zencord_bot
docker rm zencord_bot

docker build -t cryofracture/zencord_bot bot/

docker run -d -v /zencord_bot/logs:/home/cryo/projects/python/support_scripts/zencord/logs/ --name zencord_bot cryofracture/zencord_bot
