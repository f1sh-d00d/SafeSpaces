This program assumes you have the ollama model Ollama 3.1 installed

To run the app, do the following:

1. In a terminal window, move into the project folder where you are storing this app

2. Run the command 'pip install -r requirements.txt'
	- You will only need to run this command before you run the website for the first time.

3. Open a seperate terminal window and run the command "Ollama serve"
	- If you get the error  "Error: listen tcp 127.0.0.1:11434: bind: address already in use", then you can proceed to the following steps. Just ignore the error

4. Return to the terminal window where you are in the project folder

5. Run the command 'streamlit run app.py'
	- You will then be taken to the app website where you can interact with the model.
	- Be aware that the model runs pretty slowly



Message me on teams if you have any questions


