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

This is an example of a token. The token contains the following information.


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

### Svelte Frontend

We'll have two different pages: one for logging in and the other for viewing use data.

#### Login Page

Let's start with the login page.

Add a new file to "src" called *Home.svelte*:

```jsx
<script>
  import router from "page";
  import { onMount } from "svelte";
  import { getSession } from "./session";

  let username;
  let password;
  let error;

  onMount(() => {
    getSession(true, "/user");
  });

  const login = () => {
    fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ username: username, password: password }),
    })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      if (data.login == true) {
        router.redirect("/user");
      } else {
        error = "Bad credentials";
      }
    })
    .catch((err) => {
      console.log(err);
      error = "Error connecting to server";
    });
  };
</script>

<style>
  #form {
    padding-top: 10%;
  }
</style>

<center>
  <div class="container">
    <form id="form">
      username:
      <input type="text" bind:value={username} />
      <br /><br />
      password:
      <input type="password" bind:value={password} /><br /><br />
      <button type="button" on:click={login}>login</button>
    </form>
    <br /><br />
    <p>{#if error}{error}{/if}</p>
  </div>
</center>
```

What's happening?

Well, we have a simple form that takes a username and password. On button click, the credentials are sent to `/api/login` on the server. Turn to the route handler for `/api/login`. If the credentials are valid, `{"login": True}` is returned:

```python
return jsonify({"login": True})
```

The user is then redirected to `/user`.

Take note of:

```javascript
credentials: "same-origin",
```

This will send along the cookies if the URL is on the same origin as the calling script.

To prevent the page from loading if the user is already authenticated `getSession` is called when the component mounts via the [onMount](https://svelte.dev/tutorial/onmount) lifecycle function:

```javascript
export function getSession(condition, location) {
  fetch("/api/getsession", {
    credentials: "same-origin",
  })
  .then((res) => res.json())
  .then((data) => {
    console.log(data);
    if (data.login == condition) {
      router.redirect(location);
    }
  })
  .catch((err) => {
    console.log(err);
  });
}
```

Add this to a new file called *src/session.js*.

#### Router

Next, let's configure the router.

Update *src/App.svelte* like so:

```html
<script>
  import router from "page";
  import Home from "./Home.svelte";
  let page;
  router("/", () => (page = Home));
  router.start();
</script>

{#if page === Home}
  <Home />
{/if}
```

Since we're building a single page application, there is no actual routing(changing pages). Instead, the application loads different components depending on the page the user visits. 

`router("/", () => (page = Home))` means, when the user hits the route "/", the router sets the page variable as Home. If the page is Home, we load the Home component.

Next, update *src/main.js* like so:

```javascript
import App from './App.svelte';

const app = new App({
  target: document.body,
});

export default app;
```

Once the application is compiled, the code we write into `.svelte` gets compiled into `js` and `CSS`. These files are loaded into the `public/index.html` file, which serves as our SPA. In this case, we created a new app and loaded it into the whole HTML body using `target: document.body`. One can also create a div and run our SPA in that div. 

Create a build:

```bash
$ npm run build
```

After the build finishes, start the server:

```bash
$ python app.py
```

Navigate to [http://localhost:5000](http://localhost:5000). You should see:

![login page](images/login.PNG "Login page")

#### User Page

Create a new file called *src/Page.svelte*:

```javascript
<script>
  let name = "";
  let error;

  import router from "page";
  import { onMount } from "svelte";
  import { getSession } from "./session";

  onMount(() => {
    getSession(false, "/");

    fetch("/api/data", {
      credentials: "same-origin",
    })
    .then((res) => res.json())
    .then((data) => (name = data.name))
    .catch((err) => (error = err));
  });

  const logout = () => {
    fetch("/api/logout", {
      credentials: "same-origin",
    })
    .then(() => router.redirect("/"))
    .catch((err) => {
      console.log(err);
      error = "Error connecting to server";
    });
  };
</script>

<center>
  <div class="container">
    <h3>Profile</h3>
    <button type="button" on:click={logout}>logout</button>
    <hr />
    <p>Name: {name}</p>
    <br /><br />
    <p>{#if error}{error}{/if}</p>
  </div>
</center>
```

What's happening?

1. Again, `getSession` is called after the component mounts. This time, if the session doesn't exist, the user is redirected to the home page where they can log in.
1. If the session exists and is valid, the page is displayed.

Then, wire up the component and route in *src/App.svelte*:

```html
<script>
  import router from "page";
  import Home from "./Home.svelte";
  import Page from "./Page.svelte";
  let page;
  router("/", () => (page = Home));
  router("/user", () => (page = Page));
  router.start();
</script>

{#if page === Home}
  <Home />
{/if}

{#if page === Page}
  <Page />
{/if}
```

#### Test

That's it! We're ready to test.

Create a new build, then run Flask:

```bash
$ npm run build
$ python app.py
```

Log in. You should be redirected to [http://127.0.0.1:5000/user](http://127.0.0.1:5000/user).

Since the server manages the cookies, even if there is a wrong cookie value, the server return `false` for the `getSession` request.

![login](images/login.gif "cross origin demo")

## Flask and Svelte Served Separately (Cross-domain)

With this approach, set up Flask and Svelte separately to serve up cross-domain on different ports.

Start by creating a project directory:

```bash
$ mkdir flask-spa-cross-origin && cd flask-spa-cross-origin
```

Now, create a folder for the backend:

```bash
$ mkdir server && cd server
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
$ npx degit sveltejs/template app
$ cd app
```

Install the dependencies:

```bash
$ npm install
```

Install [Page.js](https://github.com/visionmedia/page.js) as well for client-side routing:

```bash
$ npm install page
```

Your project directory should now look like:

```bash
├── app
│   ├── .gitignore
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
└── server
    └── app.py
```

### Flask Backend

Our app will have the following routes:

1. `/api/login` logs a user in and generates a session
1. `/api/data` fetches user data for an authenticated user
1. `/api/logout` logs a user out
1. `/api/getsession` checks whether a session exists

Grab the full code from [here](https://github.com/testdrivenio/flask-cookie-spa/blob/master/flask-spa-cross-origin/server/app.py) and add it to the *server.app.py* file.

Take note of the CORS config:

```python
cors = CORS(
    app,
    supports_credentials=True,
    resources={r"/api/*": {"origins": "http://localhost:8080"}},
)
```

This is necessary since the frontend will be making requests to the backend from a different domain.

### Svelte Frontend

We'll have two different pages: one for logging in and the other for viewing use data.

#### Login Page

Let's start with the login page.

Add a new file to "app/src" called *Home.svelte*:

```jsx
<script>
  import router from "page";
  import { onMount } from "svelte";
  import { getSession } from "./session";

  let username;
  let password;
  let error;

  onMount(() => {
    getSession(true, "/user");
  });

  const login = () => {
    fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username: username, password: password }),
    })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      if (data.login == true) {
        router.redirect("/user");
      } else {
        error = "Bad credentials";
      }
    })
    .catch((err) => {
      console.log(err);
      error = "Error connecting to server";
    });
  };
</script>

<style>
  #form {
    padding-top: 10%;
  }
</style>

<center>
  <div class="container">
    <form id="form">
      username:
      <input type="text" bind:value={username} />
      <br /><br />
      password:
      <input type="password" bind:value={password} /><br /><br />
      <button type="button" on:click={login}>login</button>
    </form>
    <br /><br />
    <p>{#if error}{error}{/if}</p>
  </div>
</center>
```

What's happening?

Well, we have a simple form that takes a username and password. On button click, the credentials are sent to `http://localhost:5000/api/login`. Turn to the route handler for `/api/login`. If the credentials are valid, `{"login": True}` is returned:

```python
return jsonify({"login": True})
```

The user is then redirected to `/user`.

Take note of:

```javascript
credentials: "include",
```

This will send along the cookies with the request.

To prevent the page from loading if the user is already authenticated `getSession` is called when the component mounts via the [onMount](https://svelte.dev/tutorial/onmount) lifecycle function:

```javascript
export function getSession(condition, location) {
  fetch("http://localhost:5000/api/getsession", {
    credentials: "include",
  })
  .then((res) => res.json())
  .then((data) => {
    console.log(data);
    if (data.login == condition) {
      router.redirect(location);
    }
  })
  .catch((err) => {
    console.log(err);
  });
}
```

Add this to a new file called *app/src/session.js*.

#### Router

Next, let's configure the router.

Update *src/App.svelte* like so:

```html
<script>
  import router from "page";
  import Home from "./Home.svelte";
  let page;
  router("/", () => (page = Home));
  router.start();
</script>

{#if page === Home}
  <Home />
{/if}
```

Here we map the route to a variable and then load components based on the variable's value.

Next, update *src/main.js* like so:

```javascript
import App from './App.svelte';

const app = new App({
  target: document.body,
});

export default app;
```

Our SPA runs on the body of `public/index.html`.

Next, update the `start` command under `scripts` in *app/package.json* so that the single page application uses routing:

```json
"start": "sirv public --single --port 8080"
```

Create a build:

```bash
$ npm run build
```

After the build finishes, start the server:

```bash
$ npm start
```

This will run Svelte on [http://localhost:8080](http://localhost:8080).

Within a new terminal window, navigate to the "server" directory and spin up the Flask app:

```bash
$ python app.py
```

Navigate to [http://localhost:8080](http://localhost:8080). You should see:

![login page](images/login.PNG "Login page")

#### User Page

Create a new file called *app/src/Page.svelte*:

```javascript
<script>
  let name = "";
  let error;

  import router from "page";
  import { onMount } from "svelte";
  import { getSession } from "./session";

  onMount(() => {
    getSession(false, "/");

    fetch("http://localhost:5000/api/data", {
      credentials: "include",
    })
    .then((res) => res.json())
    .then((data) => (name = data.name))
    .catch((err) => (error = err));
  });

  const logout = () => {
    fetch("http://localhost:5000/api/logout", {
      credentials: "include",
    })
    .then(() => router.redirect("/"))
    .catch((err) => {
      console.log(err);
      error = "Error connecting to server";
    });
  };
</script>

<center>
  <div class="container">
    <h3>Profile</h3>
    <button type="button" on:click={logout}>logout</button>
    <hr />
    <p>Name: {name}</p>
    <br /><br />
    <p>{#if error}{error}{/if}</p>
  </div>
</center>
```

What's happening?

1. Again, `getSession` is called after the component mounts. This time, if the session doesn't exist, the user is redirected to the home page where they can log in.
1. If the session exists and is valid, the page is displayed.

Then, wire up the component and route in *app/src/App.svelte*:

```html
<script>
  import router from "page";
  import Home from "./Home.svelte";
  import Page from "./Page.svelte";
  let page;
  router("/", () => (page = Home));
  router("/user", () => (page = Page));
  router.start();
</script>

{#if page === Home}
  <Home />
{/if}

{#if page === Page}
  <Page />
{/if}
```

#### Test

That's it! We're ready to test.

Create a new build, then run Svelte:

```bash
$ npm run build
$ npm start
```

In a different terminal window, run the Flask app:

```bash
$ python app.py
```

Log in. You should be redirected to [http://127.0.0.1:8080/user](http://127.0.0.1:8080/user).

The server manages the session. In case of wrong cookie value, the server should return false.

![login](images/login.gif "cross origin demo")

## Flask and Svelte Served Separately (Same Domain)

TODO: briefly describe the changes that will need to be made to handle the same domain

## Conclusion

This article has seen how to setup cookie-based authentication for Single-Page Applications(SPAs). Whether you use sessions or tokens, it's good to use cookies for authentication when the client is a browser and it, along with the backend app, is on the same domain. It's fine to use cookies for auth cross-domain -- when the frontend and backend are served from different domains -- as long as CORS is configured properly. In both cases, setting up CSRF protection(protection against cookie hijacking) is crucial and can provide the best security possible.

All the examples are set to run on development mode by default. However, it is not recommended to use `app.run()` in production mode. Instead, use a production ready server like `gunicorn`. Also, set the cookies to be transferred over `HTTPS` by adding the following to the `.env` files.

```env
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
```
