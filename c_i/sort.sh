for file in ../langnames/ln_*
do
  temp_file=$(mktemp)
  sort "$file" > "$temp_file"
  mv "$temp_file" "$file"
done
