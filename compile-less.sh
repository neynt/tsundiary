for file in $(find tsundiary/static | grep '\.less$'); do
    echo $file
    filename=$file
    outfile="${filename%.*}.css"
    lessc "$filename" "$outfile" &
    #echo $filename
    #echo $outfile
done
# waits for lessc to finish
wait
echo "Done."
