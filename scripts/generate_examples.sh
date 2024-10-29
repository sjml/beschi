#!/usr/bin/env bash

cd "$(dirname "$0")"
cd ..

declare -A langs
langs["c"]="h"
langs["csharp"]="cs"
langs["go"]="go"
langs["rust"]="rs"
langs["swift"]="swift"
langs["typescript"]="ts"
langs["zig"]="zig"

for lang in "${!langs[@]}"; do
  ext=${langs[$lang]}

  beschi \
    --lang $lang \
    --protocol ./test/_protocols/annotated.toml \
    --output "docs/generated_examples/${lang}_example.${ext}"
done
