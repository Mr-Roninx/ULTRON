import pg from 'pg';
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import fs from 'node:fs';

export interface PoolMetrics {
  engine: 'PostgreSQL' | 'SQLite';
  totalCount: number;
  idleCount: number;
  waitingCount: number;
  database: string;
}

export interface TransactionClient {
  query<T = any>(sql: string, params?: any[]): Promise<T[]>;
  execute(sql: string, params?: any[]): Promise<{ rowCount: number }>;
}

export class DatabaseAdapter {
  private static instance: DatabaseAdapter | null = null;
  private pgPool: pg.Pool | null = null;
  private sqliteDb: DatabaseSync | null = null;
  private engine: 'PostgreSQL' | 'SQLite' = 'SQLite';
  private dbName: string = 'ultron.db';

  private initSqlite(cleanUrl: string): void {
    this.engine = 'SQLite';
    const cleanPath = cleanUrl.replace(/^sqlite:\/\/\/?/, '');
    const dbPath = process.env.DATABASE_PATH || (path.isAbsolute(cleanPath)
      ? cleanPath
      : path.resolve(process.cwd(), cleanPath || 'ultron.db'));

    try {
      const dir = path.dirname(dbPath);
      if (dir && !fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      this.sqliteDb = new DatabaseSync(dbPath);
    } catch (err: any) {
      console.warn(`⚠️ DatabaseAdapter: SQLite file '${dbPath}' could not be opened (${err.message}). Falling back to /tmp/ultron.db...`);
      try {
        this.sqliteDb = new DatabaseSync('/tmp/ultron.db');
      } catch {
        this.sqliteDb = new DatabaseSync(':memory:');
      }
    }

    try {
      this.sqliteDb.exec('PRAGMA journal_mode = WAL;');
      this.sqliteDb.exec('PRAGMA busy_timeout = 5000;');
      this.sqliteDb.exec('PRAGMA foreign_keys = ON;');
    } catch {}
    this.dbName = path.basename(dbPath);
    console.log(`🔌 DatabaseAdapter: Initialized SQLite engine (WAL mode, foreign_keys: ON, file: ${this.dbName})`);
  }

  private constructor() {
    let dbUrl = process.env.DATABASE_URL || '';

    // If DATABASE_URL is docker internal placeholder, fallback to SQLite
    if (dbUrl.includes('@postgres:5432') || !dbUrl) {
      this.initSqlite('sqlite:///ultron.db');
      return;
    }

    if (dbUrl.startsWith('postgres://') || dbUrl.startsWith('postgresql://')) {
      try {
        this.engine = 'PostgreSQL';
        const poolSize = Number(process.env.DATABASE_POOL_SIZE) || 10;
        this.pgPool = new pg.Pool({
          connectionString: dbUrl,
          max: poolSize,
          idleTimeoutMillis: 30000,
          connectionTimeoutMillis: 5000,
          ssl: dbUrl.includes('supabase') || dbUrl.includes('pooler') ? { rejectUnauthorized: false } : undefined,
        });
        
        try {
          const parsed = new URL(dbUrl);
          this.dbName = parsed.pathname.replace(/^\//, '') || 'ultron';
        } catch {
          this.dbName = 'ultron_pg';
        }
        console.log(`🔌 DatabaseAdapter: Initialized PostgreSQL connection pool (max: ${poolSize}, db: ${this.dbName})`);
      } catch (err: any) {
        console.warn('⚠️ Failed to initialize PostgreSQL pool, falling back to SQLite:', err.message);
        this.initSqlite('sqlite:///ultron.db');
      }
    } else {
      this.initSqlite(dbUrl);
    }
  }

  public static getInstance(): DatabaseAdapter {
    if (!DatabaseAdapter.instance) {
      DatabaseAdapter.instance = new DatabaseAdapter();
    }
    return DatabaseAdapter.instance;
  }

  public getEngine(): 'PostgreSQL' | 'SQLite' {
    return this.engine;
  }

  public getPoolMetrics(): PoolMetrics {
    if (this.engine === 'PostgreSQL' && this.pgPool) {
      return {
        engine: 'PostgreSQL',
        totalCount: this.pgPool.totalCount,
        idleCount: this.pgPool.idleCount,
        waitingCount: this.pgPool.waitingCount,
        database: this.dbName,
      };
    }

    return {
      engine: 'SQLite',
      totalCount: 1,
      idleCount: 1,
      waitingCount: 0,
      database: this.dbName,
    };
  }

  /**
   * Normalizes SQL queries across PostgreSQL ($1, $2, ...) and SQLite (?, ?, ...)
   */
  private normalizeSql(sql: string): string {
    if (this.engine === 'PostgreSQL') {
      let index = 1;
      return sql.replace(/\?/g, () => `$${index++}`);
    } else {
      // Normalize PostgreSQL $1, $2 to SQLite ?
      return sql.replace(/\$\d+/g, '?');
    }
  }

  /**
   * Executes a parameterized query and returns an array of result rows.
   */
  public async query<T = any>(sql: string, params: any[] = []): Promise<T[]> {
    const normalizedSql = this.normalizeSql(sql);

    if (this.engine === 'PostgreSQL' && this.pgPool) {
      const res = await this.pgPool.query(normalizedSql, params);
      return res.rows as T[];
    }

    if (this.sqliteDb) {
      const stmt = this.sqliteDb.prepare(normalizedSql);
      return stmt.all(...params) as unknown as T[];
    }

    throw new Error('DatabaseAdapter: No active database connection');
  }

  /**
   * Executes an INSERT/UPDATE/DELETE statement and returns affected row count.
   */
  public async execute(sql: string, params: any[] = []): Promise<{ rowCount: number }> {
    const normalizedSql = this.normalizeSql(sql);

    if (this.engine === 'PostgreSQL' && this.pgPool) {
      const res = await this.pgPool.query(normalizedSql, params);
      return { rowCount: res.rowCount || 0 };
    }

    if (this.sqliteDb) {
      const stmt = this.sqliteDb.prepare(normalizedSql);
      const res = stmt.run(...params);
      return { rowCount: Number(res.changes || 0) };
    }

    throw new Error('DatabaseAdapter: No active database connection');
  }

  /**
   * Runs a series of operations atomically inside a database transaction.
   * Automatically commits on success and rolls back on error.
   */
  public async withTransaction<T>(callback: (client: TransactionClient) => Promise<T>): Promise<T> {
    if (this.engine === 'PostgreSQL' && this.pgPool) {
      const client = await this.pgPool.connect();
      try {
        await client.query('BEGIN');
        const txClient: TransactionClient = {
          query: async (sql, params = []) => {
            const normalized = this.normalizeSql(sql);
            const res = await client.query(normalized, params);
            return res.rows;
          },
          execute: async (sql, params = []) => {
            const normalized = this.normalizeSql(sql);
            const res = await client.query(normalized, params);
            return { rowCount: res.rowCount || 0 };
          },
        };
        const result = await callback(txClient);
        await client.query('COMMIT');
        return result;
      } catch (err) {
        await client.query('ROLLBACK');
        throw err;
      } finally {
        client.release();
      }
    }

    if (this.sqliteDb) {
      this.sqliteDb.exec('BEGIN TRANSACTION;');
      try {
        const txClient: TransactionClient = {
          query: async (sql, params = []) => {
            const normalized = this.normalizeSql(sql);
            const stmt = this.sqliteDb!.prepare(normalized);
            return stmt.all(...params) as any;
          },
          execute: async (sql, params = []) => {
            const normalized = this.normalizeSql(sql);
            const stmt = this.sqliteDb!.prepare(normalized);
            const res = stmt.run(...params);
            return { rowCount: Number(res.changes || 0) };
          },
        };
        const result = await callback(txClient);
        this.sqliteDb.exec('COMMIT;');
        return result;
      } catch (err) {
        this.sqliteDb.exec('ROLLBACK;');
        throw err;
      }
    }

    throw new Error('DatabaseAdapter: No active database connection');
  }

  /**
   * Cleanly closes database connections.
   */
  public async close(): Promise<void> {
    if (this.pgPool) {
      await this.pgPool.end();
      this.pgPool = null;
    }
    if (this.sqliteDb) {
      this.sqliteDb.close();
      this.sqliteDb = null;
    }
    DatabaseAdapter.instance = null;
  }
}
