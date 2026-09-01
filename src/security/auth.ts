import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';
import { verifySupabaseToken } from './supabase.js';

const JWT_SECRET = process.env.JWT_SECRET || 'ultron_secure_jwt_secret_key_2026';
const SESSION_EXPIRY = '30m'; // 30-minute session expiry

export interface AuthUser {
  userId: string;
  role: string;
  merchant_id?: string;
  tenantId?: string;
}

export interface AuthenticatedRequest extends Request {
  user?: AuthUser;
}

/**
 * Generates a signed JWT session token with 30-minute expiration.
 */
export function generateSessionToken(payload: AuthUser, expiresIn: string = SESSION_EXPIRY): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: expiresIn as any });
}

/**
 * Verifies a given JWT token string.
 */
export function verifySessionToken(token: string): AuthUser {
  return jwt.verify(token, JWT_SECRET) as AuthUser;
}

/**
 * Dual-Engine Authentication Middleware (Supports local ULTRON JWT & Supabase Auth tokens).
 */
export async function authenticateJWT(req: AuthenticatedRequest, res: Response, next: NextFunction): Promise<void> {
  // Allow test / local development bypass if auth is explicitly disabled
  if (process.env.AUTH_REQUIRED === 'false' && !req.headers.authorization) {
    req.user = {
      userId: 'dev_operator',
      role: 'admin',
      merchant_id: 'merchant_default',
      tenantId: 'tenant_system_default',
    };
    return next();
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    if (process.env.AUTH_REQUIRED === 'true') {
      res.status(401).json({ error: 'Unauthorized: Missing or invalid Authorization Bearer token' });
      return;
    }
    // Fallback for dev mode
    req.user = {
      userId: 'dev_operator',
      role: 'admin',
      merchant_id: 'merchant_default',
      tenantId: 'tenant_system_default',
    };
    return next();
  }

  const token = authHeader.split(' ')[1];

  // 1. Try local session JWT token
  try {
    const user = verifySessionToken(token) as any;
    req.user = {
      userId: user.userId || user.id || 'dev_operator',
      role: user.role || 'admin',
      tenantId: user.tenantId || user.merchant_id || 'tenant_system_default',
      merchant_id: user.merchant_id || user.tenantId || 'tenant_system_default',
    };
    return next();
  } catch (localErr: any) {
    // 2. Try Supabase Auth token
    try {
      const sbResult = await verifySupabaseToken(token);
      if (sbResult.valid && sbResult.user) {
        const tenantId = sbResult.user.tenantId || `tnt_${sbResult.user.id.slice(0, 8)}`;
        req.user = {
          userId: sbResult.user.id,
          role: sbResult.user.role || 'Owner',
          merchant_id: tenantId,
          tenantId: tenantId,
        };
        return next();
      }
    } catch (sbErr) {
      // ignore
    }

    res.status(403).json({ error: 'Forbidden: Session token expired or invalid', details: localErr.message });
  }
}

