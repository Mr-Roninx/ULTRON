import crypto from 'node:crypto';
import { DatabaseAdapter } from '../db/adapter.js';

export type ApiKeyScope =
  | 'events:write'
  | 'events:read'
  | 'payments:read'
  | 'recoveries:read'
  | 'analytics:read'
  | 'agent:read'
  | 'integrations:read'
  | 'integrations:write';

export const VALID_API_KEY_SCOPES: ApiKeyScope[] = [
  'events:write',
  'events:read',
  'payments:read',
  'recoveries:read',
  'analytics:read',
  'agent:read',
  'integrations:read',
  'integrations:write',
];

export interface ApiKeyRecord {
  id: string;
  tenant_id: string;
  name: string;
  key_prefix: string;
  key_id: string;
  secret_hash: string;
  environment: 'live' | 'test';
  scopes: string[];
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
  revoked_at: string | null;
}

export class ApiKeyService {
  /**
   * Generates a new cryptographically secure API key.
   * Format: ul_{environment}_{keyId}.{rawSecret}
   * Returns rawKey (shown once only) and stores SHA-256 hash.
   */
  public static async createApiKey(params: {
    tenantId: string;
    name: string;
    environment: 'live' | 'test';
    scopes: ApiKeyScope[];
    expiresInDays?: number;
  }): Promise<{
    id: string;
    keyId: string;
    rawKey: string;
    record: ApiKeyRecord;
  }> {
    // 1. Invariant: No scope may ever include financial:execute
    for (const scope of params.scopes) {
      if ((scope as string).includes('financial:execute') || !VALID_API_KEY_SCOPES.includes(scope)) {
        throw new Error(`Invalid scope: '${scope}'. Financial execution scopes are structurally forbidden.`);
      }
    }

    const keyPrefix = `ul_${params.environment}_`;
    const keyId = crypto.randomBytes(6).toString('hex'); // 12 chars
    const rawSecret = crypto.randomBytes(16).toString('hex'); // 32 chars
    const rawKey = `${keyPrefix}${keyId}.${rawSecret}`;
    const secretHash = crypto.createHash('sha256').update(rawSecret).digest('hex');

    const id = `apk_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    const now = new Date().toISOString();
    const expiresAt = params.expiresInDays
      ? new Date(Date.now() + params.expiresInDays * 86400000).toISOString()
      : null;

    const db = DatabaseAdapter.getInstance();
    await db.execute(
      `INSERT INTO api_keys (id, tenant_id, name, key_prefix, key_id, secret_hash, environment, scopes, created_at, expires_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);`,
      [
        id,
        params.tenantId,
        params.name,
        keyPrefix,
        keyId,
        secretHash,
        params.environment,
        JSON.stringify(params.scopes),
        now,
        expiresAt,
      ]
    );

    const record: ApiKeyRecord = {
      id,
      tenant_id: params.tenantId,
      name: params.name,
      key_prefix: keyPrefix,
      key_id: keyId,
      secret_hash: secretHash,
      environment: params.environment,
      scopes: params.scopes,
      created_at: now,
      last_used_at: null,
      expires_at: expiresAt,
      revoked_at: null,
    };

    return {
      id,
      keyId,
      rawKey,
      record,
    };
  }

  /**
   * Authenticates a raw Bearer API key token.
   */
  public static async authenticateKey(rawKey: string): Promise<{
    valid: boolean;
    tenantId?: string;
    environment?: 'live' | 'test';
    scopes?: ApiKeyScope[];
    errorReason?: string;
  }> {
    if (!rawKey || (!rawKey.startsWith('ul_live_') && !rawKey.startsWith('ul_test_'))) {
      return { valid: false, errorReason: 'Malformed API key format' };
    }

    const dotIndex = rawKey.indexOf('.');
    if (dotIndex === -1) {
      return { valid: false, errorReason: 'Missing API key secret component' };
    }

    const prefixAndId = rawKey.substring(0, dotIndex);
    const rawSecret = rawKey.substring(dotIndex + 1);
    const keyId = prefixAndId.replace(/^ul_(live|test)_/, '');

    const db = DatabaseAdapter.getInstance();
    const rows = await db.query<any>(
      `SELECT * FROM api_keys WHERE key_id = ?;`,
      [keyId]
    );

    if (rows.length === 0) {
      return { valid: false, errorReason: 'API key not found' };
    }

    const record = rows[0];

    // Check revocation
    if (record.revoked_at) {
      return { valid: false, errorReason: 'API key has been revoked' };
    }

    // Check expiration
    if (record.expires_at && new Date(record.expires_at).getTime() < Date.now()) {
      return { valid: false, errorReason: 'API key has expired' };
    }

    // Verify secret hash
    const computedHash = crypto.createHash('sha256').update(rawSecret).digest('hex');
    const computedBuf = Buffer.from(computedHash, 'utf-8');
    const storedBuf = Buffer.from(record.secret_hash, 'utf-8');

    if (computedBuf.length !== storedBuf.length || !crypto.timingSafeEqual(computedBuf, storedBuf)) {
      return { valid: false, errorReason: 'Invalid API key secret' };
    }

    // Update last_used_at timestamp asynchronously
    db.execute(`UPDATE api_keys SET last_used_at = ? WHERE id = ?;`, [
      new Date().toISOString(),
      record.id,
    ]).catch(() => {});

    const scopes: ApiKeyScope[] = typeof record.scopes === 'string'
      ? JSON.parse(record.scopes)
      : record.scopes;

    return {
      valid: true,
      tenantId: record.tenant_id,
      environment: record.environment,
      scopes,
    };
  }

  /**
   * Revokes an existing API key.
   */
  public static async revokeApiKey(tenantId: string, keyId: string): Promise<boolean> {
    const db = DatabaseAdapter.getInstance();
    const now = new Date().toISOString();
    const result = await db.execute(
      `UPDATE api_keys SET revoked_at = ? WHERE tenant_id = ? AND key_id = ? AND revoked_at IS NULL;`,
      [now, tenantId, keyId]
    );
    return (result?.rowCount ?? 0) > 0;
  }

  /**
   * Lists all API keys for a tenant (without returning raw secret).
   */
  public static async listApiKeys(tenantId: string): Promise<ApiKeyRecord[]> {
    const db = DatabaseAdapter.getInstance();
    const rows = await db.query<any>(
      `SELECT id, tenant_id, name, key_prefix, key_id, secret_hash, environment, scopes, created_at, last_used_at, expires_at, revoked_at
       FROM api_keys WHERE tenant_id = ? ORDER BY created_at DESC;`,
      [tenantId]
    );

    return rows.map((r) => ({
      ...r,
      scopes: typeof r.scopes === 'string' ? JSON.parse(r.scopes) : r.scopes,
    }));
  }
}
