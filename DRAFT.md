# Session-based Auth with Flask for Single Page Apps


This article will look at how to authenticate Single-Page Applications (SPAs) with session-based authentication. We're going to use Flask as our backend with Flask-Login for managing sessions. The frontend will be built with Svelte, a JavaScript framework designed for building rich user interfaces.

## Session vs. Token-based Auth

### What Are they?

With session-based auth, a session ID is stored in a cookie.

After logging in, the server validates the credentials. If valid, it generates a session ID, stores it, and then sends it back to the browser. The browser stores the session ID as a cookie, which gets sent anytime a request is made to the server.

Session-based auth is stateful. Each time a client requests the server, the server must locate the session ID to find the auth info to tie the session ID back to the associated user.

Token-based auth, on the other hand, is relatively new compared to session-based auth. It gained traction with the rise of Single Page Applications(SPAs) and RESTful APIs.

A token is a string that encodes some information. The token can be verified and trusted because it is digitally signed using a secret(passcode) or public/private key pair. The most common type of token is a JSON Web Tokens (JWT).

> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

<small>source: [jwt.io](https://jwt.io/)</small>

This is an example of a token. This token contains the following information.


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

After logging in, the server validates the credentials and, if valid, creates and sends back a signed token to the browser. In most cases, the token is stored in localStorage. The client then adds the token to the header when a request is made to the server. Assuming the request came from an authorized source, the server decodes the token and checks its validity.

Since the token contains all information required for the server to verify a user's identity, token-based auth is stateless.

### Security Vulnerabilities

As mentioned, session-based auth maintains the state of the client in a cookie. While JWTs can be stored in localStorage or a cookie, most token-based auth implementations store the JWT in localStorage. Both of these methods come with potential security issues:

| Storage Method | Security Vulnerability                                                            |
|----------------|-----------------------------------------------------------------------------------|
| Cookie         | [Cross Site Request Forgery](https://owasp.org/www-community/attacks/csrf) (CSRF) |
| localStorage   | [Cross-Site Scripting](https://owasp.org/www-community/attacks/xss/) (XSS)        |


CSRF is an attack against a web application in which the attacker attempts to trick an authenticated user into performing a malicious action. Most CSRF attacks target web applications that use cookie-based auth since web browsers include all of the cookies associated with each request's particular domain. So when a malicious request is made, the attacker can easily make use of the stored cookies.

> To learn more about CSRF and how to prevent it in Flask, check out the [/blog/csrf-flask/](CSRF Protection in Flask) article.

XSS attacks are a type of injection where JavaScript code into the client-side, usually to bypass the browser's same-origin policy. Web applications that store tokens in localStorage are open to XSS attacks. Open a browser and navigate to any site. Open the console in developer tools and type `JSON.stringify(localStorage)`. Press enter. This should print the localStorage elements in a JSON serialized form. It's that easy for a script to access localStorage.

> For more on where to store JWTs, check out [Where to Store your JWTs – Cookies vs. HTML5 Web Storage](https://stormpath.com/blog/where-to-store-your-jwts-cookies-vs-html5-web-storage).

## Setting up Session-based Auth

There are essentially three different ways to combine Flask with a frontend framework:

1. Serve up the framework via a Jinja template
1. Serve up the framework separately from Flask on a different domain
1. Serve up the framework separately from Flask on the same domain

Feel free to swap out Svelte for the frontend of your choice -- i.e., React, Angular, or Vue.

## Flask and Svelte Served via Jinja

With this approach, we'll build the frontend and serve the *index.html* file with Flask.

Assuming, you have [Node](https://nodejs.org/en/download/package-manager/) and [npm](https://www.npmjs.com/get-npm) installed, create a new project via the official [Svelte project template](https://github.com/sveltejs/template):

```bash
$ npx degit sveltejs/template flask-spa-jinja
$ cd flask-spa-jinja
```

Install the dependencies:

```bash
$ npm install
```

Install [Page.js](https://github.com/visionmedia/page.js) as well for client-side routing:

```bash
$ npm install page
```

Create a file to hold the flask app called *app.py*:

```bash
$ touch app.py
```

Install Flask and Flask-Login:

```bash
$ python3.9 -m venv env
$ source env/bin/activate
$ pip install Flask==1.1.2 Flask-Login==0.5.0 python-dotenv==0.15.0
```

Installing `python-dotenv` let's us load variables from `.env` files. Once done, we load the env variables by setting `load_dotenv=True` in `app.run()`.

Add a "templates" folder and move the *index.html* file to it. Your project directory should now look like:

```bash
├── .gitignore
├── README.md
├── app.py
├── package-lock.json
├── package.json
├── public
│   ├── favicon.png
│   └── global.css
├── rollup.config.js
├── scripts
│   └── setupTypeScript.js
├── src
│   ├── App.svelte
│   └── main.js
└── templates
    └── index.html
```

### Flask Backend

Our app will have the following routes:

1. `/` serves up the *index.html* file
1. `/api/login` logs a user in and generates a session
1. `/api/data` fetches user data for an authenticated user
1. `/api/logout` logs a user out
1. `/api/getsession` checks whether a session exists

Grab the full code from [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-jinja/app.py) and add it to the *app.py* file.

We need to set up environment variables for our cookie configuration. Create a `.env` file with the following configuration.

```env
SESSION_COOKIE_HTTPONLY = True 
REMEMBER_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE='Lax'
```

The HttpOnly flag set to true makes the cookies inaccessible to javascript. Flask set them by default. 

Update *templates/index.html* to use load the static files via `url_for`:

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

The `csrf-token` meta tag holds the csrf token generated by the Flask application. This is important to secure our cookies from being hijacked.

### Svelte Frontend

We'll have two different pages: one for logging in and the other for viewing use data.

#### Login Page

Let's start with the login page.

Modify the *App.svelte* file in src directory:

```jsx
<script>
  let username;
  let password;
  let isAuthenticated = false;
  let csrf = document.getElementsByName("csrf-token")[0].content;

  const login = () => {
    fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf,
      },
      credentials: "same-origin",
      body: JSON.stringify({ username: username, password: password }),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if (data.login == true) {
          isAuthenticated = true;
        }
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const logout = () => {
    fetch("/api/logout", {
      credentials: "same-origin",
    })
      .then(() => {
        isAuthenticated = false;
      })
      .catch((err) => {
        console.log(err);
      });
  };
</script>

<style>
  .container {
    padding-top: 10%;
  }
</style>

<center>
  <div class="container">
    {#if isAuthenticated}
      <h1>You are authenticated!</h1>
      <button type="button" on:click={logout}>logout</button>
      <br /><br />
    {:else}
      <h1>Log in</h1>
      <form id="form">
        username:
        <input type="text" bind:value={username} />
        <br /><br />
        password:
        <input type="password" bind:value={password} /><br /><br />
        <button type="button" on:click={login}>login</button>
      </form>
      <br /><br />
    {/if}
  </div>
</center>
```

What's happening?

Well, we have a simple form that takes a username and password. On button click, the credentials are sent to `/api/login` on the server. Turn to the route handler for `/api/login`. If the credentials are valid, `{"login": True}` is returned:

```python
return jsonify({"login": True})
```

If the login value returned is `true`, the app sets isAuthenticated to true and loads the HTML defined inside the `{#if isAuthenticated}` part.

Take note of:

```javascript
credentials: "same-origin",
```

This will send along the cookies if the URL is on the same origin as the calling script.

Remember the `{{ csrf_token() }}` in *templates/index.html?* We grab the csrf token when the App component loads.

```jsx
let csrf = document.getElementsByName("csrf-token")[0].content;
```

Next, update *src/main.js* like so:

```javascript
import App from './App.svelte';

const app = new App({
  target: document.body,
});

export default app;
```

Once the application is compiled, the code we write into `.svelte` gets compiled into `js` and `CSS`. These files are loaded into the `public/index.html` file, which serves as our SPA. In this case, we created a new app and loaded it into the whole HTML body using `target: document.body`. One can also create a div and run our SPA in that div. 

#### Test

That's it! We're ready to test.

Create a new build, then run Flask:

```bash
$ npm run build
$ python app.py
```

Navigate to [http://localhost:5000](http://localhost:5000). You should see:

![login](images/login.gif "cross origin demo")

Since the server manages the cookies, even if there is a wrong cookie value, the server return `false`, and the user stays logged out.

## Flask and Svelte Served Separately (Same-domain)

With this approach, set up Flask and Svelte separately to serve up cross-domain on different ports.

Start by creating a project directory:

```bash
$ mkdir flask-spa-cross-origin && cd flask-spa-cross-origin
```

Now, create a folder for the backend:

```bash
$ mkdir backend && cd backend
```

Create a file to hold the flask app called *app.py*:

```bash
$ touch app.py
```

Also, create the extra configuration for the server to handle sessions. Create a `.env` file in the server directory.

```env
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE=None
```

Install Flask, Flask-Login, and Flask-Cors:

```bash
$ python3.9 -m venv env
$ source env/bin/activate
$ pip install Flask==1.1.2 Flask-Login==0.5.0 Flask-Cors==3.0.9 python-dotenv==0.15.0
```

Installing `python-dotenv` let's us load variables from `.env` files. Once done, we load the env variables by setting `load_dotenv=True` in `app.run()`.

Back in the project root, assuming, you have [Node](https://nodejs.org/en/download/package-manager/) and [npm](https://www.npmjs.com/get-npm) installed, create a new project via the official [Svelte project template](https://github.com/sveltejs/template):

```bash
$ npx degit sveltejs/template frontend
$ cd app
```

Install the dependencies:

```bash
$ npm install
```

### Flask Backend

Our app will have the following routes:

1. `/api/login` logs a user in and generates a session
1. `/api/logout` logs a user out
1. `/api/getcsrf` returns csrf token in response headers

Grab the full code from [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-cross-origin/server/app.py) and add it to the *backend/app.py* file.
### Svelte Frontend

The logic is the same as the one defined for the jinja example.

#### Login Page

Let's start with the login page.

Add a new file to "app/src" called *Home.svelte*:

```jsx
<script>
  import { onMount} from "svelte";

  let username;
  let password;
  let csrfToken;
  let isAuthenticated = false;


  onMount(() => {
    if (!isAuthenticated) {
      fetch("/api/getcsrf")
      .then((res) => {
        csrfToken = res.headers.get(["X-CSRFToken"])
        return res
      })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      })
      .catch((err) => {
        console.log(err);
      });
    }
  });

  const login = () => {
    fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      credentials: "same-origin",
      body: JSON.stringify({ username: username, password: password }),
    })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      if (data.login == true) {
        isAuthenticated = true;
      }
    })
    .catch((err) => {
      console.log(err);
    });
  }

  const logout = () => {
    fetch("/api/logout", {
      credentials: "same-origin",
    })
    .then(() => {
      isAuthenticated = false;
    })
    .catch((err) => {
      console.log(err);
    });
  };
</script>

<style>
  .container {
    padding-top: 10%;
  }
</style>

<center>
  <div class="container">
    {#if isAuthenticated}

      <h1>You are authenticated!</h1>
      <button type="button" on:click={logout}>logout</button>
      <br /><br />

    {:else}

      <h1>Log in</h1>
      <form id="form">
        username:
        <input type="text" bind:value={username} />
        <br /><br />
        password:
        <input type="password" bind:value={password} /><br /><br />
        <button type="button" on:click={login}>login</button>
      </form>
      <br /><br />

    {/if}
  </div>
</center>

```

What's happening?

We have a variable `authenticated` set to false initially. And the data required is only displayed when the user has authenticated successfully. Similarly, we set `isAuthenticated` to false on logout.

```python
return jsonify({"login": True})
```

The user is then shown the data part defined inside the `{#if isAuthenticated}` block.

Take note of:

```javascript
credentials: "same-origin",
```

The only major change here is the way we grab the `csrf` token. In the previous example, since the template was rendered by Flask(jinja), the flask app set the `csrf_token` directly in the HTML, and we were able to fetch it for our use. But in this case, both backend and frontend are decoupled. So we defined an endpoint in the backend that generates and returns a csrf token for us

```python
@app.route("/api/getcsrf", methods=["GET"])
def get_csrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    response.headers.set('X-CSRFToken', token)
    return response
```

We grab this token when the component loads, using the `onMount` of svelte.

```jsx
let csrfToken;

onMount(() => {
  if (!isAuthenticated) {
    fetch("/api/getcsrf")
    .then((res) => {
      csrfToken = res.headers.get(["X-CSRFToken"])
      return res
    })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
    })
    .catch((err) => {
      console.log(err);
    });
  }
});
```

Now, let's dockerize the whole application.

Create a dockerfile for backend, *backend/Dockerfile*

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

Well, we pulled an instance of python, installed all the required dependencies and run the application. The app runs on port `5000` within the container.

Now, create a dockerfile for the frontend, *frontend/Dockerfile*

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

We pulled the official nodejs image, installed all the dependencies, and started the application. The app runs on port 8080 inside the container.

Create a docker container for Nginx that works as our reverse proxy, *nginx/Dockerfile*.

```Dockerfile
FROM nginx:latest
COPY ./nginx.conf /etc/nginx/nginx.conf
```

Get the whole nginx configuration from the repo [here](https://github.com/testdrivenio/flask-cookie-spa/blob/same-origin/flask-spa-same-origin/nginx/nginx.conf). The main thing here is,

```nginx
location /api {
    proxy_pass          http://backend;
}

location / {
    proxy_pass          http://frontend;
}
```

All the requests to `/` will be forwarded to the frontend and all the requests to `/api` will be forwarded to the backend. Essentially making the service available from the same origin.

Your project directory should now look like:

```bash

├── backend
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
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

Now, let's bring all three containers together and create a *docker_compose.yml* at our project's root.

```yml
version: '3.8'

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
      - 8080
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

What we did here is built each container and expose their respective ports. 

#### Test

That's it! We're ready to test.

Build the containers

```bash
docker-compose build
```

Now run the containers using, 

```bash
docker-compose up

# or run docker-compose up directly,
# this should build the application,
# because no previous builds exist
```

Navigate to `localhost:81`, you should see your app running.

![login](images/login.gif "cross origin demo")

## Conclusion

This article has seen how to setup cookie-based authentication for Single-Page Applications(SPAs). Whether you use sessions or tokens, it's good to use cookies for authentication when the client is a browser and it, along with the backend app, is on the same domain. We also have setup CSRF protection to prevent any cookie hijacking. 

All the examples are set to run on development mode by default. However, it is not recommended to use `app.run()` in production mode. Instead, use a production-ready server like `gunicorn`. Also, set the cookies to be transferred over `HTTPS` by adding the following to the `.env` files.

```env
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
```
