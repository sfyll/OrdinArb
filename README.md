# OrdinArb
## Installation

1. **Install virtualenv**:
```bash
sudo pip install virtualenv
```
2. **Clone the repo or a fork of it**
3. **Navigate to the base repo directory and run**:
```bash
virtualenv env
```
4. **Activate your virtual environment**: 
```bash
source env/bin/activate
```
5. **Install the requirements**: 
```bash
pip install -r requirements.txt
```

## Logging transactions

The following steps cause a stream of transactions to be logged to the location specified in the DUMP_FILE_PATH constant in main.py.
The default message handlers are:
* PrintHandler: Prints incoming tx to console
* FileHandler: Writes incoming tx to file

1. **Start SSH Tunnel**:
``` ssh -N -L 28332:localhost:28332 <ordinarb>```

2. **Run main.py**:
```python main.py```

## Analayzing transactions

The following steps cause the transactions logged in the previous step to be analyzed and the results to be printed to the console.
Current analysis includes:
* Sorting by transaction bytes length
* Printing the top 10 transactions by bytes length

1. **Run analyze.py**:
```python analyze.py```
