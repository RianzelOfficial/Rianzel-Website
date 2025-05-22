import axios from 'axios';
import { ref, computed } from 'vue';
import { useToast } from 'vue-toastification';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  isVerified: boolean;
}

interface Token {
  access_token: string;
  token_type: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const currentUser = ref<User | null>(null);
const isAuthenticated = computed(() => currentUser.value !== null);

export const useAuth = () => {
  const toast = useToast();
  
  const login = async (username: string, password: string): Promise<Token | null> => {
    try {
      const response = await axios.post(`${API_URL}/token/`, {
        username,
        password
      });
      
      const token = response.data;
      localStorage.setItem('token', JSON.stringify(token));
      
      // Get user info
      const userInfo = await axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token.access_token}` }
      });
      
      currentUser.value = userInfo.data;
      toast.success('Successfully logged in!');
      return token;
    } catch (error) {
      toast.error('Login failed. Please check your credentials.');
      return null;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    currentUser.value = null;
    toast.success('Successfully logged out!');
  };

  const register = async (userData: {
    username: string;
    email: string;
    password: string;
    confirmPassword: string;
  }): Promise<boolean> => {
    try {
      await axios.post(`${API_URL}/users/`, userData);
      toast.success('Registration successful! Please verify your email.');
      return true;
    } catch (error) {
      toast.error('Registration failed. Please try again.');
      return false;
    }
  };

  const verifyEmail = async (token: string): Promise<boolean> => {
    try {
      await axios.post(`${API_URL}/users/verify/`, { token });
      toast.success('Email verified successfully!');
      return true;
    } catch (error) {
      toast.error('Email verification failed. Please try again.');
      return false;
    }
  };

  const resetPassword = async (
    email: string
  ): Promise<boolean> => {
    try {
      await axios.post(`${API_URL}/password/reset/`, { email });
      toast.success('Password reset instructions sent to your email.');
      return true;
    } catch (error) {
      toast.error('Failed to send password reset instructions.');
      return false;
    }
  };

  const updatePassword = async (
    token: string,
    newPassword: string
  ): Promise<boolean> => {
    try {
      await axios.post(`${API_URL}/password/reset/confirm/`, {
        token,
        new_password: newPassword
      });
      toast.success('Password updated successfully!');
      return true;
    } catch (error) {
      toast.error('Failed to update password.');
      return false;
    }
  };

  return {
    currentUser,
    isAuthenticated,
    login,
    logout,
    register,
    verifyEmail,
    resetPassword,
    updatePassword
  };
};
