cd sampleTracking_EMX/
now=$(date +"%m_%d_%Y")
find . -type f | xargs zip ../SampleTracking_EMX_$now.xlsx
