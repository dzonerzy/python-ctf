USER_MESSAGES = {
    "account_created": "Account successfully created, now you can login.",
    "invalid_user_password": "Invalid username or password.",
    "user_not_exists": "The specified user does not exist.",
    "too_many_attempts": "Too many reset attempts, please start over.",
    "password_reset_ok": "Password successfully reset."
}

$(document).ready(function(){
    var searchParams = new URLSearchParams(window.location.search);
    if(searchParams.has('message')) {
        let msg = searchParams.get('message');
        if(typeof(USER_MESSAGES[msg]) != "undefined" ) {
            alertify.success(USER_MESSAGES[msg], 5);
        }
    }

    if(searchParams.has('error')) {
        let msg = searchParams.get('error');
        if(typeof(USER_MESSAGES[msg]) != "undefined" ) {
            alertify.error(USER_MESSAGES[msg], 5);
        }
    }

    $("#send-code").click(function(){
        $.post("/send-code", function(data){
            if(!data.result) {
                alertify.error("Unable to sent OTP token!", 5);
            }else{
                alertify.success("OTP token sent via SMS.", 5);
            }
        });
    })
})