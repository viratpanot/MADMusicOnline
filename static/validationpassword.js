function matchPassword() {
    let pw1 = document.getElementById("password");
    let pw2 = document.getElementById("confirmpassword");
  
    if(pw1 != pw2)
  {	
  	alert("Passwords did not match");
  } else {
  	alert("Password created successfully");
  }
}
