const contactForm = document.getElementById("contactForm");
const response = document.getElementById("response");

contactForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();

    try {
        const result = await fetch("/contact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, message })
        });

        const data = await result.json();

        response.textContent = data.message;

        if (result.ok) {
            contactForm.reset();
        }

    } catch (error) {
        response.textContent = "Something went wrong. Please try again.";
        console.error(error);
    }
});