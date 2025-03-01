pdf2txt.py -o output.txt -t text -d input.pdf
pdf2txt.py -o goodOutput.txt -t text -d input.pdf
python3 main.py

diff goodOutput.txt output.txt

TODO:
    -look up LAParams, try to get extracted data more exact?

- want more info from PDF than just in this sheet?
- going forward like website and server renting
- data format going forward

1. input current sheet, output updated sheet
    -hosted on my website (?)
    -can hold logs/backups


2. connect to google sheets and automatically update
    -google account needs to be connected, maybe WASH system account?
    -could have data corruption if Tom doesn't update quick enough
    -risky
        -if bug in program, could corrupt everything
        -Tom would need to keep backups, or I could but not sustainable
    -probably more time needed
