async function get_timelines() {
    const url = 'https://codehub.p.rapidapi.com/timelines';
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': '13a3fdc433mshc472900b88d594cp11dce7jsnadce2b996b30',
            'X-RapidAPI-Host': 'codehub.p.rapidapi.com'
        }
    };
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        for (let i in result) {
            const element = result[i];
            const li = document.createElement("li");
            const title = document.createElement("h5");
            const body = document.createElement("p");
            title.innerHTML = element['title'];
            body.innerHTML = element['body'];
            li.className = 'event';
            li.setAttribute("data-date", element["date"]);
            li.appendChild(title);
            li.appendChild(body);

            const parent = document.querySelector('.timeline');
            parent.appendChild(li);
        }
    } catch (error) {
        console.error(error);
    }
}

async function get_all_users() {
    const url = 'https://codehub.p.rapidapi.com/users';
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': '13a3fdc433mshc472900b88d594cp11dce7jsnadce2b996b30',
            'X-RapidAPI-Host': 'codehub.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const users = await response.json();
        const no_of_users = Object.keys(users).length;

        document.querySelector('.no_of_users').innerHTML = no_of_users;
        document.querySelector('.no_of_users_div').setAttribute('data-counter', no_of_users);

        for (let i in users) {
            if (i < 3) {
                user = users[i];
                const parent = document.querySelector('.members');
                const li = document.createElement("li");
                const a = document.createElement("a");
                const cite = document.createElement("cite");
                a.innerHTML = user['username'];
                cite.innerHTML = "... recently joined"
                li.appendChild(a);
                li.appendChild(cite);
                li.style.display = "flex";
                li.style.alignItems = "baseline";
                li.style.gap = "1rem";
                parent.appendChild(li);
            }
            else {
                break;
            }
            i++;
        }

        if (no_of_users >= 5) {
            const parent = document.querySelector('.members_span');
            const text = `...  ${no_of_users-3} + other members`;
            parent.innerHTML = text;
        }
    } catch (error) {
        console.error(error);
    }
}

async function get_all_files() {
    const url = 'https://codehub.p.rapidapi.com/files';
    const options = {
        method: 'GET',
        headers: {
            'X-RapidAPI-Key': '13a3fdc433mshc472900b88d594cp11dce7jsnadce2b996b30',
            'X-RapidAPI-Host': 'codehub.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        const files = await response.json();

        const no_of_files = Object.keys(files).length;
        document.querySelector(".no_of_files_div").setAttribute("data-counter", no_of_files);
        document.querySelector(".no_of_files").innerHTML = no_of_files;

        if (no_of_files >= 1) {
            document.querySelector('.no_file_msg').style.display  = "none";
            for (let i  in files) {
                if (i < 5) {
                    const file = files[i];
                    if (!file.is_private_file) {
                        const parent = document.querySelector('.table_body');
                        const tr = document.createElement("tr");
                        const td1 = document.createElement("td");
                        const td2 = document.createElement("td");
                        const title = document.createElement("a");
                        const username = document.createElement("a");

                        title.innerHTML = file.title;
                        username.innerHTML = file.user_id;
                        td1.appendChild(title);
                        td2.appendChild(username);
                        td1.setAttribute("data-label", "Project");
                        td2.setAttribute("data-label", "Developer");
                        tr.appendChild(td1);
                        tr.appendChild(td2);
                        parent.appendChild(tr);
                    }
                }
                else {
                    break;
                }
            }
        }
        else {
            document.querySelector('.table').style.display = "none";
        }
    } catch (error) {
        console.error(error);
    }
}

// Function Call
get_timelines();
get_all_users();
get_all_files();

// window.onload = onload_func;