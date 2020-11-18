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
