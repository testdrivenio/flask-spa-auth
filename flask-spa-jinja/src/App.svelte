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
