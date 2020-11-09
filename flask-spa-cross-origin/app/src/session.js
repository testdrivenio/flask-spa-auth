import router from "page";

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
