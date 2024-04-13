import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CryptoJS from "crypto-js";
import "./Transactions.css";

function Transactions() {
  const navigate = useNavigate();
  const isAuthenticated = sessionStorage.getItem("isAuthenticated") === "true";
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [showInputAdd, setShowInputAdd] = useState(false);
  const [showInputWithdraw, setShowInputWithdraw] = useState(false);
  const [showBalance, setShowBalance] = useState(false);
  const username = sessionStorage.getItem("username");
  const encryptionKey = sessionStorage.getItem("encryptionKey") || "default_master_secret"; // Provide a default value if null
  const hashedPassword = sessionStorage.getItem("password"); // Retrieve hashed password from sign-in

  const macKeyBase64 = sessionStorage.getItem("macKey");
  const macKey = macKeyBase64 ? CryptoJS.enc.Base64.parse(macKeyBase64) : null;

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/signin");
    } else {
      fetchBalance(); // Fetch balance upon component initialization
    }
  }, [isAuthenticated, navigate]);

  const encryptData = (data) => {
    const key = CryptoJS.enc.Hex.parse(sessionStorage.getItem("encryptionKey"));
    const iv = CryptoJS.lib.WordArray.random(128 / 8).toString(CryptoJS.enc.Hex);
    const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key, {
      iv: CryptoJS.enc.Hex.parse(iv),
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });
    return { encryptedData: encrypted.toString(), iv: iv };
  };

  const generateHMAC = (encryptedData) => {
    if (!macKey) return "";
    return CryptoJS.HmacSHA256(encryptedData, macKey).toString(CryptoJS.enc.Base64);
  };
  
  const handleTransaction = async (endpoint, jsonData) => {
    const { encryptedData } = encryptData(jsonData);
    const hmac = generateHMAC(encryptedData);
    try {
      const response = await fetch(`http://127.0.0.1:5000/transaction/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, encryptedData, hmac })
      });
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}, Message: ${responseData.message}`);
      }
      return responseData;
    } catch (error) {
      console.error("Failed to fetch:", error);
      setErrorMessage("Failed to perform transaction.");
      return null;
    }
  };

  const handleSubmitAdd = async (e) => {
    e.preventDefault();
    const jsonData = { username, amount: parseFloat(amount) };
    const data = await handleTransaction("deposit", jsonData);

    if (data && data.message) {
      setBalance(data.new_balance);
      setAmount("");
      setShowInputAdd(false);
    } else {
      setErrorMessage("Failed to add funds.");
    }
  };

  const handleSubmitWithdraw = async (e) => {
    e.preventDefault();
    const jsonData = { username, amount: parseFloat(amount) };
    const data = await handleTransaction("withdraw", jsonData);

    if (data && data.message) {
      setBalance(data.new_balance);
      setAmount("");
      setShowInputWithdraw(false);
    } else {
      setErrorMessage("Failed to withdraw funds.");
    }
  };

  const fetchBalance = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/balance/${username}`);
      const data = await response.json();
      if (response.ok) {
        setBalance(data.balance);
      } else {
        throw new Error(data.message || "Failed to fetch balance");
      }
    } catch (error) {
      console.error("Error fetching balance:", error);
      setErrorMessage(error.message || "Failed to retrieve balance.");
    }
  };

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/signin");
  };

  return (
    <div className="form-container">
      <div className="landing-form">
        {errorMessage && <div className="error-message">{errorMessage}</div>}
        <button className="form-button" onClick={() => setShowInputAdd(true)}>Add Funds</button>
        <button className="form-button" onClick={() => setShowInputWithdraw(true)}>Withdraw Funds</button>
        <button className="form-button" onClick={() => setShowBalance(!showBalance)}>View Current Balance</button>
        <button className="form-button" onClick={handleLogout}>Logout</button>
        {showInputAdd && (
          <form onSubmit={handleSubmitAdd}>
            <input type="number" name="amount" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <button className="form-button">Submit</button>
          </form>
        )}
        {showInputWithdraw && (
          <form onSubmit={handleSubmitWithdraw}>
            <input type="number" name="amount" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <button className="form-button">Submit</button>
          </form>
        )}
        {showBalance && <div className="balance-display">Your current balance is: ${balance.toFixed(2)}</div>}
      </div>
    </div>
  );
}

export default Transactions;
