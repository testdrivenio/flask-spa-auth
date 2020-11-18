import router from 'page';

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
