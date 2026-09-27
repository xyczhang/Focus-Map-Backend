# FocusMap

FocusMap is a cute and cozy study plan maker that creates plans based off of the user's deadlines and confidence level. 

## What the Backend Does
I used the FlaskAPI for the backend which sends validated user input to the OpenAI API. The OpenAI API then used the information to create the study schedules. 

### Endpoints
There are three endpoints:
1. GET / which returns basic information about the API and lists the available endpoints.
2. GET /health which checks if the backend is running.
3. POST /generate-plan which accepts the user's study preferences as JSON.

### Parameters
There are eight parameters:
1. subjects: A list containing between one and eight subjects.
2. name: The name of a subject, limited to 60 characters.
3. deadline: An optional deadline in YYYY-MM-DD format. It cannot be in the past.
4. confidence: The user’s confidence in that subject from 1 to 5, where 1 is the least confident.
5. plan_days: The desired number of planning days, from 1 to 7.
6. available_minutes: The amount of study time available per day, from 20 to 480 minutes.
7. session_minutes: The preferred length of each study session, from 10 to 120 minutes.
8. break_minutes: The preferred break length, from 1 to 30 minutes.

### Returns
The backend returns a JSON with a title for the plan, a brief summary of the plan, the total planned time, a list of study and break sessions, the day number for each session, the subject, the session length, a specific task, an explanation for why that session was included, and a randomized study tip.

## How the Frontend Communicates with the Backend
The frontend uses the browser's fetch() function to communicate with the backend. When the user clicks "Generate My Study Plan," the frontend validates the information and converts it to JSON. After, it sends a POST request to the backend's /generate-plan endpoint. The backend then generates the study plan and sends it back to the frontend, which then converts the information into a presentable format for the user.

When the frontend is waiting for the backend, the user sees the loading screen on the side. The frontend can also use the backend’s /health endpoint to confirm that the Render service is running.

## How to Set Up and Run the Backend
1. Clone the Focus-Map-Backend repository from my Github
2. Create and activate a virtual Python environment
3. Install the required packages
4. Create a .env file based on the .env.example file in my repository
5. Start the backend and then deploy it on Render

Make sure to get an OpenAI API key and insert it into the private .env file. Also, the key should be added as an Environment Variable on Render.

## How Secrets are Handled
The private OpenAI API key is privately stored in the .env file, which is not committed to Github because it's listed in the .gitignore file. On Render, the  API key is stored as an environment variable. The Flask application reads it from the environment when making an OpenAI request.

CORS is also configured through ALLOWED_ORIGINS, restricting browser requests to approved origins like my deployed Github domain so most websites can't communicate with my backend.
