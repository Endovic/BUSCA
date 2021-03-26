// // CONTACT PAGE // //

window.onload = function() {    
    // Scroll to display flashed message once form has been submitted
    // (does not apply for larger screens where messages are displayed at top of page)
    // https://css-tricks.com/working-with-javascript-media-queries/
    let mediaQuery = window.matchMedia('(max-width: 1023px)');
    if (mediaQuery.matches)
    {
        if (document.getElementById("alert-contact"))
        {
            document.getElementById("alert-contact").scrollIntoView();
        }
    }
}
