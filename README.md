Asynchronous Python server for logging and managing IP addresses.  

Dependencies 
- Python 3.7 or later (modern async/await constructs are used) 
- Standard Python libraries (no external dependencies) 

Installation 
1. Copy the file `sh.py ` to the appropriate directory 
2. Start the server with the command: python3 sh.py 

Configuration 
Before launching, you can configure the settings in the IpLoggerServer class: 
• addr - server address (default: '127.0.0.1') 
• port - server port (default: 8080) 
• kill_time - IP address lifetime in the database (default: 30 minutes) refresh_rate - the interval for checking outdated IP addresses (default: 60 seconds) 
• data_filepath is the path to the file with saved IP addresses. 
• log_filepath - the path to the log file 

Using 
Logging an IP address 
GET http://{host}:{port}/log Example: curl http://localhost:8080/log 
The server blocks the client's IP address and returns HTTP 200 OK. 
Getting a list of IP addresses 
GET http://{host}:{port}/get Example: curl http://localhost:8080/get 
The server returns a semicolon-separated list of active IP addresses. 

Features • Auto-save: IP addresses are saved to a file when the server is shut down correctly 
• Auto-upload: At startup, the server downloads previously saved IP addresses 
• Cleanup: Outdated IP addresses are automatically deleted after the expiration time. 
• Logging: All operations are logged to a file 
• Asynchrony: Uses modern async/await designs for efficient operation 

Data format 
IP addresses are saved in the following format: 
IP address|timestamp 
Example: 192.168.1.1|2024-01-15T10:30:00+00:00 

The process of work and how everything should look like: 
After launching, for example, from the VS terminal with the python3 command sh.py the terminal line will display: 
The server is running on 127.0.0.1:8080 
To stop, press Ctrl+C 
If you go to the browser by http://127.0.0.1:8080/log it will be just a white background – without any messages or errors. This means that the server is running in the background and is waiting for HTTP requests at /get and /log addresses. 
The logs will be saved in: C:\Users\Home-pc\OneDrive\Documents\!!! PYTHON\!!! Python server for IP request log operations\IpLogger.log 
The IP data will be in: C:\Users\Home-pc\OneDrive\Documents\!!! PYTHON\!!! Python Server for IP logging operations запроса\ipdata.txt 
This is a simple txt file and you can view the IP addresses saved by the server by opening this file, for example, in Notepad. 

Launch methods: 
1.	Through the browser (the simplest one) 
Request for IP logging: 
http://127.0.0.1:8080/log 
• Open this link in your browser 
• The server will record your IP address in the database 
• You will see in the logs: 
ip logged: 127.0.0.1 
A request to get a list of IP addresses in the browser: 
http://127.0.0.1:8080/get 
2.	The method is via the command line (PowerShell) 
IP logging: 
curl http://127.0.0.1:8080/log 
Getting the IP list: 
curl http://127.0.0.1:8080/get 

3.	The method is via a Python script Running the server (for example via VS): 
python3 sh.py 
In ANOTHER terminal, we make requests: 
curl http://127.0.0.1:8080/log # Log the IP 
curl http://127.0.0.1:8080/get # Getting the IP list 
Looking at the server logs: 
Get-Content "IpLogger.log" -Tail 10 

4.	For testing from different IP addresses (if necessary): 
If the server is accessible from the network, you can test like this:
 http://ВАШ_ВНЕШНИЙ_IP:8080/log 
http://ВАШ_ВНЕШНИЙ_IP:8080/get 
What happens in the background: 
• /log - adds the client's IP address to the database with the current time 
• /get - returns all active IP addresses (no older than 30 minutes) 
• Every 60 seconds, the server automatically cleans up the old IP addresses 
• All data is saved in ipdata.txt Completion of work To shut down the server correctly, press Ctrl+C. 

The server will automatically save the current state of the IP database. 
In VS Code, the terminal will display: 
The server is stopped... 
The browser will display the following after refreshing the page: 
Unable to access the site The 127.0.0.1 website does not allow you to establish a connection.
