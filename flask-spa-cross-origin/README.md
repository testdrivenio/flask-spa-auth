# Flask SPA Cross Origin

### Setup the backend

1. cd server

1. Create virtual environment and install requirements
    ```bash
    pip install -r requirements.txt
    ```

1. Run the server
    ```bash
    python app.py
    ```

> The server runs on [http://localhost:5000](http://localhost:5000)

### Setup the frontend

1. cd app

1. Install the requirements
    ```bash
    npm i
    ```

1. Start the server
    ```bash
    npm run start
    ```
> The frontend runs on [http://localhost:8080](http://localhost:8080)

### How the app works

> All request/response are of type `application/json`
>  The session is managed by `Flask-Login`

- On login page, the frontend checks with the backend if a session exists.
- When a user logins, the frontend makes an API call to the server to validate credentials
- (user exists) The server creates session and stores it in cookies and sends a success response to the frontend
- The frontend then redirects the app to `/user` page.
- The `/page` checks for an active session with the server, if it exists, proceed to fetch data (this prevents unauthorized access)
- If the `/page` was loaded without session, the frontend redirects to `/` page
- On logout, the session is destroyed.

#### cookies are made available by setting `credentials: 'include'` in fetch.
