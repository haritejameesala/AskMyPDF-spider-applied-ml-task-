const API = "http://127.0.0.1:8000";

//stores the currently selected notebook.
//used instead of reading directly from the dropdown to avoid asnyc race conditions
let activeNotebook = "";

console.log("SCRIPT LOADED");

window.addEventListener("beforeunload", () => {
    console.log("PAGE RELOADING");
});

//to return the currently active notebook
function getNotebook(){
    return activeNotebook;
}

//to update active notebook and UI elements
function setNotebook(name){
    console.log("SET NOTEBOOK:", name);
    console.log("ACTIVE NOTEBOOK =", name);
    activeNotebook = name;
    document.getElementById("notebookSelect").value = name;
    document.getElementById("currentNotebook").textContent =
        name || "No Notebook Selected";
}

loadNotebooks();

//to load all notebooks from backend and populate dropdown
async function loadNotebooks(){
    console.log("LOAD NOTEBOOKS CALLED");

    try {

        document.getElementById("loadingOverlay").classList.remove("hidden");

        const response = await fetch(`${API}/notebooks`);
        const notebooks = await response.json();

        notebooks.sort();

        const select = document.getElementById("notebookSelect");

        const currentSelection =
            activeNotebook ||
            select.value;

        select.innerHTML = "";

        notebooks.forEach(nb => {
            const option = document.createElement("option");
            option.value = nb;
            option.textContent = nb;
            select.appendChild(option);
        });

        if (
            currentSelection &&
            notebooks.includes(currentSelection)
        ) {
            setNotebook(currentSelection);
        }
        else if (notebooks.length > 0) {
            setNotebook(notebooks[0]);
        }

        await loadPapers(getNotebook());
        await loadStats(getNotebook());

    } catch (error) {

        console.error(error);

    } finally {

        document.getElementById("loadingOverlay")
            .classList.add("hidden");
    }
}

//creates a new notebook workspace on backend
// add notebook directly to dropdown.
//avoids reloading the entire notebook list.
async function createNotebook() {

    const name = document.getElementById("newNotebook").value.trim();
    if (!name){
        alert("Enter notebook name");
        return;
    }

    try{

        const res = await fetch(`${API}/create-notebook`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        });

        if (!res.ok) throw new Error("Server error");

        document.getElementById("newNotebook").value = "";

        const select = document.getElementById("notebookSelect");

        //to prevent duplicate notebook entries
        if (![...select.options].some(o => o.value === name)){
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            select.appendChild(option);
        }

        setNotebook(name);

        await loadPapers(name);
        await loadStats(name);

        alert("Notebook Created");

    } catch (error) {

        console.error(error);
        alert("Failed to create notebook");
    }
}

//capture notebook before async operations.
//ensures upload always targets the notebook selected when the button was clicked.
async function uploadPDF(){

    const notebook = getNotebook();

    if (!notebook){
        alert("Select a notebook first");
        return;
    }

    const file = document.getElementById("pdfFile").files[0];

    if (!file){
        alert("Choose a PDF");
        return;
    }

    // Send PDF file using multipart/form-data
    const formData = new FormData();
    formData.append("file", file);

    try {

        document.getElementById("loadingOverlay").classList.remove("hidden");

        const res = await fetch(`${API}/upload/${notebook}`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) throw new Error("Upload failed");
        
        //to refresh paper list and stats after upload
        await loadPapers(notebook);
        await loadStats(notebook);

        alert("PDF Uploaded");

    }catch(error){

        console.error(error);
        alert("Upload Failed");

    }finally{

        document.getElementById("loadingOverlay").classList.add("hidden");
    }
}


async function buildIndex(){

    const notebook = getNotebook();

    if (!notebook){
        alert("Select a notebook first");
        return;
    }

    const btns = document.querySelectorAll("button");

    try{

        //disable buttons while indexing to prevent duplicate requests
        btns.forEach(b => b.disabled = true);
        document.getElementById("loadingOverlay").classList.remove("hidden");

        //build FAISS vector index for uploaded PDFs
        const res = await fetch(`${API}/build-index/${notebook}`, { method: "POST" });

        if (!res.ok) throw new Error("Build failed");

        await loadStats(notebook);

        alert("Index Built Successfully");

    }catch(error){

        console.error(error);
        alert("Build Failed");

    }finally{

        btns.forEach(b => b.disabled = false);
        document.getElementById("loadingOverlay").classList.add("hidden");
    }
}


function escapeHtml(str){
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

//add user question to chat window
function addUserMessage(text){

    const chat = document.getElementById("chat");

    const div = document.createElement("div");
    div.className = "message user";
    div.textContent = text;   

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

//display generated answer  and source documents
// show the retrieved source files used to generate the answer(based on top_k)
function addBotMessage(answer, docs){

    const chat = document.getElementById("chat");

    const wrapper = document.createElement("div");
    wrapper.className = "message bot";

    const answerDiv = document.createElement("div");
    answerDiv.innerHTML = escapeHtml(answer).replace(/\n/g, "<br>");
    wrapper.appendChild(answerDiv);


    if (docs && docs.length > 0){
        const sourcesDiv = document.createElement("div");
        sourcesDiv.className = "sources";
        docs.forEach(doc =>{
            const d = document.createElement("div");
            d.textContent = "📄 " + (doc.metadata?.source_file || "Unknown");
            sourcesDiv.appendChild(d);
        });
        wrapper.appendChild(sourcesDiv);
    }

    chat.appendChild(wrapper);
    chat.scrollTop =chat.scrollHeight;
}

//to display temporary "Thinking..." message while waiting for backend response.
function showTyping(){

    const chat =document.getElementById("chat");

    const div = document.createElement("div");
    div.id = "typing";
    div.className = "message bot";
    div.textContent = "Thinking...";

    chat.appendChild(div);
    chat.scrollTop =chat.scrollHeight;
}

//send user query to RAG backend
async function askQuestion(){

    const notebook = getNotebook();

    if(!notebook) {
        alert("Select a notebook first");
        return;
    }

    const query= document.getElementById("query").value;
    if (!query) return;

    addUserMessage(query);
    showTyping();
    document.getElementById("query").value = "";

    try {

        const response=await fetch(`${API}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ notebook, query, top_k: 8 })
        });

        const data = await response.json();

        document.getElementById("typing")?.remove();
        addBotMessage(data.answer, data.documents);

        //update query count after successful  response
        await loadStats(notebook);

    } catch(error){

        console.error(error);
        document.getElementById("typing")?.remove();
        addBotMessage("Error getting response from backend.", []);
    }
}

//fetch and display PDFs uploaded to the selected notebook
async function loadPapers(notebook) {

    if (!notebook) return;

    try {

        const response = await fetch(`${API}/papers/${notebook}`);
        const papers = await response.json();

        const paperList = document.getElementById("paperList");

        //show placeholder when  no PDFs exist
        if (papers.length === 0) {
            paperList.innerHTML = "No PDFs Uploaded";
            document.getElementById("paperCount").textContent = "0";
            return;
        }

        paperList.innerHTML = "";
        papers.forEach(paper => {
            paperList.innerHTML += `<div class="paper-item">📄 ${paper}</div>`;
        });

        document.getElementById("paperCount").textContent = papers.length;

    } catch (error) {

        console.error(error);
    }
}

//to  load notebook stats:
// papers, chunks,tokens,queries
async function loadStats(notebook){

    if (!notebook)return;

    try {

        const response = await fetch(`${API}/stats/${notebook}`);
        const data = await response.json();

        document.getElementById("paperCount").textContent = data.papers;
        document.getElementById("chunkCount").textContent = data.chunks;
        document.getElementById("tokenCount").textContent = data.tokens;
        document.getElementById("queryCount").textContent = data.queries;

    } catch (error) {

        console.error(error);
    }
}

//update UI when user selects a different notebook
document.getElementById("notebookSelect")
.addEventListener("change", function(){

    const notebook = this.value;
    setNotebook(notebook);

    loadPapers(notebook);
    loadStats(notebook);
});

//submit question when enter key is pressed
document.getElementById("query")
.addEventListener("keypress", function(e){

    if (e.key==="Enter") askQuestion();
});