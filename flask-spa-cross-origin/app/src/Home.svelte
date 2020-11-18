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
      headers: {
        "Content-Type": "application/json",
      },
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
    <p>
      {#if error}{error}{/if}
    </p>
  </div>
</center>
