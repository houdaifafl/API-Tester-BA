import React, { createContext, useContext, useMemo, useState, useCallback, useEffect } from 'react';
import { logout as apiLogout, getMe } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState({
    userId: sessionStorage.getItem('userId'),
    email: sessionStorage.getItem('email'),
    username: sessionStorage.getItem('username'),
    isAdmin: false,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((data) => {
        setUser({
          userId: data.user_id,
          email: data.email,
          username: data.username,
          isAdmin: data.is_admin,
        });
      })
      .catch(() => {
        sessionStorage.removeItem('userId');
        sessionStorage.removeItem('email');
        sessionStorage.removeItem('username');
        setUser({ userId: null, email: null, username: null, isAdmin: false });
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const logout = useCallback(() => {
    // Call backend API to delete the token cookie (failsafe, run in background)
    apiLogout().catch((err) => console.error("Failed to log out from backend:", err));

    sessionStorage.removeItem('userId');
    sessionStorage.removeItem('email');
    sessionStorage.removeItem('username');
    setUser({ userId: null, email: null, username: null, isAdmin: false });
  }, []);

  const value = useMemo(() => ({ user, setUser, logout, loading }), [user, logout, loading]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
