import crypto from 'node:crypto';
import { DatabaseAdapter } from '../db/adapter.js';

/**
 * Resolution of Decision D6: Secrets Management at Rest
 * Implements AES-256-GCM authenticated envelope encryption with tenant-scoped salt.
 */
export class SecretsManager {
  private static masterKey: Buffer = Buffer.from(
    process.env.ENCRYPTION_MASTER_KEY || 'ultron_v6_secure_master_encryption_key_32bytes!',
    'utf-8'
  ).subarray(0, 32);

  /**
   * Derives a tenant-specific encryption key using PBKDF2/Scrypt.
   */
  private static deriveTenantKey(tenantId: string): Buffer {
    return crypto.scryptSync(this.masterKey, `tenant_salt:${tenantId}`, 32);
  }

  /**
   * Encrypts plaintext string using AES-256-GCM.
   */
  public static encryptSecret(tenantId: string, plaintext: string): {
    encryptedData: string;
    iv: string;
    authTag: string;
  } {
    const key = this.deriveTenantKey(tenantId);
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);

    let encrypted = cipher.update(plaintext, 'utf-8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag().toString('hex');

    return {
      encryptedData: encrypted,
      iv: iv.toString('hex'),
      authTag,
    };
  }

  /**
   * Decrypts ciphertext string using AES-256-GCM with authentication tag verification.
   */
  public static decryptSecret(
    tenantId: string,
    encryptedData: string,
    ivHex: string,
    authTagHex: string
  ): string {
    const key = this.deriveTenantKey(tenantId);
    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');

    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encryptedData, 'hex', 'utf-8');
    decrypted += decipher.final('utf-8');
    return decrypted;
  }

  /**
   * Stores an encrypted tenant credential record in the database.
   */
  public static async storeTenantCredential(params: {
    tenantId: string;
    provider: string;
    environment: 'live' | 'test';
    credentialReference: string;
    rawSecret: string;
  }): Promise<void> {
    const { encryptedData, iv, authTag } = this.encryptSecret(params.tenantId, params.rawSecret);
    const db = DatabaseAdapter.getInstance();
    const now = new Date().toISOString();
    const id = `cred_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;

    await db.execute(
      `INSERT INTO tenant_credentials (id, tenant_id, provider, environment, credential_reference, encrypted_data, iv, auth_tag, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(credential_reference) DO UPDATE SET
         encrypted_data = excluded.encrypted_data,
         iv = excluded.iv,
         auth_tag = excluded.auth_tag,
         updated_at = excluded.updated_at;`,
      [
        id,
        params.tenantId,
        params.provider,
        params.environment,
        params.credentialReference,
        encryptedData,
        iv,
        authTag,
        now,
        now,
      ]
    );
  }

  /**
   * Retrieves and decrypts a tenant credential from the database.
   */
  public static async getTenantCredential(tenantId: string, credentialReference: string): Promise<string | null> {
    const db = DatabaseAdapter.getInstance();
    const rows = await db.query(
      `SELECT encrypted_data, iv, auth_tag FROM tenant_credentials WHERE tenant_id = ? AND credential_reference = ? LIMIT 1;`,
      [tenantId, credentialReference]
    );

    if (!rows || rows.length === 0) return null;
    const { encrypted_data, iv, auth_tag } = rows[0];

    try {
      return this.decryptSecret(tenantId, encrypted_data, iv, auth_tag);
    } catch (err) {
      console.error(`Failed to decrypt credential '${credentialReference}' for tenant '${tenantId}'`);
      return null;
    }
  }

  /**
   * Lists all credential references and metadata for a given tenant.
   */
  public static async listTenantCredentials(tenantId: string): Promise<Array<{ id: string; provider: string; environment: string; credentialReference: string; createdAt: string; updatedAt: string }>> {
    const db = DatabaseAdapter.getInstance();
    const rows = await db.query(
      `SELECT id, provider, environment, credential_reference, created_at, updated_at 
       FROM tenant_credentials 
       WHERE tenant_id = ? 
       ORDER BY created_at DESC;`,
      [tenantId]
    );
    
    return rows.map((row: any) => ({
      id: row.id,
      provider: row.provider,
      environment: row.environment,
      credentialReference: row.credential_reference,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    }));
  }

  /**
   * Deletes a tenant credential record.
   */
  public static async deleteTenantCredential(tenantId: string, credentialReference: string): Promise<boolean> {
    const db = DatabaseAdapter.getInstance();
    const result = await db.execute(
      `DELETE FROM tenant_credentials WHERE tenant_id = ? AND credential_reference = ?;`,
      [tenantId, credentialReference]
    );
    return result.rowCount > 0;
  }
}
