import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaUser, FaLock } from 'react-icons/fa';
import './login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // API integration will be added later
  };

  return (
    <div className="login-page d-flex flex-column">

      {/* Top-left brand */}
      <div className="p-3 ps-4">
        <span className="brand-title">APICraft</span>
      </div>

      {/* Centered card */}
      <div className="d-flex flex-grow-1 align-items-center justify-content-center">
        <div className="card login-card px-4 py-5" style={{paddingTop: '3.5rem', paddingBottom: '3.5rem'}}>

          <h2 className="login-title text-center mb-5">Login</h2>

          <form onSubmit={handleSubmit} className="px-3">

            {/* Username field */}
            <div className="mb-5">
              <label className="form-label text-secondary fw-semibold">Username</label>
              <div className="d-flex align-items-center gap-2">
                <FaUser className="input-icon" />
                <input
                  type="text"
                  className="form-control input-underline"
                  placeholder="Type your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>

            {/* Password field */}
            <div className="mb-1">
              <label className="form-label text-secondary fw-semibold">Password</label>
              <div className="d-flex align-items-center gap-2">
                <FaLock className="input-icon" />
                <input
                  type="password"
                  className="form-control input-underline"
                  placeholder="Type your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {/* Forgot password */}
            <div className="text-end mb-4">
              <span className="forgot-password">Forgot password?</span>
            </div>

            {/* Login button */}
            <button type="submit" className="btn btn-login w-100 mb-5">
              LOGIN
            </button>

          </form>

          {/* Sign up */}
          <div className="text-center">
            <span className="signup-text">Don't have an account yet? </span>
            <Link to="/signup" className="signup-link">Sign Up</Link>
          </div>

        </div>
      </div>

    </div>
  );
}

export default Login;
