// Central RBAC policy for the frontend.
// NOTE: this controls what the UI shows. The backend MUST enforce the same rules
// on every endpoint (the browser can never be fully trusted).

export type Role = "admin" | "operator" | "public";

export const ALL_ROLES: Role[] = ["admin", "operator", "public"];

// Route -> roles allowed to open it. Unlisted protected routes are denied by default.
export const ROUTE_ACCESS: Record<string, Role[]> = {
  "/dashboard": ["admin", "operator", "public"],
  "/live-map": ["admin", "operator", "public"],
  "/route-analysis": ["admin", "operator", "public"],
  "/alerts": ["admin", "operator", "public"],
  "/predictions": ["admin", "operator"],
  "/analytics": ["admin", "operator"],
};

export const PUBLIC_ROUTES = ["/", "/login", "/register"];

export const DEFAULT_HOME = "/dashboard";

/** Normalise any role string coming from the backend. Unknown -> least privilege. */
export function normalizeRole(raw: unknown): Role {
  const r = String(raw ?? "").toLowerCase();
  if (r === "admin") return "admin";
  if (r === "operator" || r === "traffic_operator") return "operator";
  return "public"; // commuter / public / city_planner / anything unknown
}

export function canAccess(role: Role | null, pathname: string): boolean {
  if (!role) return false;
  const match = Object.keys(ROUTE_ACCESS).find(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );
  if (!match) return false;
  return ROUTE_ACCESS[match].includes(role);
}

// Action-level permissions (used to hide/disable buttons)
export const can = {
  dispatchOrAcknowledge: (role: Role) => role === "admin" || role === "operator",
  runSimulationSandbox: (role: Role) => role === "admin" || role === "operator",
  adminOverride: (role: Role) => role === "admin",
};

/** Read the role claim out of a JWT (display/UX only - the server is the authority). */
export function roleFromJwt(token: string | null): Role | null {
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const json = JSON.parse(
      decodeURIComponent(
        atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"))
          .split("")
          .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
          .join("")
      )
    );
    return json.role ? normalizeRole(json.role) : null;
  } catch {
    return null;
  }
}
