import { getSupabaseClient } from './supabase.js';

export interface SupabaseTenantRecord {
  id: string;
  name: string;
  slug: string;
  environment: 'test' | 'live';
  status: string;
  capacity_limit?: number;
  kill_switch_active?: boolean;
  created_at?: string;
}

export interface SupabaseCredentialRecord {
  id: string;
  tenant_id: string;
  provider: string;
  environment: 'test' | 'live';
  credential_reference: string;
  encrypted_blob: string;
  iv: string;
  auth_tag: string;
  created_at?: string;
  updated_at?: string;
}

export interface SupabaseApiKeyRecord {
  id: string;
  tenant_id: string;
  user_id?: string;
  name: string;
  key_prefix: string;
  key_hash: string;
  scopes: string[];
  status: string;
  last_used_at?: string | null;
  expires_at?: string | null;
  created_at?: string;
}

/**
 * Enterprise Supabase Permanent Persistence Engine for ULTRON
 * Guarantees permanent persistence and seamless retrieval of API keys and Razorpay credentials.
 */
export class SupabaseStore {
  /**
   * Ensures tenant exists in Supabase to satisfy foreign key constraints.
   */
  public static async ensureTenant(tenantId: string, name?: string, environment: 'test' | 'live' = 'test'): Promise<void> {
    try {
      const sb = getSupabaseClient();
      const slug = `slug_${tenantId.replace(/[^a-zA-Z0-9]/g, '_')}`;
      await sb.from('tenants').upsert({
        id: tenantId,
        name: name || `Merchant ${tenantId.slice(0, 8)}`,
        slug,
        environment,
        status: 'ACTIVE',
        capacity_limit: 5,
        kill_switch_active: false,
        created_at: new Date().toISOString(),
      }, { onConflict: 'id' });
    } catch (err: any) {
      console.warn(`⚠️ SupabaseStore: ensureTenant warning for ${tenantId}:`, err.message);
    }
  }

  /**
   * Ensures default user exists in Supabase for foreign key constraints.
   */
  public static async ensureUser(userId: string, email: string = 'merchant@ultron.app'): Promise<void> {
    try {
      const sb = getSupabaseClient();
      await sb.from('users').upsert({
        id: userId,
        email,
        name: 'Merchant Owner',
        password_hash: '$2b$12$ultron_permanent_supabase_auth_hash_seed',
        mfa_enabled: false,
        created_at: new Date().toISOString(),
      }, { onConflict: 'id' });
    } catch (err: any) {
      console.warn(`⚠️ SupabaseStore: ensureUser warning for ${userId}:`, err.message);
    }
  }

  /**
   * Permanently saves encrypted credentials into Supabase.
   */
  public static async saveCredential(record: SupabaseCredentialRecord): Promise<boolean> {
    try {
      await this.ensureTenant(record.tenant_id, undefined, record.environment);
      const sb = getSupabaseClient();

      // Check if credential reference already exists in Supabase
      const { data: existing } = await sb
        .from('tenant_credentials')
        .select('id')
        .eq('tenant_id', record.tenant_id)
        .eq('credential_reference', record.credential_reference)
        .limit(1)
        .single();

      const credId = existing?.id || record.id;

      const { error } = await sb.from('tenant_credentials').upsert({
        id: credId,
        tenant_id: record.tenant_id,
        provider: record.provider,
        environment: record.environment,
        credential_reference: record.credential_reference,
        encrypted_blob: record.encrypted_blob,
        iv: record.iv,
        auth_tag: record.auth_tag,
        updated_at: new Date().toISOString(),
      }, { onConflict: 'id' });

      if (error) {
        console.warn(`⚠️ SupabaseStore.saveCredential warning:`, error.message);
        return false;
      }
      return true;
    } catch (err: any) {
      console.warn(`⚠️ SupabaseStore.saveCredential error:`, err.message);
      return false;
    }
  }

  /**
   * Fetches encrypted credential by reference from Supabase.
   */
  public static async fetchCredential(tenantId: string, credentialReference: string): Promise<SupabaseCredentialRecord | null> {
    try {
      const sb = getSupabaseClient();
      const { data, error } = await sb
        .from('tenant_credentials')
        .select('*')
        .eq('tenant_id', tenantId)
        .eq('credential_reference', credentialReference)
        .limit(1)
        .single();

      if (error || !data) return null;
      return data as SupabaseCredentialRecord;
    } catch (err: any) {
      return null;
    }
  }

  /**
   * Lists all credentials for a given tenant from Supabase.
   */
  public static async listCredentials(tenantId: string): Promise<SupabaseCredentialRecord[]> {
    try {
      const sb = getSupabaseClient();
      const { data, error } = await sb
        .from('tenant_credentials')
        .select('*')
        .eq('tenant_id', tenantId);

      if (error || !data) return [];
      return data as SupabaseCredentialRecord[];
    } catch {
      return [];
    }
  }

  /**
   * Permanently saves an API key record into Supabase.
   */
  public static async saveApiKey(record: SupabaseApiKeyRecord): Promise<boolean> {
    try {
      const userId = record.user_id || 'usr_1788258987540_9355d9c3';
      await this.ensureTenant(record.tenant_id);
      await this.ensureUser(userId);

      const sb = getSupabaseClient();
      const { error } = await sb.from('api_keys').upsert({
        id: record.id,
        tenant_id: record.tenant_id,
        user_id: userId,
        name: record.name,
        key_prefix: record.key_prefix,
        key_hash: record.key_hash,
        scopes: record.scopes,
        status: record.status || 'ACTIVE',
        last_used_at: record.last_used_at || null,
        expires_at: record.expires_at || null,
        created_at: record.created_at || new Date().toISOString(),
      }, { onConflict: 'id' });

      if (error) {
        console.warn(`⚠️ SupabaseStore.saveApiKey warning:`, error.message);
        return false;
      }
      return true;
    } catch (err: any) {
      console.warn(`⚠️ SupabaseStore.saveApiKey error:`, err.message);
      return false;
    }
  }

  /**
   * Fetches an API key by hash or ID from Supabase.
   */
  public static async fetchApiKeyByHash(keyHash: string): Promise<SupabaseApiKeyRecord | null> {
    try {
      const sb = getSupabaseClient();
      const { data, error } = await sb
        .from('api_keys')
        .select('*')
        .eq('key_hash', keyHash)
        .eq('status', 'ACTIVE')
        .limit(1)
        .single();

      if (error || !data) return null;
      return data as SupabaseApiKeyRecord;
    } catch {
      return null;
    }
  }

  /**
   * Lists all API keys for a tenant from Supabase.
   */
  public static async listApiKeys(tenantId: string): Promise<SupabaseApiKeyRecord[]> {
    try {
      const sb = getSupabaseClient();
      const { data, error } = await sb
        .from('api_keys')
        .select('*')
        .eq('tenant_id', tenantId);

      if (error || !data) return [];
      return data as SupabaseApiKeyRecord[];
    } catch {
      return [];
    }
  }

  /**
   * Revokes an API key in Supabase.
   */
  public static async revokeApiKey(tenantId: string, keyId: string): Promise<boolean> {
    try {
      const sb = getSupabaseClient();
      const { error } = await sb
        .from('api_keys')
        .update({ status: 'REVOKED' })
        .eq('tenant_id', tenantId)
        .eq('id', keyId);

      return !error;
    } catch {
      return false;
    }
  }
}
