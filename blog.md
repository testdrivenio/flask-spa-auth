# Session-based Auth with Flask for Single Page Apps

In this article, we'll look at how to authenticate [Single-Page Applications](https://en.wikipedia.org/wiki/Single-page_application) (SPAs) with session-based authentication. We're going to use [Flask](https://flask.palletsprojects.com/) as our backend with [Flask-Login](https://flask-login.readthedocs.io/) for managing sessions. The frontend will be built with [Svelte](https://svelte.dev/), a JavaScript frontend framework designed for building rich user interfaces.

> Feel free to swap out Svelte for a different tool like Angular, Vue, or React.

## Session vs. Token-based Auth

### What Are They?

With session-based auth, a session is generated and the ID is stored in a cookie.

After logging in, the server validates the credentials. If valid, it generates a session, stores it, and then sends the session ID back to the browser. The browser stores the session ID as a cookie, which gets sent anytime a request is made to the server.

TODO: add image

Session-based auth is stateful. Each time a client requests the server, the server must locate the session in memory in order to tie the session ID back to the associated user.

Token-based auth, on the other hand, is relatively new compared to session-based auth. It gained traction with the rise of SPAs and RESTful APIs.

After logging in, the server validates the credentials and, if valid, creates and sends back a signed token to the browser. In most cases, the token is stored in localStorage. The client then adds the token to the header when a request is made to the server. Assuming the request came from an authorized source, the server decodes the token and checks its validity.

TODO: add image

A token is a string that encodes user information.

For example:


```json
// token header
{
  "alg": "HS256",
  "typ": "JWT"
}

// token payload
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

The token can be verified and trusted because it is digitally signed using a secret key or public/private key pair. The most common type of token is a [JSON Web Token](https://jwt.io/) (JWT).

Since the token contains all information required for the server to verify a user's identity, token-based auth is stateless.

> For more on sessions and tokens, check out [Session Authentication vs Token Authentication](https://security.stackexchange.com/questions/81756/session-authentication-vs-token-authentication) from Stack Exchange.

### Security Vulnerabilities

As mentioned, session-based auth maintains the state of the client in a cookie. While JWTs can be stored in localStorage or a cookie, most token-based auth implementations store the JWT in localStorage. Both of these methods come with potential security issues:

| Storage Method | Security Vulnerability                                                            |
|----------------|-----------------------------------------------------------------------------------|
| Cookie         | [Cross Site Request Forgery](https://owasp.org/www-community/attacks/csrf) (CSRF) |
| localStorage   | [Cross-Site Scripting](https://owasp.org/www-community/attacks/xss/) (XSS)        |


CSRF is an attack against a web application in which the attacker attempts to trick an authenticated user into performing a malicious action. Most CSRF attacks target web applications that use cookie-based auth since web browsers include all of the cookies associated with each request's particular domain. So when a malicious request is made, the attacker can easily make use of the stored cookies.

> To learn more about CSRF and how to prevent it in Flask, check out the [CSRF Protection in Flask](/blog/csrf-flask/) article.

XSS attacks are a type of injection where malicious scripts are injected into the client-side, usually to bypass the browser's same-origin policy. Web applications that store tokens in localStorage are open to XSS attacks. Open a browser and navigate to any site. Open the console in developer tools and type `JSON.stringify(localStorage)`. Press enter. This should print the localStorage elements in a JSON serialized form. It's that easy for a script to access localStorage.

> For more on where to store JWTs, check out [Where to Store your JWTs – Cookies vs. HTML5 Web Storage](https://stormpath.com/blog/where-to-store-your-jwts-cookies-vs-html5-web-storage).

## Setting up Session-based Auth

There are essentially three different approaches to combine Flask with a frontend framework:

1. Serve up the framework via a Jinja template
1. Serve up the framework separately from Flask on the same domain
1. Serve up the framework separately from Flask on a different domain

> Again, feel free to swap out Svelte for the frontend of your choice -- i.e., Angular, React, or Vue.

## Frontend Served From flask

With this approach, we'll build the frontend and serve up the generated *index.html* file with Flask.

Assuming, you have [Node](https://nodejs.org/en/download/package-manager/) and [npm](https://www.npmjs.com/get-npm) installed, create a new project via the official [Svelte project template](https://github.com/sveltejs/template):

```bash
$ npx degit sveltejs/template flask-spa-jinja
$ cd flask-spa-jinja
```

Install the dependencies:

```bash
$ npm install
```

Create a file to hold the flask app called *app.py*:

```bash
$ touch app.py
```

Install Flask, Flask-Login, and [Flask-WTF](https://flask-wtf.readthedocs.io/):

```bash
$ python3.9 -m venv env
$ source env/bin/activate
$ pip install Flask==1.1.2 Flask-Login==0.5.0 Flask-WTF==0.14.3
```

Add a "templates" folder and move the *public/index.html* file to it. Your project structure should now look like this:

```bash
├── .gitignore
├── README.md
├── app.py
├── package-lock.json
├── package.json
├── public
│   ├── favicon.png
│   └── global.css
├── rollup.config.js
├── scripts
│   └── setupTypeScript.js
├── src
│   ├── App.svelte
│   └── main.js
└── templates
    └── index.html
```

### Flask Backend

The app has the following routes:

1. `/` serves up the *index.html* file
1. `/api/login` logs a user in and generates a session
1. `/api/data` fetches user data for an authenticated user
1. `/api/getsession` checks whether a session exists
1. `/api/logout` logs a user out

Grab the full code [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-jinja/app.py) and add it to the *app.py* file.

Take note of the handler for the `/` route:

```python
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def home(path):
    return render_template("index.html")
```

Since Flask is ultimately serving up the SPA, the CSRF cookie will be set automatically.

Turn to the config:

```python
app.config.update(
    DEBUG=True,
    SECRET_KEY="secret_sauce",
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)
```

The `HttpOnly` flag set to `True` prevents any client-side usage of the session cookie:

```python
SESSION_COOKIE_HTTPONLY=True,
REMEMBER_COOKIE_HTTPONLY=True,
```

We also prevented cookies from being sent from any external requests by setting `SESSION_COOKIE_SAMESITE` to `Strict`.

For more on these config options, review [Set-Cookie options](https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options) from the Flask docs.

> Make sure to set `SESSION_COOKIE_SECURE` and `REMEMBER_COOKIE_SECURE` to `True` to limit the cookies to HTTPS traffic only for production.

Update *templates/index.html* to load the static files via `url_for`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <meta name="csrf-token" content="{{ csrf_token() }}" />

  <title>Svelte app</title>

  <link rel='icon' type='image/png' href="{{url_for('static', filename='favicon.png')}}">
  <link rel='stylesheet' href="{{url_for('static', filename='global.css') }}">
  <link rel='stylesheet' href="{{url_for('static', filename='build/bundle.css') }}">

  <script defer src="{{url_for('static', filename='build/bundle.js') }}"></script>
</head>

<body>
</body>
</html>
```

The `csrf-token` meta tag holds the CSRF token generated by the Flask application.

### Svelte Frontend

The frontend will have a single component that displays either a login form (when the user is unauthenticated) or a simple "You are authenticated!" message (when the user is authenticated).

Grab the full code [here](https://github.com/testdrivenio/flask-spa-auth/blob/master/flask-spa-jinja/src/App.svelte) and add it to the *src/App.svelte* file.

Take note of: `credentials: "same-origin"` from each of the `fetch` requests. This will send along the cookies if the URL is on the same origin as the calling script.

For example:

```javascript
const whoami = () => {
  fetch("/api/data", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf,
    },
    credentials: "same-origin",
  })
  .then((res) => res.json())
  .then((data) => {
    console.log(data);
    alert(`Welcome, ${data.username}!`);
  })
  .catch((err) => {
    console.log(err);
  });
};
```

Where does the CSRF token come from?

We added it to the meta tag in *templates/index.html*:

```html
<meta name="csrf-token" content="{{ csrf_token() }}" />
```

We then assigned the CSRF token to the `csrf` variable when the `App` component mounts:

```javascript
let csrf = document.getElementsByName("csrf-token")[0].content;
```

Next, update *src/main.js*:

```javascript
import App from './App.svelte';

const app = new App({
  target: document.body,
});

export default app;
```

When the application is compiled, the code from the *App.svelte* file gets separated into JavaScript and CSS files. These files are then injected into *src/index.html*, which serves as our SPA. In this case, we created a new app and loaded it into the whole HTML body using `target: document.body`.

### Test

That's it! We're ready to test.

Create a new build, and then run Flask:

```bash
$ npm run build
$ python app.py
```

Navigate to [http://localhost:5000](http://localhost:5000). You should see:

TODO: add image

You can log in with:

- username: `test`
- password: `test`

Once logged in you can see the session cookie from the console and the value of the CSRF token in the HTML source:

TODO: add images

What happens if the session cookie is invalid?

TODO add image

You can find the final code for this approach [here](https://github.com/testdrivenio/flask-spa-auth/tree/master/flask-spa-jinja).

## Frontend Served Separately (Same domain)

With this approach, we'll build the frontend and serve it up separately from the Flask app on the same domain. We'll use Docker and Nginx to serve up both apps on the same domain locally.

The big difference with this approach over the Jinja approach is that you'll have to make an initial request to obtain a CSRF token since it won't get set automatically.

Start by creating a project directory:

```bash
$ mkdir flask-spa-same-origin && cd flask-spa-same-origin
```

Now, create a folder for the backend:

```bash
$ mkdir backend && cd backend
```

Create a file to hold the flask app called *app.py*:

```bash
$ touch app.py
```

Add a *requirements.txt* file as well to install Flask, Flask-Login, and Flask-WTF:

```
Flask==1.1.2
Flask-Login==0.5.0
Flask-WTF==0.14.3
```

Back in the project root, assuming, you have [Node](https://nodejs.org/en/download/package-manager/) and [npm](https://www.npmjs.com/get-npm) installed, create a new project via the official [Svelte project template](https://github.com/sveltejs/template):

```bash
$ npx degit sveltejs/template frontend
$ cd frontend
```

Install the dependencies:

```bash
$ npm install
```

Your project structure should now look like this:

```bash
├── backend
│   ├── app.py
│   └── requirements.txt
└── frontend
    ├── .gitignore
    ├── README.md
    ├── package-lock.json
    ├── package.json
    ├── public
    │   ├── favicon.png
    │   ├── global.css
    │   └── index.html
    ├── rollup.config.js
    ├── scripts
    │   └── setupTypeScript.js
    └── src
        ├── App.svelte
        └── main.js
```

### Flask Backend

The app has the following routes:

1. `/api/ping` serves a quick sanity check
1. `/api/getcsrf` returns a CSRF token in the response header
1. `/api/login` logs a user in and generates a session
1. `/api/data` fetches user data for an authenticated user
1. `/api/getsession` checks whether a session exists
1. `/api/logout` logs a user out

Grab the full code [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-same-origin/backend/app.py) and add it to the *backend/app.py* file.

Take note of:

```python
@app.route("/api/getcsrf", methods=["GET"])
def get_csrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    response.headers.set("X-CSRFToken", token)
    return response
```

Here, we create a CSRF token and set it in the response header.

### Svelte Frontend

The component again will display either a login form for unauthenticated users or a simple "You are authenticated!" message for authenticated users.

Grab the full code [here](https://github.com/testdrivenio/flask-spa-auth/blob/master/flask-spa-same-origin//src/App.svelte) and add it to the *frontend/src/App.svelte* file.

With the current approach, since the backend and frontend are decoupled, we have to manually get the token from the backend, via the `/api/getcsrf` endpoint, and store it in memory:

```javascript
const csrf = () => {
  fetch("/api/getcsrf", {
    credentials: "same-origin",
  })
  .then((res) => {
    csrfToken = res.headers.get(["X-CSRFToken"]);
    // console.log(csrfToken);
  })
  .catch((err) => {
    console.log(err);
  });
}
```

This function is called after the component mounts.

Next, update *frontend/src/main.js*:

```javascript
import App from './App.svelte';

const app = new App({
  target: document.body,
});

export default app;
```

### Docker

Next, let's Dockerize our apps.

#### Frontend and Backend

*frontend/Dockerfile*:

```Dockerfile
# pull the official base image
FROM node:15.2.0-alpine

# set working directory
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH
ENV HOST=0.0.0.0

# install and cache app dependencies
COPY package.json .
COPY package-lock.json .
RUN npm ci
RUN npm install svelte@3.0.0 -g --silent

# start app
CMD ["npm", "run", "dev"]
```

*backend/Dockerfile*:

```Dockerfile
# pull the official base image
FROM python:3.9.0-slim-buster

# set the working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .

# start app
CMD ["python", "app.py"]
```

Add a *docker-compose.yml* file to the project root to tie the two apps together:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/usr/src/app
    expose:
      - 5000

  frontend:
    stdin_open: true
    build: ./frontend
    volumes:
      - ./frontend:/usr/src/app
      - /usr/src/app/node_modules
    expose:
      - 5000
    depends_on:
      - backend
```

#### Nginx

In order to run both apps on the same domain, let's add a container for Nginx that works as our reverse proxy. Create a new folder in the project root called "nginx".

*nginx/Dockerfile*

```Dockerfile
FROM nginx:latest
COPY ./nginx.conf /etc/nginx/nginx.conf
```

Add a *nginx/nginx.conf* configuration file as well. You can find the code for it [here](https://github.com/testdrivenio/flask-spa-auth/blob/master/flask-spa-same-origin/nginx/nginx.conf).

Take note of the two [location](https://nginx.org/en/docs/http/ngx_http_core_module.html#location) blocks:

```nginx
location /api {
  proxy_pass              http://backend:5000;
  ...
}

location / {
  proxy_pass              http://frontend:5000;
  ...
}
```

Requests to `/` will be forwarded to the `http://frontend:5000` (`frontend` is the name of the service from the Docker Compose file) while requests to `/api` will be forwarded to the `http://backend:5000` (`backend` is the name of the service from the Docker Compose file).

Add the service to the *docker_compose.yml* file:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    volumes:
      - ./backend:/usr/src/app
    expose:
      - 5000

  frontend:
    stdin_open: true
    build: ./frontend
    volumes:
      - ./frontend:/usr/src/app
      - /usr/src/app/node_modules
    expose:
      - 5000
    depends_on:
      - backend

  reverse_proxy:
    build: ./nginx
    ports:
      - 81:80
    depends_on:
      - backend
      - frontend
```

Your project structure should now look like this:

```bash
├── backend
│   ├── .env
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml
├── frontend
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   │   ├── favicon.png
│   │   ├── global.css
│   │   └── index.html
│   ├── rollup.config.js
│   ├── scripts
│   │   └── setupTypeScript.js
│   └── src
│       ├── App.svelte
│       └── main.js
└── nginx
    ├── Dockerfile
    └── nginx.conf
```

### Test

Build the images and run the containers:

```bash
$ docker-compose up -d --build
```

Navigate to [http://localhost:81](http://localhost:81). You should see:

TODO: add image

You can log in with:

- username: `test`
- password: `test`

TODO: add images

What happens if the session cookie is invalid?

TODO add image

You can find the final code for this approach [here](https://github.com/testdrivenio/flask-spa-auth/tree/master/flask-spa-same-origin).

## Frontend Served Separately (cross-domain)

With this approach, we'll build the frontend and serve it up separately from the Flask app on a different domain. We'll have to relax the security a bit by allowing cross-domain requests from the frontend with [Flask-CORS](https://flask-cors.readthedocs.io/).

Start by creating a project directory:

```bash
$ mkdir flask-spa-same-origin && cd flask-spa-same-origin
```

Now, create a folder for the backend:

```bash
$ mkdir backend && cd backend
```

Create a file to hold the flask app called *app.py*:

```bash
$ touch app.py
```

Install Flask, Flask-Login, Flask-WTF, and Flask-CORS:

```bash
$ python3.9 -m venv env
$ source env/bin/activate
$ pip install Flask==1.1.2 Flask-Login==0.5.0 Flask-WTF==0.14.3 Flask-Cors==3.0.9
```

Back in the project root, assuming, you have [Node](https://nodejs.org/en/download/package-manager/) and [npm](https://www.npmjs.com/get-npm) installed, create a new project via the official [Svelte project template](https://github.com/sveltejs/template):

```bash
$ npx degit sveltejs/template frontend
$ cd frontend
```

Install the dependencies:

```bash
$ npm install
```

Your project structure should now look like this:

```bash
├── backend
│   └── app.py
└── frontend
    ├── .gitignore
    ├── README.md
    ├── package-lock.json
    ├── package.json
    ├── public
    │   ├── favicon.png
    │   ├── global.css
    │   └── index.html
    ├── rollup.config.js
    ├── scripts
    │   └── setupTypeScript.js
    └── src
        ├── App.svelte
        └── main.js
```

### Flask Backend

The app has the following routes:

1. `/api/ping` serves a quick sanity check
1. `/api/getcsrf` returns a CSRF token in the response header
1. `/api/login` logs a user in and generates a session
1. `/api/data` fetches user data for an authenticated user
1. `/api/getsession` checks whether a session exists
1. `/api/logout` logs a user out

Grab the full code [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-cross-origin/backend/app.py) and add it to the *backend/app.py* file.

First, to enable CORS, we had to configure the server to return the appropriate headers:

```python
cors = CORS(
    app,
    resources={r"*": {"origins": "http://localhost:8080"}},
    expose_headers=["Content-Type", "X-CSRFToken"],
    supports_credentials=True,
)
```

Notes:

1. `resources={r"*": {"origins": "http://localhost:8080"}}` enables cross-domain requests for all routes and HTTP methods from `"http://localhost:8080`.
1. `expose_headers=["Content-Type", "X-CSRFToken"]` indicates that the `Content-Type` and `X-CSRFToken` headers can be exposed.
1. `supports_credentials=True` allows cookies to be sent cross-domain.

Headers:

```
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Expose-Headers: Content-Type, X-CSRFToken
Access-Control-Allow-Credentials: true
```

Did you notice that `SESSION_COOKIE_SAMESITE` is set to `Lax`?

```python
SESSION_COOKIE_SAMESITE="Lax",
```

If we had left it as `Strict`, no cookies would be sent from the frontend. As the name suggests, `Lax` looses security a bit so that cookies wll be sent cross-domain for the majority of requests.

Review [Set-Cookie options](https://flask.palletsprojects.com/en/1.1.x/security/#set-cookie-options) from the Flask docs for more on this.

### Svelte Frontend

Grab the full code [here](https://github.com/testdrivenio/flask-spa-auth/blob/master/flask-spa-cross-origin//src/App.svelte) and add it to the *frontend/src/App.svelte* file.

The only change here from the same domain approach is that `credentials: "same-origin"` was changed to `credentials: "include"` so that cookies are still sent along even though the request URL is on different domain.

```javascript
credentials: "include",
```

### Test

Spin up the Flask app:

```bash
$ python app.py
```

Then, in a different terminal window, run Svelte:

```bash
$ npm run dev
```

Navigate to [http://localhost:8080](http://localhost:8080). You should see:

TODO: add image

You can log in with:

- username: `test`
- password: `test`

TODO: add images

What happens if the session cookie is invalid?

TODO add image

You can find the final code for this approach [here](https://github.com/testdrivenio/flask-spa-auth/tree/master/flask-spa-cross-origin).

## Conclusion

This article detailed how to set up session-based authentication for Single-Page Applications. Whether you use session cookies or tokens, it's good to use cookies for authentication when the client is a browser. While it's preferable to serve up both apps from the same domain, you can serve them on different domains by relaxing the cross-domain security settings.

We looked at three different approaches for combining Flask with a frontend framework with session-based auth:

| Approach                                  | Frontend                                                                                     | Backend                                                                                                                                                                                                                |
|-------------------------------------------|----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Frontend Served From flask                | Grab CSRF token from the meta tag and use `credentials: "same-origin"` in the fetch request. | Set `SESSION_COOKIE_HTTPONLY` and `REMEMBER_COOKIE_HTTPONLY` to `True` and `SESSION_COOKIE_SAMESITE` to `"Strict"`.                                                                                                    |
| Frontend Served Separately (same domain)  | Obtain CRSF token and use `credentials: "same-origin"` in the fetch request.                 | Add a route handler for generating CSRF token that gets set in the response headers. Set `SESSION_COOKIE_HTTPONLY` and `REMEMBER_COOKIE_HTTPONLY` to `True` and `SESSION_COOKIE_SAMESITE` to `"Strict"`.               |
| Frontend Served Separately (cross-domain) | Obtain CRSF token and use `credentials: "include"` in the fetch request.                     | Enable CORS and add a route handler for generating CSRF token that gets set in the response headers. Set `SESSION_COOKIE_HTTPONLY` and `REMEMBER_COOKIE_HTTPONLY` to `True` and `SESSION_COOKIE_SAMESITE` to `"Lax"`. |

Grab the code from the [flask-spa-auth](https://github.com/testdrivenio/flask-spa-auth) repo.
