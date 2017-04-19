init:
    pip install -r requirements.txt

test:
    sh test.sh

.PHONY: init test
