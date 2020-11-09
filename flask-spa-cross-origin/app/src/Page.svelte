<script>
    let name = "";
    let error;

    import router from "page";
    import { onMount } from "svelte";
    import { getSession } from "./session";

    onMount(() => {
        // fetch("http://localhost:5000/api/getsession", {
        //     credentials: "include",
        // })
        //     .then((res) => res.json())
        //     .then((data) => {
        //         console.log(data);
        //         if (data.login == false) {
        //             router.redirect("/");
        //         }
        //     })
        //     .catch((err) => {
        //         console.log(err);
        //     });

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
        <p>
            {#if error}{error}{/if}
        </p>
        <p />
    </div>
</center>
