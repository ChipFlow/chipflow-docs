#!/bin/bash

repos=(
'amaranth-lang/amaranth -- -b v0.5.4'
'chipflow/amaranth-soc -- -b reference-docs-chipflow'
'chipflow/chipflow-lib'
)

rm -rf vendor/*
for r in "${repos[@]}"; do
  repo=${r%% *} 
  name=${repo##*/} 
  if [[ "${r}" =~ "--" ]] ;then
    opts="-- ${r##* --}"
  else 
    opts="" 
  fi
  echo "Cloning $repo $opts as vendor/$name"
  echo "gh repo clone $repo vendor/$name $opts >/dev/null 2>&1 "
  gh repo clone $repo vendor/$name $opts
  echo "binding in $repo docs as $name"
  rm -rf docs/source/$name
  cp -a  vendor/$name/docs docs/source/$name
  grep -lr ':doc:' docs/source/$name/* |  xargs sed -i.bak "s/:doc:/:$name:/g"
done

find docs/source -name "*.bak" -exec rm {} \;

