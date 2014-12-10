for file in *.less; do
    echo $file
    filename="$(basename "$file")"
    outfile="${filename%.*}.css"
    lessc "$filename" "$outfile"
done
