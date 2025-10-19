export function saveToken(token){ localStorage.setItem("vt_token", token); }
export function getToken(){ return localStorage.getItem("vt_token"); }
export function clearToken(){ localStorage.removeItem("vt_token"); }
