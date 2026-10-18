#!/bin/bash
# Copia /workspace/poly/*.json a data/ y hace push si cambió. Sin secretos.
cd /workspace/poly-dashboard || exit 1
while true; do
  cp /workspace/poly/{markets,paper,state,activity}.json data/ 2>/dev/null
  if ! git diff --quiet -- data/; then
    git add data/ && git commit -qm "sync datos $(date '+%F %H:%M')" && git push -q
  fi
  sleep 900
done
