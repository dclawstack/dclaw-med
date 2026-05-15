"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { usePathname, useRouter } from "next/navigation";
import { CurrentUser, getCurrentUser, login as apiLogin } from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth-storage";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const PUBLIC_ROUTES = new Set(["/login"]);
const PORTAL_HOME = "/patient-portal";

function landingFor(user: CurrentUser): string {
  return user.role === "patient" ? PORTAL_HOME : "/";
}

function isPathAllowedForPatient(pathname: string): boolean {
  return (
    pathname === PORTAL_HOME ||
    pathname.startsWith(`${PORTAL_HOME}/`) ||
    pathname === "/settings" ||
    pathname === "/login"
  );
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      if (!PUBLIC_ROUTES.has(pathname)) router.replace("/login");
      return;
    }
    getCurrentUser()
      .then((u) => {
        setUser(u);
        // Keep patients out of clinician pages even if they paste in a URL.
        if (u.role === "patient" && !isPathAllowedForPatient(pathname)) {
          router.replace(PORTAL_HOME);
        }
      })
      .catch(() => {
        clearToken();
        router.replace("/login");
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const tok = await apiLogin(email, password);
      setToken(tok.access_token);
      const me = await getCurrentUser();
      setUser(me);
      router.replace(landingFor(me));
    },
    [router],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    router.replace("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
