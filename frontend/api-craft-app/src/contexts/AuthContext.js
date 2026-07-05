import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    userId: sessionStorage.getItem('userId'),
    email: sessionStorage.getItem('email'),
    username: sessionStorage.getItem('username'),
    token: sessionStorage.getItem('token'),
    isAdmin: sessionStorage.getItem('isAdmin') === 'true',
  });

  const logout = useCallback(() => {
    sessionStorage.removeItem('userId');
    sessionStorage.removeItem('email');
    sessionStorage.removeItem('username');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('isAdmin');
    setUser({ userId: null, email: null, username: null, token: null, isAdmin: false });
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
