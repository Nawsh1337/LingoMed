* The folder 'Outputs' contains outputs for stanza, LLM (using groq api), and chatgpt website prompt answers to show the outputs if we use openAI api.

* How to run

1. Create a .env file and define a variable with your own key.
-   GROQ_API_KEY=YOUR_API_KEY_HERE
* No need to do the next steps unless you're testing because I've already created output files
2. run ' uv sync ' to get create venv and install dependencies
3. run ' .venv\Scripts\Activate '
4. run ' uv run src/LLM_for_grammar.py ' or ' uv run src/medical_keyword_script.py '

