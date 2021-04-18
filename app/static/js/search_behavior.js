// // SEARCH PAGE // //

// https://stackoverflow.com/questions/42341761/javascript-eventlistener-not-working-in-external-js-file
window.onload = function() {
    
    // Update dependent dropdown-menu on page load (after search submitted) according to previous selection
    updateMenu();

    // Make the "see all results" button visible if valid search submitted and results listed
    makeVisible("#all-button");

    // Go to search results after a valid search has been submitted (scroll and focus)
    goToResults();

    // Remove the "new search" link if it remains on screen after results are listed (too few results)
    isLinkInViewport();

    // Listen to user's selection and update filter-search dropdown-menus in real time 
    // https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/change_event
    document.getElementById("dist-menu").addEventListener("change", filterByDist);
    document.getElementById("conc-menu").addEventListener("change", filterByConc);
}

// -- HTML TRIGGERED FUNCTIONS -- //

function toggleFilters()
// Enable/disable all filters simultaneously
{
    // https://css-tricks.com/snippets/javascript/loop-queryselectorall-matches/
    let filters = document.querySelectorAll(".checkbox-filter");
    for (let i = 0; i < filters.length; i++)
    {
        // Enable all filters if any filter is disabled, otherwise disable all filters
        if (filters[i].checked == false)
        {
            for (let i = 0; i < filters.length; i++)
            {
                filters[i].checked = true;
            }
            document.getElementById("submit-button").focus();
            return;
        }
        filters[i].checked = false;
    }
    document.getElementById("cro").focus();
}

function copyToClipboard(n, id)
// Copy contact's email address to clipboard with the click of a button
// https://www.w3schools.com/howto/howto_js_copy_clipboard.asp
{
    document.getElementById(`e${n}-address-${id}`).select();
    document.getElementById(`e${n}-address-${id}`).setSelectionRange(0, 99999); // for mobile devices

    document.execCommand("copy");
}

function toggleView()
// Reveal/conceal full contact info for all contacts
{   
    if (document.querySelector("#checkmark").style.display === "none") // (default style inline in html)
    {
        // Swap icons
        document.querySelector("#checkmark").style.display = "inline";
        document.querySelector("#pointyfinger").style.display = "none";

        // Reveal each and every contact
        let contacts = document.querySelectorAll("details");
        for (let i = 0; i < contacts.length; i++)
        {
            contacts[i].open = true;
        }
    }
    else
    {
        document.querySelector("#checkmark").style.display = "none";
        document.querySelector("#pointyfinger").style.display = "inline";

        // Conceal each and every contact
        let contacts = document.querySelectorAll("details");
        for (let i = 0; i < contacts.length; i++)
        {
            contacts[i].open = false;
        }
    }

    // Re-assess position and visibility of the "new search" link @ bottom of result list
    isLinkInViewport();
}

// -- HELPER FUNCTIONS -- //

function filterByDist()
// Populate "Concelhos" dropdown menu according to selected option in "Distritos/Ilhas" dropdown menu
{
    // Remember user choice from "Distritos/Ilhas" dropdown menu
    let selectedDist = document.getElementById("dist-menu").value;
    
    // Define "Concelhos" dropdown menu as target for update
    let targetMenu = document.getElementById("conc-menu");

    // Remember previously selected option in target menu
    let selectedOption = document.getElementById("conc-menu").value;
    
    // Retrieve data (list of concelhos per distrilha) via network request fetch()
    // https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    // https://developers.google.com/web/updates/2015/03/introduction-to-fetch
    // https://web.dev/promises/
    
    fetch(`/filter/dist/${selectedDist}`)   // send GET request to that route and return a promise containing the response
    .then(response => response.json())  // extract JSON content from the HTTP response
    .then(function (list) { // take the value returned from previous then() method as an argument to the callback function

        // Clear all options in target menu
        targetMenu.innerHTML = null;

        // Add "Todos" to target menu as first option
        let newOption = document.createElement("option");
        newOption.innerHTML = "Todos";
        targetMenu.appendChild(newOption);
        
        if (selectedDist !== "Todos")
        {    
            // Populate target menu with the list of values (concelhos) for the selected key (distrilha)
            for (let i = 0; i < list[selectedDist].length; i++)
            {
                newOption = document.createElement("option");
                newOption.innerHTML = list[selectedDist][i];
                targetMenu.appendChild(newOption);
            }
            
            // Make sure previously selected option stays selected (if exists in updated list of options),
            // otherwise "Todos" is selected by default
            if (selectedOption !== "Todos")
            {
                selectMenuOption(targetMenu, selectedOption);
            }
        }
        // Special case: user picked "Todos" from "Distritos/Ilhas" dropdown menu
        // - populate target menu with the default full list
        else    
        {            
            for (let i = 0; i < list.length; i++)
            {
                newOption = document.createElement("option");
                newOption.innerHTML = list[i];
                targetMenu.appendChild(newOption);
            }
        }        
    })
    // Error handling: deal with promise rejection cases by logging the error to the console
    .catch(error => {
        console.error("Fetch request failed.", error);  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch
    })
}

function filterByConc()
// Automatically select from "Distritos/Ilhas" dropdown menu according to selected option in "Concelhos" dropdown menu
{
    // Remember user choice from "Concelhos" dropdown menu
    let selectedConc = document.getElementById("conc-menu").value;

    // Define "Distritos/Ilhas" dropdown menu as target for update
    let targetMenu = document.getElementById("dist-menu");

    if (selectedConc !== "Todos")   // option "Todos" does not change distrilha
    {
        // Retrieve distrilha corresponding to selected concelho
        fetch(`/filter/conc/${selectedConc}`)
        .then(response => response.json())
        .then(function (result) {
            
            // Select that distrilha option if not yet selected
            if (result !== targetMenu.value)
            {
                selectMenuOption(targetMenu, result);
            }
        })
        // Error handling
        .catch(error => {
            console.error("Fetch request failed.", error);
        })
    }
}

function selectMenuOption(menu, selection)
{
    // https://usefulangle.com/post/254/javascript-loop-through-select-options
    Array.from(menu.options).forEach(function(option) {
        if (selection === option.value)
        {
            option.selected = "selected";
        }
        else
        {
            option.selected = '';
        }
    })
}

function updateMenu()
// Update "Concelhos" dropdown menu according to previous selection in "Distritos/Ilhas" dropdown menu
{
    if (document.getElementById("dist-menu").value !== "Todos")
    {
        filterByDist();
    }
}

function goToResults()
// Scroll to/focus the results section when loading the search page if a search has been submitted
{
    // Focus the "see all" button to facilitate keyboard access to the results section
    try
    {
        document.querySelector("#all-button").focus();
    }
    catch
    {
        //pass
    }
    
    // Scroll to the results or to any flashed error message
    // (does not apply for larger screens where results/messages are displayed at top of page)
    // https://css-tricks.com/working-with-javascript-media-queries/
    let mediaQuery = window.matchMedia('(max-width: 1023px)');
    if (mediaQuery.matches)
    {
        if (document.getElementById("results-container"))
        {
            document.getElementById("results-container").scrollIntoView();
        }
        else if (document.getElementById("alert-search"))
        {
            document.getElementById("alert-search").scrollIntoView();
        }
    }
}

function isLinkInViewport()
// Check if listed results push the element containing the "new search" link out of the screen
// -> if link remains on screen, remove it
{
    // Adapted from: https://gomakethings.com/how-to-check-if-any-part-of-an-element-is-out-of-the-viewport-with-vanilla-js/
    let link = document.getElementById("on-off");
    if (link)
    {
        let boundary = link.getBoundingClientRect();
        if ((boundary.top || boundary.bottom) < (window.innerHeight || document.documentElement.clientHeight))
        {
            link.innerHTML = "";            // clear content of link element
            link.removeAttribute("href");   // neutralize link function
        }
        else
        {
            if (!link.hasAttribute("href"))
            // Put link back on if it gets pushed off screen upon toggling expanded view mode for results
            {
                link.innerHTML = "&#9755; Nova pesquisa";
                link.setAttribute("href", "#nova-pesquisa");
                link.style.cursor = "pointer";
            }
        }
    }
}

function makeVisible(target)
// Set element's 'visibility' property to 'visible' only if the element is rendered
{
    let element = document.querySelector(target);
    if (element)
    {
        element.style.visibility = "visible";
    }
}
