function register_user() {
    // Get the form element
    const form = document.querySelector('#signup_form');
    const password = document.getElementById("password").value;
    const password2 = document.getElementById("password2").value;
    // console.log(" Password:", password,'\n',"Confirm Password:",password2);

    const message = document.getElementById("warning");

    // Add a submit event listener to the form
    form.addEventListener('submit', (e) => {
        e.preventDefault(); // prevent the default form submission behavior
      
        // checks that repeat password is equal to password or not
        if (password2 != password) {
            message.textContent = "Password don't match";
        }
        else {
            // Get the form data
            const formData = new FormData(form);
            const plainFormData = Object.fromEntries(formData.entries())
            const formDataJsonString = JSON.stringify(plainFormData);
        
            const url = 'https://codehub.p.rapidapi.com/auth/register';
            const options = {
                    method: 'POST',
                    headers: {
                        'content-type': 'application/json',
                        'X-RapidAPI-Key': '13a3fdc433mshc472900b88d594cp11dce7jsnadce2b996b30',
                        'X-RapidAPI-Host': 'codehub.p.rapidapi.com'
                    },
                    body: formDataJsonString,
                };
            
            // Send a POST request to the API with the form data
            fetch(url, options)
            .then(response => {
                if (response.ok) {
                // Redirect to the next HTML page
                window.location.href = './verify.html';
                } else {
                throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });
}

