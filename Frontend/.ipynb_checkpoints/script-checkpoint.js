const API = "http://127.0.0.1:8000";// Backend API URL

// Load available notebooks when page starts
loadNotebooks();


// Fetch and display all notebooks
async function loadNotebooks() {

    try {

        const response = await fetch(`${API}/notebooks`);
        const notebooks = await response.json();
        const select = document.getElementById("notebookSelect");

        select.innerHTML = "";

        notebooks.forEach(notebook => {

            const option = document.createElement("option");
            option.value = notebook;
            option.textContent = notebook;
            select.appendChild(option);

        });

        if(notebooks.length > 0){
            document.getElementById("currentNotebook").textContent = notebooks[0];
        }

    }catch(error){

        console.error(error);

    }
}

// Create a new notebook workspace
async function createNotebook() {

    const name = document.getElementById("newNotebook").value;

    if (!name) {
        alert("Enter notebook name");
        return;
    }

    try {

        await fetch(`${API}/create-notebook`,
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    name: name
                })
            }
        );

        document.getElementById("newNotebook").value = "";

        await loadNotebooks();

        alert("Notebook Created");

    } catch (error){

        console.error(error);
        alert("Failed");
    }
}

// Upload PDF to selected notebook
async function uploadPDF() {

    const notebook = document.getElementById("notebookSelect").value;

    const file = document.getElementById("pdfFile").files[0];

    if (!file) {

        alert("Choose a PDF");
        return;

    }

    const formData =new FormData();

    formData.append("file",file);

    try {

        await fetch(
            `${API}/upload/${notebook}`,
            {
                method: "POST",
                body: formData
            }
        );

        alert("PDF Uploaded");

    } catch (error) {

        console.error(error);
        alert("Upload Failed");

    }
}

// Build FAISS index from uploaded PDFs
async function buildIndex() {

    const notebook = document.getElementById( "notebookSelect" ).value;

    try {

        const btns = document.querySelectorAll("button");

        btns.forEach(
            b => b.disabled = true
        );

        await fetch(
            `${API}/build-index/${notebook}`,
            {
                method: "POST"
            }
        );

        btns.forEach(
            b => b.disabled = false
        );

        alert("Index Built Successfully");

    } catch (error) {

        console.error(error);
        alert("Build Failed");

    }
}

// Display user message in chat
function addUserMessage(text) {

    const chat = document.getElementById("chat");

    chat.innerHTML += `
        <div class="message user">
            ${text}
        </div>
    `;

    chat.scrollTop = chat.scrollHeight;
}

// Display AI response and sources
function addBotMessage(answer, docs) {

    const chat = document.getElementById("chat");

    let sources = "";

    if (docs) {

        docs.forEach(doc => {

            sources += `
                <div>
                    📄 ${doc.metadata.source_file}
                </div>
            `;

        });

    }

    chat.innerHTML += `
        <div class="message bot">

            <div>
                ${answer}
            </div>

            <div class="sources">
                ${sources}
            </div>

        </div>
    `;

    chat.scrollTop = chat.scrollHeight;
}

// Send query to backend RAG system
async function askQuestion() {

    const notebook = document.getElementById("notebookSelect").value;

    const query =document.getElementById("query").value;

    if (!query) {
        return;
    }

    addUserMessage(query);

    document.getElementById("query").value = "";

    try {

        const response =
            await fetch(
                `${API}/ask`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        notebook: notebook,
                        query: query,
                        top_k: 8
                    })
                }
            );

        const data = await response.json();

        addBotMessage(data.answer,data.documents);

    } catch (error) {

        console.error(error);

        addBotMessage("Error getting response from backend.",[]);
		
    }
}


document.getElementById("notebookSelect").addEventListener("change",function () {document.getElementById("currentNotebook").textContent = this.value});


document.getElementById("query").addEventListener("keypress",function (e) {if (e.key === "Enter") {askQuestion();}});