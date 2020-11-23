<script>
  import { onMount} from "svelte";

  let username;
  let password;
  let csrfToken;
  let isAuthenticated = false;

  onMount(() => {
    fetch("http://localhost:5000/api/getsession", {
      credentials: "include",
    })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      if (data.login == true) {
        isAuthenticated = true;
      } else {
        isAuthenticated = false;
        csrf();
      }
    })
    .catch((err) => {
      console.log(err);
    });
  });

  const csrf = () => {
    fetch("http://localhost:5000/api/getcsrf", {
      credentials: "include",
    })
    .then((res) => {
      csrfToken = res.headers.get(["X-CSRFToken"]);
      // console.log(csrfToken);
    })
    .catch((err) => {
      console.log(err);
    });
  }

  const login = () => {
    fetch("http://localhost:5000/api/login", {
      method: "POST",
      headers: {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      credentials: "include",
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

  const whoami = () => {
    fetch("http://localhost:5000/api/data", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      credentials: "include",
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

  const logout = () => {
    fetch("http://localhost:5000/api/logout", {
      credentials: "include",
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
      <button type="button" on:click={whoami}>whoami</button>
      <button type="button" on:click={logout}>logout</button>
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
    {/if}
  </div>
</center>
