# Flask SPA Jinja

### cd into `flask-spa-jinja` folder

1.  ```bash
    npm install
    npm run build
    ```

    This will build the frontend to `public` folder.

1.  Create virtual environment and

    ```bash
    pip install -r requirements.txt
    python app.py
    ```

### How the app works

- Same as the cross origin, except the server is calling it's own endpoints(eg: /api/login, /api/logout)

- Setup wildcard route to prevent Flask from intercepting urls

    When the user enters `localhost:5000/user` manually(bookmarked links), the Flask might intercept the route and throws error. So set wildcard route such that whatever the path be, flask must send `index.html` file.

#### cookies are made available by setting `credentials: 'include'` in fetch.
