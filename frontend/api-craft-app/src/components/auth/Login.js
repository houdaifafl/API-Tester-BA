import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaUser, FaLock, FaEye, FaEyeSlash } from 'react-icons/fa';
import { login } from '../../services/authService';
import { useAuth } from '../../contexts/AuthContext';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await login(username, password);
      localStorage.setItem('firstName', data.first_name);
      localStorage.setItem('userId', data.user_id);
      localStorage.setItem('email', data.email);
      setUser({ userId: data.user_id, email: data.email, firstName: data.first_name });
      navigate('/main');
    } catch (err) {
      setError(err.message || 'Could not connect to the server.');
    }
  };

  return (
    <div className="login-page d-flex flex-column">

      {/* Top-left brand */}
      <div className="p-3 ps-4">
        <span className="brand-title">APICraft</span>
      </div>

      {/* Centered card */}
      <div className="d-flex flex-grow-1 align-items-center justify-content-center px-3 px-xl-0">
        <div className="card login-card px-4 py-4">

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
                <div className="password-underline d-flex align-items-center flex-grow-1">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-control input-underline"
                    placeholder="Type your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="eye-toggle"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>
            </div>

            {/* Forgot password */}
            <div className="text-end mb-4">
              <span className="forgot-password">Forgot password?</span>
            </div>

            {/* Login button */}
            {error && <p className="text-danger small mb-2">{error}</p>}
            <button type="submit" className="btn btn-login w-100 mb-5">
              LOGIN
            </button>

          </form>

          {/* Sign up */}
          <div className="text-center">
            <span className="signup-text">Don't have an account yet? </span>
            <br></br>
            <Link to="/signup" className="signup-link">Sign Up</Link>
          </div>

        </div>
      </div>

    </div>
  );
}

export default Login;
