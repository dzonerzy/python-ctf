$(document).ready(function() {
    $.get("/check-virtual", function(data) {
        if(data.result == 1) {
            document.body.innerHTML = "Redirecting to your virtual phone...";
            setTimeout(function() {
                document.location.href = "/my-virtual-phone";
            }, 3000);
        }
    })
})