#!/bin/bash
# Need to do this for Defense, Gamelogs, Games, Rosters, Teams
FILES=/Users/christianholmes/NBA/players/2015/Prices/

for f in $FILES
do
  echo "Processing $f file..."
  cd $f
  sed -i '.bak' -e 's|\]\[|\],\[|g' -e 's|^\[|[[|g' -e 's|\]$|]]|g'  *
  rm *.bak
  cd ..
  cat $f
done
