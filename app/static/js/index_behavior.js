// // INDEX PAGE // //

window.onload = function() {

    // Hide "info-panel" sections on page load
    hideOnPageLoad(".info-panel")

    // Hide "info-arrow" icons on page load
    hideOnPageLoad(".info-arrow")

    // Turn off scrollbar on page load
    toggleScrollbarVisibility("off");

    // Display "info-panel" sections when URL contains their href
    // (e.g. user opened link in a new window/tab or refreshed the page)    
    // https://css-tricks.com/snippets/javascript/get-url-and-url-parts-in-javascript/
    // https://stackoverflow.com/questions/6076576/how-to-execute-a-js-function-based-on-url-hash-urlnameoffunction
    let href = window.location.hash;
    if (href === "#como-procurar" || href === "#onde-procurar")
    {
        // Reveal referenced "info-panel" section
        let section = document.querySelector(href);
        section.style.display = "block";

        // Show "info-arrow" icon and make sure it points to the right section
        document.querySelector(".info-arrow").style.display = "block";
        let arrowLink = document.getElementById("info-arrow");
        arrowLink.href = href;

        // Adjust margins
        adjustMarginTop(arrowLink)
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/substr
        let backtopLink = document.getElementById(`backtop-${href.substr(1, 4)}`);
        let currentSectionHeight = section.clientHeight;
        adjustMarginBottom(backtopLink, currentSectionHeight)
                
        // Turn on scrollbar
        toggleScrollbarVisibility("on");

        // Scroll to "info-panel" section
        section.scrollIntoView();        
    }
}

// -- HTML TRIGGERED FUNCTIONS -- //

// User clicked on a "silhouette" link to open an "info-panel"
function revealSection(id) {

    // Hide previously active "info-panel" section
    document.getElementById(`${id[1]}-procurar`).style.display = "none";

    // Reveal selected "info-panel" section
    let section = document.getElementById(`${id[0]}-procurar`);
    section.style.display = "block";

    // Show "info-arrow" icon
    document.querySelector(".info-arrow").style.display = "block";
    let arrowLink = document.getElementById("info-arrow");
    arrowLink.href = `#${id[0]}-procurar`;

    // Adjust margins
    adjustMarginTop(arrowLink)    
    let backtopLink = document.getElementById(`backtop-${id[0]}`);
    let currentSectionHeight = section.clientHeight;
    adjustMarginBottom(backtopLink, currentSectionHeight)

    // Scroll to "info-panel" section
    document.getElementById(`${id[0]}-procurar`).scrollIntoView();

    // Turn on scrollbar in the "info-panel" section (smoothly...)
    // https://stackoverflow.com/questions/17883692/how-to-set-time-delay-in-javascript
    setTimeout(function() {
        toggleScrollbarVisibility("on");
    }, 150);
}

// User clicked on the "X" link on the top corner of an "info-panel" to close it
function hideSection(id) {            
    // Hide "info-panel" section
    document.getElementById(`${id}-procurar`).style.display = "none";

    // Hide "info-arrow" icon
    document.querySelector(".info-arrow").style.display = "none";

    // Turn off scrollbar
    toggleScrollbarVisibility("off");

    // Close any expanded collapsibles
    let collapsibles = document.querySelectorAll(".toggle");
    // https://css-tricks.com/snippets/javascript/loop-queryselectorall-matches/
    for (let i = 0; i < collapsibles.length; i++)
    {
        if (id === "como" && i < 4)
        {
            collapsibles[i].checked = false;
        }
        else if (id === "onde" && i > 3)
        {
            collapsibles[i].checked = false;
        }
    }
}

// User focused on a "collapsible" toggle using the keyboard and pressed the Enter key
function reactEnterKey(event, id)
// https://stackoverflow.com/questions/54176751/is-it-possible-to-get-the-key-code-from-onkeyup
// https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/key/Key_Values
{
    collapsible = document.getElementById(`collaps-${id}`);
    if (event.key === "Enter" && collapsible.checked === false)
    {
        // Scroll to view collapsible
        scrollViewCollapsible(id);
        // Expand collapsible inner content
        collapsible.checked = true;
    }
    else if (event.key === "Enter" && collapsible.checked === true)
    {
        // Collapse if already expanded
        collapsible.checked = false;
    }
}

// User clicked on a "collapsible" label to expand/collapse its inner content
function scrollViewCollapsible(id) {
    // Scroll collapsible content into view when expanding
    if (document.getElementById(`collaps-${id}`).checked === false)
    {
        document.getElementById(`${id}`).scrollIntoView(); // doesn't seem to be working in Chrome/Edge...
    }

    // Adjust the section's bottom margin each time a "collapsible" is expanded/collapsed
    setTimeout(function() {
    // (wait for the collapsible content to expand to get the new section height)
        if (id <= 4)
        {
            let backtopLink = document.getElementById("backtop-como");
            let currentSectionH = document.getElementById("como-procurar").clientHeight;
            adjustMarginBottom(backtopLink, currentSectionH);

            // If all "collapsibles" become collapsed make sure the navigation arrow does not stay on screen
            // by scrolling to the top of the "info-panel" - only relevant for Firefox...
            if (document.getElementById("collaps-1").checked === false &&
            document.getElementById("collaps-2").checked === false &&
            document.getElementById("collaps-3").checked === false &&
            document.getElementById("collaps-4").checked === false)
            {
                readjustView("como-procurar");
            }
        }
        else if (id >= 5)
        {
            let backtopLink = document.getElementById("backtop-onde");
            let currentSectionH = document.getElementById("onde-procurar").clientHeight;
            adjustMarginBottom(backtopLink, currentSectionH);

            if (document.getElementById("collaps-5").checked === false &&
            document.getElementById("collaps-6").checked === false &&
            document.getElementById("collaps-7").checked === false)
            {
                readjustView("onde-procurar");
            }
        }

        function readjustView(panel)
        // Compare the boundaries of the header and the navigation arrow.
        // If the arrow is lower than the header (thus visible), scroll up to push it out of the viewport
        {
            let logoHeader = document.querySelector(".logo");
            let navigationArrow = document.getElementById("info-arrow");
            let headerBoundary = logoHeader.getBoundingClientRect();
            let arrowBoundary = navigationArrow.getBoundingClientRect();
            if ((arrowBoundary.top > headerBoundary.bottom) || (arrowBoundary.bottom > headerBoundary.bottom))
            {
                document.getElementById(panel).scrollIntoView();
            }
        }
    }, 1);
}

// -- HELPER FUNCTIONS -- //

function hideOnPageLoad(target)
// Hide elements by re-setting their 'display' property to 'none'
{
    // https://css-tricks.com/snippets/javascript/loop-queryselectorall-matches/
    let elements = document.querySelectorAll(target);
    for (let i = 0; i < elements.length; i++)
    {
        elements[i].style.display = "none";
    }
}

function toggleScrollbarVisibility(state)
// Switch scrollbar visibility on/off
{
    let scrollable = document.querySelector("main");

    if (state === "on" && scrollable.hasAttribute("class"))
    {
        scrollable.removeAttribute("class");
    }
    else if (state === "off" && !scrollable.hasAttribute("class"))
    {
        scrollable.setAttribute("class", "in-out-scrollbar");
    }
}

function adjustMarginTop(targetElement)
// Check height of the viewport and adjust the top margin of key elements to ensure a responsive layout
{
    let windowH = window.innerHeight;
    let headerH = document.querySelector("header").clientHeight;
    let interfaceH = document.querySelector(".interface").clientHeight;

    // https://developer.mozilla.org/en-US/docs/Web/API/Window/getComputedStyle
    let elementStyles = window.getComputedStyle(targetElement);

    // Must discount the previous top margin   
    // (get rid of pixel units from style) https://www.w3schools.com/jsref/jsref_parseint.asp
    let previousMginTop = parseInt(elementStyles.marginTop);

    // Apply margin if there's deadspace to fill in the viewport
    if (windowH > (headerH + interfaceH - previousMginTop))
    {
        targetElement.style.marginTop = `${windowH - headerH - interfaceH + previousMginTop}px`;
    }
}

function adjustMarginBottom(targetElement, panelH)
// Check height of the viewport and adjust the bottom margin of key elements to ensure a responsive layout
{
    let windowH = window.innerHeight;
    let headerH = document.querySelector("header").clientHeight;
    let footerH = document.querySelector("footer").clientHeight;

    // https://developer.mozilla.org/en-US/docs/Web/API/Window/getComputedStyle
    let elementStyles = window.getComputedStyle(targetElement);

    // Must discount the previous bottom margin   
    // (get rid of pixel units from style) https://www.w3schools.com/jsref/jsref_parseint.asp
    let previousMginBottom = parseInt(elementStyles.marginBottom);

    // Apply margin if there's deadspace to fill in the viewport
    if (windowH > (headerH + panelH + footerH - previousMginBottom))
    {
        targetElement.style.marginBottom =
            `${windowH - headerH - panelH - footerH + previousMginBottom}px`;
    }
    // Otherwise keep the default style
    else
    {
        targetElement.style.marginBottom = "5vh";
    }
}
