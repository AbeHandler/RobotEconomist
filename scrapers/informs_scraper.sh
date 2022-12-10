for i in $(pages -b https://pubsonline.informs.org/toc/mnsc/ -m 68); do
    for var in $(seq 1 4); do
        echo $i"/"$var
    done
done



