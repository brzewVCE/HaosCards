// Function to move the selected white card to the black card container
function onClickSelectButton() {
    // Check if a white card is selected
    if (selected_white_card) {
        // Remove the "selected" class from the selected white card
        selected_white_card.classList.remove("selected");

        // Clone the selected white card element
        const clonedCard = selected_white_card.cloneNode(true);

        // Add the cloned white card to the black card container
        black_cardContainer.appendChild(clonedCard);

        // Remove the selected white card from the white card container
        selected_white_card.parentNode.removeChild(selected_white_card);

        // Reset the selected_white_card variable to null
        selected_white_card = null;

        // Create a new white card and add it to the white card container
        const newWhiteCardDescription = "New White Card Description";
        const newWhiteCard = create_white_card(newWhiteCardDescription);
        white_cardContainer.appendChild(newWhiteCard);
    }
}

function startTimer(duration, display) {
    var timer = duration, minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            timer = duration;
        }
    }, 1000);
}

window.onload = function () {
    var roundTime = 60 * 5,
        display = document.querySelector('#timer');
    startTimer(fiveMinutes, display);
};


// Get the "selectButton" element from the document
const button = document.getElementById("selectButton");

// Attach the "onClickSelectButton" function to the button's click event
button.onclick = onClickSelectButton;

// Define an array of white card descriptions
const white_cardsData = [
    "white_card 1 Description",
    "white_card 2 Description",
    "white_card 3 Description",
    "white_card 4 Description",
    "white_card 5 Description",
    "white_card 6 Description",
    "white_card 7 Description",
    "white_card 8 Description"
];

// Define an array of black card descriptions (currently contains "Test")
const black_cardsData = [
    "Test"
];

// Get the "whitecardContainer" and "blackcardContainer" elements from the document
const white_cardContainer = document.getElementById("whitecardContainer");
const black_cardContainer = document.getElementById("blackcardContainer");

// Initialize a variable to keep track of the selected white card (null initially)
let selected_white_card = null;

// Function to create a white card element given a description and index
function create_white_card(description, index) {
    const white_card = document.createElement("div");
    white_card.className = "white_card";
    white_card.textContent = description;

    // Add a click event listener to each white card
    white_card.addEventListener("click", () => {
        // If a white card is already selected, remove the "selected" class
        if (selected_white_card) {
            selected_white_card.classList.remove("selected");
        }

        // Set the clicked white card as the selected one and add the "selected" class
        selected_white_card = white_card;
        selected_white_card.classList.add("selected");
    });

    return white_card;
}
function create_black_card(description, index) {
    const black_card = document.createElement("div");
    black_card.className = "black_card";
    black_card.textContent = description;
    return black_card;
}
// Function to initialize the white cards and add them to the white card container
function initialize_white_cards() {
    white_cardsData.forEach((description, index) => {
        const white_card = create_white_card(description, index);
        white_cardContainer.appendChild(white_card);
    });
}

function initialize_black_card() {
    black_cardsData.forEach((description, index) => {
        const black_card = create_black_card(description, index);
        black_cardContainer.appendChild(black_card);
    });
}

// Call the initialize_white_cards function to populate the white card container
initialize_white_cards();
initialize_black_card();
