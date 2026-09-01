import jwt from 'jsonwebtoken';
import crypto from 'node:crypto';
import { DatabaseAdapter } from '../db/adapter.js';
import { UserRole } from './rbac.js';

export interface SessionUser {
  userId: string;
  tenantId: string;
  email: string;
  role: UserRole;
  mfaVerified?: boolean;
}

export interface SessionRecord {
  id: string;
  user_id: string;
  tenant_id: string;
  token_hash: string;
  role: UserRole;
  expires_at: string;
  created_at: string;
  revoked_at: string | null;
}

/**
 * Resolution of Decision D7: Dashboard Session Authentication
 * Provides signed JWT tokens with database session tracking, revocation, and MFA state.
 */
export class SessionAuthService {
  private static jwtSecret = process.env.JWT_SECRET || 'ultron_v6_jwt_session_secret_2026';
  private static defaultSessionDurationSec = 1800; // 30 minutes

  /**
   * Creates a new user session and stores its hash in SQLite.
   */
  public static async createSession(params: {
    userId: string;
    tenantId: string;
    email: string;
    role: UserRole;
    ipAddress?: string;
    userAgent?: string;
    mfaVerified?: boolean;
  }): Promise<{
    sessionId: string;
    token: string;
    expiresAt: string;
  }> {
    const sessionId = `ses_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    const now = new Date();
    const expiresAt = new Date(now.getTime() + this.defaultSessionDurationSec * 1000).toISOString();

    const payload: SessionUser & { sessionId: string } = {
      sessionId,
      userId: params.userId,
      tenantId: params.tenantId,
      email: params.email,
      role: params.role,
      mfaVerified: Boolean(params.mfaVerified),
    };

    const token = jwt.sign(payload, this.jwtSecret, {
      expiresIn: this.defaultSessionDurationSec,
    });

    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    const db = DatabaseAdapter.getInstance();

    await db.execute(
      `INSERT INTO sessions (id, user_id, tenant_id, token_hash, role, ip_address, user_agent, expires_at, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);`,
      [
        sessionId,
        params.userId,
        params.tenantId,
        tokenHash,
        params.role,
        params.ipAddress || '127.0.0.1',
        params.userAgent || 'Unknown',
        expiresAt,
        now.toISOString(),
      ]
    );

    return {
      sessionId,
      token,
      expiresAt,
    };
  }

  /**
   * Validates a session JWT token against the database session store.
   */
  public static async validateSession(token: string): Promise<{
    valid: boolean;
    user?: SessionUser;
    errorReason?: string;
  }> {
    try {
      const decoded = jwt.verify(token, this.jwtSecret) as SessionUser & { sessionId: string };
      const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

      const db = DatabaseAdapter.getInstance();
      const rows = await db.query<any>(
        `SELECT * FROM sessions WHERE token_hash = ? AND tenant_id = ?;`,
        [tokenHash, decoded.tenantId]
      );

      if (rows.length === 0) {
        return { valid: false, errorReason: 'Session not found in active registry' };
      }

      const session = rows[0];
      if (session.revoked_at) {
        return { valid: false, errorReason: 'Session has been revoked' };
      }

      if (new Date(session.expires_at).getTime() < Date.now()) {
        return { valid: false, errorReason: 'Session has expired' };
      }

      return {
        valid: true,
        user: {
          userId: decoded.userId,
          tenantId: decoded.tenantId,
          email: decoded.email,
          role: decoded.role,
          mfaVerified: decoded.mfaVerified,
        },
      };
    } catch (err: any) {
      return { valid: false, errorReason: err.message || 'Invalid session token' };
    }
  }

  /**
   * Revokes a session token.
   */
  public static async revokeSession(sessionId: string): Promise<boolean> {
    const db = DatabaseAdapter.getInstance();
    const result = await db.execute(
      `UPDATE sessions SET revoked_at = ? WHERE id = ? AND revoked_at IS NULL;`,
      [new Date().toISOString(), sessionId]
    );
    return (result?.rowCount ?? 0) > 0;
  }

  /**
   * Revokes a session by its raw JWT token (hashes it and looks up the DB record).
   */
  public static async revokeSessionByToken(token: string): Promise<boolean> {
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    const db = DatabaseAdapter.getInstance();
    const result = await db.execute(
      `UPDATE sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL;`,
      [new Date().toISOString(), tokenHash]
    );
    return (result?.rowCount ?? 0) > 0;
  }

}
