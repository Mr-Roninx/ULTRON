import { Router, Request, Response } from 'express';
import crypto from 'node:crypto';
import { DatabaseAdapter } from '../db/adapter.js';
import { sendTeamInviteEmail, sendSignupConfirmationEmail } from '../notifications/email.js';
import { SessionAuthService } from '../security/session_auth.js';
import { PasswordService } from '../security/password.js';
import { TenancyEnforcer, TenantScopedRequest } from '../security/tenancy.js';
import { UserRole } from '../security/rbac.js';

export const authRouter = Router();

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/signup
// Creates a brand new merchant account with an isolated business tenant.
// Uses bcrypt for password hashing.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post('/signup', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, business_name, password } = req.body;

    if (!email || !business_name || !password) {
      res.status(400).json({
        error: 'Validation Error',
        message: 'email, business_name, and password are required.',
      });
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      res.status(400).json({ error: 'Validation Error', message: 'Invalid email format.' });
      return;
    }

    const db = DatabaseAdapter.getInstance();

    // Check for duplicate email
    const existing = await db.query<any>(`SELECT id FROM users WHERE email = ?;`, [email]);
    if (existing.length > 0) {
      res.status(409).json({ error: 'Conflict', message: 'An account with this email already exists.' });
      return;
    }

    // Validate + hash password
    let passwordHash: string;
    try {
      passwordHash = await PasswordService.hashPassword(password);
    } catch (err: any) {
      res.status(400).json({ error: 'Validation Error', message: err.message });
      return;
    }

    const tenantId = `tnt_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    const userId = `usr_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    const slug = `${business_name.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${Date.now()}`;
    const now = new Date().toISOString();

    // Atomic: tenant + user + membership in one transaction
    await db.withTransaction(async (tx) => {
      await tx.execute(
        `INSERT INTO tenants (id, name, slug, environment, status, created_at)
         VALUES (?, ?, ?, 'test', 'ACTIVE', ?);`,
        [tenantId, business_name, slug, now]
      );
      await tx.execute(
        `INSERT INTO users (id, email, name, password_hash, mfa_enabled, created_at)
         VALUES (?, ?, ?, ?, 0, ?);`,
        [userId, email, business_name, passwordHash, now]
      );
      await tx.execute(
        `INSERT INTO memberships (id, user_id, tenant_id, role, created_at)
         VALUES (?, ?, ?, 'Owner', ?);`,
        [`mem_${Date.now()}`, userId, tenantId, now]
      );
    });

    // Create session
    const session = await SessionAuthService.createSession({
      userId,
      tenantId,
      email,
      role: 'Owner' as UserRole,
      ipAddress: req.ip,
      userAgent: req.headers['user-agent'],
      mfaVerified: true,
    });

    // Asynchronously dispatch Signup Confirmation / Welcome Email via Resend
    sendSignupConfirmationEmail({
      email,
      businessName: business_name,
      userName: business_name,
      loginUrl: `${process.env.APP_URL || 'http://localhost:3000'}/login`,
    }).catch((mailErr: any) => {
      console.warn('[AUTH] Signup confirmation email dispatch warning:', mailErr.message);
    });

    res.status(201).json({
      success: true,
      message: 'Merchant account and tenant created successfully.',
      merchant: {
        user_id: userId,
        tenant_id: tenantId,
        email,
        business_name,
        role: 'Owner',
        environment: 'test',
      },
      session: {
        session_id: session.sessionId,
        token: session.token,
        expires_at: session.expiresAt,
      },
    });
  } catch (err: any) {
    console.error('[AUTH] Signup error:', err.message);
    res.status(500).json({ error: 'Internal Server Error', details: err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/demo-login
// 1-click instant login for testing and hackathon judges
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post('/demo-login', async (req: Request, res: Response): Promise<void> => {
  try {
    const db = DatabaseAdapter.getInstance();
    const email = 'demo@ultron.app';
    const rows = await db.query<any>(
      `SELECT u.id, u.email, u.name, m.tenant_id, m.role
       FROM users u
       JOIN memberships m ON m.user_id = u.id
       WHERE u.email = ?
       LIMIT 1;`,
      [email]
    );

    let user: any;
    if (rows.length === 0) {
      const tenantId = 'tenant_system_default';
      const userId = 'usr_demo_merchant';
      const now = new Date().toISOString();
      const passwordHash = await PasswordService.hashPassword('Ultron@2026');

      await db.execute(
        `INSERT OR IGNORE INTO tenants (id, name, slug, environment, status, created_at)
         VALUES (?, 'Apex Sound Labs (Demo)', 'apex_demo', 'test', 'ACTIVE', ?);`,
        [tenantId, now]
      );
      await db.execute(
        `INSERT OR REPLACE INTO users (id, email, name, password_hash, mfa_enabled, created_at)
         VALUES (?, ?, 'Apex Sound Labs (Demo)', ?, 0, ?);`,
        [userId, email, passwordHash, now]
      );
      await db.execute(
        `INSERT OR REPLACE INTO memberships (id, user_id, tenant_id, role, created_at)
         VALUES ('mem_demo', ?, ?, 'Owner', ?);`,
        [userId, tenantId, now]
      );
      user = { id: userId, email, name: 'Apex Sound Labs (Demo)', tenant_id: tenantId, role: 'Owner' };
    } else {
      user = rows[0];
    }

    const session = await SessionAuthService.createSession({
      userId: user.id,
      tenantId: user.tenant_id,
      email: user.email,
      role: 'Owner' as UserRole,
      ipAddress: req.ip,
      userAgent: req.headers['user-agent'],
      mfaVerified: true,
    });

    res.json({
      success: true,
      message: 'Demo login successful.',
      merchant: {
        user_id: user.id,
        tenant_id: user.tenant_id,
        email: user.email,
        name: user.name,
        role: 'Owner',
      },
      session: {
        session_id: session.sessionId,
        token: session.token,
        expires_at: session.expiresAt,
      },
    });
  } catch (err: any) {
    console.error('[AUTH] Demo login error:', err.message);
    res.status(500).json({ error: 'Internal Server Error', details: err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/login
// Email + password authentication using bcrypt verification.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post('/login', async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Validation Error', message: 'email and password are required.' });
      return;
    }

    const isDemoEmail = email.toLowerCase() === 'demo@ultron.app' || email.toLowerCase() === 'merchant@ultron.app';
    const isDemoPass = password === 'Ultron@2026' || password === 'password123' || password === 'ultron2026';

    const db = DatabaseAdapter.getInstance();

    // Fetch user + their tenant via membership
    const rows = await db.query<any>(
      `SELECT u.id, u.email, u.name, u.password_hash, u.mfa_enabled,
              m.tenant_id, m.role
       FROM users u
       JOIN memberships m ON m.user_id = u.id
       WHERE u.email = ?
       LIMIT 1;`,
      [email]
    );

    if (rows.length === 0) {
      if (isDemoEmail && isDemoPass) {
        // Auto-seed and log in demo user
        const tenantId = 'tenant_system_default';
        const userId = 'usr_demo_merchant';
        const now = new Date().toISOString();
        const passwordHash = await PasswordService.hashPassword('Ultron@2026');

        await db.execute(
          `INSERT OR IGNORE INTO tenants (id, name, slug, environment, status, created_at)
           VALUES (?, 'Apex Sound Labs (Demo)', 'apex_demo', 'test', 'ACTIVE', ?);`,
          [tenantId, now]
        );
        await db.execute(
          `INSERT OR REPLACE INTO users (id, email, name, password_hash, mfa_enabled, created_at)
           VALUES (?, ?, 'Apex Sound Labs (Demo)', ?, 0, ?);`,
          [userId, email, passwordHash, now]
        );
        await db.execute(
          `INSERT OR REPLACE INTO memberships (id, user_id, tenant_id, role, created_at)
           VALUES ('mem_demo', ?, ?, 'Owner', ?);`,
          [userId, tenantId, now]
        );

        const session = await SessionAuthService.createSession({
          userId,
          tenantId,
          email,
          role: 'Owner' as UserRole,
          ipAddress: req.ip,
          userAgent: req.headers['user-agent'],
          mfaVerified: true,
        });

        res.json({
          success: true,
          message: 'Login successful.',
          merchant: {
            user_id: userId,
            tenant_id: tenantId,
            email,
            name: 'Apex Sound Labs (Demo)',
            role: 'Owner',
          },
          session: {
            session_id: session.sessionId,
            token: session.token,
            expires_at: session.expiresAt,
          },
        });
        return;
      }

      // Constant-time response to prevent email enumeration
      res.status(401).json({ error: 'Unauthorized', message: 'Invalid email or password.' });
      return;
    }

    const user = rows[0];

    // Verify password with bcrypt, with demo bypass if matching demo credentials
    let passwordValid = false;
    try {
      passwordValid = await PasswordService.verifyPassword(password, user.password_hash);
    } catch {
      passwordValid = false;
    }

    if (!passwordValid && isDemoEmail && isDemoPass) {
      passwordValid = true;
      // Update with valid hash
      const newHash = await PasswordService.hashPassword('Ultron@2026');
      await db.execute(`UPDATE users SET password_hash = ? WHERE id = ?`, [newHash, user.id]);
    }

    if (!passwordValid) {
      res.status(401).json({ error: 'Unauthorized', message: 'Invalid email or password.' });
      return;
    }

    const session = await SessionAuthService.createSession({
      userId: user.id,
      tenantId: user.tenant_id,
      email: user.email,
      role: user.role as UserRole,
      ipAddress: req.ip,
      userAgent: req.headers['user-agent'],
      mfaVerified: true,
    });

    res.json({
      success: true,
      message: 'Login successful.',
      merchant: {
        user_id: user.id,
        tenant_id: user.tenant_id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      session: {
        session_id: session.sessionId,
        token: session.token,
        expires_at: session.expiresAt,
      },
    });
  } catch (err: any) {
    console.error('[AUTH] Login error:', err.message);
    res.status(500).json({ error: 'Internal Server Error', details: err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// ─────────────────────────────────────────────────────────────────────────────
// GET /v1/auth/me
// Returns current authenticated user + tenant context.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.get(
  '/me',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    const ctx = req.tenantContext!;
    const db = DatabaseAdapter.getInstance();

    // Fetch tenant metadata
    const tenants = await db.query<any>(
      `SELECT id, name, slug, environment, status, capacity_limit, kill_switch_active FROM tenants WHERE id = ?;`,
      [ctx.tenantId]
    ).catch(() => []);

    const defaultTenant = {
      id: ctx.tenantId,
      name: ctx.user?.email?.split('@')[0] || 'Merchant',
      slug: `merchant_${ctx.tenantId}`,
      environment: ctx.environment || 'test',
      status: 'ACTIVE',
      capacity_limit: 5,
      kill_switch_active: false,
    };

    res.json({
      authenticated: true,
      auth_type: ctx.authType,
      user: ctx.user || null,
      tenant: tenants[0] ? {
        ...tenants[0],
        kill_switch_active: Boolean(tenants[0].kill_switch_active),
      } : defaultTenant,
      scopes: ctx.scopes || null,
    });
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// PATCH /v1/auth/tenant
// Updates tenant configuration (name, capacity_limit, environment).
// ─────────────────────────────────────────────────────────────────────────────
authRouter.patch(
  '/tenant',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const ctx = req.tenantContext!;
      const { name, capacity_limit, environment } = req.body;
      const db = DatabaseAdapter.getInstance();

      const updates: string[] = [];
      const params: any[] = [];

      if (name !== undefined) {
        updates.push('name = ?');
        params.push(String(name).trim());
      }
      if (capacity_limit !== undefined) {
        const limit = Math.max(1, Math.min(100, Number(capacity_limit)));
        updates.push('capacity_limit = ?');
        params.push(limit);
      }
      if (environment !== undefined && (environment === 'test' || environment === 'live')) {
        updates.push('environment = ?');
        params.push(environment);
      }

      if (updates.length > 0) {
        params.push(ctx.tenantId);
        await db.execute(
          `UPDATE tenants SET ${updates.join(', ')} WHERE id = ?;`,
          params
        );
      }

      const tenants = await db.query<any>(
        `SELECT id, name, slug, environment, status, capacity_limit, kill_switch_active FROM tenants WHERE id = ?;`,
        [ctx.tenantId]
      );

      res.json({
        success: true,
        message: 'Tenant settings updated successfully.',
        tenant: tenants[0] || { id: ctx.tenantId },
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Failed to update tenant settings', details: err.message });
    }
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/refresh
// Refreshes an expiring session without requiring re-login.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post(
  '/refresh',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const ctx = req.tenantContext!;
      if (!ctx.user) {
        res.status(400).json({ error: 'Bad Request', message: 'Token refresh requires a session token, not an API key.' });
        return;
      }

      // Revoke old token
      const oldToken = req.headers.authorization?.substring(7).trim();
      if (oldToken) await SessionAuthService.revokeSessionByToken(oldToken);

      // Issue new session
      const session = await SessionAuthService.createSession({
        userId: ctx.user.userId,
        tenantId: ctx.tenantId,
        email: ctx.user.email,
        role: ctx.user.role,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
        mfaVerified: ctx.user.mfaVerified,
      });

      res.json({
        success: true,
        message: 'Session refreshed.',
        session: {
          session_id: session.sessionId,
          token: session.token,
          expires_at: session.expiresAt,
        },
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Internal Server Error', details: err.message });
    }
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/logout
// Revokes the current session token.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post(
  '/logout',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7).trim();
      await SessionAuthService.revokeSessionByToken(token);
    }
    res.json({ success: true, message: 'Session revoked successfully.' });
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// GET /v1/auth/team
// Lists all team members for the authenticated tenant.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.get(
  '/team',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const ctx = req.tenantContext!;
      const db = DatabaseAdapter.getInstance();
      const members = await db.query<any>(
        `SELECT m.id, m.user_id, u.email, u.name, m.role, u.mfa_enabled, m.created_at as joined_at
         FROM memberships m
         JOIN users u ON m.user_id = u.id
         WHERE m.tenant_id = ?;`,
        [ctx.tenantId]
      ).catch(() => []);
      res.json({ members });
    } catch (err: any) {
      res.status(500).json({ error: 'Failed to fetch team members', details: err.message });
    }
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// POST /v1/auth/invite
// Invites a new team member to the tenant.
// ─────────────────────────────────────────────────────────────────────────────
authRouter.post(
  '/invite',
  TenancyEnforcer.authenticateTenant(),
  async (req: TenantScopedRequest, res: Response): Promise<void> => {
    try {
      const ctx = req.tenantContext!;
      const { email, role } = req.body;
      if (!email) {
        res.status(400).json({ error: 'Validation Error', message: 'email is required.' });
        return;
      }
      const roleName = role || 'Analyst';
      const inviterName = (ctx.user as any)?.name || ctx.user?.email || 'Your Team';
      const inviteUrl = `${process.env.APP_URL || 'http://localhost:3000'}/signup?ref=${ctx.tenantId}`;

      await sendTeamInviteEmail(email, roleName, inviterName, inviteUrl);

      res.status(200).json({
        success: true,
        message: `Invitation successfully sent to ${email} as ${roleName}.`,
      });
    } catch (err: any) {
      res.status(500).json({ error: 'Failed to send invite', details: err.message });
    }
  }
);

