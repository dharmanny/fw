export $PYTHONPATH="${PWD}/../../.."
coverage3 run runner.py
coverage3 html -d ./results
read -p