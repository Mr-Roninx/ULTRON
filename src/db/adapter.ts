import pg from 'pg';
import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';

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

  private constructor() {
    const dbUrl = process.env.DATABASE_URL || 'sqlite:///ultron.db';

    if (dbUrl.startsWith('postgres://') || dbUrl.startsWith('postgresql://')) {
      this.engine = 'PostgreSQL';
      const poolSize = Number(process.env.DATABASE_POOL_SIZE) || 10;
      this.pgPool = new pg.Pool({
        connectionString: dbUrl,
        max: poolSize,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 5000,
      });
      this.dbName = new URL(dbUrl).pathname.replace(/^\//, '') || 'ultron';
      console.log(`🔌 DatabaseAdapter: Initialized PostgreSQL connection pool (max: ${poolSize}, db: ${this.dbName})`);
    } else {
      this.engine = 'SQLite';
      const cleanPath = dbUrl.replace(/^sqlite:\/\/\/?/, '');
      const dbPath = path.isAbsolute(cleanPath)
        ? cleanPath
        : path.resolve(process.cwd(), cleanPath || 'ultron.db');

      this.sqliteDb = new DatabaseSync(dbPath);
      this.sqliteDb.exec('PRAGMA journal_mode = WAL;');
      this.sqliteDb.exec('PRAGMA busy_timeout = 5000;');
      this.sqliteDb.exec('PRAGMA foreign_keys = ON;');
      this.dbName = path.basename(dbPath);
      console.log(`🔌 DatabaseAdapter: Initialized SQLite engine (WAL mode, foreign_keys: ON, file: ${this.dbName})`);
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
