# Marias Server

## Setup & Run
Server is run by **Python 3.8.5** for 64-bit.

### Linux
1) install anaconda
2) open anaconda-navigator
3) click on environments -> import environment -> open the environment.yml file, call the environment marias-sever for example.
4) in Terminal, type `conda activate marias-server` to use the correct environment. (It will only be used in that terminal window. Remember to type `conda activate marias-server` each time before testing if you shut off computer etc.)
5) run server:
    1) locally with emulator: run server with `uvicorn main:app --reload` and client has to connect to localhost (in android connect to ip address 10.0.2.2, port is default in this case 8000)
    2) via LAN using client on phone - `uvicorn main:app --host YOUR_IP_ADDRESS --port 8000 --reload` and client has to connect to YOUR_IP_ADDRESS

### Other OS
1) set a [virtual environment](https://virtualenv.pypa.io/en/latest/) 
2) install requirements via `pip install -r requirements.txt`
3) run server:
    1) locally with emulator: run server with `uvicorn main:app --reload` and client has to connect to localhost (in android connect to ip address 10.0.2.2, port is default in this case 8000)
    2) via LAN using client on phone - `uvicorn main:app --host YOUR_IP_ADDRESS --port 8000 --reload` and client has to connect to YOUR_IP_ADDRESS
 
## DATABASE

based on https://fastapi.tiangolo.com/tutorial/sql-databases/

### Development

`git push staging main` pushes the code to the staging app on heroku. This allows us to test that everything works well in the online heroku environment before pushing our changes to production.

`git push production main` pushes the code to the production app on heroku.