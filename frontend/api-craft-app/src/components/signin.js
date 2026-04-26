import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import './signin.css';

function Signin() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('http://localhost:5000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: name, email, password }),
      });
      if (res.ok) {
        navigate('/login');
      } else {
        const data = await res.json();
        setError(data.error);
      }
    } catch {
      setError('Could not connect to the server.');
    }
  };

  return (
    <div className="signup-page d-flex flex-column">

      {/* Top-left brand */}
      <div className="p-3 ps-4">
        <span className="brand-title">APICraft</span>
      </div>

      {/* Centered card */}
      <div className="d-flex flex-grow-1 align-items-center justify-content-center px-3 px-xl-0">
        <div className="card signup-card px-4 py-4">

          <h2 className="signup-title text-center mb-4">Sign up</h2>

          <form onSubmit={handleSubmit} className="px-2">

            {/* Name field */}
            <div className="mb-4">
              <label className="form-label text-secondary fw-semibold">Name</label>
              <input
                type="text"
                className="form-control su-input-underline w-100"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            {/* Email field */}
            <div className="mb-4">
              <label className="form-label text-secondary fw-semibold">Email</label>
              <input
                type="email"
                className="form-control su-input-underline w-100"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password field */}
            <div className="mb-4">
              <label className="form-label text-secondary fw-semibold">Password</label>
              <div className="su-password-underline d-flex align-items-center">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control su-input-underline flex-grow-1"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="su-eye-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Sign up button */}
            {error && <p className="text-danger small mb-2">{error}</p>}
            <button type="submit" className="btn btn-signup w-100 mb-4">
              Sign up
            </button>

          </form>

          {/* Access quickly divider */}
          <div className="d-flex align-items-center gap-2 px-2 mb-3">
            <hr className="flex-grow-1 su-divider" />
            <span className="su-divider-text">ACCESS QUICKLY</span>
            <hr className="flex-grow-1 su-divider" />
          </div>

          {/* Google */}
          <div className="text-center mb-3">
            <button type="button" className="btn-google">GOOGLE</button>
          </div>

          {/* Already have an account */}
          <div className="text-center">
            <span className="su-footer-text">Already have an account? </span>
            <Link to="/login" className="su-footer-link">Login</Link>
          </div>

        </div>
      </div>

    </div>
  );
}

export default Signin;
