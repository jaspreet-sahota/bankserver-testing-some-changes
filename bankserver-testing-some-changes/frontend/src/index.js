import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SimpleReactLightbox from "simple-react-lightbox";

import SignIn from "./components/pages/signin/SignIn";
import Layout from "./components/app";
import Transactions from "./components/pages/transactions/Transactions";

import "./index.css";
import "./index.scss";

class Root extends React.Component {
  render() {
    return (
      <BrowserRouter basename={"/"}>
        <SimpleReactLightbox>
          <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route path="/" element={<SignIn />} />
            <Route path="/transactions" element={<Transactions />}>
            </Route>
            {/* If there are no other routes for the root, you can remove redundant declarations */}
          </Routes>
        </SimpleReactLightbox>
      </BrowserRouter>
    );
  }
}

ReactDOM.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
  document.getElementById("root")
);
