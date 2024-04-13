import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CryptoJS from 'crypto-js';

const SignIn = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/transactions");
    }
  }, [isAuthenticated, navigate]);

  async function hashPassword(password) {
    const wordArray = CryptoJS.SHA256(password);
    return CryptoJS.enc.Hex.stringify(wordArray); // Return hexadecimal string
  }

  const onLoginButtonClick = async (e) => {
    e.preventDefault();
    const hashedPassword = await hashPassword(password);
    const macKey = CryptoJS.enc.Hex.parse(hashedPassword); // Directly parse the hashed password to use as macKey
    const hmac = CryptoJS.HmacSHA256(password, macKey).toString(CryptoJS.enc.Base64);

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password: hashedPassword, mac: hmac }),
        });

        const data = await response.json();
        if (response.ok && data.authenticated) {
            sessionStorage.setItem("isAuthenticated", "true");
            sessionStorage.setItem("encryptionKey", "default_master_secret");
            sessionStorage.setItem("password", hashedPassword); // Store the hashed password
            sessionStorage.setItem("username", username);
            setIsAuthenticated(true);
            //const macKeyBase64 = CryptoJS.enc.Base64.stringify(macKey);
            sessionStorage.setItem("macKey", data.mackKey);
            navigate("/transactions");
        } else {
            setErrorMessage(data.message || "Invalid username or password.");
        }
    } catch (error) {
        console.error("Error during sign in:", error);
        setErrorMessage("Error during sign in. Please try again.");
    }
  };

  return (
    <div className="form-container">
      <form className="signin-form" onSubmit={onLoginButtonClick}>
        <h2 className="form-title text-center">SIGN IN</h2>
        {errorMessage && <div className="error-message">{errorMessage}</div>}
        <input className="form-input" type="text" name="USER ID" placeholder="User ID" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="form-input" type="password" name="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button className="form-button" type="submit">Login</button>
      </form>
    </div>
  );
};

export default SignIn;
