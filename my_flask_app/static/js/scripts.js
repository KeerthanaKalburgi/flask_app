/* scripts.js (JavaScript for fetching and displaying data) */

// In a real application, you would fetch project data from a database.
// Here, we're using sample data for illustration.

const projects = [    {        title: "Project Title 1",        description: "Project description goes here. This is a sample project in the domain of XYZ.",        leader: "John Doe",        email: "john.doe@example.com",    },    {        title: "Project Title 2",        description: "Project description goes here. This is another sample project in the domain of ABC.",        leader: "Jane Smith",        email: "jane.smith@example.com",    },    // Add more project data as needed];

const projectList = document.querySelector(".project-list");

projects.forEach((project, index) => {
    const projectTemplate = document.createElement("div");
    projectTemplate.classList.add("project-template");
    
    projectTemplate.innerHTML = `
        <h2>${project.title}</h2>
        <p class="project-description">
            ${project.description}<br>
            <span class="team-leader">Team Leader: ${project.leader}</span><br>
            <span class="email">Email: ${project.email}</span>
        </p>
    `;

    projectList.appendChild(projectTemplate);
    
});
// scripts.js

// Sample project data
const projects = [
    {
        title: "Project Title 1",
        description: "Project description goes here. This is a sample project in the domain of XYZ.",
        skills: ["Skill 1", "Skill 2"],
    },
    {
        title: "Project Title 2",
        description: "Project description goes here. This is another sample project in the domain of ABC.",
        skills: ["Skill 2", "Skill 3"],
    },
    // Add more project data as needed
];

// Function to create and append project templates to the project list
function createProjectTemplates(projects) {
    const projectList = document.getElementById("project-list");

    projects.forEach((project, index) => {
        const projectTemplate = document.createElement("div");
        projectTemplate.classList.add("project-template");
        
        projectTemplate.innerHTML = `
            <h2>${project.title}</h2>
            <p class="project-description">
                ${project.description}<br>
                <span class="skills">Skills: ${project.skills.join(", ")}</span>
            </p>
            <button class="apply-button">Apply</button>
        `;

        projectList.appendChild(projectTemplate);
    });
}

// Function to show the apply popup
function showApplyPopup() {
    const popup = document.getElementById("apply-popup");
    popup.style.display = "block";
}

// Function to hide the apply popup
function hideApplyPopup() {
    const popup = document.getElementById("apply-popup");
    popup.style.display = "none";
}

// Function to show the success notification
function showSuccessNotification() {
    const notification = document.getElementById("notification");
    notification.style.display = "block";

    // Hide the notification after a few seconds (you can adjust the delay as needed)
    setTimeout(() => {
        notification.style.display = "none";
    }, 3000);
}

// Function to apply to a project
function applyToProject() {
    // Here, you can implement the logic to apply to a project.
    // For simplicity, we're just showing a success notification.
    showSuccessNotification();
    hideApplyPopup();
}

// Add event listeners
document.addEventListener("DOMContentLoaded", () => {
    createProjectTemplates(projects);

    const applyButtons = document.querySelectorAll(".apply-button");
    applyButtons.forEach((button) => {
        button.addEventListener("click", showApplyPopup);
    });

    const closePopup = document.querySelector(".close");
    closePopup.addEventListener("click", hideApplyPopup);

    const applyYesButton = document.getElementById("apply-yes");
    applyYesButton.addEventListener("click", applyToProject);

    const applyNoButton = document.getElementById("apply-no");
    applyNoButton.addEventListener("click", hideApplyPopup);
});