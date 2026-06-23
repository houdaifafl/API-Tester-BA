import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    userId: localStorage.getItem('userId'),
    email: localStorage.getItem('email'),
    username: localStorage.getItem('username'),
    token: localStorage.getItem('token'),
  });

  const logout = useCallback(() => {
    localStorage.removeItem('userId');
    localStorage.removeItem('email');
    localStorage.removeItem('username');
    localStorage.removeItem('token');
    setUser({ userId: null, email: null, username: null, token: null });
  }, []);

  const value = useMemo(() => ({ user, setUser, logout }), [user, logout]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
