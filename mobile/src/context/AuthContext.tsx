import React, { createContext, useContext, useState, useEffect } from "react";
import { mobileApiRequest, setAuthTokens } from "../services/api";

export interface StudentUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  college: string;
  college_name: string;
  student_number?: string;
  roll_number?: string;
  department_name?: string;
  course_name?: string;
  batch_name?: string;
  semester_number?: number;
}

interface AuthContextType {
  user: StudentUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  loginAsDemoStudent: (type: "rahul" | "rohan" | "ananya") => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<StudentUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const tokenRes = await mobileApiRequest<{ access: string; refresh: string }>("/auth/token/", {
        method: "POST",
        body: { email, password: pass },
      });

      setAuthTokens(tokenRes.access, tokenRes.refresh);

      // Fetch user profile
      const meRes = await mobileApiRequest<{ data: StudentUser }>("/auth/me/");
      setUser(meRes.data || (meRes as unknown as StudentUser));
    } finally {
      setIsLoading(false);
    }
  };

  const loginAsDemoStudent = async (type: "rahul" | "rohan" | "ananya") => {
    const emailMap = {
      rahul: "student.rahul@apex.edu",
      rohan: "rohan.gupta@apex.edu",
      ananya: "ananya.sen@apex.edu",
    };
    await login(emailMap[type], "Password123!");
  };

  const logout = () => {
    setAuthTokens(null, null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        loginAsDemoStudent,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
