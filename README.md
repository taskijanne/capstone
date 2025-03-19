# Documentation

See "Documentation.docx" file for detailed documentation of the application

# Prerequisites

1. Docker and docker compose

# How to run

1. Optional: if you want to use OpenAI (GPT-4o) or Groq (Llama 3.3):
* Create .env file to ./backend -folder
* Add OPENAI_APIKEY and/or GROQ_APIKEY variables with correct api keys

2. To run the application go to the root folder and run:

docker compose up

# How to use

1. Open browser and go to http://localhost:3000/
2. You should see a text input and dropdown with value "custom t5-small" selected
3. If the dropdown has no values, make sure backend has been started (it takes a while for the backend to start)
4. Write something to the text field such as "how can I convert pounds to euros"
5. You should see two columns, the left column includes the search query that was optimized by chosen model.
6. The right column includes the original search query
7. Both columns list the results that were fetched from Elasticsearch with the queries
