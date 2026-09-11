from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
import os
import shutil
import io
import unittest
from unittest.mock import patch

FILEPATH = 'structured_restaurant_data.json'
BACKUP_PATH = 'structured_restaurant_data.json.bak'
EXAMPLE_RESTAURANT_PARAGRAPH = 'Down in **Santa Monica**, **Mar de Cortez** serves as a **sun-drenched**, **casual taqueria** specializing in **Baja-style seafood**. With a **4.2/5** rating, it captures the salt-air energy of the coast through its signature beer-battered snapper tacos and zesty octopus ceviche, making it a premier spot for open-air dining near the pier. Price range: 

## Exercise 1: Integrate the LLM model from Lesson 1

You will need the LLMs you defined in lesson 1 to structure new restaurant paragraph inputs. In addition to these functions, you will need to implement a new function `new_data_entry_process(paragraph, itemId)`, which takes inputs:

-   `paragraph`: the new restaurant paragraph;
    
-   `itemId`: the ID of this new item.
    

This new function combines and uses the generative models you defined in lesson 1 to structure a given new restaurant paragraph.

In your `restaurant_data_management.py`, copy and paste the following code block and complete the functions.

  **Important**: Take a screenshot of your implementation of the `new_data_entry_process()` and name it `M1L3_new_data_entry_process.jpg`.

```python
#Update your restaurant_data_structure_prompt_generation
def restaurant_data_structure_prompt_generation(restaurant_paragraph):
	#YOUR CODE HERE
    pass

# Might need to explain why we are using granite here (cheap)
def llm_model(system_msg, prompt_txt, params=None):
	#YOUR CODE HERE
    pass

def JSON_auto_repair_prompts(response, error_message):
	#YOUR CODE HERE
    pass

def new_data_entry_process(paragraph, itemId):
	#YOUR CODE HERE
    pass
