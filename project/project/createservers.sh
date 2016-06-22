for i in "Alford" "Bolden" "Hamilton" "Parker" "Powell"
do
	echo Create server: $i
	python server.py $i &
done